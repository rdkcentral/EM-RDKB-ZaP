# Copyright 2026 RDK Management
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pathlib import Path
import pytest
from scapy.all import rdpcap
from scapy.all import Ether
from scapy.plist import PacketList
from .message_verify import *
import pytest_check as check
from zaero.utils import zi_logger
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
            header[6] = 0x00                  # reassembled CMDU should have fragment_id = 0
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
def get_tlv_from_config():
    yaml_path = Path(__file__).with_name("config_ver6.yaml")
    tlv_data = load_yaml(str(yaml_path))
    return tlv_data
def parse_tlvs(payload):
    """
    Parse TLVs from IEEE1905 payload.
    Input:
        payload (bytes)
    Returns:
        found_tlvs (list)
        tlv_lengths (list)
        tlv_values (list)
        end_of_message_found (bool)
        error (None or string)
    """
    tlv_start = 8
    current_position = tlv_start
    found_tlvs = []  # Changed from set to list to preserve order
    tlv_lengths = []
    tlv_values = []  # New list to store TLV values
    found_end_of_message = False
    while current_position < len(payload):
        # Check TLV header size
        if current_position + 3 > len(payload):
            return None, None, None, False, "Incomplete TLV header"
        tlv_type = payload[current_position]
        tlv_length = (payload[current_position + 1] << 8) | payload[current_position + 2]
        # Extract TLV value
        tlv_value_start = current_position + 3
        tlv_value_end = tlv_value_start + tlv_length
        if tlv_value_end > len(payload):
            return None, None, None, False, "Incomplete TLV value"
        tlv_value = payload[tlv_value_start:tlv_value_end]
        found_tlvs.append(tlv_type)  # Append to list to preserve order
        tlv_lengths.append(tlv_length)
        tlv_values.append(tlv_value)  # Append TLV value
        # Check End of Message
        if tlv_type == TLV_TYPE_END_OF_MESSAGE:
            found_end_of_message = True
            break
        current_position += 3 + tlv_length
    return found_tlvs, tlv_lengths, tlv_values, found_end_of_message, None
def extract_profile_type(filtered_packets):
    """
    Extract profile type from 1905 messages.
    Args:
        filtered_packets: list of reassembled and filtered packets
    Returns:
        Profile type value if found, None otherwise
    """
    message_presence = False
    tlv_presence = False
    for pkt in filtered_packets:
        eth = pkt[Ether]       
        if eth.type != ETHERTYPE_1905:
            continue       
        payload = bytes(eth.payload)
        message_type = (payload[2] << 8) | payload[3]
        #check if the message type is AP Autoconfiguration search or topology query message or topology response message or BSS Configuration Request
        if message_type == MSG_TYPE_AP_AUTOCONFIG_SEARCH or message_type == MSG_TYPE_AP_TOPOLOGY_QUERY or message_type == MSG_TYPE_AP_TOPOLOGY_RESPONSE or message_type == MSG_TYPE_BSS_CONFIGURATION_REQUEST:
            message_presence = True
            found_tlvs, _, tlv_values, _, error = parse_tlvs(payload)
            if error or not found_tlvs:
                pytest.fail(error or "extract_profile_type: Failed to parse TLVs from payload", pytrace=False)
            for tlv_type, tlv_value in zip(found_tlvs, tlv_values):
                if tlv_type == TLV_TYPE_MULTI_AP_PROFILE:
                    tlv_presence = True
                    # Profile type is typically at offset 0 in Multi-AP Profile TLV
                    if len(tlv_value) == 1:
                        profile_type = tlv_value[0]
                        if profile_type in [0x01, 0x02, 0x03]:
                            profile_name = get_profile_name(profile_type)
                            zi_logger.print_success(f"Profile type extracted: 0x{profile_type:02X} ({profile_name})")
                            return profile_type
                        else:
                            zi_logger.print_error(f"Profile type extracted: 0x{profile_type:02X} (Unknown profile type)")
                            pytest.fail(f"Profile type extracted: 0x{profile_type:02X} (Unknown profile type)", pytrace=False)
                    else:
                        zi_logger.print_error("Multi-AP Profile TLV found but length is insufficient to extract profile type")
                        pytest.fail("Multi-AP Profile  TLV found but length is insufficient to extract profile type", pytrace=False)
    if not message_presence:
        zi_logger.print_error("Can't detect profile : AP Autoconfiguration search message or topology query message or topology response message or bss configuration request not found in the capture file.")
        pytest.fail("Can't detect profile : AP Autoconfiguration search message or topology query message or topology response message or bss configuration request not found in the capture file", pytrace=False)
    if not tlv_presence:
        zi_logger.print_error("Multi-AP Profile TLV not found")
        pytest.fail("Multi-AP Profile TLV not found", pytrace=False)
