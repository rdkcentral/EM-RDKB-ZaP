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


def test_client_association_traffic_flow_TCP_downstream(initialize):
    """
    Verify that Wi-Fi clients can associate with the EasyMesh SSID
    and establish TCP downstream traffic flow from the Controller.
    """
    report_logger.print_test(  "Entering test_client_association_traffic_flow_TCP_downstream")
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
        report_logger.print_info("INFO: Verify association status for connected clients.")
        for client in connected_clients:
            if not client_utils.verify_client_association(initialize, client):
                step_passed = False
        if step_passed and len(connected_clients) == len(selected_clients):
            report_logger.print_success("PASS: All selected clients successfully associated with EasyMesh SSID")
        else:
            report_logger.print_error("FAIL: One or more selected clients failed to connect or associate with EasyMesh SSID")
        report_logger.print_info(f"INFO: Successfully connected clients: {connected_clients}")
        report_logger.print_step("STEP 3: Start TCP downstream traffic flow from the Controller to the connected clients.")
        traffic_step_passed = True
        for client in connected_clients:
            report_logger.print_info(f"INFO: Fetch IP address of client {client}.")
            client_ip = initialize.get_wlan_ip_address(client, "cli")
            server_ip = initialize.read_from_database("controller", "bridge_ip")
            if not client_ip or not server_ip:
                report_logger.print_error(f"FAIL: Unable to retrieve IP address for {client} or Controller.")
                traffic_step_passed = False
                continue
            report_logger.print_info(f"INFO: Client {client} IP address: {client_ip}")
            report_logger.print_info(f"INFO: Controller server IP address: {server_ip}")
            time.sleep(5)
            report_logger.print_info("INFO: Removing existing iperf server log on Controller.")
            server_log_removed = initialize.execute_command("controller","rm -f controller_downstream_tcp_iperf_server.log",return_stderr=True)
            report_logger.print_info(f"INFO: Removed server log: {server_log_removed}")
            report_logger.print_info(f"INFO: Starting TCP iperf server on Controller {server_ip}.")
            initialize.start_iperf_server("controller",server_ip,"controller_downstream_tcp_iperf_server.log")
            time.sleep(5)
            report_logger.print_info(f"INFO: Removing existing iperf client log on {client}.")
            client_log_removed = initialize.execute_command(client,"rm -f controller_downstream_tcp_iperf_client.log",return_stderr=True)
            report_logger.print_info(f"INFO: Removed client log: {client_log_removed}")
            time.sleep(5)
            report_logger.print_info(f"INFO: Starting TCP downstream traffic from Controller {server_ip} to client {client} ({client_ip}).")

            try:
                initialize.start_iperf_client(
                    client,
                    server_ip,
                    client_ip,
                    protocol="tcp",
                    log_name="controller_downstream_tcp_iperf_client.log",
                    time=10,
                    mode="reverse")
                time.sleep(30)
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to start TCP downstream traffic for {client}: {e}")
                traffic_step_passed = False
            finally:
                initialize.stop_iperf_server("controller")
            time.sleep(5)
            report_logger.print_info(f"INFO: Reading TCP downstream iperf log for {client}.")
            log_output = initialize.execute_command(client,"cat controller_downstream_tcp_iperf_client.log")
            if log_output and "iperf Done" in log_output:
                report_logger.print_info(f"INFO: TCP downstream traffic flow for {client} completed.")
                sender_match = re.search(
                    r'\]\s+[\d.]+-[\d.]+\s+sec\s+[\d.]+\s+\S+\s+'
                    r'([\d.]+)\s+(\S+)\s+(\d+)\s+sender',
                    log_output)
                receiver_match = re.search(
                    r'\]\s+[\d.]+-[\d.]+\s+sec\s+[\d.]+\s+\S+\s+'
                    r'([\d.]+)\s+(\S+).*receiver',
                    log_output)
                if sender_match:
                    sender_bitrate = sender_match.group(1)
                    sender_unit = sender_match.group(2)
                    retransmissions = sender_match.group(3)
                    report_logger.print_info(f"INFO: TCP Sender Bitrate: {sender_bitrate} {sender_unit}")
                    report_logger.print_info(f"INFO: TCP Retransmissions: {retransmissions}")
                else:
                    report_logger.print_error("FAIL: Failed to retrieve TCP sender bitrate and retransmissions.")
                    traffic_step_passed = False
                if receiver_match:
                    receiver_bitrate = receiver_match.group(1)
                    receiver_unit = receiver_match.group(2)
                    report_logger.print_info(f"INFO: TCP Receiver Bitrate: {receiver_bitrate} {receiver_unit}")
                else:
                    report_logger.print_error("FAIL: Failed to retrieve TCP receiver bitrate.")
                    traffic_step_passed = False
                packet_loss_match = re.search(
                    r'(\d+)/(\d+)\s+\(([\d.]+)%\)',
                    log_output)
                if packet_loss_match:
                    lost_packets = packet_loss_match.group(1)
                    total_packets = packet_loss_match.group(2)
                    packet_loss = packet_loss_match.group(3)
                    report_logger.print_info( f"INFO: Packet Loss: {packet_loss}% ({lost_packets}/{total_packets} packets)")
                else:
                    report_logger.print_info( "INFO: Packet loss percentage is not reported in this TCP iperf3 log.")
            else:
                report_logger.print_error(f"FAIL: TCP downstream traffic flow from Controller to {client} failed.")
                traffic_step_passed = False
        if traffic_step_passed:
            report_logger.print_success("PASS: TCP downstream traffic flow verified successfully for all connected clients.")
        else:
            pytest.fail("FAIL: TCP downstream traffic verification failed.")
    finally:
        report_logger.print_test("Exiting test_client_association_traffic_flow_TCP_downstream")