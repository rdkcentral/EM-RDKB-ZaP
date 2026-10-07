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
    ssh.switch_connection(client)
    result = ssh.execute_command(
        "nmcli -t --escape no -f BSSID,SSID device wifi list"
    )
    bssids = []
    for row in (result or "").splitlines():
        row = row.replace("\\:", ":")
        if len(row) >= 19 and row[17] == ":" and row[18:] == ssid:
            bssid = row[:17]
            if re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", bssid):
                bssids.append(bssid.lower())
    return bssids

def get_connected_client_bssid(initialize, client):
    """
    Syntax: get_connected_client_bssid(initialize, client)
    Description: Returns the BSSID currently associated with the client's Wi-Fi interface.
    Parameters: 
        initialize : Test initialization object.
        client : Client device name.
    Return Value: str | None: Connected BSSID in lowercase format, or None if unavailable.
    """
    try:
        return initialize.get_association_status(client, "cli").lower()
    except RuntimeError:
        return None

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
            and present.strip().lower() in {"false", "no", "0", "off"}
        ):
            continue
        try:
            bssids.update(
                bssid.lower()
                for bssid in initialize.get_fronthaul_bssids(device)
            )
        except Exception as error:
            report_logger.print_info(
                f"Unable to read fronthaul BSSIDs from present device "
                f"'{device}': {error}"
            )
    return bssids

def connect_client_to_bssid(
    initialize, client, ssid, passphrase, bssid, ssh, allowed_bssids=None
):
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
        f"ifname {shlex.quote(wifi_interface)}"
    )
    ssh.switch_connection(client)
    output = ssh.execute_command(command)
    connected_bssid = get_connected_client_bssid(initialize, client)
    accepted_bssids = (
        {value.lower() for value in allowed_bssids}
        if allowed_bssids is not None
        else {bssid.lower()}
    )
    if connected_bssid in accepted_bssids:
        if connected_bssid != bssid.lower():
            owner = client.rsplit("_wlan_client_", 1)[0]
            report_logger.print_info(
                f"INFO: BSSID mismatch for client '{client}' owned by "
                f"'{owner}': requested={bssid.lower()}, actual={connected_bssid}; "
                "actual BSSID belongs to another present mesh device"
            )
        return
    if "successfully activated" not in output.lower() and connected_bssid is None:
        raise RuntimeError(f"Failed to connect {client} to BSSID {bssid}: {output}")
    raise RuntimeError(
        f"{client} connected to {connected_bssid}, expected BSSID {bssid}: {output}"
    )

def connect_clients_to_extender(
    initialize, client_devices, extender, allowed_bssids=None
):
    """
    Syntax: connect_clients_to_extender(initialize, client_devices, extender,allowed_bssids=None) 
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
        bssid.lower() for bssid in extender_bssids
    }
    accepted_bssids = (
        {bssid.lower() for bssid in allowed_bssids}
        if allowed_bssids is not None
        else normalized_extender_bssids
    )
    for client in client_devices:
        password = initialize.read_from_database(client, "password")
        interface = initialize.read_from_database(client, "data_iface")
        ssh.switch_connection(client)
        ssh.execute_command(
            f"printf '%s\\n' {shlex.quote(password)} | "
            f"sudo -S -p '' nmcli device disconnect {shlex.quote(interface)}"
        )
        time.sleep(2)
        initialize.check_ap_ssid_visibility(client, ssid)
        visible_bssids = get_client_bssids(client, ssid, ssh)
        target_bssid = next(
            (
                bssid
                for bssid in visible_bssids
                if bssid in normalized_extender_bssids
            ),
            None,
        )
        if not target_bssid:
            raise RuntimeError(
                f"No expected BSSID for '{ssid}' was visible; "
                f"expected={sorted(normalized_extender_bssids)}, "
                f"visible={sorted(visible_bssids)}"
            )
        connect_client_to_bssid(
            initialize,
            client,
            ssid,
            passphrase,
            target_bssid,
            ssh,
            accepted_bssids,
        )

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
        raise RuntimeError("No fronthaul BSSIDs found for present mesh devices")
    last_errors = {}
    connected_clients = []
    for client in clients:
        try:
            match = re.fullmatch(r"(.+)_wlan_client_\d+", client)
            if not match:
                raise ValueError(
                    f"Cannot determine owning device from client name '{client}'"
                )
            connect_clients_to_extender(
                initialize, [client], match.group(1), allowed_bssids
            )
            connected_bssid = get_connected_client_bssid(initialize, client)
            if connected_bssid is None:
                raise RuntimeError(
                    f"{client} is not connected after connection attempt"
                )
            if connected_bssid not in allowed_bssids:
                raise RuntimeError(
                    f"{client} is connected to {connected_bssid}, not an "
                    f"allowed present-device BSSID {sorted(allowed_bssids)}"
                )
            connected_clients.append(client)
        except Exception as error:
            last_errors[client] = error
            if not require_all:
                try:
                    connected_bssid = get_connected_client_bssid(initialize, client)
                except Exception:
                    connected_bssid = None
                if connected_bssid in allowed_bssids:
                    report_logger.print_info(
                        f"Client '{client}' remains connected to BSSID "
                        f"{connected_bssid}; connection setup failed "
                        f"({error}), continuing with link validation"
                    )
                    connected_clients.append(client)
                    continue
            report_logger.print_info(
                f"Client '{client}' connection attempt failed: {error}"
            )
    if not require_all:
        unavailable = [client for client in clients if client not in connected_clients]
        if unavailable:
            report_logger.print_info(
                "Skipping unavailable WLAN clients after one attempt: "
                f"{', '.join(unavailable)}"
            )
        return connected_clients
    if len(connected_clients) == len(clients):
        return connected_clients
    raise RuntimeError(
        f"Unable to connect all clients after one attempt: {last_errors}"
    ) from next(iter(last_errors.values()), None)
