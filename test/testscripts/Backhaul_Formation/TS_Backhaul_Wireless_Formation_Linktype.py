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
import time
from packet_analyzer.ieee1905_utils import (
    MSG_TYPE_TOPOLOGY_DISCOVERY,
    MSG_TYPE_TOPOLOGY_NOTIFICATION,
    MSG_TYPE_AP_AUTOCONFIG_SEARCH,
)
from packet_analyzer.packet_dissector import reassemble_packets, check_message_presence
from rdkbmeshzap.common_utils import device_utils, report_logger

# Time (seconds) to keep capturing so the IEEE 1905 messages can be collected (test plan: 60 seconds).
ONBOARDING_SETTLE_SECONDS = 60
# Maximum time (seconds) to wait for each milestone after the agent reboot (SSH reachable, backhaul connected).
ONBOARDING_TIMEOUT_SECONDS = 240
# Interval (seconds) between consecutive status checks.
POLL_INTERVAL_SECONDS = 10
# Time (seconds) to let the agent go down after the reboot command is issued.
REBOOT_WAIT_SECONDS = 30
# Number of ICMP echo requests sent to the agent (test plan: ping -c 3).
PING_COUNT = "3"
# Number of ping attempts and the gap (seconds) between attempts, to allow the backhaul path to settle.
PING_ATTEMPTS = 3
PING_RETRY_DELAY_SECONDS = 10

_MAC_PATTERN = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$", re.IGNORECASE)

def _wait_until(check, timeout=ONBOARDING_TIMEOUT_SECONDS):
    """
    Poll check() every POLL_INTERVAL_SECONDS until it returns a truthy value or the timeout expires.
    Exceptions raised by check() are treated as "not ready yet".
    """
    deadline = time.monotonic() + timeout
    while True:
        try:
            if check():
                return True
        except Exception as error:
            report_logger.print_info(f"INFO: Not ready yet: {error}")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))

def _reconnect_agent(initialize, agent):
    """
    Re-open the management connection to the agent after its reboot.
    A failed login removes the connection alias, so closing it again on the next retry raises
    "Given alias - <agent> is not present"; that error is ignored so every retry reaches the SSH login.
    """
    try:
        initialize.close_connection(agent)
    except Exception as error:
        report_logger.print_info(f"INFO: No open connection to close for {agent}: {error}")
    return initialize.connect_with_device(agent) is not False

def _ssh_exec(initialize, device, command):
    """
    Run a command on device over its framework connection and return stdout (plus stderr, if any).
    Uses the same API as rdkbmeshzap/cli/feature_interface_cli.py: execute_command(device, command, return_stderr=True).
    """
    connection = initialize.read_from_database(device, "connection")
    connection_obj = initialize.get_connection_module_object(connection)
    output, error = connection_obj.execute_command(device, command, return_stderr=True)
    return f"{output or ''}\n{error or ''}".strip()

def _ping_from_device(initialize, device, target_ip, count=PING_COUNT):
    """
    Ping target_ip from device over the framework SSH connection and return (reachable, output).
    The target is reachable when at least one echo reply is received (packet loss below 100%).
    """
    output = _ssh_exec(initialize, device, f"ping -c {int(count)} -W 2 {target_ip}")
    loss_match = re.search(r"(\d+(?:\.\d+)?)%\s+packet loss", output)
    return (bool(loss_match) and float(loss_match.group(1)) < 100.0), output

def _get_fdb_ports(initialize, agent, mac):
    """
    Return (ports, output): the bridge ports on which the agent's bridge has learned mac (bridge fdb show), and the raw output.
    The port that leads to the controller is the agent's backhaul, so its type gives the backhaul link type.
    """
    output = _ssh_exec(initialize, agent, f"bridge fdb show | grep -i '{mac}'")
    ports = []
    for line in output.splitlines():
        if line.lower().startswith(mac.lower()):
            port_match = re.search(r"\bdev\s+(\S+)", line)
            if port_match and port_match.group(1) not in ports:
                ports.append(port_match.group(1))
    return ports, output

