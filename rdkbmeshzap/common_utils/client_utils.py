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

import re
import shlex
import time
from rdkbmeshzap.common_utils import report_logger
NMCLI_SCAN_RETRY_LIMIT = 16

def get_client_bssids(client, ssid, ssh):
    """
    Syntax: get_client_bssids(client, ssid, ssh)
    Description: 
        Scans for the specified SSID on the client device and returns
        the matching BSSID(s).
    Parameters:
        client : Client device name.
        ssid : SSID to search for.
        ssh : SSH handler object. 
    Return Value:
        list: Matching BSSID(s) in lowercase format.
    """
    report_logger.print_info(
        f"INFO: Scanning for SSID '{ssid}' on {client}")
    result = ssh.execute_command(
        client,
        "nmcli -t --escape no -f BSSID,SSID device wifi list")
    bssids = []
    for row in (result or "").splitlines():
        row = row.replace("\\:", ":")
        if len(row) >= 19 and row[17] == ":" and row[18:] == ssid:
            bssid = row[:17]
            if re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", bssid):
                bssids.append(bssid.lower())
    return bssids

def get_present_device_bssids(initialize):
    """
    Syntax: get_present_device_bssids(initialize)
    Description: Returns the fronthaul BSSIDs of all present mesh devices in the topology. 
    Parameters: 
        initialize : Test initialization object.
    Return Value: set: Fronthaul BSSIDs of present mesh devices in lowercase format.
    """
    bssids = set()
    for device in initialize.get_testbed_devices():
        if device != "controller" and not re.fullmatch(r"extender\d+", device):
            continue
        present = initialize.read_from_database(device, "device_present")
        if present is False or (
            isinstance(present, str)
            and present.strip().lower() in {"false", "no", "0", "off"}):
            continue
        try:
            bssids.update(
                bssid.lower()
                for bssid in initialize.get_fronthaul_bssids(device))
        except Exception as error:
            report_logger.print_info(
                f"Unable to read fronthaul BSSIDs from present device "
                f"'{device}': {error}")
    return bssids

def connect_client_to_bssid(initialize, client, ssid, passphrase, bssid, ssh, allowed_bssids=None):
    """"
    Syntax: connect_client_to_bssid( initialize, client, ssid, passphrase, bssid, ssh, allowed_bssids=None
    Description: Connects a client to the specified BSSID and verifies the resulting association. 
    Parameters:
        initialize : Test initialization object.
        client : Client device name.
        ssid : Target SSID.
        passphrase : Wi-Fi passphrase.
        bssid : Preferred BSSID to connect.
        ssh : SSH handler object.
        allowed_bssids : Optional set/list of acceptable BSSIDs.
    Return Value: None
    """
    client_password = initialize.read_from_database(client, "password")
    wifi_interface = initialize.read_from_database(client, "data_iface")
    command = (
        f"printf '%s\\n' {shlex.quote(client_password)} | "
        f"sudo -S -p '' nmcli device wifi connect {shlex.quote(ssid)} "
        f"password {shlex.quote(passphrase)} bssid {shlex.quote(bssid.upper())} "
        f"ifname {shlex.quote(wifi_interface)}")
    output = ssh.execute_command(client, command)
    try:
        connected_bssid = (
            initialize.get_association_status(client, "cli").lower())
    except Exception as error:
        report_logger.print_error(
            f"Failed to get connected BSSID for {client}: {error}")
        return None
    accepted_bssids = (
        {value.lower() for value in allowed_bssids}
        if allowed_bssids is not None
        else {bssid.lower()})
    if connected_bssid in accepted_bssids:
        if connected_bssid != bssid.lower():
            owner = client.rsplit("_wlan_client_", 1)[0]
            report_logger.print_info(
                f"INFO: Client '{client}' is associated with BSSID "
                f"'{connected_bssid}'.")
        return
    if "successfully activated" not in output.lower() and connected_bssid is None:
        message = f"Failed to connect {client} to BSSID {bssid}: {output}"
        raise Exception(message)
    message = (f"{client} connected to {connected_bssid}, expected BSSID {bssid}: {output}") 
    raise Exception(message)

