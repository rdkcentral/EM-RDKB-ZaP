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
import sys
import pytest
from scapy.all import rdpcap
from scapy.all import Ether
from scapy.plist import PacketList
from .message_verify import *
from zaero.utils import zi_logger
from rdkbmeshzap.common_utils import report_logger

ETHERTYPE_1905 = 0x893A
#create an empty error list to collect all errors and print at the end
error_list = []
message_frame_map = {}

def reassemble_packets(pcap_local_dir):
    """
    Syntax : reassemble_packets(pcap_local_dir)
    Description : Reads an IEEE 1905 capture file and reassembles fragmented CMDU messages.
    Parameters :
        pcap_local_dir - Path to the packet capture file to process.
    Return Value: A PacketList containing complete and reassembled IEEE 1905 Ethernet packets.
    """
    packets = rdpcap(pcap_local_dir)
    reassembled_packets = PacketList()
    fragment_store = {}
    frame_number = 0
    for pkt in packets:
        #capture frame number
        frame_number = frame_number + 1
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
        message_frame_map[(message_type, message_id)] = frame_number
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
            reassembled_pkt = Ether(dst=eth.dst, src=eth.src, type=ETHERTYPE_1905) / bytes(reassembled)
            reassembled_pkt.time = pkt.time
            reassembled_packets.append(reassembled_pkt)
            del fragment_store[key]
    return reassembled_packets

def check_message_presence(reassembled_packets, message_type, src_mac=None, dst_mac=None):
    """
    Syntax : check_message_presence(reassembled_packets, message_type, src_mac=None, dst_mac=None)
    Description : Finds payloads for a CMDU message type, optionally limited to source and destination MAC addresses.
    Parameters :
        reassembled_packets - PacketList of reassembled IEEE 1905 packets to search.
        message_type - Numeric CMDU message type to locate.
        src_mac - Optional source MAC address filter.
        dst_mac - Optional destination MAC address filter.
    Return Value: A list of matching payload bytes, or None when no matching message is found.
    """
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

def check_tlv_presence(message_payload, tlv_type=None):
    """
    Syntax : check_tlv_presence(message_payload, tlv_type=None)
    Description : Extracts TLVs from a CMDU payload, optionally filtering by TLV type.
    Parameters :
        message_payload - CMDU payload bytes containing an 8-byte header followed by TLVs.
        tlv_type - Optional numeric TLV type to include.
    Return Value: A list of raw TLV bytes, or None when no matching TLV is present.
    """
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
    """
    Syntax : get_tlv_from_config()
    Description : Loads IEEE 1905 profile and TLV validation rules from config_ver6.yaml.
    Parameters :
        None.
    Return Value: The parsed TLV configuration data.
    """
    yaml_path = Path(__file__).with_name("config_ver6.yaml")
    tlv_data = load_yaml(str(yaml_path))
    return tlv_data

