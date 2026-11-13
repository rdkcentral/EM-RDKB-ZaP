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
from rdkbmeshzap.common_utils import report_logger, device_utils, client_utils
import random
import time

def select_wifi_clients(initialize):
    """
    Syntax: select_wifi_clients(initialize)
    Description: Retrieve the enabled Wi-Fi clients and randomly select one client each from the controller and Extender-1, if available.
    Parameters: initialize - Testbed interface.
    Return Value: List of selected Wi-Fi clients (one controller client and one extender client, if available).
    Example: select_wifi_clients(initialize)
    """
    clients = device_utils.get_enabled_clients(initialize)
    controller_clients = [
        client for client in clients
        if "controller_wlan_client" in client]
    extender_clients = [
        client for client in clients
        if "extender1_wlan_client" in client]
    report_logger.print_info(f"INFO: Available controller clients: {controller_clients}")
    report_logger.print_info(f"INFO: Available extender clients: {extender_clients}")
    selected_clients = []
    if controller_clients:
        selected = random.choice(controller_clients)
        selected_clients.append(selected)
        report_logger.print_info(f"INFO: Selected controller client: {selected}")
    else:
        report_logger.print_error("FAIL: No controller WLAN clients available")
    if extender_clients:
        selected = random.choice(extender_clients)
        selected_clients.append(selected)
        report_logger.print_info(f"INFO: Selected extender client: {selected}")
    else:
        report_logger.print_error("FAIL: No extender WLAN clients available")
    return selected_clients

def connect_and_verify_clients(initialize, selected_clients):
    """
    Syntax: connect_and_verify_clients(initialize, selected_clients)
    Description: Connect the selected Wi-Fi clients to the controller's fronthaul network and verify their association status.
    Parameters: initialize - Testbed interface;
                selected_clients - List of selected Wi-Fi clients to connect and verify.
    Return Value: A tuple containing the list of successfully connected clients and a boolean indicating whether all clients were connected and their associations verified successfully (True if successful, False otherwise).
    Example: connect_and_verify_clients(initialize, ["controller_wlan_client1", "extender1_wlan_client1"])
    """
    ssid = initialize.get_ssid("controller", "controller_device_index", "de")
    password = initialize.get_fronthaul_password("controller")
    if not ssid or not password:
        report_logger.print_error("FAIL: Failed to retrieve SSID or password")
        return [], False
    connected_clients = []
    step_passed = True
    for client in selected_clients:
        connected = client_utils.remove_and_connect_client(initialize, client, ssid, password)
        if connected:
            connected_clients.append(client)
        else:
            report_logger.print_error(f"FAIL: Failed to connect {client}")
            step_passed = False
    if not connected_clients:
        return [], False
    for client in connected_clients:
        if client_utils.verify_client_association(initialize, client):
            report_logger.print_success(f"PASS: {client} association verified")
        else:
            report_logger.print_error(f"FAIL: {client} association verification failed")
            step_passed = False
    if len(connected_clients) != len(selected_clients):
        step_passed = False
    return connected_clients, step_passed

