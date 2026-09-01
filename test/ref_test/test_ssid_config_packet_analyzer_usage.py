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
import pytest
import time
import os
from zaero.utils import zi_logger
from packet_analyzer.packet_dissector import *
from packet_analyzer.message_verify import *
from packet_analyzer.ieee1905_utils import *
def test_config_ssid_with_packet_capture(initialize):
    pcap_file_name = "sample_6"
    ssid = initialize.get_random_ssid()
    pcap_remote_dir = initialize.read_from_database("controller", "pcap_remote_dir")
    pcap_local_dir = initialize.read_from_database("controller", "pcap_local_dir")
    backhaul_iface = initialize.read_from_database("controller", "backhaul_capture_iface")
    frame_filter = initialize.read_from_database("controller", "filter_1905")
    initialize.set_sniffer_log_file("controller", pcap_file_name)
    zi_logger.log(f"Starting packet capture on controller for interface {backhaul_iface} with filter {frame_filter}")
    initialize.start_frame_capture("controller", backhaul_iface, frame_filter)
    initialize.set_ssid("controller", "mld_iface_index", ssid, 'gui')
    for i in range(1, 31):
        try:
            initialize.check_ssid("controller", "mld_iface_index", ssid, 'cli')
        except Exception as ERR:
            zi_logger.print_step(f"{ERR}")
        else:
            zi_logger.print_success(f"SSID matched {ssid} on controller")
            break
        time.sleep(5)
    else:
        pytest.fail("SSID is not changed in DUT by checking with iw command")
    initialize.stop_frame_capture("controller")
    pcap_remote_dir = os.path.join(pcap_remote_dir, pcap_file_name + '.pcapng')
    initialize.download_pcap("controller", pcap_remote_dir, pcap_local_dir)
    pcap_local_path = os.path.join(pcap_local_dir, pcap_file_name + '.pcapng')
    initialize.delete_pcap("controller", f"{pcap_file_name}.pcapng")
    time.sleep(10)
    reassembled = reassemble_packets(pcap_local_path)
    message_type = MSG_TYPE_AP_AUTOCONFIGURATION_RENEW
    controler_almac = initialize.get_al_mac_address("controller", 'cli')
    extender1_almac = initialize.get_al_mac_address("extender1", 'cli')
    zi_logger.log(f"Controller AL MAC address : {controler_almac}")
    zi_logger.log(f"Extender1 AL MAC address : {extender1_almac}")
    #common packet analyzer for completed message type and TLV type check
    #TODO: run the packet_analyzer method only if user wants
    packet_analyzer(pcap_local_path, controler_almac, extender1_almac)
    #get the list of payloads of the message type from the captured packets
    zi_logger.log(f"checking for message of type {get_message_type_name(message_type)} in the captured packets")
    payloads = check_message_presence(reassembled, message_type, src_mac=controler_almac, dst_mac=extender1_almac)
    if not payloads:
        pytest.fail(f"Message of type {get_message_type_name(message_type)} not found in the captured packets")
    else:
        zi_logger.print_success(f"Message of type {get_message_type_name(message_type)} found in the captured packets")
    tlv_type = TLV_TYPE_SUPPORTED_ROLE
    zi_logger.log(f"checking for TLV of type {get_tlv_type_name(tlv_type)} in the captured message type {get_message_type_name(message_type)}")
    tlvs = check_tlv_presence(payloads[0], tlv_type)
    #if tlvs is empty then fail the test
    if not tlvs:
        pytest.fail(f" TLVs of type {get_tlv_type_name(tlv_type)} not found in the captured message type {get_message_type_name(message_type)}")
    else:
        zi_logger.print_success(f"Found {len(tlvs)} TLVs of type {get_tlv_type_name(tlv_type)} as expected")