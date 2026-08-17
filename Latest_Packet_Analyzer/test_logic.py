from . import conftest
from scapy.all import rdpcap, Ether
from . import message_verify
import pytest
from scapy.plist import PacketList
from .ieee1905_utils import print_completed_step, print_success, print_error, print_step, print_warning, print_main_step, print_sub_step
from .ieee1905_utils import *
from pathlib import Path


controller_mac = conftest.controller_mac
agent_mac = conftest.agent_mac



fragment_store = {}
header_1905 = ""
ETHERTYPE_1905 = 0x893A
reassembled_packets = PacketList()


def packet_parser(flow_packets):
    global header_1905
    for pkt in flow_packets:
        if not pkt.haslayer(Ether):
            continue
        eth = pkt[Ether]
        if eth.type != ETHERTYPE_1905:
            continue

        payload = bytes(eth.payload)
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

        # Extract and store 1905 header (first 8 bytes)
        if not header_1905:
            header_1905 = bytearray(payload[:8])
            header_1905[7] = 0x80

        payload = payload[8:]
        # Case 2: Fragmented packet
        if key not in fragment_store:
            fragment_store[key] = []

        fragment_store[key].append((fragment_id, payload))
        # Case 3: Last fragment received
        if last_fragment == 1:
            fragments = fragment_store[key]
            # Sort fragments by fragment id
            fragments.sort(key=lambda x: x[0])
            # Combine payloads
            reassembled = header_1905 + b''.join([f[1] for f in fragments])
            header_1905 = ""
            # Store reassembled frame as a proper Ethernet packet so downstream
            # code can safely access Ether fields (src/dst/type).
            reassembled_pkt = Ether(dst=eth.dst, src=eth.src, type=ETHERTYPE_1905) / bytes(reassembled)
            reassembled_packets.append(reassembled_pkt)
            # Clear buffer
            del fragment_store[key]


def get_profile_details(pcap_local_dir):

    packets = rdpcap(pcap_local_dir)
    # Step 1: Filter packets between controller and agent
    flow_packets = [
        pkt for pkt in packets
        if pkt.haslayer(Ether) and
           ((pkt[Ether].src == controller_mac.lower() and pkt[Ether].dst == agent_mac.lower()) or
            (pkt[Ether].src == agent_mac.lower() and pkt[Ether].dst == controller_mac.lower()))
    ]

    if not flow_packets:
        print_error(f"No messages between controller {controller_mac} and agent {agent_mac} found in the capture file.")
        pytest.fail(f"No messages between controller {controller_mac} and agent {agent_mac} found in the capture file.", pytrace=False)
    
    packet_parser(flow_packets)
    print(f"Total packets between controller {controller_mac} and agent {agent_mac} in the capture file: {len(flow_packets)}")
    print(f"Total packets in after reassembly: {len(reassembled_packets)}")

    #add logic to print the message types in the captured packets and its count
    message_type_count = {}
    for pkt in reassembled_packets:
        eth = pkt[Ether]
        if eth.type != ETHERTYPE_1905:
            continue
        payload = bytes(eth.payload)
        message_type = (payload[2] << 8) | payload[3]
        message_type_name = message_verify.get_message_type_name(message_type)
        if message_type_name not in message_type_count:
            message_type_count[message_type_name] = 0
        message_type_count[message_type_name] += 1

    for message_type_name, count in message_type_count.items():
        print(f"Message type: {message_type_name}, Count: {count}")


    print_main_step("Trying to extract profile type from AP Autoconfiguration Response message in captured packets")
    # profiletype = message_verify.extract_profile_type_from_autoconfig_response(pcap_local_dir)
    profiletype = 0x03
    yaml_path = Path(__file__).with_name("config_ver6.yaml")
    tlv_data = message_verify.load_yaml(str(yaml_path))
    return profiletype, tlv_data
    
def packet_analyzer(pcap_local_dir):
    profiletype, tlv_data = get_profile_details(pcap_local_dir)
    #iterate through the captured packets and validate the messages
    for pkt in reassembled_packets:
        controller_or_agent = None
        eth = pkt[Ether]
        if eth.type != ETHERTYPE_1905:
            continue

        payload = bytes(eth.payload)
        # Extract fields from CMDU header
        message_type = (payload[2] << 8) | payload[3]
        # check if the message is from controller or agent. This is valid incase of AP Autoconfiguration WSC Messages
        if message_type == conftest.MSG_TYPE_AP_AUTOCONFIG_WSC:
            if eth.src == controller_mac.lower():
                controller_or_agent = "controller"
            else:
                controller_or_agent = "agent"
  
        message_type_name = message_verify.get_message_type_name(message_type)
        if not message_type_name.startswith("Unknown message type"):
            # if message_type == conftest.MSG_TYPE_AP_CAPABILITY_QUERY:
            print_main_step(f"Validating {message_type_name} from captured packets")
            message_verify.validate_1905_message(tlv_data, profiletype, message_type, payload, controller_or_agent)
            print_completed_step(f"{message_verify.get_message_type_name(message_type)} validation completed successfully")

