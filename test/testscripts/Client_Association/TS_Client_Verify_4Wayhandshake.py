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

import pytest
import time
from rdkbmeshzap.common_utils import device_utils, report_logger, client_utils

def test_client_association_4wayhandshake(initialize):
    """
    Verify that Wi-Fi clients can successfully authenticate and associate
    with the EasyMesh SSID using correct WPA2/WPA3-Personal credentials.
    """
    report_logger.print_test("Entering test_client_association_4wayhandshake")
    try:
        report_logger.print_step("STEP 1: Retrieve and store device indexes for controller and enabled extenders")
        devices = ["controller"] + device_utils.get_enabled_extenders(initialize)
        for device in devices:
            device_mac = initialize.read_from_database(device, "2g_radio_mac")
            device_index = device_utils.retrieve_and_store_device_index(initialize, device, device_mac)
            report_logger.print_info(f"INFO: Device index for {device}: {device_index}")
        report_logger.print_step("STEP 2: Get SSID AKM Configuration from DataElements")
        try:
            ssid_akm = initialize.get_ssid_AKMAllowed("controller", "controller_device_index", "de")
            if not ssid_akm:
                report_logger.print_error("FAIL: Failed to get SSID AKM Configuration from DataElements")
                pytest.fail("Failed to retrieve SSID AKM Configuration")
            report_logger.print_success(f"PASS: SSID AKM Configuration retrieved successfully: {ssid_akm}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to query SSID AKM Configuration: {e}")
        report_logger.print_step("STEP 3: Get PMF Configuration from DataElements")
        try:
            pmf_config = initialize.get_ssid_MFPConfig("controller", "controller_device_index", "de")
            if not pmf_config:
                report_logger.print_error("FAIL: Failed to get PMF Configuration from DataElements")
            report_logger.print_success(f"PASS: PMF Configuration retrieved successfully: {pmf_config}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to query PMF Configuration: {e}")
        report_logger.print_step("STEP 4: Get SSID from DataElements and Passphrase from GUI")      
        ssid = initialize.get_ssid("controller", "controller_device_index", "de")
        password = initialize.get_fronthaul_password("controller", "gui")
        if not ssid or password is None:
            report_logger.print_error("FAIL: Failed to retrieve SSID or Fronthaul password")
            pytest.fail("Failed to retrieve SSID or Fronthaul password")
        report_logger.print_success(f"PASS: SSID {ssid} and Fronthaul password retrieved successfully")
        report_logger.print_step( "STEP 5: Enable WPA supplicant DEBUG logging")
        clients = [client for client in device_utils.get_enabled_clients(initialize)
            if initialize.read_from_database(client, "device_present")]
        if not clients:
            report_logger.print_error("FAIL: No enabled and present Wi-Fi clients found")
            pytest.fail("No Wi-Fi clients available")
        step_passed = True
        for client in clients:
            try:
                initialize.set_wpa_log_level(client, "DEBUG", "cli")
                report_logger.print_info( f"INFO: WPA supplicant DEBUG logging enabled on {client}")
            except Exception as e:
                report_logger.print_error( f"FAIL: Failed to enable WPA supplicant DEBUG logging on {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: WPA supplicant DEBUG logging enabled successfully for all clients")
        else:
            report_logger.print_error("FAIL: Failed to enable WPA supplicant DEBUG logging on one or more clients")
        report_logger.print_step("STEP 6: Wait for SSID propagation")
        report_logger.print_info("INFO: Waiting for 10 seconds for SSID propagation across the mesh network")
        time.sleep(10)
        report_logger.print_step("STEP 7: Remove existing connections and connect clients using correct credentials")
        connected_clients = []
        step_passed = True
        for client in clients:
            if client_utils.remove_and_connect_client(initialize, client, ssid, password):
                connected_clients.append(client)
            else:
                step_passed = False
        if not connected_clients:
            report_logger.print_error("FAIL: No clients successfully connected to the EasyMesh SSID")
            pytest.fail("No clients successfully connected to the EasyMesh SSID")
        if step_passed:
            report_logger.print_success("PASS: All clients connected to the EasyMesh SSID")
        else:
            report_logger.print_error("FAIL: One or more clients failed to connect to the EasyMesh SSID")
        report_logger.print_info(f"INFO: Successfully connected clients: {connected_clients}")
        clients = connected_clients
        report_logger.print_step("STEP 8: Verify 4-way handshake completion status for each connected client")
        step_passed = True
        for client in clients:
            try:
                handshake_completed = initialize.get_wpa_cli_status(client, "cli")
                if str(handshake_completed) == "wpa_state=COMPLETED":
                    report_logger.print_info(f"INFO: 4-way handshake completed successfully for {client}")
                else:
                    report_logger.print_error(f"FAIL: 4-way handshake did not complete for {client}")
                    step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Error while verifying 4-way handshake for {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: 4-way handshake completed for all connected clients")
        else:
            report_logger.print_error("FAIL: 4-way handshake did not complete for one or more clients")
        report_logger.print_step("STEP 9: Verify WPA 4-Way Handshake messages of Wi-Fi clients")
        step_passed = True
        for client in clients:
            try:
                interface = initialize.read_from_database(client, 'data_iface')
                handshake_messages = ( initialize.verify_four_way_handshake_messages(client, interface, "cli"))
                if handshake_messages:
                    report_logger.print_info(f"INFO: 4-way handshake messages verified for {client}")
                else:
                    report_logger.print_error(f"FAIL: 4-way handshake messages verification failed for {client}")
                    step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Error while verifying handshake messages for {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: 4-way handshake messages verified for all connected clients")
        else:
            report_logger.print_error("FAIL: 4-way handshake messages verification failed")
        report_logger.print_step("STEP 10: Verify pairwise and group keys installed with a supported cipher")
        step_passed = True
        for client in clients:
            try:
                pairwise_caps = initialize.get_wpa_cli_capability(client, "pairwise", "cli")
                group_caps = initialize.get_wpa_cli_capability( client, "group", "cli")
                report_logger.print_info( f"INFO: {client} pairwise capability: {pairwise_caps}")
                report_logger.print_info(f"INFO: {client} group capability: {group_caps}")
                if pairwise_caps and group_caps:
                    report_logger.print_info(f"INFO: Pairwise and group keys installed for {client}")
                else:
                    report_logger.print_error(f"FAIL: Pairwise or group keys not installed for {client}")
                    step_passed = False
            except Exception as e:
                report_logger.print_error( f"FAIL: Error while verifying pairwise and group keys for {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: Pairwise and group keys installed with supported cipher for all clients")
        else:
            report_logger.print_error("FAIL: Pairwise and group key verification failed")
        report_logger.print_step("STEP 11: Verify association status on clients")
        step_passed = True
        for client in clients:
            if client_utils.verify_client_association(initialize, client):
                report_logger.print_info(f"INFO: Association status verified successfully for {client}")
            else:
                report_logger.print_error(f"FAIL: Association status verification failed for {client}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: Association status verified successfully for all connected clients")
        else:
            report_logger.print_error("FAIL: Association status verification failed for one or more clients")
        report_logger.print_step("STEP 12: Test connectivity by pinging 8.8.8.8")
        step_passed = True
        for client in clients:
            try:
                ping_result = initialize.ping_ipv4(client, "8.8.8.8", "3")
                if ping_result == 0:
                    report_logger.print_info(f"INFO: {client} can ping 8.8.8.8")
                else:
                    report_logger.print_error(f"FAIL: {client} cannot ping 8.8.8.8" )
                    step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to test connectivity for {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: All connected WLAN clients can ping 8.8.8.8")
        else:
            report_logger.print_error("FAIL: One or more clients failed the connectivity test")
    finally:
        report_logger.print_test("Exiting test_client_association_4wayhandshake")

