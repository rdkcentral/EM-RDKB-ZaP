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

def get_present_wlan_clients(initialize):
    """
    Return WLAN client entries marked present in the testbed YAML.
    """
    clients = []
    for device in initialize.get_testbed_devices():
        if not re.fullmatch(r".+_wlan_client_\d+", device):
            continue
        value = initialize.read_from_database(device, "device_present")
        if value is None or (
            isinstance(value, str)
            and value.strip().lower() in {"true", "yes", "1", "on"}
        ) or (not isinstance(value, str) and bool(value)):
            clients.append(device)
    return clients

def get_client_bssids(client, ssid, ssh):
    """
    Return scan results matching the requested SSID.
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

def get_connected_client_bssid(initialize, client, ssh):
    """
    Return the BSSID currently used by a client Wi-Fi interface.
    """
    wifi_interface = initialize.read_from_database(client, "data_iface")
    ssh.switch_connection(client)
    output = ssh.execute_command(f"iw dev {shlex.quote(wifi_interface)} link")
    match = re.search(
        r"Connected to ((?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})",
        output or "",
    )
    return match.group(1).lower() if match else None

def get_present_device_bssids(initialize):
    """Return fronthaul BSSIDs belonging to present mesh devices."""
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
        bssids.update(
            bssid.lower() for bssid in initialize.get_fronthaul_bssids(device)
        )
    return bssids

def connect_client_to_bssid(
    initialize, client, ssid, passphrase, bssid, ssh, allowed_bssids=None
):
    """
    Connect a client Wi-Fi interface to a specific BSSID.
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
    connected_bssid = get_connected_client_bssid(initialize, client, ssh)
    accepted_bssids = (
        {value.lower() for value in allowed_bssids}
        if allowed_bssids is not None
        else {bssid.lower()}
    )
    if connected_bssid in accepted_bssids:
        if connected_bssid != bssid.lower():
            report_logger.print_info(
                f"Client '{client}' connected to present device BSSID "
                f"{connected_bssid} instead of requested BSSID {bssid.lower()}"
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
    Connect WLAN clients to an extender's visible fronthaul BSSID.
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
    Connect clients to their owning device's fronthaul BSSID.

    Client names must use the ``<device>_wlan_client_<number>`` format. The
    Each requested client is attempted once. When ``require_all`` is false,
    return clients that remain connected and log unavailable clients.
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
            connected_bssid = get_connected_client_bssid(
                initialize, client, ssh
            )
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
                    connected_bssid = get_connected_client_bssid(
                        initialize, client, ssh
                    )
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