def run_udp_traffic(initialize, client, direction,mode=None):
    """
    Syntax: run_udp_traffic(initialize, client, direction, mode=None)
    Description: Run UDP traffic between the specified Wi-Fi client and the controller using iperf, and validate the traffic output.
    Parameters: initialize - Testbed interface;
                client - Wi-Fi client device name;
                direction - UDP traffic direction (upstream or downstream);
                mode - Optional traffic mode specifying the direction of traffic.
    Return Value: Boolean indicating whether the UDP traffic was executed and validated successfully (True if successful, False otherwise).
    Example: run_udp_traffic(initialize, "controller_wlan_client1", "upstream")
    """
    traffic_step_passed = True
    server_log = f"controller_{direction}_UDP_iperf_server.log"
    client_log = f"controller_{direction}_UDP_iperf_client.log"
    server_started = False
    try:
        report_logger.print_info(f"INFO: Fetch IP address of client {client}")
        client_ip = initialize.get_wlan_ip_address(client, "cli")
        server_ip = initialize.read_from_database("controller", "bridge_ip")
        if not client_ip or not server_ip:
            report_logger.print_error(f"FAIL: Unable to retrieve IP address for {client} or Controller")
            traffic_step_passed = False
        report_logger.print_info(f"INFO: Client IP: {client_ip}")
        report_logger.print_info(f"INFO: Controller IP: {server_ip}")
        time.sleep(5)
        # Remove previous server log
        initialize.execute_command("controller", f"rm -f {server_log}")
        # Start iperf server
        report_logger.print_info(f"INFO: Starting UDP iperf server for {direction}")
        initialize.start_iperf_server("controller", server_ip, server_log)
        server_started = True
        time.sleep(5)
        # Remove previous client log
        initialize.execute_command(client, f"rm -f {client_log}")
        time.sleep(5)
        # Start iperf client
        report_logger.print_info(f"INFO: Starting UDP {direction} traffic for {client}")
        client_args = {"protocol": "udp","log_name": client_log,"time": 10}
        if mode:
            client_args["mode"] = mode
        initialize.start_iperf_client(client,server_ip,client_ip,**client_args)
        time.sleep(30)
        # Read and validate iperf output
        report_logger.print_info(f"INFO: Reading UDP {direction} iperf log for {client}")
        log_output = initialize.execute_command( client, f"cat {client_log}")
        if validate_udp_iperf_output(log_output, client):
            report_logger.print_success(f"PASS: UDP {direction} traffic validation successful for {client}")
        else:
            traffic_step_passed = False
    except Exception as e:
        report_logger.print_error(f"FAIL: UDP {direction} traffic failed for {client}: {e}")
        traffic_step_passed = False
    finally:
        if server_started:
            report_logger.print_info("INFO: Stopping UDP iperf server on Controller")
            try:
                initialize.stop_iperf_server("controller")
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to stop iperf server: {e}")
                traffic_step_passed = False
    return traffic_step_passed

def validate_udp_iperf_output(log_output,client,max_jitter=30.0,max_packet_loss=1.0):
    """
    Syntax: validate_udp_iperf_output(log_output, client, max_jitter=30.0, max_packet_loss=1.0)
    Description: Validate the UDP iperf output for a given client by checking sender and receiver statistics, bitrate, jitter, packet loss, and datagram count against the specified thresholds.
    Parameters: log_output - UDP iperf client execution output;
                client - Wi-Fi client device name;
                max_jitter - Maximum acceptable UDP jitter in milliseconds (default: 30.0);
                max_packet_loss - Maximum acceptable UDP packet loss percentage (default: 1.0).
    Return Value: Boolean indicating whether all UDP traffic validation checks passed (True if successful, False otherwise).
    Example: validate_udp_iperf_output(log_output, "controller_wlan_client1", max_jitter=30.0, max_packet_loss=1.0)
    """
    if not log_output or "iperf Done." not in log_output:
        report_logger.print_error(f"FAIL: iperf execution did not complete for {client}")
        return False
    udp_summary_pattern = (
        r'^\[\s*\d+\]\s+[\d.]+-[\d.]+\s+sec\s+'
        r'[\d.]+\s+\S+\s+'
        r'(?P<bitrate>[\d.]+)\s+(?P<unit>\S+)\s+'
        r'(?P<jitter>[\d.]+)\s+ms\s+'
        r'(?P<lost>\d+)/(?P<total>\d+)\s+'
        r'\((?P<loss>[\d.]+)%\)\s+'
        r'(?P<role>sender|receiver)\s*$')
    summaries = list(re.finditer(udp_summary_pattern,log_output,re.IGNORECASE | re.MULTILINE))
    sender = None
    receiver = None
    for summary in summaries:
        role = summary.group("role").lower()
        if role == "sender":
            sender = summary
        elif role == "receiver":
            receiver = summary
    step_passed = True
    # Validate sender
    if sender:
        sender_bitrate = float(sender.group("bitrate"))
        if sender_bitrate > 0:
            report_logger.print_info("INFO: UDP sender bitrate is greater than zero")
        else:
            report_logger.print_error("FAIL: UDP sender bitrate is zero")
            step_passed = False
    else:
        report_logger.print_error("FAIL: UDP sender statistics not found")
        step_passed = False
    # Validate receiver
    if receiver:
        bitrate = float(receiver.group("bitrate"))
        jitter = float(receiver.group("jitter"))
        lost = int(receiver.group("lost"))
        total = int(receiver.group("total"))
        packet_loss = float(receiver.group("loss"))
        if bitrate > 0:
            report_logger.print_info("INFO: UDP receiver bitrate is greater than zero")
        else:
            report_logger.print_error("FAIL: UDP receiver bitrate is zero")
            step_passed = False
        if jitter <= max_jitter:
            report_logger.print_info("INFO: UDP jitter is within the acceptable limit")
        else:
            report_logger.print_error(f"FAIL: UDP jitter exceeded limit: {jitter} ms")
            step_passed = False
        if packet_loss <= max_packet_loss:
            report_logger.print_info("INFO: UDP packet loss is within the acceptable limit")
        else:
            report_logger.print_error(f"FAIL: UDP packet loss exceeded limit: {packet_loss}%")
            step_passed = False
        if total > 0 and 0 <= lost <= total:
            report_logger.print_info("INFO: UDP datagram count is valid")
        else:
            report_logger.print_error("FAIL: Invalid UDP datagram count")
            step_passed = False
    else:
        report_logger.print_error("FAIL: UDP receiver statistics not found")
        step_passed = False
    return step_passed

