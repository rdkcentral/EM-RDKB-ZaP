# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
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

import time
from packet_analyzer.packet_dissector import *
from packet_analyzer.message_verify import *
from packet_analyzer.ieee1905_utils import *
from rdkbmeshzap.common_utils import report_logger, client_utils, traffic_utils

def test_client_association_disassociation_event(initialize):
    """
    Verify that when a client disconnects, the serving node sends a Topology Notification 
    with a Client Association Event (left) to the Controller.
    """
    report_logger.print_test("Entering test_client_association_disassociation_event")
    try:
        report_logger.print_step(f"Step 1: Select Wi-Fi client for repeated association testing")
        selected_clients = traffic_utils.select_wifi_clients(initialize)
        controller_clients = [
            client for client in selected_clients
            if client.startswith("controller_wlan_client_")]
        if not controller_clients:
            report_logger.print_error("FAIL: No Controller WLAN client available for testing")
            return
        client = controller_clients[0]
        report_logger.print_info(f"INFO: Selected client for testing: {client}")
        report_logger.print_step("Step 2: Retrieve and store AL MAC address of the Controller")
        controller_al_mac = initialize.execute_command('controller', "ifconfig eth1_virt_peer | grep -i HWaddr | awk '{print $5}'").strip()
        if not controller_al_mac:
            report_logger.print_error("FAIL: Failed to retrieve AL MAC address of the Controller")
            return False
        else:
            report_logger.print_info(f"AL MAC address of the Controller: {controller_al_mac}")
        # initialize.write_into_database('test_parameters', 'profile_type', f"{controller_al_mac}: 0x03")

        report_logger.print_step("Step 3: Get Client MAC address and serving BSSID to the Controller")
        client_mac = initialize.read_from_database(client, "mac")
        if not client_mac:
            report_logger.print_error(f"FAIL: Failed to retrieve MAC address of the client {client}")
            return False
        else:
            report_logger.print_info(f"MAC address of the client {client}: {client_mac}")
        association_status = initialize.get_association_status(client,'cli')
        if association_status == initialize.read_from_database('controller', '2g_radio_mac') or association_status == initialize.read_from_database('controller', '5g_radio_mac') or association_status == initialize.read_from_database('controller', '6g_radio_mac'):
            report_logger.print_success(f"PASS: {client} is already associated with the Controller with BSSID: {association_status}")
        else:
            report_logger.print_info(f"INFO: {client} is not associated with the Controller ")
            ssid = initialize.get_ssid("controller", "controller_device_index", "de")
            password = initialize.get_fronthaul_password("controller", "gui")
            if not ssid or password is None:
                report_logger.print_error("FAIL: Failed to retrieve SSID or Fronthaul password")
                return False
            report_logger.print_success(f"PASS: SSID and Fronthaul password retrieved successfully")
            report_logger.print_info(f"INFO: Attempting to connect {client} to SSID {ssid} ")
            if not client_utils.remove_and_connect_client(initialize, client, ssid, password):
                report_logger.print_error(f"FAIL: {client} failed to connect to SSID {ssid}")
                return False
        report_logger.print_step("Step 4: Start packet capture on the Controller to monitor Topology Notification messages")
        # device_utils.create_capture_name()
        backhaul_interface = initialize.read_from_database('controller', 'backhaul_capture_iface')
        frame_filter = initialize.read_from_database('controller', 'filter_1905')
        initialize.start_frame_capture('controller', backhaul_interface, frame_filter, "controller_topology_notification_capture.pcap")
        report_logger.print_info("INFO: Packet capture started on the Controller for Topology Notification messages")
        time.sleep(5)  # Wait for a few seconds to ensure the packet capture is started
        report_logger.print_step("Step 5: Disconnect the client from the Controller and verify the client association status")
        for i in range(1, 11):
            report_logger.print_info(f"INFO: Attempting to disconnect {client} from the Controller (Attempt {i})")
            initialize.disconnect_wifi_client(client)
            time.sleep(30)  # Wait for a few seconds to allow the disassociation event to be processed
            association_status_after_disconnection = initialize.get_association_status(client,'cli')
            if association_status_after_disconnection == "Not associated":
                report_logger.print_success(f"PASS: {client} successfully disconnected from the Controller")
                break
            else:
                report_logger.print_error(f"FAIL: {client} is still associated with the Controller with BSSID: {association_status_after_disconnection}")
        else:
            report_logger.print_error(f"FAIL: {client} failed to disconnect from the Controller after multiple attempts")
            return False
        report_logger.print_step("Step 6: Stop packet capture on the controller")
        initialize.stop_frame_capture('controller') 
        report_logger.print_info("INFO: Packet capture stopped on the Controller")
        report_logger.print_step("Step 7: Download and delete the captured packets from the Controller for analysis")
        remote_path = initialize.read_from_database("controller", "pcap_remote_dir")
        is_file_exists = initialize.execute_command('controller', f"ls {remote_path}/| grep controller_topology_notification_capture.pcap")
        if is_file_exists == "controller_topology_notification_capture.pcap":
            initialize.download_captured_pcap('controller', "controller_topology_notification_capture.pcap")
            initialize.delete_captured_pcap('controller', "controller_topology_notification_capture.pcap")
            report_logger.print_success("PASS: Packet capture file downloaded and deleted successfully from the Controller")
        else:
            report_logger.print_error("FAIL: Packet capture file not found on the Controller")
            return False
        time.sleep(10)  # Wait for a few seconds to ensure the file is downloaded and deleted
        report_logger.print_step("Step 8: Analyze the captured packets to verify the presence of a Topology Notification message with a Client Association Event")
        pcap_local_dir = initialize.read_from_database("controller", "pcap_local_dir")
        report_logger.print_info(f"INFO: Captured pcap file is located at {pcap_local_dir}/controller_topology_notification_capture.pcap")        
        pcap_path = f"{pcap_local_dir}/controller_topology_notification_capture.pcap"
        reassembled = reassemble_packets(pcap_path)
        report_logger.print_info(f"INFO: Reassembled packets from the captured pcap file at {pcap_path}")
        msg_type = MSG_TYPE_TOPOLOGY_NOTIFICATION
        packet_analyzer(pcap_path, initialize, controller_al_mac)
        report_logger.print_info(f"INFO: Checking for message of type {get_message_type_name(msg_type)} in the captured packets")
        payloads = check_message_presence(reassembled, msg_type, src_mac=controller_al_mac)
        if not payloads:
            report_logger.print_error(f"FAIL: Message of type {get_message_type_name(msg_type)} not found in the captured packets")
            return False
        else:
            report_logger.print_success(f"PASS: Message of type {get_message_type_name(msg_type)} found in the captured packets")
        report_logger.print_step("STEP 9: Verifying the presence of a Client Association Event in the Topology Notification message")
        tlv_type = TLV_TYPE_CLIENT_ASSOCIATION_EVENT
        report_logger.print_info(f"INFO: Checking for TLV of type {get_tlv_type_name(tlv_type)} in the captured message type {get_message_type_name(msg_type)}")
        tlvs = check_tlv_presence(payloads[0], tlv_type)
        if not tlvs:
            report_logger.print_error(f"FAIL: TLV of type {get_tlv_type_name(tlv_type)} not found in the captured message type {get_message_type_name(msg_type)}")
            return False
        else:
            report_logger.print_success(f"PASS: Found {len(tlvs)} TLV(s) of type {get_tlv_type_name(tlv_type)} as expected")
    finally:
        report_logger.print_test("Exiting test_client_association_disassociation_event")