def connect_client_to_target_device(initialize, client_devices, extender, allowed_bssids=None):
    """
    Syntax: connect_client_to_target_device(initialize, client_devices, extender, allowed_bssids=None) 
    Description: Connects WLAN clients to a visible fronthaul BSSID advertised by the specified extender and verifies successful association.
     Parameters:
        initialize : Test initialization object.
        client_devices : List of client device names.
        extender : Target extender device name.
        allowed_bssids : Optional set/list of acceptable BSSIDs.
    Return Value: None
    """
    ssh = initialize.get_connection_module_object("ssh")
    ssid, passphrase = initialize.get_fronthaul_credentials("controller")
    extender_bssids = initialize.get_fronthaul_bssids(extender)
    normalized_extender_bssids = {
        bssid.lower() for bssid in extender_bssids}
    accepted_bssids = (
        {bssid.lower() for bssid in allowed_bssids}
        if allowed_bssids is not None
        else normalized_extender_bssids)
    for client in client_devices:
        password = initialize.read_from_database(client, "password")
        interface = initialize.read_from_database(client, "data_iface")
        ssh.execute_command(
            client,
            f"printf '%s\\n' {shlex.quote(password)} | "
            f"sudo -S -p '' nmcli device disconnect {shlex.quote(interface)}")
        ssh.execute_command(client, f"printf '%s\\n' {shlex.quote(password)} | "
            f"sudo -S -p '' nmcli connection delete {shlex.quote(ssid)}")
        time.sleep(2)
        initialize.check_ap_ssid_visibility(client, ssid)
        visible_bssids = get_client_bssids(client, ssid, ssh)
        target_bssid = next(
            (
                bssid
                for bssid in visible_bssids
                if bssid in normalized_extender_bssids),
            None,)
        if not target_bssid:
            message = (f"No expected BSSID for '{ssid}' was visible; expected={sorted(normalized_extender_bssids)}, visible={sorted(visible_bssids)}")
            raise Exception(message)
        connect_client_to_bssid(initialize, client, ssid, passphrase, target_bssid, ssh, accepted_bssids,)

def connect_wlan_clients(initialize, client_devices, require_all=True):
    """
    Syntax: connect_wlan_clients(initialize, client_devices,require_all=True)
    Description: Connects WLAN clients to the fronthaul BSSID of their owning mesh device and verifies successful association.
    Parameters:
        initialize : Test initialization object.
        client_devices : List of WLAN client device names.
        require_all : If True, all clients must connect successfully.
        If False, returns only successfully connected clients.
    Return Value: list: Connected client devices.
    """
    clients = list(client_devices)
    if not clients:
        return []
    ssh = initialize.get_connection_module_object("ssh")
    allowed_bssids = get_present_device_bssids(initialize)
    if not allowed_bssids:
        message = ("No fronthaul BSSIDs found for present mesh devices")
        raise Exception(message)  
    last_errors = {}
    connected_clients = []
    for client in clients:
        try:
            match = re.fullmatch(r"(.+)_wlan_client_\d+", client)
            if not match:
                raise ValueError(
                    f"Cannot determine owning device from client name '{client}'")
            connect_client_to_target_device(
                initialize, [client], match.group(1), allowed_bssids)
            connected_bssid = initialize.get_association_status(client, "cli").lower()
            if connected_bssid is None:
                message = (f"{client} is not connected after connection attempt")
                raise Exception(message)
            if connected_bssid not in allowed_bssids:
                message = (f"{client} is connected to {connected_bssid}, not an "
                            f"allowed present-device BSSID {sorted(allowed_bssids)}")
                raise Exception(message)
            connected_clients.append(client)
        except Exception as error:
            last_errors[client] = error
            if not require_all:
                try:
                    connected_bssid = initialize.get_association_status(client, "cli").lower()
                except Exception:
                    connected_bssid = None
                if connected_bssid in allowed_bssids:
                    report_logger.print_info(
                        f"Client '{client}' remains connected to BSSID {connected_bssid}; connection setup failed ({error}), continuing with link validation")
                    connected_clients.append(client)
                    continue
            report_logger.print_info(f"Client '{client}' connection attempt failed: {error}")
    if not require_all:
        unavailable = [client for client in clients if client not in connected_clients]
        if unavailable:
            report_logger.print_info(f"Skipping unavailable WLAN clients after one attempt: {', '.join(unavailable)}")
        return connected_clients
    if len(connected_clients) == len(clients):
        return connected_clients
    raise Exception(
        f"Unable to connect all clients after one attempt: {last_errors}") from next(iter(last_errors.values()), None)

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
        report_logger.print_error(f"FAIL: {client} could not connect through 2G, 5G or 6G radio")
        return False
    except Exception as e:
        report_logger.print_error(f"FAIL: Failed to connect client {client} to SSID {ssid}: {e}")
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
    for line in nmcli_output.splitlines():
        fields = line.split()
        # Skip header, blank lines, and malformed entries
        if len(fields) < 9:
            continue
        if fields[0] == "*":
            bssid = fields[1]
            security_mode = " ".join(fields[9:])
        else:
            bssid = fields[0]
            security_mode = " ".join(fields[8:])
        if bssid.lower() == target_bssid.lower():
            return security_mode == expected_security_mode, security_mode
    raise LookupError(
        f"BSSID '{target_bssid}' not found in nmcli output"
    )