def run_tcp_traffic(initialize, client, direction, mode=None):
    """
    Syntax: run_tcp_traffic(initialize, client, direction, mode=None)
    Description: Run TCP traffic between the specified Wi-Fi client and the controller using iperf, and validate the traffic execution output.
    Parameters: initialize - Testbed interface;
                client - Wi-Fi client device name;
                direction - TCP traffic direction (upstream or downstream);
                mode - Optional traffic mode specifying the direction of traffic.
    Return Value: Boolean indicating whether the TCP traffic was executed and validated successfully (True if successful, False otherwise).
    Example: run_tcp_traffic(initialize, "controller_wlan_client1", "upstream")
    """
    traffic_passed = True
    server_log = f"controller_{direction}_tcp_iperf_server.log"
    client_log = f"controller_{direction}_tcp_iperf_client.log"
    server_started = False
    client_started = False
    try:
        client_ip = initialize.get_wlan_ip_address(client, "cli")
        server_ip = initialize.read_from_database("controller", "bridge_ip")
        if not client_ip or not server_ip:
            traffic_passed = False
        initialize.execute_command("controller", f"rm -f {server_log}")
        initialize.execute_command(client, f"rm -f {client_log}")
        initialize.start_iperf_server("controller", server_ip, server_log)
        server_started = True
        initialize.start_iperf_client(
            client,
            server_ip,
            client_ip,
            protocol="tcp",
            log_name=client_log,
            time=10,
            mode=mode)
        client_started = True
        time.sleep(30)
    except Exception as error:
        report_logger.print_error(f"FAIL: TCP traffic failed for {client}: {error}")
        traffic_passed = False
    finally:
        if server_started:
            initialize.stop_iperf_server("controller")
    if client_started:
        report_logger.print_info(f"INFO: Reading TCP {direction} iperf log for {client}.")
        log_output = initialize.execute_command(client, f"cat {client_log}")
        if not validate_tcp_iperf_output(log_output, client):
            traffic_passed = False
    else:
        traffic_passed = False
    return traffic_passed

