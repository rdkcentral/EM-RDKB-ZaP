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
from rdkbmeshzap.common_utils import device_utils, report_logger

def test_client_association_authentication_incorrect_credentials(initialize):
    """
    Verify that Wi-Fi clients cannot authenticate to the EasyMesh SSID
    when using incorrect credentials.
    """
    report_logger.print_test("Entering test_client_association_authentication_incorrect_credentials")
    try:
        report_logger.print_step("STEP 1: Retrieve the SSID and passphrase")
        ssid = initialize.get_ssid("controller", "controller_device_index", "de")
        password = initialize.get_fronthaul_password("controller", "gui")
        if not ssid:
            pytest.fail("Failed to retrieve the EasyMesh SSID")
        if not password:
            pytest.fail("Failed to retrieve the Fronthaul password")
        wrong_password = (("X" if password[0] != "X" else "Y") + password[1:])
        report_logger.print_step("STEP 2: Find enabled clients")
        clients = device_utils.get_enabled_clients(initialize)
        report_logger.print_info(f"INFO: Enabled clients: {clients}")
        tested_clients = 0
        clients_that_connected = []
        clients_not_verified = []
        report_logger.print_step("STEP 3: Attempt to connect clients using incorrect credentials")
        for client in clients:
            if not initialize.read_from_database(client, "device_present"):
                continue
            tested_clients += 1
            device = client.split("_wlan_client")[0]
            radio_macs = {
                "2G": initialize.read_from_database(device, "2g_radio_mac"),
                "5G": initialize.read_from_database(device, "5g_radio_mac"),
                "6G": initialize.read_from_database(device, "6g_radio_mac"),}
            available_radios = {radio: mac for radio, mac in radio_macs.items() if mac}
            if not available_radios:
                report_logger.print_error(f"FAIL: No radio MACs available for {client}")
                clients_not_verified.append(client)
                continue
            initialize.remove_all_wifi_connections(client)
            time.sleep(2)
            connected_with_wrong_password = False
            status_verified = True
            for radio, bssid in available_radios.items():
                report_logger.print_info(f"INFO: Attempting to connect {client} to {ssid} via {radio} radio ({bssid}) using incorrect credentials")
                try:
                    initialize.connect_client_to_ssid(client, ssid, wrong_password)
                except Exception as e:
                    # A connection/authentication failure is expected.
                    report_logger.print_info(f"INFO: Connection attempt via {radio} was rejected: {e}")
                time.sleep(10)
                try:
                    associated_mac = initialize.get_association_status(client, "cli")
                    associated_mac = (associated_mac or "").strip()
                    if associated_mac.lower() == bssid.lower():
                        report_logger.print_error(f"FAIL: {client} associated with {radio} radio ({bssid}) using incorrect credentials")
                        connected_with_wrong_password = True
                        break
                except Exception as e:
                    error_message = str(e).lower()
                    if "not associated" in error_message:
                        # The API raises this when the client is disconnected; that is expected.
                        report_logger.print_info(f"PASS: {client} is not associated after the rejected {radio} authentication attempt")
                        continue
                    report_logger.print_error(f"FAIL: Could not verify association status for {client}: {e}")
                    status_verified = False
                    break
            if connected_with_wrong_password:
                clients_that_connected.append(client)
            elif status_verified:
                report_logger.print_success(f"PASS: {client} was not associated with any tested radio using incorrect credentials")
            else:
                clients_not_verified.append(client)
        if tested_clients == 0:
            pytest.fail("No present clients were available to test")
        if clients_that_connected or clients_not_verified:
            pytest.fail(
                f"Incorrect-credential authentication test failed. Clients that connected: {clients_that_connected}; clients whose association status could not be verified: {clients_not_verified}")
        report_logger.print_success("PASS: All tested clients were rejected when using incorrect credentials")
    finally:
        report_logger.print_test("Exiting test_client_association_authentication_incorrect_credentials")