def verify_tlv_presence_with_type(requested_message_type, tlv_to_verify, payload):
    """
    Verify if a specific TLV type is present in a message
    Args:
        requested_message_type: CMDU message type to search for
        tlv_to_verify: TLV type to verify presence
        payload: The payload of the message to search within
    Returns:
        True if TLV is found, False otherwise
    """
    tlv_presence_flag = False
    tlv_length_valid_flag = False
    expected_tlv_length = ""
    found_tlvs, tlv_length, tlv_values, _, error = parse_tlvs(payload)
    if error or not found_tlvs:
        return False, error or "Failed to parse TLVs from payload"   
    for tlv_type, tlv_length, tlv_value in zip(found_tlvs, tlv_length, tlv_values):
        if tlv_type == tlv_to_verify:
            tlv_presence_flag = True
            expected_tlv_length, tlv_length_valid_flag = validate_tlv_length(tlv_to_verify, tlv_length)
            break
    if tlv_presence_flag and tlv_length_valid_flag:
        zi_logger.print_success(f"{get_tlv_type_name(tlv_to_verify)} is present in the {get_message_type_name(requested_message_type)} and the expected tlv length is {expected_tlv_length} and actual tlv length is {tlv_length}")
        return True, ""    
    if tlv_presence_flag and not tlv_length_valid_flag:
        zi_logger.print_success(f"{get_tlv_type_name(tlv_to_verify)} present in the {get_message_type_name(requested_message_type)}")
        zi_logger.print_error(f"{get_tlv_type_name(tlv_to_verify)} length is invalid in the {get_message_type_name(requested_message_type)}, expected tlv length is {expected_tlv_length} and actual tlv length is {tlv_length}")
        return False, f"Invalid TLV length for {get_tlv_type_name(tlv_to_verify)}: expected {expected_tlv_length}, got {tlv_length}"    
    if not tlv_presence_flag:
        zi_logger.print_error(f"{get_tlv_type_name(tlv_to_verify)} not found in {get_message_type_name(requested_message_type)}")
        return False, f"{get_tlv_type_name(tlv_to_verify)} not found in {get_message_type_name(requested_message_type)}"
def verify_no_additional_tlvs(message_type, mandatory_tlvs, optional_tlvs, payload):
    """
    Check for additional TLVs in a message beyond the mandatory ones.
    Input:
        message_type (int): CMDU message type to search for
        mandatory_tlvs (set): Set of mandatory TLV types
        optional_tlvs (set): Set of optional TLV types
        payload (bytes): The payload of the CMDU message to analyze
    Returns:
        additional_tlvs (set): Set of additional TLV types found beyond mandatory ones, or empty if none found
    """
    found_tlvs, _, _, _, error = parse_tlvs(payload)
    if error or not found_tlvs:
        pytest.fail(error or "verify_no_additional_tlvs: Failed to parse TLVs from payload", pytrace=False)
    found_set = set(found_tlvs)
    mandatory_set = set(mandatory_tlvs)
    optional_set = set(optional_tlvs)    
    extra_tlvs = found_set - mandatory_set - optional_set
    if extra_tlvs:
        extra_tlvs_list = [f"{get_tlv_type_name(tlv)} (0x{tlv:02X})" for tlv in sorted(extra_tlvs)]
        zi_logger.print_error(f" Found Extra TLVs (neither mandatory nor optional) in {get_message_type_name(message_type)}: {extra_tlvs_list}")
        return False
    else:
        zi_logger.print_success(f"No extra TLVs found beyond mandatory and optional tlvs in {get_message_type_name(message_type)}.")
        return True
