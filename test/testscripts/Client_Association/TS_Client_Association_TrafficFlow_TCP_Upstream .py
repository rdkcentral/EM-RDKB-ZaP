# # If not stated otherwise in this file or this component LICENSE file the
# # following copyright and licenses apply:
# #
# # Copyright 2026 Zilogic Systems
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# # http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.

import re
import time
import random
import pytest
from rdkbmeshzap.common_utils import device_utils, report_logger, client_utils

def test_client_association_traffic_flow_TCP_upstream(initialize):
    """
    Verify that Wi-Fi client devices can successfully associate with the
    EasyMesh SSID and establish upstream TCP traffic flow to the Controller.
    """
    report_logger.print_test("Entering test_client_association_traffic_flow_TCP_upstream")
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
        report_logger.print_step("STEP 3: Start TCP upstream traffic flow from selected Wi-Fi clients to Controller")
        traffic_step_passed = True
        for client in connected_clients:
            report_logger.print_info(f"INFO: Fetch IP address of client {client}")
            client_ip = initialize.get_wlan_ip_address(client, "cli")
            server_ip = initialize.read_from_database("controller", "bridge_ip")
            if not client_ip or not server_ip:
                report_logger.print_error(f"FAIL: Unable to retrieve client IP or controller IP for {client}")
                traffic_step_passed = False
                continue
            report_logger.print_info(f"INFO: Client {client} IP address: {client_ip}")
            time.sleep(5)
            report_logger.print_info("INFO: Removing existing iperf server log file on Controller")
            server_log_removed = initialize.execute_command("controller","rm -f controller_upstream_tcp_iperf_server.log",return_stderr=True)
            report_logger.print_info(f"INFO: Removed existing iperf server log file: {server_log_removed}")
            report_logger.print_info(f"INFO: Starting TCP upstream traffic from {client} to Controller {server_ip}")
            initialize.start_iperf_server(
                "controller",
                server_ip,
                "controller_upstream_tcp_iperf_server.log")
            time.sleep(5)
            report_logger.print_info(f"INFO: Removing existing iperf client log file on {client}")
            client_log_removed = initialize.execute_command(client,"rm -f controller_upstream_tcp_iperf_client.log",return_stderr=True)
            report_logger.print_info(f"INFO: Removed existing iperf client log file: {client_log_removed}")
            time.sleep(5)
            report_logger.print_info(f"INFO: Starting iperf client on {client} to connect to Controller {server_ip}")
            try:
                initialize.start_iperf_client(
                    client,
                    server_ip,
                    client_ip,
                    protocol="tcp",
                    log_name="controller_upstream_tcp_iperf_client.log",
                    time=10)
                time.sleep(30)
            finally:
                report_logger.print_info(f"INFO: Stopping iperf server on Controller")
                initialize.stop_iperf_server("controller")
                time.sleep(5)
            report_logger.print_info(f"INFO: Verifying TCP upstream iperf client log for {client}")
            log_output = initialize.execute_command( client,"cat controller_upstream_tcp_iperf_client.log")
            if "iperf Done" in log_output:
                sender_match = re.search(
                    r'\]\s+[\d.]+-[\d.]+\s+sec\s+[\d.]+\s+\S+\s+'
                    r'([\d.]+)\s+(\S+)\s+(\d+)\s+sender',
                    log_output)
                receiver_match = re.search(
                    r'\]\s+[\d.]+-[\d.]+\s+sec\s+[\d.]+\s+\S+\s+'
                    r'([\d.]+)\s+(\S+).*receiver',
                    log_output)
                if sender_match and receiver_match:
                    sender_bitrate = sender_match.group(1)
                    sender_unit = sender_match.group(2)
                    retransmissions = sender_match.group(3)
                    receiver_bitrate = receiver_match.group(1)
                    receiver_unit = receiver_match.group(2)
                    report_logger.print_info(f"INFO: TCP Sender Bitrate: {sender_bitrate} {sender_unit}")
                    report_logger.print_info(f"INFO: TCP Receiver Bitrate: {receiver_bitrate} {receiver_unit}")
                    report_logger.print_info(f"INFO: TCP Retransmissions: {retransmissions}")
                    if float(sender_bitrate) > 0 and float(receiver_bitrate) > 0:
                         report_logger.print_info(f"INFO: TCP upstream traffic flow from {client} to Controller completed successfully")
                    else:
                         report_logger.print_error(f"FAIL: TCP upstream throughput is zero for {client}")
                         traffic_step_passed = False
                else:
                    report_logger.print_error(f"FAIL: Sender or receiver statistics are missing for {client}")
                    traffic_step_passed = False
            else:
                report_logger.print_error(f"FAIL: TCP upstream traffic flow from {client} to Controller failed")
                traffic_step_passed = False
        if traffic_step_passed:
            report_logger.print_success("PASS: TCP upstream traffic flow completed successfully for all selected clients")
        else:
            report_logger.print_error("FAIL: TCP upstream traffic flow failed for one or more selected clients")
    finally:
        report_logger.print_test("Exiting test_client_association_traffic_flow_TCP_upstream")