def _verify_agent_backhaul_formation(initialize, agent):
    """
    Verify the established wireless backhaul of one agent to the controller: IEEE 1905 capture, link status, backhaul SSID,
    signal strength, link type (bridge FDB), connectivity and IEEE 1905 topology/autoconfiguration messages. The controller station dump is not
    used: on this platform it is not refreshed when an agent leaves (stale entries stay until the controller reboots).
    """
    report_logger.print_info(f"INFO: Verifying wireless backhaul formation for {agent}")
    capture_name = None
    capture_started = False

    try:
        report_logger.print_step(f"STEP 1 ({agent}): Start the IEEE 1905 packet capture on the controller")
        backhaul_iface = initialize.read_from_database(agent, "backhaul_interface")
        agent_ip = initialize.read_from_database(agent, "bridge_ip")
        expected_ssid = initialize.read_from_database("controller", "mesh_backhaul_ssid")
        capture_interface = initialize.read_from_database("controller", "bridge_iface")
        if not backhaul_iface or not agent_ip or not expected_ssid or not capture_interface:
            report_logger.print_error(f"FAIL: Missing configuration for {agent}: backhaul_interface={backhaul_iface!r}, bridge_ip={agent_ip!r}, mesh_backhaul_ssid={expected_ssid!r}, controller bridge_iface={capture_interface!r}")
            return
        agent_al_mac = initialize.get_al_mac_address(agent, "cli")
        if not agent_al_mac or not _MAC_PATTERN.match(str(agent_al_mac).strip()):
            report_logger.print_error(f"FAIL: Could not read a valid AL MAC address for {agent}: {agent_al_mac!r}; the IEEE 1905 messages cannot be verified")
            return
        agent_al_mac = str(agent_al_mac).strip().lower()
        controller_al_mac = initialize.get_al_mac_address("controller", "cli")
        if not controller_al_mac or not _MAC_PATTERN.match(str(controller_al_mac).strip()):
            report_logger.print_error(f"FAIL: Could not read a valid controller AL MAC address: {controller_al_mac!r}; the backhaul link type cannot be verified")
            return
        controller_al_mac = str(controller_al_mac).strip().lower()
        report_logger.print_info(f"INFO: Agent: {agent}; backhaul interface: {backhaul_iface}; IP: {agent_ip}; AL MAC: {agent_al_mac}; expected backhaul SSID: {expected_ssid}")
        capture_name = device_utils.create_capture_name(f"test_backhaul_wireless_formation_linktype_{agent}")
        capture_filter = initialize.read_from_database("controller", "filter_1905")
        initialize.start_frame_capture("controller", capture_interface, capture_filter, capture_name)
        capture_started = True
        report_logger.print_success(f"PASS: Packet capture started on the controller; capture name: {capture_name}; interface: {capture_interface}")

        report_logger.print_step(f"STEP 2 ({agent}): Reboot {agent} to trigger wireless backhaul onboarding and wait for it to come back online")
        initialize.reboot_device(agent, method="cli")
        report_logger.print_info(f"INFO: {agent} reboot command executed; waiting {REBOOT_WAIT_SECONDS}s for it to go down")
        time.sleep(REBOOT_WAIT_SECONDS)
        if not _wait_until(lambda: _reconnect_agent(initialize, agent)):
            report_logger.print_error(f"FAIL: Could not reconnect to {agent} within {ONBOARDING_TIMEOUT_SECONDS}s after the reboot")
            return
        if not _wait_until(lambda: initialize.get_wireless_backhaul_connection_status(agent, backhaul_iface)):
            report_logger.print_error(f"FAIL: {agent} did not re-establish the wireless backhaul on {backhaul_iface} within {ONBOARDING_TIMEOUT_SECONDS}s")
            return
        report_logger.print_success(f"PASS: {agent} rebooted, came back online and started the wireless backhaul re-establishment")

        report_logger.print_step(f"STEP 3 ({agent}): Verify the wireless backhaul status (iw dev {backhaul_iface} link)")
        link_info = initialize.get_iw_dev_link_info(agent, backhaul_iface)
        report_logger.print_info(f"INFO: Link information:\n{link_info}")
        bssid_match = re.search(r"Connected to\s+([0-9a-fA-F:]{17})", str(link_info))
        if not bssid_match:
            report_logger.print_error(f"FAIL: {agent} is not connected to a backhaul BSSID on {backhaul_iface}")
        else:
            report_logger.print_success(f"PASS: {agent} is connected to backhaul BSSID {bssid_match.group(1).lower()}")
        ssid = initialize.get_iw_link_details(agent, backhaul_iface, "ssid")
        if not ssid:
            report_logger.print_error("FAIL: Unable to retrieve the connected SSID")
        elif str(ssid[0]).strip() != str(expected_ssid).strip():
            report_logger.print_error(f"FAIL: Connected SSID {ssid[0]!r} does not match the expected backhaul SSID {expected_ssid!r}")
        else:
            report_logger.print_success(f"PASS: Connected SSID {ssid[0]} matches the expected backhaul SSID")
        signal = initialize.get_iw_link_details(agent, backhaul_iface, "signal")
        signal_match = re.search(r"-?\d+(?:\.\d+)?", str(signal[0])) if signal else None
        if not signal_match:
            report_logger.print_error(f"FAIL: Signal strength is not available on {backhaul_iface}: {signal}")
        else:
            report_logger.print_success(f"PASS: Signal strength is displayed: {signal[0]}")

        report_logger.print_step(f"STEP 4 ({agent}): Verify the backhaul link type: the controller AL MAC {controller_al_mac} must be learned on {backhaul_iface} in the {agent} bridge (bridge fdb show)")
        fdb_result = {}
        def _controller_learned():
            fdb_result["ports"], fdb_result["output"] = _get_fdb_ports(initialize, agent, controller_al_mac)
            return bool(fdb_result["ports"])
        _wait_until(_controller_learned, timeout=ONBOARDING_SETTLE_SECONDS * 2)
        fdb_ports = fdb_result.get("ports", [])
        report_logger.print_info(f"INFO: Bridge FDB entries for the controller AL MAC:\n{fdb_result.get('output', '')}")
        if not fdb_ports:
            report_logger.print_error(f"FAIL: Controller AL MAC {controller_al_mac} is not learned in the {agent} bridge; the backhaul link type cannot be determined")
        elif any(port == backhaul_iface or port.startswith(f"{backhaul_iface}.") for port in fdb_ports):
            report_logger.print_success(f"PASS: Backhaul link type is Wi-Fi: controller AL MAC is learned on the wireless backhaul interface {backhaul_iface} (ports: {fdb_ports})")
        else:
            report_logger.print_error(f"FAIL: Backhaul link type is not Wi-Fi: controller AL MAC is learned on {fdb_ports}, not on the wireless backhaul interface {backhaul_iface}")

        report_logger.print_step(f"STEP 5 ({agent}): Ping {agent} ({agent_ip}) from the controller (ping -c {PING_COUNT})")
        reachable = False
        for attempt in range(1, PING_ATTEMPTS + 1):
            try:
                reachable, ping_output = _ping_from_device(initialize, "controller", agent_ip)
            except Exception as error:
                reachable, ping_output = False, f"ping could not be executed: {error}"
            report_logger.print_info(f"INFO: Ping attempt {attempt}/{PING_ATTEMPTS}:\n{ping_output}")
            if reachable:
                break
            if attempt < PING_ATTEMPTS:
                time.sleep(PING_RETRY_DELAY_SECONDS)
        if reachable:
            report_logger.print_success(f"PASS: {agent} ({agent_ip}) responds to ping from the controller")
        else:
            report_logger.print_error(f"FAIL: {agent} ({agent_ip}) did not respond to ping from the controller after {PING_ATTEMPTS} attempts")

        report_logger.print_step(f"STEP 6 ({agent}): Stop the capture after the IEEE 1905 onboarding exchange and verify Topology Discovery and AP Autoconfiguration Search for {agent} AL MAC {agent_al_mac} (Topology Notification informational)")
        report_logger.print_info(f"INFO: Waiting {ONBOARDING_SETTLE_SECONDS}s for the IEEE 1905 onboarding messages")
        time.sleep(ONBOARDING_SETTLE_SECONDS)
        local_path = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        packets = reassemble_packets(local_path)
        report_logger.print_success(f"PASS: Packet capture stopped and collected: {local_path}")

        for message_type, message_name in (
            (MSG_TYPE_TOPOLOGY_DISCOVERY, "Topology Discovery"),
            (MSG_TYPE_AP_AUTOCONFIG_SEARCH, "AP Autoconfiguration Search"),
        ):
            present = (check_message_presence(packets, message_type, src_mac=agent_al_mac)
                       or check_message_presence(packets, message_type, dst_mac=agent_al_mac))
            if present:
                report_logger.print_success(f"PASS: {message_name} observed for {agent} (AL MAC {agent_al_mac}); count: {len(present)}")
            else:
                report_logger.print_error(f"FAIL: {message_name} was not observed for {agent} (AL MAC {agent_al_mac}) in the capture")

        present = check_message_presence(packets, MSG_TYPE_TOPOLOGY_NOTIFICATION)
        if present:
            report_logger.print_info(f"INFO: Topology Notification observed in the capture; count: {len(present)}")
        else:
            report_logger.print_info("INFO: Topology Notification was not observed in the capture (not required for this test case)")
    finally:
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
            except Exception as error:
                report_logger.log(f"Could not collect remote packet capture: {error}")

def test_backhaul_wireless_formation_linktype(initialize):
    """
    EM_Backhaul_Wireless_Formation_LinkType: verify that the Wi-Fi backhaul link between each enabled agent
    (extender1 / extender2 ... as enabled in infra.yaml) and the Controller is re-established after the agent reboots:
    link status, backhaul SSID, signal strength, link type (controller AL MAC learned on the Wi-Fi backhaul interface
    in the agent bridge FDB), connectivity and IEEE 1905 topology/autoconfiguration messages.
    The controller station dump is not used (it is not refreshed when an agent leaves, so it can show stale entries).
    The packet capture is started before the reboot so the onboarding exchange is
    captured; each following step waits until the reboot has completed and the backhaul is up.
    """
    report_logger.print_test("Entering test_backhaul_wireless_formation_linktype")
    try:
        agents = device_utils.get_enabled_extenders(initialize)
        if not agents:
            report_logger.print_error("FAIL: No enabled extender found in the infrastructure configuration")
            return
        report_logger.print_info(f"INFO: Agents under test: {agents}")
        for agent in agents:
            _verify_agent_backhaul_formation(initialize, agent)
    finally:
        report_logger.print_test("Exiting test_backhaul_wireless_formation_linktype")
