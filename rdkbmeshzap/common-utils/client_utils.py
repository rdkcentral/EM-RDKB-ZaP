"""Shared client Wi-Fi helpers for Controller Recovery tests."""

import os
import re
import shlex
import time
from pathlib import Path

import pytest
import test_report_utils as zi_logger

def get_client_bssids(initialize, client, ssid, ssh):
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

def connect_client_to_bssid(initialize, client, ssid, passphrase, bssid, ssh):
    """
    Connect a client Wi-Fi interface to a specific BSSID.
    """
    client_password = initialize.read_from_database(client, "password")
    wifi_interface = initialize.read_from_database(client, "data_iface")
    ssh.switch_connection(client)
    command = (
        f"printf '%s\\n' {shlex.quote(client_password)} | "
        f"sudo -S -p '' nmcli device wifi connect {shlex.quote(ssid)} "
        f"password {shlex.quote(passphrase)} bssid {shlex.quote(bssid.upper())} "
        f"ifname {shlex.quote(wifi_interface)}"
    )
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
        except Exception:
            zi_logger.print_step(f"{client}: Wi-Fi interface already disconnected")
        time.sleep(2)
        for attempt in range(3):
            try:
                initialize.check_ap_ssid_visibility(client, ssid)
                visible_bssids = get_client_bssids(initialize, client, ssid, ssh)
                target_bssid = next(
                    (bssid for bssid in extender_bssids if bssid in visible_bssids),
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
    Require an outage followed by successful ping replies.
    """
    lines = ping_output.splitlines()
    outage_indexes = [
        index for index, line in enumerate(lines)
        if "unreachable" in line.lower() or "100% packet loss" in line.lower()
    ]
    if not outage_indexes:
        pytest.fail(f"{client}: ping did not show an outage during recovery")
    last_outage = outage_indexes[-1]
    if not any("bytes from" in line for line in lines[last_outage + 1:]):
        pytest.fail(
            f"{client}: ping produced no successful replies after the outage:\n"
            f"{ping_output}"
        )

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
        ssh.execute_command("killall ping", return_stdout=False, return_stderr=True)
        output = ssh.execute_command(f"cat {shlex.quote(remote_path)}")
        local_path = local_directory / f"{extender}_{client}_ping.txt"
        local_path.write_text(output, encoding="utf-8")
        outputs[client] = output
        zi_logger.print_step(f"{client}: ping output stored at {local_path}")
    return outputs
