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

import os
import re
import shlex
import time
from pathlib import Path
from rdkbmeshzap.common_utils import report_logger

def get_client_wifi_scannned_bssids(client, ssid, ssh):
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

# This API is temporarily used to resolve the sudo access issue.
def connect_client_to_bssid(initialize, client, ssid, passphrase, bssid, ssh):
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
    if "successfully activated" not in output.lower():
        raise RuntimeError(f"Failed to connect {client} to BSSID {bssid}: {output}")

def start_client_ping(initialize, client_devices, output_path):
    """
    Start continuous IPv4 ping collection on client interfaces.
    """
    ssh = initialize.get_connection_module_object("ssh")
    for client in client_devices:
        wifi_interface = initialize.read_from_database(client, "data_iface")
        ssh.switch_connection(client)
        ssh.execute_command(
            f"rm -f {shlex.quote(output_path)}; "
            f"nohup ping -4 -I {shlex.quote(wifi_interface)} "
            f"-i 1 8.8.8.8 > {shlex.quote(output_path)} 2>&1 </dev/null &"
        )

def connect_clients_to_extender(initialize, client_devices, extender):
    """
    Connect WLAN clients to an extender's visible fronthaul BSSID.
    """
    ssh = initialize.get_connection_module_object("ssh")
    ssid, passphrase = initialize.get_fronthaul_credentials("controller")
    extender_bssids = initialize.get_fronthaul_bssids(extender)
    for client in client_devices:
        password = initialize.read_from_database(client, "password")
        interface = initialize.read_from_database(client, "data_iface")
        ssh.switch_connection(client)
        try:
            ssh.execute_command(
                f"printf '%s\\n' {shlex.quote(password)} | "
                f"sudo -S -p '' nmcli device disconnect {shlex.quote(interface)}"
            )
        except Exception as error:
            report_logger.print_info(
                f"INFO: Could not disconnect {client} interface {interface} "
                f"before reassociation; continuing with nmcli connect: {error}"
            )
        time.sleep(2)
        for attempt in range(3):
            try:
                initialize.check_ap_ssid_visibility(client, ssid)
                visible_bssids = get_client_wifi_scannned_bssids(client, ssid, ssh)
                normalized_extender_bssids = {
                    bssid.lower() for bssid in extender_bssids
                }
                target_bssid = next(
                    (
                        bssid
                        for bssid in visible_bssids
                        if bssid in normalized_extender_bssids
                    ),
                    None,
                )
                if not target_bssid:
                    raise RuntimeError(f"BSSID for '{ssid}' was not found")
                break
            except Exception as error:
                if attempt == 2:
                    raise RuntimeError(
                        f"{client}: SSID '{ssid}' was not visible after retries: {error}"
                    ) from error
                time.sleep(5)
        connect_client_to_bssid(
            initialize, client, ssid, passphrase, target_bssid, ssh
        )

def validate_ping_recovery(ping_output, client):
    """
    Validate an outage followed by successful ping replies.
    """
    lines = ping_output.splitlines()
    outage_indexes = [
        index for index, line in enumerate(lines)
        if "unreachable" in line.lower() or "100% packet loss" in line.lower()
    ]
    if not outage_indexes:
        report_logger.print_error(
            f"{client}: ping did not show an outage during recovery"
        )
        return False
    last_outage = outage_indexes[-1]
    if not any(
        re.search(r"\b\d+\s+bytes from\s+", line, re.IGNORECASE)
        for line in lines[last_outage + 1:]
    ):
        report_logger.print_error(
            f"{client}: ping produced no successful replies after the outage:\n"
            f"{ping_output}"
        )
        return False
    return True

def download_client_pings(initialize, clients, extender):
    """
    Stop client pings and save their remote output locally.
    """
    ssh = initialize.get_connection_module_object("ssh")
    remote_path = f"/tmp/controller_recovery_{extender}_client_ping.txt"
    local_directory = Path(os.environ.get("TEST_RUN_DIR", "Reports"), "ping_logs")
    local_directory.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for client in clients:
        ssh.switch_connection(client)
        ssh.execute_command(
            "killall ping",
        )
        output = ssh.execute_command(f"cat {shlex.quote(remote_path)}") or ""
        safe_extender = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(extender)).strip("._")
        safe_client = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(client)).strip("._")
        local_path = local_directory / f"{safe_extender or 'unknown'}_{safe_client or 'unknown'}_ping.txt"
        local_path.write_text(output, encoding="utf-8")
        outputs[client] = output
        report_logger.print_step(f"{client}: ping output stored at {local_path}")
    return outputs
