# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 RDK Management
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
import shlex
import time
from datetime import datetime
from rdkbmeshzap.common_utils import report_logger

def remove_and_connect_client(initialize, client, ssid, password):
    """
    Syntax: remove_and_connect_client(initialize, client, ssid, password)
    Description: Remove existing Wi-Fi connections from the client and attempt to connect it to the specified SSID using the available 2.4 GHz, 5 GHz, or 6 GHz radio BSSID of the associated device.
    Parameters: initialize - Testbed interface, 
                client - Client device name, 
                ssid - Wi-Fi network SSID, 
                password - Wi-Fi network password.
    Return Value: True if the client successfully connects through any available radio; otherwise, False.
    Example: remove_and_connect_client(initialize, "controller_wlan_client_1", "EasyMesh_SSID", "password123")
    """
    if not initialize.read_from_database(client, "device_present"):
        report_logger.print_info(f"INFO: {client} is not present, skipping")
        return False
    device = client.split("_wlan_client")[0]
    try:
        radio_macs = {
            "2G": initialize.read_from_database(device, "2g_radio_mac"),
            "5G": initialize.read_from_database(device, "5g_radio_mac"),
            "6G": initialize.read_from_database(device, "6g_radio_mac")
        }
        for radio, device_bssid in radio_macs.items():
            if not device_bssid:
                report_logger.print_info(f"INFO: {radio} radio MAC is not available for {device}, skipping")
                continue
            report_logger.print_info(f"INFO: Removing existing Wi-Fi connections for {client}")
            initialize.remove_all_wifi_connections(client)
            report_logger.print_info(f"INFO: Trying to connect {client} through {radio} radio ({device_bssid})")
            try:
                initialize.connect_client_to_ssid(client, ssid, password, device_bssid)
                time.sleep(10)
                report_logger.print_success(f"PASS: {client} connected through {radio} radio ({device_bssid})")
                return True
            except Exception as e:
                report_logger.print_info(f"INFO: {client} failed to connect through {radio} radio ({device_bssid}): {e} ")
        report_logger.print_info(f"INFO: {client} could not connect through 2G, 5G or 6G radio")
        return False
    except Exception as e:
        report_logger.print_info(f"INFO: Failed to connect client {client} to SSID {ssid}: {e}")
        return False

def verify_client_association(initialize, client):
    """
    Syntax: verify_client_association(initialize, client)
    Description: Verify whether a Wi-Fi client is successfully associated with any known 2.4 GHz, 5 GHz, or 6 GHz radio of its corresponding device by comparing the associated MAC address with the available radio MAC addresses.
    Parameters: initialize - Testbed interface,
                client - Client device name.
    Return Value: True if the client is successfully associated with any known radio; otherwise, False.
    Example: verify_client_association(initialize, "controller_wlan_client_1")
    """
    try:
        device = client.split("_wlan_client")[0]
        radio_macs = {"2G": initialize.read_from_database(device, "2g_radio_mac"),"5G": initialize.read_from_database(device, "5g_radio_mac"),"6G": initialize.read_from_database(device, "6g_radio_mac")}
        associated_mac = initialize.get_association_status(client, "cli")
        if not associated_mac:
            report_logger.print_error(f"FAIL: No associated MAC found for {client}.")
            return False
        associated_radio = None
        for radio, radio_mac in radio_macs.items():
            if radio_mac and associated_mac.lower() == radio_mac.lower():
                associated_radio = radio
                break
        if associated_radio:
            report_logger.print_info(f"INFO: {client} is associated with {device} {associated_radio} radio ({associated_mac})")           
            return True
        report_logger.print_error(f"FAIL: {client} is not associated with any known radio of {device}. Associated MAC: {associated_mac}")        
        return False
    except Exception as e:
        report_logger.print_error(f"FAIL: Association verification failed for {client}: {e}")
        return False

def verify_security_mode(nmcli_output, target_bssid, expected_security_mode):
    """
    Verify the security mode of a specific BSSID from nmcli output.
    Args:
        nmcli_output (str): Output of 'nmcli device wifi list'.
        target_bssid (str): BSSID to search for.
        expected_security_mode (str): Expected security mode.
    Returns:
        tuple:
            (True, actual_security_mode)  -> if matched
            (False, actual_security_mode) -> if not matched
    Raises:
        LookupError: If the BSSID is not found.
    """
    for line in nmcli_output.splitlines()[1:]:  # Skip header
        line = line.strip()
        if not line:
            continue
        fields = line.split(maxsplit=1)
        bssid = fields[0]
        security_mode = fields[1] if len(fields) > 1 else ""
        if bssid.lower() == target_bssid.lower():
            return security_mode == expected_security_mode, security_mode
    raise LookupError(
        f"BSSID '{target_bssid}' not found in nmcli output"
    )

