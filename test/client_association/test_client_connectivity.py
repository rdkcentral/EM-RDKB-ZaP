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
from zaero.utils import zi_logger

# ---------------------------------------------------------------------------
# Test Case-1: EM_Client_Association_Discovery_EasyMesh_SSID
# ---------------------------------------------------------------------------

def test_client_association_discovery_easymesh_ssid(initialize):
    zi_logger.print_step("------------------------------------------EM_Client_Association_Discovery_EasyMesh_SSID----------------------------------------- ")
    zi_logger.print_step("Step 1: Get SSID from DataElements")
    ssid = initialize.get_ssid("controller", "controller_device_index", 'de')
    zi_logger.print_step(f"Retrieved SSID: {ssid}")
    zi_logger.print_step("Step 2: Wait for some time for SSID propagation")
    time.sleep(10)
    zi_logger.print_step("Step 3: Initiate WiFi scan on each wlan client of the devices")
    clients = initialize.get_enabled_clients()
    for client in clients:
        if initialize.read_from_database(client, "device_present"):
            output = []
            try:
                output = initialize.get_ap_ssid_visibility(client, ssid, 'cli')
                zi_logger.print_success(f"PASS: WiFi scan initiated successfully on {client} with SSID: {ssid} and output: {output}")
                zi_logger.print_step(f"Step 4: Count SSID occurrences for {client}")
                if len(output) >= 2:
                    zi_logger.print_success(f"PASS: {client}: SSID Count: {len(output)}")
                else:
                    zi_logger.print_error(f"FAIL: {client}: SSID count: {len(output)}")
            except Exception as e:
                zi_logger.print_error(f"FAIL: Failed to initiate WiFi scan on {client}: {e}")

# ---------------------------------------------------------------------------
# Test Case-2: EM_Client_Association_Authentication_Correct_Credentials
# ---------------------------------------------------------------------------

