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
import pytest
from rdkbmeshzap.common_utils import report_logger

BACKHAUL_AKM_PARAMETER = "Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.1.BackhaulAKMsAllowed"
BACKHAUL_LINK_COMMAND = "iw dev wifi1.3 link"
AGENT = "extender1"
CONTROLLER = "controller"
BACKHAUL_IFACE = "wifi1.3"
LINK_CMD = f"iw dev {BACKHAUL_IFACE} link"
PCAP_PATH = "/tmp/backhaul_reassoc.pcap"
DOWN_WAIT_SECONDS = 10
RECONNECT_TIMEOUT_SECONDS = 120
RECONNECT_POLL_SECONDS = 5
MAC_RE = r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}"

def run_command(initialize, device, command, check=True):
    """Execute a command on a device and return (stdout, rc)."""
    stdout, stderr, rc = initialize.execute_command(
        device, command, return_stderr=True, return_rc=True
    )
    output = str(stdout or "")
    if check:
        assert rc == 0, (
            f"{device}: command failed\n"
            f"Command : {command}\n"
            f"RC      : {rc}\n"
            f"STDOUT  : {output}\n"
            f"STDERR  : {stderr}"
        )
    report_logger.print_info(output)
    return output, rc

def try_run_command(initialize, device, command):
    """Execute a command that may fail while backhaul connectivity is unavailable."""
    try:
        return run_command(initialize, device, command, check=False)
    except Exception as exc:
        report_logger.print_info(f"{device}: command temporarily unavailable: {exc}")
        return None, None

def parse_link(output):
    """Parse 'iw dev <iface> link' output and return (bssid, ssid)."""
    if not output:
        return None, None
    connected = re.search(rf"^\s*Connected to ({MAC_RE})\b", output, re.MULTILINE)
    ssid = re.search(r"^\s*SSID:\s*(.*?)\s*$", output, re.MULTILINE)
    return (
        connected.group(1).lower() if connected else None,
        ssid.group(1).strip() if ssid else None,
    )

def get_backhaul_akm(initialize):
    """Return the configured BackhaulAKMsAllowed value from the controller."""
    output, _ = run_command(initialize, CONTROLLER, f"rbuscli get {BACKHAUL_AKM_PARAMETER}")
    akm = re.search(
        rf"^\s*Name\s*:\s*{re.escape(BACKHAUL_AKM_PARAMETER)}[ \t]*\r?\n"
        rf"\s*Type\s*:[^\r\n]+\r?\n"
        rf"\s*Value\s*:\s*([^\r\n]*)",
        output,
        re.MULTILINE,
    )
    assert akm, f"AKM property/value was not returned:\n{output}"
    value = akm.group(1).strip().strip("\"'")
    assert value, f"Configured AKM value is empty:\n{output}"
    return value

def get_expected_ssid(initialize):
    """Return the controller's configured backhaul SSID."""
    expected_ssid = initialize.read_from_database(CONTROLLER, "mesh_backhaul_ssid")
    assert isinstance(expected_ssid, str) and expected_ssid.strip(), (
        "controller.mesh_backhaul_ssid must be configured"
    )
    return expected_ssid.strip()

def get_agent_ip(initialize):
    """Return the agent's bridge IP."""
    agent_ip = initialize.read_from_database(AGENT, "bridge_ip")
    assert isinstance(agent_ip, str) and agent_ip.strip(), (
        f"{AGENT}.bridge_ip must be configured"
    )
    return agent_ip.strip()

def verify_backhaul_association(initialize, agent):
    """Verify the agent is associated to the expected backhaul SSID and return the link output."""
    expected_ssid = get_expected_ssid(initialize)
    output, _ = run_command(initialize, agent, BACKHAUL_LINK_COMMAND)
    assert re.search(rf"^\s*Connected to {MAC_RE}\b", output, re.MULTILINE), (
        f"Agent is not connected:\n{output}"
    )
    ssid = re.search(r"^\s*SSID:\s*(.*?)\s*$", output, re.MULTILINE)
    assert ssid, f"SSID not found in link output:\n{output}"
    assert ssid.group(1).strip() == expected_ssid, (
        f"Agent is not connected to expected SSID {expected_ssid!r}:\n{output}"
    )
    return output

def verify_link_metrics(output):
    """Verify signal strength, frequency and transmit bitrate are reported in the link output."""
    signal = re.search(r"^\s*signal:\s*(-?\d+(?:\.\d+)?)\s+dBm\b", output, re.MULTILINE)
    frequency = re.search(r"^\s*freq:\s*(\d+(?:\.\d+)?)", output, re.MULTILINE)
    tx_bitrate = re.search(r"^\s*tx bitrate:\s*(\d+(?:\.\d+)?)", output, re.MULTILINE)
    assert signal, f"Signal strength information missing:\n{output}"
    assert frequency and float(frequency.group(1)) > 0, f"Frequency information missing:\n{output}"
    assert tx_bitrate and float(tx_bitrate.group(1)) > 0, f"Transmit bitrate information missing:\n{output}"

def verify_controller_connectivity(initialize, agent):
    """Verify the agent can ping the controller's bridge IP."""
    controller_ip = initialize.read_from_database(CONTROLLER, "bridge_ip")
    assert isinstance(controller_ip, str) and controller_ip.strip(), (
        "controller.bridge_ip must be configured"
    )
    ping_output, _ = run_command(
        initialize, agent, f"ping -c 4 -W 2 {shlex.quote(controller_ip.strip())}"
    )
    assert (
        "0% packet loss" in ping_output
        or "4 packets transmitted, 4 received" in ping_output
        or "4 received" in ping_output
    ), f"Controller-Agent connectivity failed:\n{ping_output}"

def wait_for_reconnect(initialize, expected_ssid):
    """Wait until the agent reconnects to the expected backhaul SSID and return (bssid, output)."""
    deadline = time.monotonic() + RECONNECT_TIMEOUT_SECONDS
    last_output = ""
    while time.monotonic() < deadline:
        output, rc = try_run_command(initialize, AGENT, LINK_CMD)
        if output is not None and rc == 0:
            last_output = output
            bssid, ssid = parse_link(output)
            if bssid and ssid == expected_ssid:
                return bssid, output
        time.sleep(RECONNECT_POLL_SECONDS)
    pytest.fail(
        f"{AGENT}: Backhaul did not reconnect within {RECONNECT_TIMEOUT_SECONDS} seconds.\n\n"
        f"Last link output:\n{last_output}"
    )

def verify_eapol_handshake(dump_output):
    """Verify at least two EAPOL-Key frames were captured after reassociation and return their count."""
    eapol_key_frames = [
        line for line in dump_output.splitlines()
        if re.search(r"EAPOL\s+key", line, re.IGNORECASE)
    ]
    report_logger.print_info("Captured EAPOL Frames:\n" + "\n".join(eapol_key_frames))
    assert len(eapol_key_frames) >= 2, (
        f"Expected EAPOL-Key handshake activity after reassociation. "
        f"Found {len(eapol_key_frames)} frame(s).\n\n{dump_output}"
    )
    return len(eapol_key_frames)