def verify_repeated_association_cycles(initialize,client,ssid,password,total_cycles,connection_wait=10,disconnection_wait=5):
    """
    Syntax: verify_repeated_association_cycles(initialize,client,ssid,password,total_cycles,connection_wait=10,disconnection_wait=5)
    Description: Perform repeated Wi-Fi association and disassociation cycles
                 for a client device by connecting it to the specified EasyMesh
                 SSID andverifying successful disassociation for the configured number
                 of cycles.
    Parameters: initialize - Testbed interface,
                client - Client device name,
                ssid - EasyMesh SSID to connect the client to,
                password - Password for the EasyMesh SSID,
                total_cycles - Number of association/disassociation cycles,
                connection_wait - Time in seconds to wait after connection before verifying association (default: 10),
                disconnection_wait - Time in seconds to wait after disconnection before verifying disassociation (default: 5).
    Return Value: Dictionary containing:
                  - total: Total number of cycles performed,
                  - success: Number of successfully completed cycles,
                  - failures: Number of failed cycles,
                  - failure_details: List containing failure information,
                                     including cycle number, timestamp,
                                     and error description.
    Example: verify_repeated_association_cycles(initialize,"controller_wlan_client_1","EasyMesh_SSID","password",total_cycles=5)
    """
    results = {"total": total_cycles,"success": 0,"failures": 0,"failure_details": []}
    report_logger.print_info(f"Starting {total_cycles} association/disassociation cycles for client {client}")
    for cycle in range(1, total_cycles + 1):
        report_logger.print_step(f"Association Cycle {cycle}/{total_cycles}")
        try:
            # STEP 1: Remove existing connections and reconnect
            connection_status = remove_and_connect_client(initialize,client,ssid,password)
            if not connection_status:
                raise Exception("Failed to connect client to EasyMesh SSID")
            # STEP 2: Wait for connection stabilization
            time.sleep(connection_wait)
            # STEP 3: Verify client association
            association_status = verify_client_association(initialize,client)
            if not association_status:
                raise Exception("Client association verification failed")
            report_logger.print_success(f"PASS: Cycle {cycle} - Client successfully associated")
            # STEP 4: Disconnect client
            report_logger.print_info(f"Disconnecting client {client}")
            initialize.remove_all_wifi_connections(client)
            time.sleep(disconnection_wait)
            # STEP 5: Verify disconnection
            association_mac = initialize.get_association_status(client, "cli")
            if association_mac != "Not associated":
                raise Exception(f"Client still associated after disconnect: {association_mac}")
            results["success"] += 1
            report_logger.print_success(f"PASS: Cycle {cycle} - Disconnection successful")
        except Exception as error:
            results["failures"] += 1
            failure_info = {"cycle": cycle,"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"error": str(error)}
            results["failure_details"].append(failure_info)
            report_logger.print_error(f"FAIL: Cycle {cycle} - {error}")
            # Cleanup before proceeding to the next cycle
            try:
                initialize.remove_all_wifi_connections(client)
            except Exception as cleanup_error:
                report_logger.print_error(f"Cleanup failed for cycle {cycle}: {cleanup_error}")
        report_logger.print_info(f"Progress: {cycle}/{total_cycles} | Success: {results['success']} | Failures: {results['failures']}")
    report_logger.print_info("Repeated association testing completed")
    return results

def verify_kernel_errors(initialize):
    """
    Syntax: verify_kernel_errors(initialize)
    Description: Check the Controller's kernel logs for critical errors
                 such as kernel panic, segmentation fault, kernel Oops,
                 and BUG messages by executing a filtered dmesg command.
    Parameters: initialize - Testbed interface.
    Return Value: True if no critical kernel errors are detected in the
                  Controller's kernel logs; otherwise, False.
    Example: verify_kernel_errors(initialize)
    """
    output = initialize.execute_command("controller",'dmesg | grep -Ei "kernel panic|segfault|Oops:|BUG:"')
    if output and str(output).strip():
        report_logger.print_error( f"FAIL :Critical kernel errors detected: {output}")
        return False
    return True

def connect_client_without_bssid(initialize,client,ssid,password,threshold=10,timeout=15):
    """
    Syntax: connect_client_without_bssid(initialize, client, ssid, password,
                                         threshold=10, timeout=15)
    Description: Connect the Wi-Fi client to the specified SSID without restricting the connection to a particular BSSID. Measure
                 the association time and total time taken to acquire an IPv4 address, and validate both against the acceptance
                 threshold.
    Parameters:
        initialize - Testbed interface.
        client     - Wi-Fi client device name.
        ssid       - Wi-Fi network SSID to connect to.
        password   - Password required to connect to the SSID.
        threshold  - Maximum acceptable association and total connection
                     time in seconds (default: 10).
        timeout    - Maximum allowed time in seconds for association and
                     IP address acquisition (default: 15).
    Return Value: Dictionary containing: association_time,total_time ,associated_bssid,ip_address,status,reason           
    Example: connect_client_without_bssid(initialize, "client1",
                                          "EasyMesh_SSID", "password",
                                          threshold=10, timeout=15)
    """
    result = {
        "association_time": None,
        "total_time": None,
        "associated_bssid": None,
        "ip_address": None,
        "status": "FAIL",
        "reason": None}
    try:
        # Remove previous Wi-Fi profiles before every attempt
        initialize.remove_all_wifi_connections(client)
        start_time = time.monotonic()
        # Connect WITHOUT specifying a BSSID
        initialize.connect_client_to_ssid(client,ssid,password,None)
        # Wait until association is confirmed
        while time.monotonic() - start_time < timeout:
            associated_bssid = initialize.get_association_status(client, "cli")
            if associated_bssid:
                result["associated_bssid"] = associated_bssid
                result["association_time"] = round(time.monotonic() - start_time, 3)
                break
            time.sleep(0.2)
        if not result["associated_bssid"]:
            result["reason"] = "Association timeout"
            return result
        # Wait until the client receives IPv4 address
        while time.monotonic() - start_time < timeout:
            ip_address = initialize.get_wlan_ip_address(client, "cli")
            if ip_address:
                result["ip_address"] = ip_address
                result["total_time"] = round(time.monotonic() - start_time, 3)
                break
            time.sleep(0.2)
        if not result["ip_address"]:
            result["reason"] = "IP address acquisition timeout"
            return result
        # Validate the 10-second acceptance threshold
        if (result["association_time"] <= threshold and result["total_time"] <= threshold):
            result["status"] = "PASS"
        else:
            result["reason"] = (f"Threshold exceeded: association={result['association_time']}s, total={result['total_time']}s")
    except Exception as e:
        result["reason"] = str(e)
    return result