def test_client_association_authentication_correct_credentials(initialize):
    zi_logger.print_step("--------------EM_Client_Association_Authentication_Correct_Credentials------------------------------------------------- ")
    zi_logger.print_step("Step 1: Get SSID AKM Configuration from DataElements")
    try:
        ssid_akm = initialize.get_ssid_AKMAllowed("controller", "controller_device_index", 'de')
        if not ssid_akm:
            zi_logger.print_error("FAIL: Failed to get SSID AKM Configuration from DataElements")
        else:
            zi_logger.print_success(f"PASS: SSID AKM Configuration retrieved successfully: {ssid_akm}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query SSID AKM Configuration from DataElements: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    zi_logger.print_step("Step 2: Get PMF Configuration from DataElements")
    try:
        pmf_config = initialize.get_ssid_MFPConfig("controller", "controller_device_index", 'de')
        if not pmf_config:
            zi_logger.print_error("FAIL: Failed to get PMF Configuration from DataElements")
        else:
            zi_logger.print_success(f"PASS: PMF Configuration retrieved successfully: {pmf_config}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query PMF Configuration from DataElements: {e}")
        pytest.fail(f"DataElements query failed: {e}")   
    zi_logger.print_step("Step 3: Get Passphrase from GUI")
    password = initialize.get_fronthaul_password("controller", "gui")
    zi_logger.print_success(f"PASS: Fronthaul password retrieved successfully: {password}")
    zi_logger.print_step("Step 4: Wait for some time for SSID propagation")
    time.sleep(10)
    zi_logger.print_step("Step 5: Connect client with correct credentials and verify the connection status")
    ssid = initialize.get_ssid("controller", "controller_device_index", 'de')
    clients = initialize.get_enabled_clients()
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        device = client.split("_wlan_client")[0]
        try:
            device_bssid = initialize.read_from_database(device, "2g_radio_mac")
            initialize.connect_client_to_ssid(client, ssid, password, device_bssid)
            zi_logger.print_success(f"PASS: Client {client} connected to SSID {ssid} with correct credentials")
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to connect client {client} to SSID {ssid}: {e}")
    zi_logger.print_step("Step 6: Verify association status on clients")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        device = client.split("_wlan_client")[0]
        try:
            associated_mac = initialize.get_association_status(client, 'cli')
            device_mac = initialize.read_from_database(device, "2g_radio_mac")
            zi_logger.print_step(
                f"Verifying association for client {client} with {device}. "
                f"Associated MAC: {associated_mac}, {device} MAC: {device_mac}"
            )
            if associated_mac == device_mac:
                zi_logger.print_success(f"PASS: Client {client} is associated with {device}")
            else:
                zi_logger.print_error(
                    f"FAIL: Client {client} is not associated with {device}. "
                    f"Associated MAC: {associated_mac}, {device} MAC: {device_mac}"
                )
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to verify association status for client {client}: {e}")
    zi_logger.print_step("Step 7: Verify negotiated security on clients")
    for client in clients:
        if initialize.read_from_database(client, "device_present"):
            try:
                client_security = initialize.get_client_encryption(client)
                expected_security = initialize.normalize_security(ssid_akm)               # "dpp" -> "WPA3"
                actual_security = initialize.normalize_security(client_security)          # "SAE" -> "WPA3"
                zi_logger.print_step(
                    f"Comparing security for {client}: "
                    f"Controller AKM='{ssid_akm}' ({expected_security}) vs "
                    f"Client negotiated='{client_security}' ({actual_security})"
                )
                if expected_security == actual_security:
                    zi_logger.print_success(
                        f"PASS: {client} negotiated security matches: {client_security} ({actual_security}) "
                        f"is consistent with controller AKM {ssid_akm} ({expected_security})"
                    )
                else:
                    zi_logger.print_error(
                        f"FAIL: {client} negotiated security {client_security} ({actual_security}) "
                        f"does not match expected {ssid_akm} ({expected_security})"
                    )
            except Exception as e:
                zi_logger.print_error(f"FAIL: Failed to verify negotiated security for client {client}: {e}")
            zi_logger.print_step("Step 8: Test connectivity by pinging 8.8.8.8")
    for client in clients:
        if initialize.read_from_database(client, "device_present"):
            try:
                ping_result = initialize.ping_ipv4(client, "8.8.8.8", "3")
                if ping_result == 0:
                    zi_logger.print_success(f"PASS: Client {client} can ping 8.8.8.8")
                else:
                    zi_logger.print_error(f"FAIL: Client {client} cannot ping 8.8.8.8")
            except Exception as e:
                zi_logger.print_error(f"FAIL: Failed to test connectivity for client {client}: {e}")

# ---------------------------------------------------------------------------
# Test Case-3: EM_Client_Association_DHCP_IP_Assignment
# ---------------------------------------------------------------------------

def test_client_association_dhcp_ip_assignment(initialize):
    zi_logger.print_step("--------------EM_Client_Association_DHCP_IP_Assignment------------------------------------------------- ")
    zi_logger.print_step("Step 1: Get DHCP Server is enabled or not")
    try:
        dhcp_server_enabled = initialize.get_dhcpv4_server_enable("controller", 'de')
        if dhcp_server_enabled:
            zi_logger.print_success(f"PASS: DHCP Server is enabled on controller: {dhcp_server_enabled}")
        else:
            zi_logger.print_error(f"FAIL: DHCP Server is not enabled on controller: {dhcp_server_enabled}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query DHCP Server status from DataElements: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    zi_logger.print_step("Step 2: Get DHCP Server Pool minimum address from DataElements")
    try:
        dhcp_pool_min_address = initialize.get_dhcpv4_server_pool_Minaddress("controller", "controller_device_index", 'de')
        if not dhcp_pool_min_address:
            zi_logger.print_error(f"FAIL: Failed to get DHCP Server Pool minimum address from DataElements")
        else:
            zi_logger.print_success(f"PASS: DHCP Server Pool minimum address retrieved successfully: {dhcp_pool_min_address}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query DHCP Server Pool minimum address from DataElements: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    zi_logger.print_step("Step 3: Get DHCP Server Pool maximum address from DataElements")
    try:
        dhcp_pool_max_address = initialize.get_dhcpv4_server_pool_Maxaddress("controller", "controller_device_index", 'de')
        if not dhcp_pool_max_address:
            zi_logger.print_error(f"FAIL: Failed to get DHCP Server Pool maximum address from DataElements")
        else:
            zi_logger.print_success(f"PASS: DHCP Server Pool maximum address retrieved successfully: {dhcp_pool_max_address}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query DHCP Server Pool maximum address from DataElements: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    zi_logger.print_step("Step 4: Perform WiFi scan on each client")
    ssid = initialize.get_ssid("controller", "controller_device_index", 'de')
    zi_logger.print_step(f"Retrieved SSID: {ssid}")
    clients = initialize.get_enabled_clients()
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            output = initialize.get_ap_ssid_visibility(client, ssid, 'cli')
            zi_logger.print_success(f"WiFi scan initiated successfully on {client} with SSID: {ssid} and output: {output}")
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to initiate WiFi scan on {client}: {e}")
    zi_logger.print_step("Step 5: Connect client with correct credentials and verify the connection status")
    password = initialize.get_fronthaul_password("controller", "gui")
    try:
        if not password:
            zi_logger.print_error(f"FAIL: Failed to get Fronthaul password from GUI")
        else:
            zi_logger.print_success(f"PASS: Fronthaul password retrieved successfully: {password}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query Fronthaul password from GUI: {e}")
        pytest.fail(f"GUI query failed: {e}")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        device = client.split("_wlan_client")[0]
        try:
            device_bssid = initialize.read_from_database(device, "2g_radio_mac")
            initialize.connect_client_to_ssid(client, ssid, password, device_bssid)
            zi_logger.print_success(f"Client {client} connected to SSID {ssid} with correct credentials")
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to connect client {client} to SSID {ssid} and password {password}: {e}")
    zi_logger.print_step("Step 6: Wait for some time for association completion")
    time.sleep(10)
    zi_logger.print_step("Step 7: Verify association status on clients")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        device = client.split("_wlan_client")[0]
        try:
            associated_mac = initialize.get_association_status(client, 'cli')
            device_mac = initialize.read_from_database(device, "2g_radio_mac")
            if associated_mac == device_mac:
                zi_logger.print_success(f"PASS:Client {client} is associated with {device}")
            else:
                zi_logger.print_error(
                    f"FAIL:Client {client} is not associated with {device}. "
                    f"Associated MAC: {associated_mac}, {device} MAC: {device_mac}"
                )
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to verify association status for client {client}: {e}")
    zi_logger.print_step("Step 8:  Verify DHCP Process and lease time ")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            dhcp_process = initialize.verify_dhcp_process(client, 'cli')
            if dhcp_process:
                zi_logger.print_success(f"PASS: Client {client} DHCP process is successful")
            else:
                zi_logger.print_error(f"FAIL: Client {client} DHCP process is not successful")
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to verify DHCP process for client {client}: {e}")      
    zi_logger.print_step("Step 9: Verify IP address assignment on clients")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            ip_address = initialize.get_client_ipv4(client)
            if ip_address:
                zi_logger.print_success(f"PASS: Client {client} has been assigned IP address: {ip_address}")
            else:
                zi_logger.print_error(f"FAIL: Client {client} has not been assigned an IP address")
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to verify IP address assignment for client {client}: {e}")
    zi_logger.print_step("Step 10: Verify IP Address assignment is within the DHCP pool range")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            zi_logger.print_step(f"FAIL: Client {client} is not present in the database")
            continue
        try:
            ip_address = initialize.get_client_ipv4(client)
            if ip_address:
                if int(dhcp_pool_min_address.split('.')[-1]) <= int(ip_address.split('.')[-1]) <= int(dhcp_pool_max_address.split('.')[-1]):
                    zi_logger.print_success(
                        f"PASS: Client {client} IP address {ip_address} is within the DHCP pool range: "
                        f"{dhcp_pool_min_address} - {dhcp_pool_max_address}"
                    )
                else:
                    zi_logger.print_error(
                        f"FAIL: Client {client} IP address {ip_address} is NOT within the DHCP pool range: "
                        f"{dhcp_pool_min_address} - {dhcp_pool_max_address}"
                    )
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to verify IP address assignment for client {client}: {e}")

# ---------------------------------------------------------------------------
# Test Case-4: EM_Client_Association_Gateway_Reachability
# ---------------------------------------------------------------------------

def test_client_association_gateway_reachability(initialize):
    zi_logger.print_step("--------------EM_Client_Association_Gateway_Reachability------------------------------------------------- ")
    zi_logger.print_step("Step 1: Get Gateway interface is up or not from DataElements")
    gateway_interface = initialize.get_IP_Interface_Enable("controller", "controller_device_index",'de')
    if  gateway_interface != "true":
        zi_logger.print_error(f"FAIL: Gateway interface is not up")
    else:
        zi_logger.print_success(f"PASS: Gateway interface is up")
    zi_logger.print_step("Step 2: Get Gateway IP address from DataElements and compare with controller gateway IP Address")
    try:
        gateway_ip = initialize.get_IP_Interface_IPv4Address_IPAddress("controller", "gateway_ip_index", "ip_index", 'de')
        if not gateway_ip:
            zi_logger.print_error(f"FAIL: Failed to get Gateway IP address from DataElements")
        else:
            zi_logger.print_success(f"PASS: Gateway IP address retrieved successfully: {gateway_ip}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query Gateway IP address from DataElements: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    controller_gateway_ip = initialize.read_from_database("controller", "bridge_ip")
    if gateway_ip != controller_gateway_ip:
        zi_logger.print_error(f"FAIL: Gateway IP address {gateway_ip} does not match controller gateway IP address {controller_gateway_ip}")
    else:
        zi_logger.print_success(f"PASS: Gateway IP address {gateway_ip} matches controller gateway IP address {controller_gateway_ip}")
    zi_logger.print_step("Step 3: Verify client IP Address assignment")
    clients = initialize.get_enabled_clients()
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            ip_address = initialize.get_client_ipv4(client)
            if ip_address:
                zi_logger.print_success(f"PASS: Client {client} has been assigned IP address: {ip_address}")
            else:
                zi_logger.print_error(f"FAIL: Client {client} has not been assigned an IP address")
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to verify IP address assignment for client {client}: {e}")
    zi_logger.print_step("Step 4: Verify IP route on clients")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            ip_route = initialize.get_default_route(client, 'cli')
            if ip_route:
                zi_logger.print_success(f"PASS: Client {client} has IP route: {ip_route}")
            else:
                zi_logger.print_error(f"FAIL: Client {client} does not have an IP route")
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to verify IP route for client {client}: {e}")
    zi_logger.print_step("Step 5: Ping to gateway IP address from clients and verify the connectivity")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            ping_result = initialize.ping_ipv4(client, gateway_ip, "3")
            if ping_result == 0:
                zi_logger.print_success(f"PASS: Client {client} can ping Gateway IP address {gateway_ip}")
            else:
                zi_logger.print_error(f"FAIL: Client {client} cannot ping Gateway IP address {gateway_ip}")
        except Exception as e:
            zi_logger.print_error(f"FAIL: Failed to ping Gateway IP address from client {client}: {e}")
    zi_logger.print_step("Step 6: Get count of connected clients")
    clients_count = initialize.get_dhcpv4_server_pool_clientNumberOfEntries("controller", "controller_device_index", 'de')
    if int(clients_count) >= 1:
        zi_logger.print_success(f"PASS: Number of connected clients: {clients_count}")
    else:
        zi_logger.print_error(f"FAIL: No clients got connected to the controller")
    zi_logger.print_step("Step 7: Get client IP from the controller side")
    client_mac = initialize.get_dhcpv4_server_pool_client_Chaddr("controller", "controller_device_index", "sta_index", 'de')
    if not client_mac:
        zi_logger.print_error(f"FAIL: Failed to get client MAC address from controller")
    else:
        zi_logger.print_success(f"PASS: Client MAC address retrieved successfully from controller: {client_mac}")