def validate_1905_message(tlv_data_from_config, profiletype, message, payload, controller_or_agent = None):
    """
    Validate a 1905 message against expected mandatory and optional TLVs based on profile and message type.
    Args:
        tlv_data_from_config: TLV data loaded from configuration
        profiletype: Multi-AP profile type (1, 2, or 3)
        message: CMDU message type to validate
        controller_or_agent (str, optional): Specify "controller" or "agent" to validate
    Returns: None. Prints validation results and errors.
    """
    message_type_string = get_message_type_name(message)
    profiles_cfg = tlv_data_from_config.get("profiles", {})
    profile_cfg = profiles_cfg.get(profiletype)
    if profile_cfg is None:
        zi_logger.log(f"Profile {profiletype} is not defined in the configuration. Skipping validation for {message_type_string}.")
        return
    message_cfg = profile_cfg.get(message)
    if message_cfg is None:
        zi_logger.log(
            f"No TLV definition found for {message_type_string} (0x{message:04X}) in profile {profiletype}. "
            "Skipping validation for this message."
        )
        return
    if controller_or_agent == "controller":
        role_cfg = message_cfg.get("controller_tlvs")
        if role_cfg is None:
            zi_logger.log(
                f"No controller-specific TLV definition found for {message_type_string} in profile {profiletype}. "
                "Skipping validation for this message."
            )
            return
        mandatory = role_cfg.get("mandatory_tlvs", []) or []
        optional = role_cfg.get("optional_tlvs", []) or []
    elif controller_or_agent == "agent":
        role_cfg = message_cfg.get("agent_tlvs")
        if role_cfg is None:
            zi_logger.log(
                f"No agent-specific TLV definition found for {message_type_string} in profile {profiletype}. "
                "Skipping validation for this message."
            )
            return
        mandatory = role_cfg.get("mandatory_tlvs", []) or []
        optional = role_cfg.get("optional_tlvs", []) or []
    else:
        mandatory = message_cfg.get("mandatory_tlvs", []) or []
        optional = message_cfg.get("optional_tlvs", []) or []
    if not mandatory:
        zi_logger.log(f"No mandatory TLVs defined for {message_type_string} in the profile. Skipping mandatory TLV presence verification.")
    else:
        for index, tlv in enumerate(mandatory, start=1):
            tlv_type_string = get_tlv_type_name(tlv)
            zi_logger.log(f"Analyzing the {message_type_string}" +(f" from {controller_or_agent}" if controller_or_agent else "")+f" to verify the presence of the {tlv_type_string}")
            # if controller_or_agent:
            tlv_validation_result, reason = verify_tlv_presence_with_type(message, tlv, payload)
            check.equal(tlv_validation_result, True, f"\nFail: {reason}")
    zi_logger.log(f"Analyzing the {message_type_string}" +(f" from {controller_or_agent}" if controller_or_agent else "")+" to check for any unexpected TLVs that are not defined as mandatory or optional in the profile")
    check.equal(verify_no_additional_tlvs(message, mandatory, optional, payload), True, f"\nFail: Extra TLVs found in {message_type_string}" +(f" from {controller_or_agent}" if controller_or_agent else "")+ f" that are not listed as mandatory or optional in the profile definition.")
def packet_analyzer(pcap_local_dir, ctrl_al_mac=None, extender_al_mac=None):
    reassembled_packets = reassemble_packets(pcap_local_dir)
    #add logic to print the message types in the captured packets and its count
    message_type_count = {}
    for pkt in reassembled_packets:
        eth = pkt[Ether]
        if eth.type != ETHERTYPE_1905:
            continue
        payload = bytes(eth.payload)
        message_type = (payload[2] << 8) | payload[3]
        message_type_name = get_message_type_name(message_type)
        if message_type_name not in message_type_count:
            message_type_count[message_type_name] = 0
        message_type_count[message_type_name] += 1
    for message_type_name, count in message_type_count.items():
        print(f"Message type: {message_type_name}, Count: {count}")
    filtered_packets = [
        pkt for pkt in reassembled_packets
        if pkt.haslayer(Ether) and
           ((pkt[Ether].src == ctrl_al_mac.lower() and pkt[Ether].dst == extender_al_mac.lower()) or
            (pkt[Ether].src == extender_al_mac.lower() and pkt[Ether].dst == ctrl_al_mac.lower()))
    ]
    if not filtered_packets:
        pytest.fail(f"No messages between controller {ctrl_al_mac} and agent {extender_al_mac} found in the capture file.", pytrace=False)
    profiletype = extract_profile_type(filtered_packets)
    tlv_data_from_config = get_tlv_from_config()
    #iterate through the captured packets and validate the messages
    for pkt in filtered_packets:
        controller_or_agent = None
        eth = pkt[Ether]
        if eth.type != ETHERTYPE_1905:
            continue
        payload = bytes(eth.payload)
        # Extract fields from CMDU header
        message_type = (payload[2] << 8) | payload[3]
        # check if the message is from controller or agent. This is valid incase of AP Autoconfiguration WSC Messages
        if message_type == MSG_TYPE_AP_AUTOCONFIGURATION_WSC:
            if eth.src == ctrl_al_mac.lower():
                controller_or_agent = "controller"
            else:
                controller_or_agent = "agent"
        message_type_name = get_message_type_name(message_type)
        if not message_type_name.startswith("Unknown message type"):
            # if message_type == conftest.MSG_TYPE_AP_CAPABILITY_QUERY:
            zi_logger.print_step(f"Validating {message_type_name} from captured packets")
            validate_1905_message(tlv_data_from_config, profiletype, message_type, payload, controller_or_agent)
            zi_logger.print_step(f"{get_message_type_name(message_type)} validation completed successfully")