def validate_tcp_iperf_output(log_output, client, min_bitrate_delivery_percent=80.0, min_data_delivery_percent=80.0):
    """
    Syntax: validate_tcp_iperf_output(log_output, client, min_bitrate_delivery_percent=80.0, min_data_delivery_percent=80.0)
    Description: Validate TCP iperf3 client output by checking sender and receiver statistics, bitrate, data transfer, and delivery percentages.
    Parameters: log_output - TCP iperf3 client execution output;
                client - Wi-Fi client device name;
                min_bitrate_delivery_percent - Minimum acceptable receiver bitrate delivery percentage (default: 80.0);
                min_data_delivery_percent - Minimum acceptable receiver data delivery percentage (default: 80.0).
    Return Value: Boolean indicating whether the TCP iperf output was validated successfully (True if successful, False otherwise).
    Example: validate_tcp_iperf_output(log_output, "controller_wlan_client1", 80.0, 80.0)
    """
    report_logger.print_info(f"INFO: Validating TCP iperf output for {client}")
    # Match iperf3 sender and receiver summary lines.
    tcp_summary_pattern = (
        r'^\[\s*\d+\]\s+'
        r'[\d.]+-[\d.]+\s+sec\s+' 
        r'(?P<transfer>[\d.]+)\s+(?P<transfer_unit>\S+)\s+'
        r'(?P<bitrate>[\d.]+)\s+(?P<bitrate_unit>\S+)'
        r'(?:\s+(?P<retransmissions>\d+))?\s+'
        r'(?P<role>sender|receiver)\s*$')
    # Convert transfer units into bytes.
    transfer_unit_conversion = {"Bytes": 1, "KBytes": 1024, "MBytes": 1024 ** 2, "GBytes": 1024 ** 3, "TBytes": 1024 ** 4}
    # Convert bitrate units into bits per second.
    bitrate_unit_conversion = {"bits/sec": 1, "Kbits/sec": 1000, "Mbits/sec": 1000 ** 2, "Gbits/sec": 1000 ** 3, "Tbits/sec": 1000 ** 4}
    sender_data = None
    receiver_data = None
    # Parse sender and receiver summary lines.
    for line in log_output.splitlines():
        match = re.search(tcp_summary_pattern, line.strip())
        if not match:
            continue
        role = match.group("role")
        transfer = float(match.group("transfer"))
        transfer_unit = match.group("transfer_unit")
        bitrate = float(match.group("bitrate"))
        bitrate_unit = match.group("bitrate_unit")
        retransmissions = match.group("retransmissions")
        # Validate supported units.
        if transfer_unit not in transfer_unit_conversion:
            report_logger.print_error(f"FAIL: Unsupported transfer unit: {transfer_unit}" )
            return False
        if bitrate_unit not in bitrate_unit_conversion:
            report_logger.print_error(f"FAIL: Unsupported bitrate unit: {bitrate_unit}")
            return False
        # Convert values into common units.
        transfer_bytes = (transfer * transfer_unit_conversion[transfer_unit])
        bitrate_bps = (bitrate * bitrate_unit_conversion[bitrate_unit])
        summary = {
            "transfer_bytes": transfer_bytes,
            "bitrate_bps": bitrate_bps,
            "retransmissions": (int(retransmissions)
                if retransmissions is not None else None)}
        if role == "sender":
            sender_data = summary
        elif role == "receiver":
            receiver_data = summary
    if sender_data is None:
        report_logger.print_error(f"FAIL: TCP sender summary not found for {client}")
        return False
    if receiver_data is None:
        report_logger.print_error(f"FAIL:TCP receiver summary not found for {client}")
        return False
    if sender_data["transfer_bytes"] <= 0:
        report_logger.print_error(f"FAIL: TCP sender transferred zero data for {client}")
        return False
    if sender_data["bitrate_bps"] <= 0:
        report_logger.print_error(f"FAIL: TCP sender bitrate is zero for {client}")
        return False
    if receiver_data["transfer_bytes"] <= 0:
        report_logger.print_error(f"FAIL: TCP receiver received zero data for {client}")
        return False
    if receiver_data["bitrate_bps"] <= 0:
        report_logger.print_error(f"FAIL: TCP receiver bitrate is zero for {client}")
        return False
    bitrate_delivery_percent = (receiver_data["bitrate_bps"] /sender_data["bitrate_bps"]) * 100
    data_delivery_percent = (receiver_data["transfer_bytes"] /sender_data["transfer_bytes"]) * 100
    report_logger.print_info(f"INFO: TCP bitrate delivery: {bitrate_delivery_percent:.2f}%")
    report_logger.print_info(f"INFO: TCP data delivery: {data_delivery_percent:.2f}%")
    report_logger.print_info(f"INFO: TCP retransmissions: {sender_data['retransmissions']}")
    if bitrate_delivery_percent < min_bitrate_delivery_percent:
        report_logger.print_error(f"FAIL: TCP bitrate delivery below threshold for {client}. Expected: {min_bitrate_delivery_percent}%, Actual: {bitrate_delivery_percent:.2f}%")
        return False
    if data_delivery_percent < min_data_delivery_percent:
        report_logger.print_error(f"FAIL: TCP data delivery below threshold for {client}. Expected: {min_data_delivery_percent}%, Actual: {data_delivery_percent:.2f}%")
        return False
    report_logger.print_info(f"INFO: Bitrate and data delivery validation succeeded for {client}")
    return True 