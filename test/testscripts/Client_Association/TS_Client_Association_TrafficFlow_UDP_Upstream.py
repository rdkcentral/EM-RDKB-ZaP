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

import re

from streamlit import radio
import zaero
import pytest
import time
import random
from rdkbmeshzap.common_utils import device_utils, report_logger, client_utils

def test_client_association_traffic_flow_UDP_upstream(initialize):
    """
    Verify that Wi-Fi clients can successfully associate with the EasyMesh
    SSID and establish UDP upstream traffic flow to the Controller.
    """
    report_logger.print_test("Entering test_client_association_traffic_flow_UDP_upstream")
    try:
        report_logger.print_step("STEP 1: Get enabled clients and randomly select one controller client and one extender client")
        clients = device_utils.get_enabled_clients(initialize)
        selected_clients = []
        controller_clients = [
            client for client in clients
            if "controller_wlan_client" in client]
        report_logger.print_info(f"INFO: Available controller clients: {controller_clients}")
        extender_clients = [
            client for client in clients
            if "extender1_wlan_client" in client]
        report_logger.print_info(f"INFO: Available extender clients: {extender_clients}")
        if controller_clients:
            controller_client = random.choice(controller_clients)
            report_logger.print_info(f"INFO: Selected controller client: {controller_client}")
            selected_clients.append(controller_client)
        else:
            report_logger.print_error("FAIL: No controller WLAN clients available")
        if extender_clients:
            extender_client = random.choice(extender_clients)
            report_logger.print_info(f"INFO: Selected extender client: {extender_client}")
            selected_clients.append(extender_client)
        else:
            report_logger.print_error("FAIL: No extender WLAN clients available")
        if not selected_clients:
            report_logger.print_error("FAIL: No WLAN clients available for testing")
            pytest.fail("No WLAN clients available for testing")
        report_logger.print_step("STEP 2: Connect selected clients to EasyMesh SSID and verify association")
        ssid = initialize.get_ssid("controller", "controller_device_index", "de")
        password = initialize.get_fronthaul_password("controller")
        if not ssid or not password:
            report_logger.print_error("FAIL: Failed to retrieve SSID or password")
            pytest.fail("Failed to retrieve SSID or password")
        connected_clients = []
        step_passed = True
        for client in selected_clients:
            connected = client_utils.remove_and_connect_client(initialize, client, ssid, password)
            if connected:
                connected_clients.append(client)
            else:
                step_passed = False
        if not connected_clients:
            report_logger.print_error("FAIL: No selected clients successfully connected to EasyMesh SSID")
            pytest.fail("No selected clients successfully connected")
        report_logger.print_info("INFO: Verify association status for connected clients.")
        for client in connected_clients:
            if not client_utils.verify_client_association(initialize, client):
                step_passed = False
        if step_passed and len(connected_clients) == len(selected_clients):
            report_logger.print_success("PASS: All selected clients successfully associated with EasyMesh SSID")
        else:
            report_logger.print_error("FAIL: One or more selected clients failed to connect or associate with EasyMesh SSID")
        report_logger.print_info(f"INFO: Successfully connected clients: {connected_clients}")
        report_logger.print_step("STEP 3: Start UDP upstream traffic flow from selected Wi-Fi clients to Controller")
        traffic_step_passed = True
        for client in connected_clients:
            report_logger.print_info( f"INFO: Fetch IP address of client {client}")
            client_ip = initialize.get_wlan_ip_address(client, "cli")
            server_ip = initialize.read_from_database("controller", "bridge_ip")
            if not client_ip or not server_ip:
                report_logger.print_error(f"FAIL: Unable to retrieve client IP or controller IP for {client}")                
                traffic_step_passed = False
                continue
            report_logger.print_info(f"INFO: Client {client} IP address: {client_ip}")
            time.sleep(5)
            report_logger.print_info("INFO: Removing existing iperf server log file on Controller")
            server_log_removed = initialize.execute_command("controller","rm -f controller_upstream_UDP_iperf_server.log",return_stderr=True)
            report_logger.print_info( f"INFO: Removed existing iperf server log file: {server_log_removed}")
            report_logger.print_info(f"INFO: Starting UDP upstream traffic from {client} to Controller {server_ip}")
            initialize.start_iperf_server("controller",server_ip,"controller_upstream_UDP_iperf_server.log")
            time.sleep(5)
            report_logger.print_info(f"INFO: Removing existing iperf client log file on {client}")
            client_log_removed = initialize.execute_command(client,"rm -f controller_upstream_UDP_iperf_client.log", return_stderr=True)
            report_logger.print_info(f"INFO: Removed existing iperf client log file: {client_log_removed}")
            time.sleep(5)
            report_logger.print_info(f"INFO: Starting iperf client on {client} to connect to Controller {server_ip} for UDP upstream traffic")
            initialize.start_iperf_client(
                client,
                server_ip,
                client_ip,
                protocol="udp",
                log_name="controller_upstream_UDP_iperf_client.log",
                time=10)
            time.sleep(30)
            report_logger.print_info("INFO: Stopping iperf server on Controller")
            initialize.stop_iperf_server("controller")
            time.sleep(5)
            report_logger.print_info(f"INFO: Verifying UDP upstream iperf client log for {client}")
            log_output = initialize.execute_command(client,"cat controller_upstream_UDP_iperf_client.log")
            if "iperf Done." in log_output:
                report_logger.print_info( f"INFO: UDP upstream traffic flow from {client} to Controller is successful")
                udp_summary_pattern = (
                    r'\]\s+[\d.]+-[\d.]+\s+sec\s+'
                    r'[\d.]+\s+\S+\s+'
                    r'([\d.]+)\s+(\S+)\s+'
                    r'([\d.]+)\s+ms\s+'
                    r'(\d+)/(\d+)\s+\(([\d.]+)%\)\s+'
                    r'(sender|receiver)')
                udp_summaries = re.findall(udp_summary_pattern,log_output,re.IGNORECASE)
                sender_summary = None
                receiver_summary = None
                for summary in udp_summaries:
                    if summary[6].lower() == "sender":
                        sender_summary = summary
                    elif summary[6].lower() == "receiver":
                        receiver_summary = summary
                if sender_summary:
                    sender_bitrate = sender_summary[0]
                    sender_unit = sender_summary[1]
                    report_logger.print_info(f"INFO: UDP Sender Bitrate: {sender_bitrate} {sender_unit}")
                else:
                    report_logger.print_error(f"FAIL: Failed to retrieve UDP sender bitrate for {client}")
                    traffic_step_passed = False
                if receiver_summary:
                    receiver_bitrate = receiver_summary[0]
                    receiver_unit = receiver_summary[1]
                    receiver_jitter = receiver_summary[2]
                    lost_datagrams = receiver_summary[3]
                    total_datagrams = receiver_summary[4]
                    packet_loss = receiver_summary[5]
                    report_logger.print_info(f"INFO: UDP Receiver Bitrate: {receiver_bitrate} {receiver_unit}")
                    report_logger.print_info(f"INFO: UDP Receiver Jitter: {receiver_jitter} ms")
                    report_logger.print_info(f"INFO: UDP Lost Datagrams: {lost_datagrams}/{total_datagrams}")
                    report_logger.print_info( f"INFO: UDP Packet Loss: {packet_loss}%")
                else:
                    report_logger.print_error(f"FAIL: Failed to retrieve UDP receiver statistics for {client}")
                    traffic_step_passed = False
            else:
                report_logger.print_error(f"FAIL: UDP upstream traffic flow from {client} to Controller failed")
                traffic_step_passed = False
        if traffic_step_passed:
            report_logger.print_success("PASS: UDP upstream traffic flow completed successfully for all selected clients")
        else:
            report_logger.print_error("FAIL: UDP upstream traffic flow failed for one or more selected clients")
            pytest.fail("UDP upstream traffic flow failed")
    finally:
        report_logger.print_test("Exiting test_client_association_traffic_flow_UDP_upstream")
