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
from scapy.all import Ether
from scapy.all import rdpcap
from rdkbmeshzap.common_utils import report_logger
from rdkbmeshzap.common_utils import device_utils

DOWN_WAIT_SECONDS = 10
RECONNECT_TIMEOUT_SECONDS = 120
RECONNECT_POLL_SECONDS = 5
EAPOL_CAPTURE_FILTER = "ether proto 0x888e"
ETHERTYPE_EAPOL = 0x888E
EAPOL_TYPE_KEY = 3

def verify_backhaul_association(initialize, agent, backhaul_iface, expected_ssid):
    """
    Syntax: verify_backhaul_association(initialize, agent, backhaul_iface, expected_ssid)
    Description: Verify association to the expected backhaul SSID.
    Parameters: initialize - Testbed interface; agent - Agent device name;
                backhaul_iface - Agent backhaul interface; expected_ssid - Expected backhaul SSID.
    Return Value: The iw dev link output for the backhaul interface.
    Example: verify_backhaul_association(initialize, "extender1", "wifi1.3", "mesh_backhaul")
    """
    assert initialize.get_wireless_backhaul_connection_status(agent, backhaul_iface), f"{agent}: Agent is not connected on {backhaul_iface}"
    _, ssid = initialize.get_backhaul_link_details(agent, backhaul_iface)
    assert ssid is not None, f"{agent}: SSID not found in link output"
    assert ssid == expected_ssid, f"{agent}: Agent is not connected to expected SSID {expected_ssid!r}; got {ssid!r}"
    return initialize.get_iw_dev_link_info(agent, backhaul_iface)

def verify_controller_connectivity(initialize, agent, controller_ip):
    """
    Syntax: verify_controller_connectivity(initialize, agent, controller_ip)
    Description: Verify the agent can reach the controller by ping with 0% packet loss.
    Parameters: initialize - Testbed interface; agent - Agent device name;
                controller_ip - Controller bridge IP address.
    Return Value: None; asserts when the ping output is missing or shows packet loss.
    Example: verify_controller_connectivity(initialize, "extender1", "192.168.1.1")
    """
    ping_output = initialize.execute_command(agent, f"ping -c 4 -W 2 {shlex.quote(controller_ip)}")
    match = re.search(r"(\d+(?:\.\d+)?)%\s+packet loss", ping_output)
    assert match, f"Packet loss value not found in ping output:\n{ping_output}"
    assert float(match.group(1)) == 0, f"Controller-Agent connectivity failed: {match.group(1)}% packet loss\n{ping_output}"

def wait_for_reconnect(initialize, agent, backhaul_iface, expected_ssid):
    """
    Syntax: wait_for_reconnect(initialize, agent, backhaul_iface, expected_ssid)
    Description: Wait for successful backhaul reconnection to the expected SSID.
    Parameters: initialize - Testbed interface; agent - Agent device name;
                backhaul_iface - Agent backhaul interface; expected_ssid - SSID to reconnect to.
    Return Value: A tuple of (bssid, ssid) on reconnection, otherwise None after logging the error.
    Example: wait_for_reconnect(initialize, "extender1", "wifi1.3", "mesh_backhaul")
    """
    deadline = time.monotonic() + RECONNECT_TIMEOUT_SECONDS
    last_state = "no link information"
    while time.monotonic() < deadline:
        try:
            bssid, ssid = initialize.get_backhaul_link_details(agent, backhaul_iface)
            last_state = f"bssid={bssid}, ssid={ssid}"
            if bssid and ssid == expected_ssid:
                return bssid, ssid
        except Exception as exc:
            last_state = f"command temporarily unavailable: {exc}"
            report_logger.print_info(f"{agent}: {last_state}")
        time.sleep(RECONNECT_POLL_SECONDS)
    report_logger.print_error(f"FAIL: {agent}: Backhaul did not reconnect within {RECONNECT_TIMEOUT_SECONDS} seconds. Last link state: {last_state}")
    return None

def count_eapol_key_frames(pcap_path):
    """
    Syntax: count_eapol_key_frames(pcap_path)
    Description: Count EAPOL-Key frames in a packet capture.
    Parameters: pcap_path - Path to the local pcap file.
    Return Value: The number of EAPOL-Key frames.
    Example: count_eapol_key_frames("capture.pcapng")
    """
    count = 0
    for pkt in rdpcap(pcap_path):
        if not pkt.haslayer(Ether) or pkt[Ether].type != ETHERTYPE_EAPOL:
            continue
        payload = bytes(pkt[Ether].payload)
        if len(payload) >= 2 and payload[1] == EAPOL_TYPE_KEY:
            count += 1
    return count

def verify_eapol_handshake(pcap_path):
    """
    Syntax: verify_eapol_handshake(pcap_path)
    Description: Verify EAPOL authentication activity following reassociation.
    Parameters: pcap_path - Path to the local pcap file.
    Return Value: The number of EAPOL-Key frames found.
    Example: verify_eapol_handshake("capture.pcapng")
    """
    frame_count = count_eapol_key_frames(pcap_path)
    report_logger.print_info(f"Captured EAPOL-Key frames in {pcap_path}: {frame_count}")
    assert frame_count >= 2, f"Expected a complete EAPOL authentication exchange after reassociation. Found {frame_count} frame(s)."
    return frame_count

def get_bssid_owner(initialize, bssid, devices):
    """
    Syntax: get_bssid_owner(initialize, bssid, devices)
    Description: Identify which device owns a BSSID by scanning all wireless interfaces (including MLD link addresses).
    Parameters: initialize - Testbed interface; bssid - BSSID to resolve; devices - Candidate owner devices.
    Return Value: The owning device name, or None when no candidate owns the BSSID.
    Example: get_bssid_owner(initialize, "02:02:21:52:a6:48", ["controller", "extender1"])
    """
    for device in devices:
        try:
            interfaces = initialize.get_wireless_interfaces_list(device)
        except Exception:
            continue
        for interface in interfaces:
            try:
                output = initialize.get_iw_dev_interface_info(device, interface)
            except Exception:
                continue
            if re.search(rf"\baddr\s+{re.escape(bssid)}\b", str(output), re.IGNORECASE):
                return device
    return None

def verify_bssid_owned_by_controller(initialize, agent, bssid, controller="controller"):
    """
    Syntax: verify_bssid_owned_by_controller(initialize, agent, bssid, controller="controller")
    Description: Verify a connected BSSID belongs to the Controller, not to another Agent (multi-hop).
    Parameters: initialize - Testbed interface; agent - Agent device name; bssid - Connected BSSID;
                controller - Controller device name.
    Return Value: None; asserts when the BSSID is not a Controller BSS.
    Example: verify_bssid_owned_by_controller(initialize, "extender1", "02:02:21:52:a6:48")
    """
    if get_bssid_owner(initialize, bssid, [controller]):
        return
    other_agents = [device for device in device_utils.get_enabled_extenders(initialize) if device != agent]
    owner = get_bssid_owner(initialize, bssid, other_agents)
    assert False, f"{agent}: BSSID {bssid} does not belong to {controller} (owner: {owner or 'unknown'})"