def parse_tlvs(payload):
    """
    Syntax : parse_tlvs(payload)
    Description : Parses TLV types, lengths, and values from an IEEE 1905 CMDU payload.
    Parameters :
        payload - CMDU payload bytes containing an 8-byte header followed by TLVs.
    Return Value: A five-item tuple containing TLV types, TLV lengths, TLV values, an end-of-message flag, and an error string or None.
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
    Syntax : extract_profile_type(filtered_packets)
    Description : Extracts and validates the Multi-AP profile type from supported IEEE 1905 messages.
    Parameters :
        filtered_packets - Reassembled IEEE 1905 packets to inspect.
    Return Value: The numeric Multi-AP profile type when found; otherwise the function fails the current pytest test.
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
                raise ValueError(error or "extract_profile_type: Failed to parse TLVs from payload")
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
                            raise ValueError(f"Profile type extracted: 0x{profile_type:02X} (Unknown profile type)")
                    else:
                        raise ValueError("Multi-AP Profile TLV found but length is insufficient to extract profile type")
    if not message_presence:
        raise ValueError("Can't detect profile : AP Autoconfiguration search message or topology query message or topology response message or bss configuration request not found in the capture file.")
    if not tlv_presence:
        raise ValueError("Multi-AP Profile TLV not found")

def verify_tlv_presence_with_type(requested_message_type, tlv_to_verify, payload):
    """
    Syntax : verify_tlv_presence_with_type(requested_message_type, tlv_to_verify, payload)
    Description : Verifies that a specified TLV exists in a CMDU payload and has a valid configured length.
    Parameters :
        requested_message_type - Numeric CMDU message type used in validation output.
        tlv_to_verify - Numeric TLV type to find and validate.
        payload - CMDU payload bytes to inspect.
    Return Value: None. Validation results are written to the report logger and error list.
    """
    message_type = (payload[2] << 8) | payload[3]
    message_id   = (payload[4] << 8) | payload[5]
    frame_number = message_frame_map.get((message_type, message_id))
    tlv_presence_flag = False
    tlv_length_valid_flag = False
    expected_tlv_length = ""
    found_tlvs, tlv_length, tlv_values, _, error = parse_tlvs(payload)
    if error or not found_tlvs:
        raise ValueError(error or "Failed to parse TLVs from payload")
    for tlv_type, tlv_length, tlv_value in zip(found_tlvs, tlv_length, tlv_values):
        if tlv_type == tlv_to_verify:
            tlv_presence_flag = True
            expected_tlv_length, tlv_length_valid_flag = validate_tlv_length(tlv_to_verify, tlv_length)
            break
    if tlv_presence_flag and tlv_length_valid_flag:
        report_logger.print_success(f"PASS: {get_tlv_type_name(tlv_to_verify)} is present and the expected tlv length is {expected_tlv_length} and actual tlv length is {tlv_length}")  
    if tlv_presence_flag and not tlv_length_valid_flag:
        report_logger.print_success(f"PASS:{get_tlv_type_name(tlv_to_verify)} present.")
        report_logger.print_error(f"FAIL: framenumber :{frame_number} {get_tlv_type_name(tlv_to_verify)} length is invalid. expected tlv length is {expected_tlv_length} and actual tlv length is {tlv_length}")
        error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
    if not tlv_presence_flag:
        report_logger.print_error(f"FAIL: framenumber :{frame_number} {get_tlv_type_name(tlv_to_verify)} not found.")
        error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")

def verify_no_additional_tlvs(message_type, mandatory_tlvs, optional_tlvs, payload):
    """
    Syntax : verify_no_additional_tlvs(message_type, mandatory_tlvs, optional_tlvs, payload)
    Description : Checks that a CMDU payload contains no TLVs outside its mandatory and optional definitions.
    Parameters :
        message_type - Numeric CMDU message type used in validation output.
        mandatory_tlvs - Iterable of required TLV types.
        optional_tlvs - Iterable of allowed optional TLV types.
        payload - CMDU payload bytes to inspect.
    Return Value: True when no unexpected TLVs are found; otherwise False.
    """
    message_type = (payload[2] << 8) | payload[3]
    message_id   = (payload[4] << 8) | payload[5]
    frame_number = message_frame_map.get((message_type, message_id))
    found_tlvs, _, _, _, error = parse_tlvs(payload)
    if error or not found_tlvs:
        raise ValueError(error or "verify_no_additional_tlvs: Failed to parse TLVs from payload")
    found_set = set(found_tlvs)
    mandatory_set = set(mandatory_tlvs)
    optional_set = set(optional_tlvs)    
    extra_tlvs = found_set - mandatory_set - optional_set
    if extra_tlvs:
        extra_tlvs_list = [f"{get_tlv_type_name(tlv)} (0x{tlv:02X})" for tlv in sorted(extra_tlvs)]
        report_logger.print_error(f"FAIL: framenumber :{frame_number} Found Extra TLVs (neither mandatory nor optional) in {get_message_type_name(message_type)}: {extra_tlvs_list}")
        error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
    else:
        report_logger.print_success(f"PASS: No extra TLVs found beyond mandatory and optional tlvs in {get_message_type_name(message_type)}.")

def validate_1905_message(tlv_data_from_config, profiletype, message, payload, controller_or_agent = None):
    """
    Syntax : validate_1905_message(tlv_data_from_config, profiletype, message, payload, controller_or_agent=None)
    Description : Validates a CMDU payload against the mandatory and optional TLVs configured for its profile and device role.
    Parameters :
        tlv_data_from_config - Parsed TLV configuration data.
        profiletype - Numeric Multi-AP profile type.
        message - Numeric CMDU message type to validate.
        payload - CMDU payload bytes to inspect.
        controller_or_agent - Optional role, either controller or agent, for role-specific TLV rules.
    Return Value: None. Validation results are written to the report logger.
    """
    message_type_string = get_message_type_name(message)
    profiles_cfg = tlv_data_from_config.get("profiles", {})
    profile_cfg = profiles_cfg.get(profiletype)
    if profile_cfg is None:
        report_logger.print_info(f"INFO: Profile {profiletype} is not defined in the configuration. Skipping validation for {message_type_string}.")
        return
    message_cfg = profile_cfg.get(message)
    if message_cfg is None:
        report_logger.print_info(
            f"INFO: No TLV definition found for {message_type_string} (0x{message:04X}) in profile {profiletype}. "
            "Skipping validation for this message."
        )
        return
    if controller_or_agent == "controller":
        role_cfg = message_cfg.get("controller_tlvs")
        if role_cfg is None:
            report_logger.print_info(
                f"INFO: No controller-specific TLV definition found for {message_type_string} in profile {profiletype}. "
                "Skipping validation for this message."
            )
            return
        mandatory = role_cfg.get("mandatory_tlvs", []) or []
        optional = role_cfg.get("optional_tlvs", []) or []
    elif controller_or_agent == "agent":
        role_cfg = message_cfg.get("agent_tlvs")
        if role_cfg is None:
            report_logger.print_info(
                f"INFO: No agent-specific TLV definition found for {message_type_string} in profile {profiletype}. "
                "Skipping validation for this message."
            )
            return
        mandatory = role_cfg.get("mandatory_tlvs", []) or []
        optional = role_cfg.get("optional_tlvs", []) or []
    else:
        mandatory = message_cfg.get("mandatory_tlvs", []) or []
        optional = message_cfg.get("optional_tlvs", []) or []
    
    if not mandatory:
        report_logger.print_info(f"INFO: No mandatory TLVs defined for {message_type_string} in the profile. Skipping mandatory TLV presence verification.")
    else:
        for index, tlv in enumerate(mandatory, start=1):
            tlv_type_string = get_tlv_type_name(tlv)
            report_logger.print_info(f"INFO: checking the presence of the {tlv_type_string}")
            try:
                verify_tlv_presence_with_type(message, tlv, payload)
            except ValueError as e:
                report_logger.print_error(f"FAIL: {str(e)}")
                error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
                return
    report_logger.print_info(f"INFO: check for any unexpected TLVs that are not defined as mandatory or optional in the profile")
    try:
        verify_no_additional_tlvs(message, mandatory, optional, payload)
    except ValueError as e:
        report_logger.print_error(f"FAIL: {str(e)}")
        error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
        return

def parse_config(tlv_data_from_config, profiletype, message):
    """
    syntax : parse_config(tlv_data_from_config, profiletype, message)
    Description : Parses the TLV configuration for a given profile and message type, returning the list of mandatory TLVs if defined.
    Parameters :
        tlv_data_from_config - The TLV configuration data.
        profiletype - The profile type to look up in the configuration.
        message - The message type to look up in the configuration.
    Return Value :
        A tuple containing two lists:
        - The first list contains the mandatory TLVs for the specified message in the profile.
        - The second list contains the optional TLVs for the specified message in the profile.

    """
    message_type_string = get_message_type_name(message)
    mandatory_tlv_list = []
    optional_tlv_list = []
    profiles_cfg = tlv_data_from_config.get("profiles", {})
    profile_cfg = profiles_cfg.get(profiletype)
    if profile_cfg is None:
        raise ValueError(f"Profile {profiletype} is not defined in the configuration.")
    message_cfg = profile_cfg.get(message)
    if message_cfg is None:
        raise ValueError(f"Message {message_type_string} (0x{message:04X}) is not defined in profile {profiletype}.")
    mandatory_tlv_list = message_cfg.get("mandatory_tlvs", []) or []
    optional_tlv_list = message_cfg.get("optional_tlvs", []) or []
    #check if mandatory_tlv_list lists are empty and raise value error
    if not mandatory_tlv_list:
        raise ValueError(f"No mandatory TLVs defined for message {message_type_string} (0x{message:04X}) in profile {profiletype}.")
    return mandatory_tlv_list, optional_tlv_list

def packet_analyzer(pcap_local_dir, initialize, al_mac1=None, al_mac2=None):
    """
    Syntax : packet_analyzer(pcap_local_dir, al_mac1=None, al_mac2=None)
    Description : Reassembles IEEE 1905 packets from a capture file, filters them by AL MAC addresses, and validates known CMDU messages.
    Parameters :
        pcap_local_dir - Path to the packet capture file to analyze.
        al_mac1 - Optional first AL MAC address used to filter packets.
        al_mac2 - Optional second AL MAC address used to filter packets.
    Return Value: None. Message counts and validation results are written to the report logger.
    """
    report_logger.print_info("INFO: Entering packet_analyzer")
    profile_dict = initialize.read_from_database("test_parameters","profile_type")
    if "device_present" in profile_dict:
        del profile_dict["device_present"]
    for key, value in profile_dict.items():
        if "aa:bb:cc:dd:ee:ff" in key:
            report_logger.print_error(f"FAIL: kindly update the device al mac and profile type in the database.")
            error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
            return
        if type(value) is not int or value not in (0x01, 0x02, 0x03):
            report_logger.print_error(f"FAIL: Invalid Multi-AP profile type {value!r} for {key}; expected 0x01, 0x02, or 0x03.")
            error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
            return
    reassembled_packets = reassemble_packets(pcap_local_dir)
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
        report_logger.print_info(
            f"INFO: Message type: {message_type_name}, Count: {count}"
        )

    if al_mac1 is None and al_mac2 is None:
        filtered_packets = reassembled_packets
    if al_mac2 is None and al_mac1 is not None:
        filtered_packets = [
            pkt for pkt in reassembled_packets
            if pkt.haslayer(Ether) and
               (pkt[Ether].src == al_mac1.lower() or pkt[Ether].dst == al_mac1.lower())
        ]
    if al_mac1 is None and al_mac2 is not None:
        filtered_packets = [
            pkt for pkt in reassembled_packets
            if pkt.haslayer(Ether) and
               (pkt[Ether].src == al_mac2.lower() or pkt[Ether].dst == al_mac2.lower())
        ]
    if al_mac2 is not None and al_mac1 is not None:
        #filter packets where src is ctrl_mac and dst is ext_mac or vice versa
        filtered_packets = [
            pkt for pkt in reassembled_packets
            if pkt.haslayer(Ether) and
               ((pkt[Ether].src == al_mac1.lower() and pkt[Ether].dst == al_mac2.lower()) or
                (pkt[Ether].src == al_mac2.lower() and pkt[Ether].dst == al_mac1.lower()))
        ]

    if not filtered_packets:
        #instead of pytest fail wright alternatives
        report_logger.print_error(f"FAIL: No messages between {al_mac1} and {al_mac2} found in the capture file.")
        error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
        return
    tlv_data_from_config = get_tlv_from_config()
    #iterate through the captured packets and validate the messages
    for pkt in filtered_packets:
        profiletype = None
        controller_or_agent = None
        eth = pkt[Ether]
        if eth.type != ETHERTYPE_1905:
            continue
        #read all the almacs available under profile_type in the platform.yaml
        src_al_mac = eth.src.lower()
        dst_al_mac = eth.dst.lower()
        mac_list = list(profile_dict.keys())
        mac_list.append("01:80:c2:00:00:13")
        mac_list = [mac.lower() for mac in mac_list]
        payload = bytes(eth.payload)
        # Extract fields from CMDU header
        message_type = (payload[2] << 8) | payload[3]
        message_id   = (payload[4] << 8) | payload[5]
        frame_number = message_frame_map.get((message_type, message_id))
        if src_al_mac not in mac_list:
            report_logger.print_info(f"INFO: framenumber :{frame_number} No Multi-AP profile type found in the configuration file for Source AL MAC {src_al_mac}. Skipping the frame.")
            continue
        if dst_al_mac not in mac_list:
            report_logger.print_info(f"INFO: framenumber :{frame_number} No Multi-AP profile type found in the configuration file for Destination AL MAC {dst_al_mac}. Skipping the frame.")
            continue
        src_profiletype = None
        dst_profiletype = None
        try:
            src_profiletype = initialize.read_from_database("test_parameters","profile_type", src_al_mac)
        except Exception as e:
            if "Could not fetch data from database dictionary for the values" in str(e):
                src_profiletype = initialize.read_from_database("test_parameters","profile_type", src_al_mac.upper())
            else:
                report_logger.print_error(f"FAIL: failed to retrieve profile type for source AL MAC {src_al_mac} : {str(e)}")
                error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
                continue
        if dst_al_mac == "01:80:c2:00:00:13":
            profiletype = src_profiletype
        else:
            try:
                dst_profiletype = initialize.read_from_database("test_parameters","profile_type", dst_al_mac)
            except Exception as e:
                if "Could not fetch data from database dictionary for the values" in str(e):
                    dst_profiletype = initialize.read_from_database("test_parameters","profile_type", dst_al_mac.upper())
                else:
                    report_logger.print_error(f"FAIL: failed to retrieve profile type for destination AL MAC {dst_al_mac} : {str(e)}")
                    error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
                    continue
        if profiletype is None:
            #choose profile type which is lower src_profiletype or dst_profiletype
            profiletype = min(src_profiletype, dst_profiletype)
        report_logger.print_info(f"INFO: Profile Type using for 1905 message validation between {src_al_mac} and {dst_al_mac} = {profiletype:#04x}")
        message_type_name = get_message_type_name(message_type)
        # check if the message is from controller or agent. This is valid incase of AP Autoconfiguration WSC Messages
        if message_type == MSG_TYPE_AP_AUTOCONFIGURATION_WSC:
            found_tlvs, _tlv_length, tlv_values, _, error = parse_tlvs(payload)
            if error or not found_tlvs:
                report_logger.print_error(f"FAIL: {error or 'Failed to parse WSC message TLVs'}")
                error_list.append(report_logger.get_error_logs()[-1])
                continue
            if any(
                tlv_type == TLV_TYPE_WSC and len(value) < 10
                for tlv_type, value in zip(found_tlvs, tlv_values)
            ):
                report_logger.print_error("FAIL: WSC TLV is too short to extract the message type")
                error_list.append(report_logger.get_error_logs()[-1])
                continue
            for tlv_type, tlv_length, tlv_value in zip(found_tlvs, _tlv_length, tlv_values):
                if tlv_type == TLV_TYPE_WSC:
                    wsc_message_type = tlv_value[9]
                    if wsc_message_type == 0x04:
                        controller_or_agent = "agent"
                    if wsc_message_type == 0x05:
                        controller_or_agent = "controller"
        if message_type == MSG_TYPE_LINK_METRIC_RESPONSE:
            report_logger.print_title(f"Analyzing the {message_type_name}")
            try:
                link_meteric_response_mandatory_tlvs, link_meteric_response_optional_tlvs = parse_config(tlv_data_from_config, profiletype, message_type)
            except ValueError as e:
                continue
            found_tlvs, _tlv_length, tlv_values, _, error = parse_tlvs(payload)
            if error or not found_tlvs:
                report_logger.print_error(f"FAIL: framenumber :{frame_number} {error or 'Failed to parse Link Metric Response TLVs'}")
                error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
                continue
            for tlv_type, tlv_length, tlv_value in zip(found_tlvs, _tlv_length, tlv_values):
                report_logger.print_info(f"INFO: Processing {get_tlv_type_name(tlv_type)} with length {tlv_length}")
                if tlv_type not in link_meteric_response_mandatory_tlvs:
                    report_logger.print_error(f"FAIL: framenumber :{frame_number} Found Extra TLVs in {get_message_type_name(message_type)}: {get_tlv_type_name(tlv_type)}")
                    error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
                else:
                     expected_tlv_length, tlv_length_valid_flag = validate_tlv_length(tlv_type, tlv_length)
                     if tlv_length_valid_flag:
                        report_logger.print_success(f"PASS: {get_tlv_type_name(tlv_type)} is expected and the  tlv length is valid : {tlv_length}") 
                     else: 
                        report_logger.print_success(f"PASS: {get_tlv_type_name(tlv_type)} is expected.")
                        report_logger.print_error(f"FAIL: framenumber :{frame_number} {get_tlv_type_name(tlv_type)} length is invalid. expected tlv length is {expected_tlv_length} and actual tlv length is {tlv_length}")
                        error_list.append(report_logger._error_logs[-1] if report_logger._error_logs else "")
            continue
        if not message_type_name.startswith("Unknown message type"):
            report_logger.print_title(f"Analyzing the {message_type_name}")
            validate_1905_message(tlv_data_from_config, profiletype, message_type, payload, controller_or_agent)
        else:
            report_logger.print_info(f"INFO: Skipping {get_message_type_name(message_type)} encountered between {src_al_mac} and {dst_al_mac}")