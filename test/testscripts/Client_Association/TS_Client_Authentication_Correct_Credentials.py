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

import zaero
import pytest
import time
from rdkbmeshzap.common_utils import device_utils, report_logger

def test_client_association_authentication_correct_credentials(initialize):
    """
    Verify that  Wi-Fi client devices can successfully authenticate and associate to the EasyMesh SSID using correct credentials, whether it associates to the Controller or to any of the 3 Agents.
    """
    report_logger.print_test(" Entering test_client_association_authentication_correct_credentials")
    try:
        report_logger.print_step(f"STEP 1: Retrieving and storing device index into the database for controller and enabled extenders")
        devices = ["controller"] + device_utils.get_enabled_extenders(initialize)
        for device in devices:
            device_mac = initialize.read_from_database(device, "2g_radio_mac")
            device_index = device_utils.retrieve_and_store_device_index(initialize, device, device_mac)   
            report_logger.print_info(f"INFO: Device index for {device}: {device_index}")
        report_logger.print_step("STEP 2: Get SSID AKM Configuration from DataElements")
        try:
            ssid_akm = initialize.get_ssid_AKMAllowed( "controller","controller_device_index",'de')
            if not ssid_akm:
                report_logger.print_error("FAIL: Failed to get SSID AKM Configuration from DataElements")
            else:
                report_logger.print_success(f"PASS: SSID AKM Configuration retrieved successfully: {ssid_akm}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to query SSID AKM Configuration from DataElements: {e}")
            pytest.fail(f"DataElements query failed: {e}")
        report_logger.print_step("STEP 3: Get PMF Configuration from DataElements")
        try:
            pmf_config = initialize.get_ssid_MFPConfig("controller","controller_device_index",'de')
            if not pmf_config:
                report_logger.print_error("FAIL: Failed to get PMF Configuration from DataElements")
            else:
                report_logger.print_success(f"PASS: PMF Configuration retrieved successfully: {pmf_config}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to query PMF Configuration from DataElements: {e}")
            pytest.fail(f"DataElements query failed: {e}")
        report_logger.print_step("STEP 4: Get Passphrase from GUI")
        password = initialize.get_fronthaul_password("controller","gui")
        if password is not None:
            report_logger.print_success(f"PASS: Fronthaul password retrieved successfully")
        else:
            report_logger.print_error(f"FAIL: Failed to retrieve Fronthaul password from GUI")
            pytest.fail("Failed to retrieve Fronthaul password from GUI")
        report_logger.print_step("STEP 5: Wait for some time for SSID propagation")
        time.sleep(10)
        report_logger.print_step("STEP 6: Connect client with correct credentials and verify the connection status" )
        step_passed = True
        ssid = initialize.get_ssid("controller","controller_device_index",'de')
        clients = device_utils.get_enabled_clients(initialize)
        for client in clients:
            if not initialize.read_from_database(client, "device_present"):
                continue
            device = client.split("_wlan_client")[0]
            try:
                # Get all available radio MAC addresses
                radio_macs = {"2G": initialize.read_from_database(device,"2g_radio_mac"),
                              "5G": initialize.read_from_database(device,"5g_radio_mac"),
                              "6G": initialize.read_from_database(device,"6g_radio_mac")}
                connected = False
                # Try 2G -> 5G -> 6G
                for radio, device_bssid in radio_macs.items():
                    if not device_bssid:
                        report_logger.print_info(f"{radio} radio MAC is not available for {device}, skipping")
                        continue
                    report_logger.print_info(f"INFO: Deleting any existing connection for {client} before attempting to connect to SSID {ssid}")
                    initialize.remove_all_wifi_connections(client)
                    report_logger.print_info(f"INFO:Trying to connect {client} to {radio} radio ({device_bssid})")
                    try:
                        initialize.connect_client_to_ssid(client,ssid,password,device_bssid)
                        time.sleep(10)
                        report_logger.print_info(f"INFO: {client} connected to SSID {ssid} through {radio} radio ({device_bssid})")
                        connected = True
                        step_passed = True
                        break
                    except Exception as e:
                        report_logger.print_info(f"INFO: {client} failed to connect through {radio} radio ({device_bssid}): {e}")
                        step_passed = False
                if not connected:
                    report_logger.print_error(f" FAIL: {client} could not connect to SSID {ssid} through 2G, 5G or 6G radio")
                    step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to connect client {client} to SSID {ssid}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: All clients connected to the EasyMesh SSID using correct credentials")
        report_logger.print_step("STEP 7: Verify association status on clients")
        step_passed = True
        for client in clients:
            if not initialize.read_from_database( client,"device_present"):
                continue
            device = client.split("_wlan_client")[0]
            try:
                associated_mac = initialize.get_association_status(client,'cli')
                # Get all radio MAC addresses
                radio_macs = {
                    "2G": initialize.read_from_database(device,"2g_radio_mac"),
                    "5G": initialize.read_from_database(device,"5g_radio_mac"),
                    "6G": initialize.read_from_database(device,"6g_radio_mac")}
                associated_radio = None
                for radio, radio_mac in radio_macs.items():
                    if radio_mac and associated_mac.lower() == radio_mac.lower():
                        associated_radio = radio
                        break
                report_logger.print_info(f"INFO: {client} associated MAC: {associated_mac}")
                if associated_radio:
                    report_logger.print_info(f"INFO: {client} is associated with {device} {associated_radio} radio ({associated_mac})")
                else:
                    report_logger.print_error(f"FAIL: {client} is not associated with any known radio of {device}. Associated MAC: {associated_mac}")
                    step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to verify association status for client {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: Association status verified successfully for all connected clients")
        report_logger.print_step("STEP 9: Verify negotiated security on clients")
        step_passed = True
        for client in clients:
            if initialize.read_from_database(client,"device_present"):
                try:
                    client_security = initialize.get_client_encryption( client)
                    expected_security = device_utils.normalize_security( ssid_akm)
                    actual_security = device_utils.normalize_security(client_security)
                    if expected_security == actual_security:
                        report_logger.print_info(f"INFO: {client} negotiated security matches: {client_security} ({actual_security}) is consistent with controller AKM {ssid_akm} ({expected_security})")
                    else:
                        report_logger.print_error(f"FAIL: {client} negotiated security {client_security} ({actual_security}) does not match expected {ssid_akm} ({expected_security})")
                        step_passed = False
                except Exception as e:
                    report_logger.print_error(f"FAIL: Failed to verify negotiated security for client {client}: {e}")
                    step_passed = False
        if step_passed:
            report_logger.print_success("PASS: Clients negotiated security matches the controller AKM configuration")
        report_logger.print_step("STEP 10: Test connectivity by pinging 8.8.8.8")
        step_passed = True
        for client in clients:
            if initialize.read_from_database(client,"device_present"):
                try:
                    ping_result = initialize.ping_ipv4(client,"8.8.8.8","3")
                    if ping_result == 0:
                        report_logger.print_info(f"INFO: {client} can ping 8.8.8.8")
                    else:
                        report_logger.print_error(f"FAIL: {client} cannot ping 8.8.8.8")
                        step_passed = False
                except Exception as e:
                    report_logger.print_error(f"FAIL: Failed to test connectivity for client {client}: {e}")
                    step_passed = False
        if step_passed:
            report_logger.print_success("PASS: All clients can ping 8.8.8.8")
    finally:
        report_logger.print_test("Exiting test_client_association_authentication_correct_credentials")