from scapy.all import rdpcap
from scapy.all import Ether
from scapy.plist import PacketList

ETHERTYPE_1905 = 0x893A

def reassemble_packets(pcap_local_dir):
    packets = rdpcap(pcap_local_dir)
    reassembled_packets = PacketList()
    fragment_store = {}

    for pkt in packets:
        # 1905 messages are encapsulated in Ethernet frames with EtherType 0x893A. Filter out non Ethernet packets.
        if not pkt.haslayer(Ether):
            continue
        eth = pkt[Ether]
        # Filter out non-1905 packets, since Ethernet frames can carry other protocols as well (e.g., ARP, IPv4, etc.).
        if eth.type != ETHERTYPE_1905:
            continue

        payload = bytes(eth.payload)
         # Guard against malformed/short CMDU headers
        if len(payload) < 8:
            continue
        # Extract fields from CMDU header
        message_type = (payload[2] << 8) | payload[3]
        message_id   = (payload[4] << 8) | payload[5]
        fragment_id = payload[6]
        last_fragment = (payload[7] >> 7) & 0x01
        # Improved key
        key = (eth.src, message_type, message_id)

        # Case 1: Not fragmented
        if fragment_id == 0 and last_fragment == 1:
            reassembled_packets.append(pkt)
            #process_complete_message(message_type, payload, eth)
            continue

        # Case 2: Fragmented packet — store the header and fragment per key
        if key not in fragment_store:
            header = bytearray(payload[:8])
            header[7] = 0x80                     # mark reassembled frame as last fragment
            fragment_store[key] = {"header": header, "fragments": []}

        fragment_store[key]["fragments"].append((fragment_id, payload[8:]))

        # Case 3: Last fragment received
        if last_fragment == 1:
            entry = fragment_store[key]
            entry["fragments"].sort(key=lambda x: x[0])
            reassembled = entry["header"] + b''.join(f[1] for f in entry["fragments"])
            # Store reassembled frame as a proper Ethernet packet so downstream
            # code can safely access Ether fields (src/dst/type).
            reassembled_pkt = Ether(dst=eth.dst, src=eth.src, type=ETHERTYPE_1905) / bytes(reassembled)
            reassembled_packets.append(reassembled_pkt)
            del fragment_store[key]

    return reassembled_packets


#message presence checker function to check if the message is present in the captured packets. if present return list of payload of the same message type
#  else return None
def check_message_presence(reassembled_packets, message_type, src_mac=None, dst_mac=None):
    matching_payloads = []
    for pkt in reassembled_packets:
        if not pkt.haslayer(Ether):
            continue
        eth = pkt[Ether]
        if eth.type != ETHERTYPE_1905:
            continue
        payload = bytes(eth.payload)

        if len(payload) < 4:
            continue
        msg_type = (payload[2] << 8) | payload[3]

        if msg_type != message_type:
            continue
        if src_mac and eth.src.lower() != src_mac.lower():
            continue
        if dst_mac and eth.dst.lower() != dst_mac.lower():
            continue
        matching_payloads.append(payload)
    return matching_payloads or None

#return the list of tlvs present in the message payload. 
def check_tlv_presence(message_payload, tlv_type=None):
    if len(message_payload) < 8:
        return None
    tlvs = []
    index = 8  # TLVs start after the 8-byte header
    while index + 3 <= len(message_payload):
        current_tlv_type = message_payload[index]
        current_tlv_length = (message_payload[index + 1] << 8) | message_payload[index + 2]
        end = index + 3 + current_tlv_length
        if end > len(message_payload):
            break
        # Raw TLV bytes: 1-byte type + 2-byte length + value
        current_tlv_raw = message_payload[index:end]
        if tlv_type is None or current_tlv_type == tlv_type:
            tlvs.append(current_tlv_raw)
         # End-of-Message TLV
        if current_tlv_type == 0x00 and current_tlv_length == 0:
            break
        index = end
    return tlvs or None

