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
import pytest
import time
import random
from rdkbmeshzap.common_utils import device_utils, report_logger, client_utils

def test_client_association_traffic_flow_UDP_downstream(initialize):
    """
    Verify that Wi-Fi clients can successfully associate with the EasyMesh SSID
    and establish UDP downstream traffic flow from the Controller.
    """
    report_logger.print_test("Entering test_client_association_traffic_flow_UDP_downstream")
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
            report_logger.print_error(
                "FAIL: No selected clients successfully connected to EasyMesh SSID")
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
        report_logger.print_step("STEP 3: Start UDP downstream traffic flow from the Controller to the connected clients.")
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
            report_logger.print_info( f"INFO: Controller server IP address: {server_ip}")
            time.sleep(5)
            report_logger.print_info("INFO: Removing existing UDP iperf server log on Controller.")
            server_log_removed = initialize.execute_command("controller","rm -f controller_downstream_UDP_iperf_server.log",return_stderr=True)
            report_logger.print_info(f"INFO: Removed server log: {server_log_removed}")
            report_logger.print_info(f"INFO: Starting UDP iperf server on Controller {server_ip}.")
            initialize.start_iperf_server("controller",server_ip,"controller_downstream_UDP_iperf_server.log")
            time.sleep(5)
            report_logger.print_info(f"INFO: Removing existing UDP iperf client log on {client}.")
            client_log_removed = initialize.execute_command(client,"rm -f controller_downstream_UDP_iperf_client.log",return_stderr=True)
            report_logger.print_info(f"INFO: Removed client log: {client_log_removed}")
            time.sleep(5)
            report_logger.print_info(f"INFO: Starting UDP downstream traffic from Controller {server_ip} to client {client} ({client_ip}).")
            try:
                initialize.start_iperf_client(
                    client,
                    server_ip,
                    client_ip,
                    protocol="udp",
                    log_name="controller_downstream_UDP_iperf_client.log",
                    time=10,
                    mode="reverse")
                time.sleep(30)
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to start UDP downstream traffic for {client}: {e}")
                traffic_step_passed = False
            finally:
                initialize.stop_iperf_server("controller")
            time.sleep(5)
            report_logger.print_info(f"INFO: Reading UDP downstream iperf log for {client}.")
            log_output = initialize.execute_command(client,"cat controller_downstream_UDP_iperf_client.log")
            if log_output and "iperf Done" in log_output:
                report_logger.print_info(f"INFO: UDP downstream traffic flow for {client} completed.")
                udp_summary_pattern = (
                    r'\]\s+[\d.]+-[\d.]+\s+sec\s+'
                    r'[\d.]+\s+\S+\s+'
                    r'([\d.]+)\s+(\S+)\s+'
                    r'([\d.]+)\s+ms\s+'
                    r'(\d+)/(\d+)\s+\(([\d.]+)%\)\s+'
                    r'(sender|receiver)')
                udp_summaries = re.findall(
                    udp_summary_pattern,
                    log_output,
                    re.IGNORECASE)
                sender_found = False
                receiver_found = False
                for summary in udp_summaries:
                    bitrate = summary[0]
                    bitrate_unit = summary[1]
                    jitter = summary[2]
                    lost_datagrams = summary[3]
                    total_datagrams = summary[4]
                    packet_loss = summary[5]
                    summary_type = summary[6].lower()
                    if summary_type == "sender":
                        sender_found = True
                        report_logger.print_info( f"INFO: UDP Sender Bitrate: {bitrate} {bitrate_unit}")
                        report_logger.print_info(f"INFO: UDP Sender Packet Loss: {packet_loss}% ({lost_datagrams}/{total_datagrams} datagrams)")                    

                    elif summary_type == "receiver":
                        receiver_found = True
                        report_logger.print_info(f"INFO: UDP Receiver Bitrate: {bitrate} {bitrate_unit}")
                        report_logger.print_info(f"INFO: UDP Receiver Jitter: {jitter} ms")
                        report_logger.print_info(f"INFO: UDP Receiver Lost Datagrams: "f"{lost_datagrams}/{total_datagrams}")
                        report_logger.print_info(f"INFO: UDP Receiver Packet Loss: {packet_loss}%")
                if not sender_found:
                    report_logger.print_error("ERROR: Failed to retrieve UDP sender statistics.")
                    traffic_step_passed = False
                if not receiver_found:
                    report_logger.print_error("ERROR: Failed to retrieve UDP receiver statistics.")
                    traffic_step_passed = False
            else:
                report_logger.print_error(f"FAIL: UDP downstream traffic flow from Controller to {client} failed.")
                traffic_step_passed = False
        if traffic_step_passed:
            report_logger.print_success("PASS: UDP downstream traffic flow verified successfully for all connected clients.")
        else:
            pytest.fail("FAIL: UDP downstream traffic verification failed.")
    finally:
        report_logger.print_test("Exiting test_client_association_traffic_flow_UDP_downstream")
