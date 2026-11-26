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

from rdkbmeshzap.common_utils import report_logger, client_utils, traffic_utils
import time

def test_client_reassociation_after_disconnection(initialize):
    """
    Verify that a Wi-Fi client automatically reassociates with theEasyMesh SSID after Wi-Fi is disabled and re-enabled, without
    manually entering credentials.
    """
    report_logger.print_test("Entering test_client_association_reassociation_after_disconnection")
    try:
        step_index = 1
        report_logger.print_step(f"STEP {step_index}: Select Wi-Fi client for reassociation testing")
        selected_clients = traffic_utils.select_wifi_clients(initialize)
        if not selected_clients:
            report_logger.print_error("FAIL: No WLAN clients available for testing")
            return
        step_index += 1
        report_logger.print_step( f"STEP {step_index}: Verify EasyMesh SSID is enabled on Controller")
        ssid = initialize.get_ssid("controller", "controller_device_index", "de")
        if not ssid:
            report_logger.print_error("FAIL: Unable to retrieve EasyMesh SSID")
            return
        report_logger.print_success(f"PASS: EasyMesh SSID retrieved successfully: {ssid}")
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Retrieve Fronthaul password")
        password = initialize.get_fronthaul_password("controller", "gui")
        if not password:
            report_logger.print_error("FAIL: Unable to retrieve Fronthaul password")
            return
        report_logger.print_success("PASS: Fronthaul password retrieved successfully")
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Verify initial association for each selected client")
        step_passed = True
        for client in selected_clients:
            report_logger.print_info(f"INFO: Verifying initial association for {client}")
            old_bssid = initialize.get_association_status(client, "cli")
            if not old_bssid or old_bssid == "Not associated":
                report_logger.print_info(f"INFO: {client} is not initially associated.Attempting initial connection.")
                if not client_utils.remove_and_connect_client(
                        initialize, client, ssid, password):
                    report_logger.print_error(f"FAIL: Failed to establish initial connection for {client}")
                time.sleep(5)
                old_bssid = initialize.get_association_status(client, "cli")
                if not old_bssid or old_bssid == "Not associated":
                    report_logger.print_error(f" FAIL: {client} failed to associate after initial connection")
                    step_passed = False
                else:
                    report_logger.print_success(f"Initial association for {client} successful: {old_bssid}")
            else:
                report_logger.print_success(f"{client} is already associated with BSSID: {old_bssid}")        
            step_index += 1
            report_logger.print_step(f"STEP {step_index}: Capture DHCP client count before disconnection")
            initial_client_count = initialize.get_dhcpv4_server_pool_clientNumberOfEntries('controller', 'controller_device_index', 'de')
            report_logger.print_info(f"Initial DHCP client count: {initial_client_count}")
            if int(initial_client_count) < 1:
                report_logger.print_error("FAIL: No DHCP clients found before disconnection")
                step_passed = False
            else:
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Disable {client} Wi-Fi radio")
                initialize.set_client_radio_state(client, 0)
                time.sleep(5)
                report_logger.print_info(f"INFO:Wi-Fi radio disabled on {client}")
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Verify {client} disconnection")
                association_status = initialize.get_association_status(client, "cli")
                if association_status and association_status != "Not associated":
                    report_logger.print_error(f"FAIL: {client} still associated after Wi-Fi disable: {association_status}")
                    step_passed = False
                else:
                    report_logger.print_success(f"{client} successfully disconnected")
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Check DHCP client count after disconnection")
                time.sleep(5)
                disconnected_count = initialize.get_dhcpv4_server_pool_clientNumberOfEntries("controller", "controller_device_index","de")
                report_logger.print_info(f"INFO:DHCP count before disconnection: {initial_client_count}")
                report_logger.print_info(f"INFO: DHCP count after disconnection: {disconnected_count}")
                if int(disconnected_count) < int(initial_client_count):
                    report_logger.print_success("PASS: DHCP client count decreased after disconnection")
                else:
                    report_logger.print_error("FAIL: DHCP lease entry is still present. Reassociation will be verified independently.")
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Re-enable client Wi-Fi radio")
                initialize.set_client_radio_state(client, 1)
                time.sleep(5)
                report_logger.print_info(f"INFO: Client Wi-Fi radio re-enabled")
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Verify automatic client reassociation")
                new_bssid = None
                reassociation_timeout = 30
                elapsed_time = 0
                while elapsed_time < reassociation_timeout:
                    association_status = initialize.get_association_status(client, "cli")
                    if (association_status and association_status != "Not associated"):
                        new_bssid = association_status
                        break
                    time.sleep(2)
                    elapsed_time += 2
                if not new_bssid:
                    report_logger.print_error(f"FAIL:Client failed to automatically reassociate within {reassociation_timeout} seconds")
                    step_passed = False
                else:
                    report_logger.print_success(f"PASS: Client automatically reassociated with BSSID: {new_bssid}")
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Verify reassociation status")
                if old_bssid == new_bssid:
                    report_logger.print_info("INFO: Client reassociated with the same BSSID")
                else:
                    report_logger.print_info(f"INFO: Client reassociated with a different BSSID: "f"{old_bssid} -> {new_bssid}")
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Verify client IPv4 address assignment")
                client_ip = None
                elapsed_time = 0
                while elapsed_time < 30:
                    client_ip = initialize.get_client_ipv4(client)
                    if client_ip and str(client_ip).strip():
                        break
                    time.sleep(2)
                    elapsed_time += 2
                if not client_ip or not str(client_ip).strip():
                    report_logger.print_error("FAIL: Client did not receive an IPv4 address after reassociation")
                    step_passed = False
                else:
                    report_logger.print_success(f"PASS: Client received IPv4 address: {client_ip}")
                step_index += 1
                report_logger.print_step( f"STEP {step_index}: Verify DHCP client count after reassociation")
                final_count = initialize.get_dhcpv4_server_pool_clientNumberOfEntries("controller", "controller_device_index","de")
                report_logger.print_info(f"Initial DHCP client count: {initial_client_count}")
                report_logger.print_info(f"Final DHCP client count: {final_count}")
                if int(final_count) < 1:
                    report_logger.print_error("FAIL: DHCP client entry missing after reassociation")
                    step_passed = False
                else:
                    report_logger.print_success(f"PASS: DHCP client entry found after reassociation")
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Verify client MAC in DHCP Chaddr")
                client_mac = initialize.read_from_database(client, "mac")
                for i in range(1, int(final_count) + 1):
                    dhcp_client_mac = initialize.get_dhcpv4_server_pool_client_Chaddr("controller","controller_device_index",str(i),"de")                    
                    print(f"INFO: DHCP client MAC at index {i}: {dhcp_client_mac}")
                    if dhcp_client_mac.lower() != client_mac.lower():
                        report_logger.print_info(f"INFO: DHCP MAC mismatch. Expected: {client_mac}, Received: {dhcp_client_mac}")
                        i+=1
                    else:                   
                        report_logger.print_success(f"PASS:Client MAC found in DHCP list: {dhcp_client_mac}")
                        break
                step_index += 1
                report_logger.print_step(f"STEP {step_index}: Verify gateway connectivity")
                gateway_ip = initialize.read_from_database("controller", "bridge_ip")
                ping_result = initialize.ping_ipv4(client, gateway_ip, "3")
                if ping_result != 0:
                    report_logger.print_error(f"FAIL: {client} cannot ping gateway IP address {gateway_ip}")
                    step_passed = False
                else:
                    report_logger.print_success(f"PASS: {client} successfully pinged gateway {gateway_ip}")
        if step_passed:
            report_logger.print_success(f"PASS: {', '.join(selected_clients)} successfully reassociated after disconnection without manual credential entry")
        else:
            report_logger.print_error(f"FAIL: {', '.join(selected_clients)} failed to reassociate after disconnection without manual credential entry")
    finally:
        report_logger.print_test("Exiting test_client_association_reassociation_after_disconnection")
