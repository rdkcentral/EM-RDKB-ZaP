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

def test_client_association_gateway_reachability(initialize):
    """
    Verify that Wi-Fi client devices can successfully ping and reach the gateway after receiving a valid IP address via DHCP and associating to the EasyMesh SSID, whether attached to the Controller or one of the 3 Agents.
    """
    report_logger.print_test("Entering EM_Client_Association_Gateway_Reachability")
    report_logger.print_step("STEP 1: Get Gateway interface is up or not from DataElements")
    gateway_interface = initialize.get_IP_Interface_Enable("controller", "controller_device_index",'de')
    if  gateway_interface != "true":
        report_logger.print_error(f"FAIL: Gateway interface is not up")
    else:
        report_logger.print_success(f"PASS: Gateway interface is up")
    report_logger.print_step("STEP 2: Get Gateway IP address from DataElements and compare with controller gateway IP Address")
    try:
        gateway_ip = initialize.get_IP_Interface_IPv4Address_IPAddress("controller", "gateway_ip_index", "ip_index", 'de')
        if not gateway_ip:
            report_logger.print_error(f"FAIL: Failed to get Gateway IP address from DataElements")
        else:
            report_logger.print_success(f"PASS: Gateway IP address retrieved successfully: {gateway_ip}")
    except Exception as e:
        report_logger.print_error(f"FAIL: Failed to query Gateway IP address from DataElements: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    controller_gateway_ip = initialize.read_from_database("controller", "bridge_ip")
    if gateway_ip != controller_gateway_ip:
        report_logger.print_error(f"FAIL: Gateway IP address {gateway_ip} does not match controller gateway IP address {controller_gateway_ip}")
    else:
        report_logger.print_success(f"PASS: Gateway IP address {gateway_ip} matches controller gateway IP address {controller_gateway_ip}")
    report_logger.print_step("STEP 3: Verify client IP Address assignment")
    clients = device_utils.get_enabled_clients(initialize)
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            ip_address = initialize.get_client_ipv4(client)
            if ip_address:
                report_logger.print_success(f"PASS: Client {client} has been assigned IP address: {ip_address}")
            else:
                report_logger.print_error(f"FAIL: Client {client} has not been assigned an IP address")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to verify IP address assignment for client {client}: {e}")
    report_logger.print_step("STEP 4: Verify IP route on clients")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            ip_route = initialize.get_default_route(client, 'cli')
            if ip_route:
                report_logger.print_success(f"PASS: Client {client} has IP route: {ip_route}")
            else:
                report_logger.print_error(f"FAIL: Client {client} does not have an IP route")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to verify IP route for client {client}: {e}")
    report_logger.print_step("STEP 5: Ping to gateway IP address from clients and verify the connectivity")
    for client in clients:
        if not initialize.read_from_database(client, "device_present"):
            continue
        try:
            ping_result = initialize.ping_ipv4(client, gateway_ip, "3")
            if ping_result == 0:
                report_logger.print_success(f"PASS: Client {client} can ping Gateway IP address {gateway_ip}")
            else:
                report_logger.print_error(f"FAIL: Client {client} cannot ping Gateway IP address {gateway_ip}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to ping Gateway IP address from client {client}: {e}")
    report_logger.print_step("STEP 6: Get count of connected clients")
    clients_count = initialize.get_dhcpv4_server_pool_clientNumberOfEntries("controller", "controller_device_index", 'de')
    if int(clients_count) >= 1:
        report_logger.print_success(f"PASS: Number of connected clients: {clients_count}")
    else:
        report_logger.print_error(f"FAIL: No clients got connected to the controller")
    report_logger.print_step("STEP 7: Get client IP from the controller side")
    client_mac = initialize.get_dhcpv4_server_pool_client_Chaddr("controller", "controller_device_index", "sta_index", 'de')
    if not client_mac:
        report_logger.print_error(f"FAIL: Failed to get client MAC address from controller")
    else:
        report_logger.print_success(f"PASS: Client MAC address retrieved successfully from controller: {client_mac}")