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

def test_client_association_dhcp_ip_assignment(initialize):
    """
    Verify that  Wi-Fi client devices receives a valid IP address via DHCP after successful authentication and association to the EasyMesh SSID, regardless of whether it associates to the Controller or one of the 3 Agents .
    """
    try:
        report_logger.print_test("Entering EM_Client_Association_DHCP_IP_Assignment")
        report_logger.print_info(f"INFO: Retrieving and storing device index into the database for controller and enabled extenders")
        devices = ["controller"] + device_utils.get_enabled_extenders(initialize)
        for device in devices:
            device_mac = initialize.read_from_database(device, "2g_radio_mac")
            device_index = initialize.get_device_index("controller", device_mac, "de")   
        report_logger.print_info(f"INFO: Device index for {device}: {device_index}")
        report_logger.print_step("STEP 1: Get DHCP Server is enabled or not")
        try:
            dhcp_server_enabled = initialize.get_dhcpv4_server_enable("controller",'de')
            if dhcp_server_enabled:
                report_logger.print_success(f"PASS: DHCP Server is enabled on controller: {dhcp_server_enabled}")
            else:
                report_logger.print_error(f"FAIL: DHCP Server is not enabled on controller: {dhcp_server_enabled}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to query DHCP Server status from DataElements: {e}")
            pytest.fail(f"DataElements query failed: {e}")
        report_logger.print_step("STEP 2: Retrieve DHCP Server Pool minimum address from DataElements")
        try:
            dhcp_pool_min_address = initialize.get_dhcpv4_server_pool_Minaddress("controller","controller_device_index",'de')
            if not dhcp_pool_min_address:
                report_logger.print_error("FAIL: Failed to get DHCP Server Pool minimum address from DataElements")
            else:
                report_logger.print_success(f"PASS: DHCP Server Pool minimum address retrieved successfully: {dhcp_pool_min_address}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to query DHCP Server Pool minimum address from DataElements: {e}")
            pytest.fail(f"DataElements query failed: {e}")
        report_logger.print_step("STEP 3: Retrieve DHCP Server Pool maximum address from DataElements")
        try:
            dhcp_pool_max_address = initialize.get_dhcpv4_server_pool_Maxaddress("controller","controller_device_index",'de')
            if not dhcp_pool_max_address:
                report_logger.print_error("FAIL: Failed to get DHCP Server Pool maximum address from DataElements")
            else:
                report_logger.print_success(f"PASS: DHCP Server Pool maximum address retrieved successfully: {dhcp_pool_max_address}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to query DHCP Server Pool maximum address from DataElements: {e}")
            pytest.fail(f"DataElements query failed: {e}")
        report_logger.print_step("STEP 4: Retrieve SSID from DataElements for client association")
        ssid = initialize.get_ssid("controller","controller_device_index",'de')
        report_logger.print_info(f"INFO: Retrieved SSID: {ssid}")
        clients = device_utils.get_enabled_clients(initialize)
        report_logger.print_step("STEP 5: Connect client with correct credentials and verify the connection status")
        password = initialize.get_fronthaul_password("controller","gui")
        try:
            if not password:
                report_logger.print_error("FAIL: Failed to get Fronthaul password from GUI")
            else:
                report_logger.print_info(f"INFO: Fronthaul password retrieved successfully")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to query Fronthaul password from GUI: {e}")
            pytest.fail(f"GUI query failed: {e}")
        for client in clients:
            if not initialize.read_from_database(client,"device_present"):
                continue
            device = client.split("_wlan_client")[0]
            try:
                # Get all available radio MAC addresses
                radio_macs = {
                    "2G": initialize.read_from_database(device,"2g_radio_mac"),
                    "5G": initialize.read_from_database(device,"5g_radio_mac"),
                    "6G": initialize.read_from_database(device,"6g_radio_mac")}
                connected = False
                # Try 2G -> 5G -> 6G
                for radio, device_bssid in radio_macs.items():
                    if not device_bssid:
                        report_logger.print_info(f"INFO: {radio} radio MAC is not available for {device}, skipping")
                        continue
                    report_logger.print_info(f"INFO: Trying to connect client {client} to {radio} radio ({device_bssid})")
                    try:
                        initialize.connect_client_to_ssid(client,ssid,password,device_bssid)
                        time.sleep(10)
                        report_logger.print_success(f"PASS: Client {client} connected to SSID {ssid} through {radio} radio ({device_bssid})")
                        connected = True
                        break
                    except Exception as e:
                        report_logger.print_info(f"INFO: Client {client} failed to connect through {radio} radio ({device_bssid})")
                if not connected:
                    report_logger.print_error(f"FAIL: Client {client} could not connect to SSID {ssid} through 2G, 5G or 6G radio")
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to connect client {client} to SSID {ssid}: {e}")
        report_logger.print_step("STEP 6: Wait for some time for association completion")
        time.sleep(10)
        report_logger.print_step("STEP 7: Validate the Client's association with expected AP")
        step_passed = True
        for client in clients:
            if not initialize.read_from_database(client,"device_present"):
                continue
            device = client.split("_wlan_client")[0]
            try:
                associated_mac = initialize.get_association_status(client,'cli')
                # Get all radio MAC addresses
                radio_macs = {"2G": initialize.read_from_database(device,"2g_radio_mac"),
                    "5G": initialize.read_from_database(device,"5g_radio_mac"),
                    "6G": initialize.read_from_database(device,"6g_radio_mac")}
                associated_radio = None
                for radio, radio_mac in radio_macs.items():
                    if radio_mac and associated_mac.lower() == radio_mac.lower():
                        associated_radio = radio
                        break
                report_logger.print_info(f"INFO: Client {client} associated MAC: {associated_mac}")
                if associated_radio:
                    report_logger.print_info(f"INFO: Client {client} is associated with {device} {associated_radio} radio ({associated_mac})")
                else:
                    report_logger.print_error(f"FAIL: Client {client} is not associated with any known radio of {device}. Associated MAC: {associated_mac}")
                    step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to verify association status for client {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: All clients are association status verified successfully ")
        report_logger.print_step("STEP 8: Confirm the DHCP Process is successful for each client")
        step_passed = True
        for client in clients:
            if not initialize.read_from_database(client,"device_present"):
                continue
            try:
                dhcp_process = initialize.verify_dhcp_process(client,'cli')
                if dhcp_process:
                    report_logger.print_info(f"INFO: Client {client} DHCP process is successful")
                else:
                    report_logger.print_error(f"FAIL: Client {client} DHCP process is not successful")
                    step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to verify DHCP process for client {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: All clients have successful DHCP processes")
        report_logger.print_step("STEP 9: Verify IP address assignment on clients")
        step_passed = True
        for client in clients:
            if not initialize.read_from_database(client,"device_present"):
                continue
            try:
                ip_address = initialize.get_client_ipv4(client)
                if ip_address:
                    report_logger.print_info(f"INFO: Client {client} has been assigned IP address: {ip_address}")
                else:
                    report_logger.print_error(f"FAIL: Client {client} has not been assigned an IP address")
                    step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to verify IP address assignment for client {client}: {e}")
                step_passed = False
        if step_passed:
            report_logger.print_success("PASS: All clients have been assigned valid IP addresses")
        report_logger.print_step("STEP 10: Verify IP Address assignment is within the DHCP pool range")
        step_passed = True
        for client in clients:
            if not initialize.read_from_database(client,"device_present"):
                report_logger.print_error(f"FAIL: Client {client} is not present in the database")
                continue
            try:
                ip_address = initialize.get_client_ipv4(client)
                if ip_address:
                    if (int(dhcp_pool_min_address.split('.')[-1]) <= int(ip_address.split('.')[-1])<= int(dhcp_pool_max_address.split('.')[-1])):
                        report_logger.print_info(f"INFO: Client {client} IP address {ip_address} is within the DHCP pool range: {dhcp_pool_min_address} - {dhcp_pool_max_address}")
                    else:
                        report_logger.print_error(f"FAIL: Client {client} IP address {ip_address} is NOT within the DHCP pool range: {dhcp_pool_min_address} - {dhcp_pool_max_address}")
                        step_passed = False
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to verify IP address assignment "f"for client {client}: {e}")
                step_passed = False
            if step_passed:
                report_logger.print_success("PASS: All clients have IP addresses within the DHCP pool range")
    finally:
        report_logger.print_test("Exiting EM_Client_Association_DHCP_IP_Assignment")    