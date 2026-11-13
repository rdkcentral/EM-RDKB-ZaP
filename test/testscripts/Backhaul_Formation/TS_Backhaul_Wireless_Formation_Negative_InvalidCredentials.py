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
from collections import Counter
from scapy.all import Ether
from packet_analyzer.ieee1905_utils import (
    MSG_TYPE_TOPOLOGY_DISCOVERY,
    MSG_TYPE_AP_AUTOCONFIG_SEARCH,
    MSG_TYPE_AP_AUTOCONFIGURATION_RESPONSE,
    MSG_TYPE_AP_AUTOCONFIGURATION_WSC,
)
from packet_analyzer.message_verify import get_message_type_name
from packet_analyzer.packet_dissector import reassemble_packets, check_message_presence
from rdkbmeshzap.common_utils import device_utils, report_logger

# Test settings (defined only in this script).
# Agent under test. None selects the first enabled extender from infra.yaml.
AGENT = None
# File on the agent that holds the provisioned backhaul credentials (Backhaul_SSID / Backhaul_KeyPassphrase).
AGENT_BACKHAUL_CONFIG = "/nvram/EasymeshCfg.json"
# Copy of the original file, kept on the agent so the valid credentials can be restored manually after the test.
AGENT_BACKHAUL_CONFIG_BACKUP = "/nvram/EasymeshCfg.json.tc12.bak"
# Deliberately wrong backhaul passphrase. It must not contain the characters / & \ (used inside a sed expression).
INVALID_PASSPHRASE = "InvalidBackhaulPassphrase_TC12"
# Command to restart the agent services; used only in the manual restore instructions (the test reboots the agent).
AGENT_RESTART_COMMAND = "systemctl restart onewifi em_agent ieee1905_em_agent"
# Command run on the agent so that it boots with the invalid credentials from /nvram (no old association survives).
AGENT_REBOOT_COMMAND = "sync; reboot"
# Time (seconds) to let the agent reboot and attempt the backhaul with the invalid credentials before the observation.
APPLY_SETTLE_SECONDS = 180
# Time (seconds) during which the agent must NOT form the backhaul with the invalid credentials.
OBSERVATION_SECONDS = 240
# Interval (seconds) between the samples taken during the observation window.
POLL_INTERVAL_SECONDS = 30
# Number of ICMP echo requests sent to the agent from the controller.
PING_COUNT = "2"

# Onboarding related CMDUs. With invalid credentials the first ones may still be exchanged (partial onboarding) while
# the agent is going down for the reboot. They are informational evidence only; onboarding
# is considered completed only by the AP Autoconfiguration WSC sent by the controller to the agent.
_ONBOARDING_MESSAGE_TYPES = (
    MSG_TYPE_AP_AUTOCONFIG_SEARCH,
    MSG_TYPE_AP_AUTOCONFIGURATION_RESPONSE,
    MSG_TYPE_AP_AUTOCONFIGURATION_WSC,
)

def _last_line(text):
    """Return the last non-empty line of text (stripped), or an empty string."""
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    return lines[-1] if lines else ""

def _ssh_exec(initialize, device, command):
    """
    Run a command on device over its framework connection and return its stdout.
    Uses the same API as rdkbmeshzap/cli/feature_interface_cli.py: execute_command(device, command, return_stderr=True).
    stderr is only logged, so callers that check the last output line (grep -c ...) are not affected by it.
    """
    connection = initialize.read_from_database(device, "connection")
    connection_obj = initialize.get_connection_module_object(connection)
    output, error = connection_obj.execute_command(device, command, return_stderr=True)
    if error and str(error).strip():
        report_logger.print_info(f"INFO: stderr of '{command}' on {device}: {str(error).strip()}")
    return str(output or "")

def _ping_from_device(initialize, device, target_ip, count=None):
    """
    Ping target_ip from device over the framework SSH connection and return (reachable, output).
    The target is reachable when at least one echo reply is received (packet loss below 100%).
    """
    count = PING_COUNT if count is None else count
    output = _ssh_exec(initialize, device, f"ping -c {int(count)} -W 2 {target_ip}")
    loss_match = re.search(r"(\d+(?:\.\d+)?)%\s+packet loss", output)
    return (bool(loss_match) and float(loss_match.group(1)) < 100.0), output

def _controller_epoch(initialize):
    """
    Current time (epoch seconds) on the controller. The capture is taken on the controller, so its packet timestamps are on
    the same clock; using it avoids any clock offset between the test host and the controller.
    """
    output = _last_line(_ssh_exec(initialize, "controller", "date +%s.%N"))
    if not re.match(r"^\d+\.\d+$", output):
        output = _last_line(_ssh_exec(initialize, "controller", "date +%s"))
    return float(output)

def _agent_1905_messages(packets, agent_al_mac, observation_start):
    """
    Collect the IEEE 1905 messages sent by or addressed to the agent AL MAC, split at observation_start (controller epoch).
    Returns (before_observation, during_observation); every entry is (message_type, sent_by_agent, timestamp).
    """
    agent_mac = agent_al_mac.lower()
    before, during = [], []
    for pkt in packets:
        if not pkt.haslayer(Ether):
            continue
        eth = pkt[Ether]
        from_agent = eth.src.lower() == agent_mac
        if not from_agent and eth.dst.lower() != agent_mac:
            continue
        payload = bytes(eth.payload)
        if len(payload) < 4:
            continue
        entry = ((payload[2] << 8) | payload[3], from_agent, float(pkt.time))
        (during if entry[2] >= observation_start else before).append(entry)
    return before, during

def _describe(entries):
    """Return a compact 'Message name (direction) xcount' description of the entries."""
    counts = Counter((get_message_type_name(message_type), "agent->controller" if from_agent else "controller->agent")
                     for message_type, from_agent, _ in entries)
    return "; ".join(f"{name} ({direction}) x{count}" for (name, direction), count in sorted(counts.items())) or "none"

def _collect_samples(initialize, agent, agent_ip):
    """
    Observation window: every POLL_INTERVAL_SECONDS, for OBSERVATION_SECONDS, sample from the controller whether the agent
    answers a ping. The controller station dump / station count is not used: on this platform it is not refreshed when
    an agent leaves (stale entries stay until the controller reboots). Nothing is judged here.
    Each sample is a dict: poll, elapsed, reachable, ping_output.
    """
    samples = []
    started = time.monotonic()
    deadline = started + OBSERVATION_SECONDS
    while True:
        sample = {"poll": len(samples) + 1, "elapsed": time.monotonic() - started}
        try:
            sample["reachable"], sample["ping_output"] = _ping_from_device(initialize, "controller", agent_ip)
        except Exception as error:
            sample["reachable"], sample["ping_output"] = False, f"ping could not be executed: {error}"
        samples.append(sample)
        report_logger.print_info(f"INFO: Poll {sample['poll']} (+{sample['elapsed']:.0f}s): {agent} reachable from the controller: {sample['reachable']}")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return samples
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))

def _verify_not_reachable(agent, agent_ip, samples):
    """Plan check: the agent is not reachable from the controller (every sample, including the final one)."""
    reachable_polls = [s for s in samples if s["reachable"]]
    for sample in reachable_polls:
        report_logger.print_error(f"FAIL: Poll {sample['poll']}: {agent} ({agent_ip}) is reachable from the Controller although its backhaul credentials are invalid:\n{sample['ping_output']}")
    if reachable_polls:
        report_logger.print_error(f"FAIL: {agent} is reachable from the Controller in {len(reachable_polls)} of {len(samples)} polls; the backhaul link must not form with invalid credentials")
    else:
        report_logger.print_success(f"PASS: {agent} ({agent_ip}) is not reachable from the Controller in all {len(samples)} polls over {OBSERVATION_SECONDS}s")

def _verify_onboarding_not_completed(agent, agent_al_mac, controller_al_mac, packets, observation_start):
    """
    Plan check: the capture is valid and onboarding does not complete successfully. Onboarding completes with the AP
    Autoconfiguration WSC (M2) sent by the controller to the agent. Returns (before_observation, during_observation)
    agent 1905 messages, which are reviewed (partial onboarding traffic) in the last step.
    """
    if check_message_presence(packets, MSG_TYPE_TOPOLOGY_DISCOVERY, src_mac=controller_al_mac):
        report_logger.print_success(f"PASS: The capture is valid: Topology Discovery from the Controller (AL MAC {controller_al_mac}) is present")
    else:
        report_logger.print_error(f"FAIL: No Topology Discovery from the Controller (AL MAC {controller_al_mac}) in the capture; the capture cannot be used as evidence")

    before, during = _agent_1905_messages(packets, agent_al_mac, observation_start)
    completed = [entry for entry in during if entry[0] == MSG_TYPE_AP_AUTOCONFIGURATION_WSC and not entry[1]]
    if completed:
        report_logger.print_error(f"FAIL: Onboarding of {agent} completed successfully with invalid credentials: AP Autoconfiguration WSC from the Controller to {agent_al_mac} x{len(completed)} during the observation window")
    else:
        report_logger.print_success(f"PASS: Onboarding of {agent} did not complete successfully: no AP Autoconfiguration WSC from the Controller to {agent_al_mac} during the observation window")
    return before, during

def _verify_not_in_active_topology(agent, agent_al_mac, agent_messages, samples):
    """
    Plan check: the agent does not rejoin the active topology. It must not be reachable from the controller in the final
    sample, and must not send 1905 messages other than AP Autoconfiguration (Topology Discovery, Topology Notification,
    Topology Response, ...) during the observation window.
    """
    final = samples[-1]
    if final["reachable"]:
        report_logger.print_error(f"FAIL: {agent} rejoined the active topology: it is reachable from the Controller in the final poll")
    else:
        report_logger.print_success(f"PASS: In the final poll {agent} is not reachable from the Controller")

    topology = [entry for entry in agent_messages if entry[1] and entry[0] not in _ONBOARDING_MESSAGE_TYPES]
    if topology:
        report_logger.print_error(f"FAIL: {agent} (AL MAC {agent_al_mac}) rejoined the active topology: 1905 messages from the Agent during the observation window: {_describe(topology)}")
    else:
        report_logger.print_success(f"PASS: {agent} (AL MAC {agent_al_mac}) did not rejoin the active topology: no topology messages from the Agent during the observation window")

def _review_onboarding_traffic(agent, agent_al_mac, before, during, restart_requested_at, observation_start):
    """
    Plan review: partial onboarding traffic (AP Autoconfiguration Search/Response, or an early WSC) may be present with
    invalid credentials; it is reported as information only. Only a WSC from the controller to the agent during the
    observation window would be a successful onboarding, and that is already failed by the onboarding check.
    """
    early = [entry for entry in before if entry[0] in _ONBOARDING_MESSAGE_TYPES]
    report_logger.print_info(f"INFO: Onboarding traffic for {agent} (AL MAC {agent_al_mac}) before the observation window (restart requested at {restart_requested_at:.0f}, "
                             f"observation from {observation_start:.0f}); partial onboarding is expected and is informational only: {_describe(early)}")
    partial = [entry for entry in during if entry[0] in _ONBOARDING_MESSAGE_TYPES]
    report_logger.print_info(f"INFO: Onboarding traffic for {agent} during the observation window (partial onboarding is informational only, not a failure): {_describe(partial)}")

def test_backhaul_wireless_formation_negative_invalidcredentials(initialize):
    """
    EM_Backhaul_Wireless_Formation_Negative_InvalidCredentials: verify that an agent configured with an invalid backhaul
    passphrase does not form the wireless backhaul with the controller. All verification is done from the controller:
      - the Agent is not reachable from the Controller;
      - onboarding does not complete successfully (no AP Autoconfiguration WSC from the Controller to the Agent);
      - the Agent does not rejoin the active topology (final state and no topology messages from the Agent);
      - partial onboarding traffic may be present, but successful onboarding is not observed.
    The Controller station dump / station count is not used: on this platform it is not refreshed when an agent leaves.
    AP Autoconfiguration Search/Response/WSC traffic seen before the observation window, or an unanswered Search during
    it, is partial onboarding that is expected with invalid credentials; it is informational only and never a failure on
    its own. The capture is still validated (Topology Discovery from the Controller must be present).

    The invalid passphrase is written to the agent configuration over SSH while the backhaul is still up. The agent
    is then rebooted detached (AGENT_REBOOT_COMMAND; the SSH connection is lost). It boots with the invalid credentials
    from /nvram and no old association, so the only way to form the backhaul is with the invalid credentials.

    The valid credentials are NOT restored by the test; restore them manually on the agent (a backup is kept):
        cp -f /nvram/EasymeshCfg.json.tc12.bak /nvram/EasymeshCfg.json && sync
        systemctl restart onewifi em_agent ieee1905_em_agent
    """
    report_logger.print_test("Entering test_backhaul_wireless_formation_negative_invalidcredentials")
    agent = None
    capture_name = None
    capture_started = False
    invalid_applied = False
    try:
        if APPLY_SETTLE_SECONDS < 120:
            report_logger.print_error(f"FAIL: apply_settle_seconds ({APPLY_SETTLE_SECONDS}s) must be at least 120s so the agent "
                                      f"has rebooted before the observation starts")
            return
        agents = device_utils.get_enabled_extenders(initialize)
        agent = AGENT or (agents[0] if agents else None)
        if not agent or agent not in agents:
            report_logger.print_error(f"FAIL: Agent under test {agent!r} is not enabled in the infrastructure configuration; enabled extenders: {agents}")
            return

        report_logger.print_step(f"STEP 1 ({agent}): Verify the Agent is connected to the Controller and reachable before test execution")
        backhaul_iface = initialize.read_from_database(agent, "backhaul_interface")
        agent_ip = initialize.read_from_database(agent, "bridge_ip")
        capture_interface = initialize.read_from_database("controller", "bridge_iface")
        capture_filter = initialize.read_from_database("controller", "filter_1905")
        if not backhaul_iface or not agent_ip or not capture_interface:
            report_logger.print_error(f"FAIL: Missing configuration for {agent}: backhaul_interface={backhaul_iface!r}, bridge_ip={agent_ip!r}, controller bridge_iface={capture_interface!r}")
            return
        if not initialize.get_wireless_backhaul_connection_status(agent, backhaul_iface):
            report_logger.print_error(f"FAIL: Precondition not met: {agent} is not connected on {backhaul_iface}; the test must start from a formed backhaul")
            return
        agent_al_mac = initialize.get_al_mac_address(agent, "cli")
        controller_al_mac = initialize.get_al_mac_address("controller", "cli")
        report_logger.print_success(f"PASS: Agent: {agent}; backhaul interface: {backhaul_iface}; IP: {agent_ip}; AL MAC: {agent_al_mac}; Controller AL MAC: {controller_al_mac}")

        # The later "not reachable" check is only meaningful when the agent is reachable from the controller now.
        reachable, ping_output = _ping_from_device(initialize, "controller", agent_ip)
        if not reachable:
            report_logger.print_error(f"FAIL: Precondition not met: {agent} ({agent_ip}) is not reachable from the Controller before the test:\n{ping_output}")
            return
        report_logger.print_success(f"PASS: Initial state: {agent} has its backhaul up on {backhaul_iface} and is reachable from the Controller")

        report_logger.print_step(f"STEP 2 ({agent}): Start the IEEE 1905 packet capture on the Controller ({capture_interface})")
        capture_name = device_utils.create_capture_name(f"test_backhaul_wireless_formation_negative_invalidcredentials_{agent}")
        initialize.start_frame_capture("controller", capture_interface, capture_filter, capture_name)
        capture_started = True
        report_logger.print_success(f"PASS: Capture started on the Controller; capture name: {capture_name}; interface: {capture_interface}")

        report_logger.print_step(f"STEP 3 ({agent}): Configure invalid backhaul credentials on {agent} and reboot it")
        if _last_line(_ssh_exec(initialize, agent, f"grep -c {INVALID_PASSPHRASE} {AGENT_BACKHAUL_CONFIG}")) != "0":
            report_logger.print_error(f"FAIL: {AGENT_BACKHAUL_CONFIG} on {agent} already contains the invalid passphrase; restore it from {AGENT_BACKHAUL_CONFIG_BACKUP} first")
            return
        backup_check = _ssh_exec(initialize, agent, f"cp -f {AGENT_BACKHAUL_CONFIG} {AGENT_BACKHAUL_CONFIG_BACKUP} && grep -c Backhaul_KeyPassphrase {AGENT_BACKHAUL_CONFIG_BACKUP}")
        if _last_line(backup_check) != "1":
            report_logger.print_error(f"FAIL: Could not back up {AGENT_BACKHAUL_CONFIG} on {agent} (or Backhaul_KeyPassphrase is missing in it): {backup_check!r}")
            return
        report_logger.print_success(f"PASS: Original {AGENT_BACKHAUL_CONFIG} backed up to {AGENT_BACKHAUL_CONFIG_BACKUP} on {agent}")
        sed_command = ("sed -i 's/\\(\"Backhaul_KeyPassphrase\"[[:space:]]*:[[:space:]]*\"\\)[^\"]*\"/\\1"
                       + INVALID_PASSPHRASE + "\"/' " + AGENT_BACKHAUL_CONFIG + " && sync")
        _ssh_exec(initialize, agent, sed_command)
        invalid_applied = True
        applied = _ssh_exec(initialize, agent, f"grep -c {INVALID_PASSPHRASE} {AGENT_BACKHAUL_CONFIG}")
        if _last_line(applied) != "1":
            report_logger.print_error(f"FAIL: The invalid passphrase could not be written to {AGENT_BACKHAUL_CONFIG} on {agent}: {applied!r}")
            return
        restart_requested_at = _controller_epoch(initialize)
        try:
            # Detached, so the command returns before the reboot and the SSH connection is lost.
            _ssh_exec(initialize, agent, f"nohup sh -c 'sleep 2; {AGENT_REBOOT_COMMAND}' >/dev/null 2>&1 </dev/null &")
        except Exception as error:
            report_logger.print_info(f"INFO: The connection to {agent} ended while requesting the reboot (expected): {error}")
        report_logger.print_success(f"PASS: Invalid backhaul passphrase configured on {agent} and reboot requested ({AGENT_REBOOT_COMMAND}); "
                                    f"it boots with the invalid credentials only")
        report_logger.print_info(f"INFO: Waiting {APPLY_SETTLE_SECONDS}s for {agent} to reboot and attempt the backhaul before the observation")
        time.sleep(APPLY_SETTLE_SECONDS)
        # Everything captured from here on is the final state: the old link is gone and only the invalid credentials remain.
        observation_start = _controller_epoch(initialize)

        report_logger.print_step(f"STEP 4 ({agent}): Observe the Controller for {OBSERVATION_SECONDS}s: {agent} must stay unreachable from the Controller")
        samples = _collect_samples(initialize, agent, agent_ip)
        report_logger.print_success(f"PASS: Observation completed: {len(samples)} polls taken over {OBSERVATION_SECONDS}s")
        _verify_not_reachable(agent, agent_ip, samples)

        report_logger.print_step(f"STEP 5 ({agent}): Stop the packet capture on the Controller")
        local_path = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        packets = reassemble_packets(local_path)
        report_logger.print_success(f"PASS: Packet capture stopped and collected: {local_path}")

        report_logger.print_step(f"STEP 6 ({agent}): Analyze the IEEE 1905 traffic: onboarding not completed, Agent not in the active topology (partial onboarding informational)")
        before, during = _verify_onboarding_not_completed(agent, agent_al_mac, controller_al_mac, packets, observation_start)
        _verify_not_in_active_topology(agent, agent_al_mac, during, samples)
        _review_onboarding_traffic(agent, agent_al_mac, before, during, restart_requested_at, observation_start)
    finally:
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
            except Exception as error:
                report_logger.log(f"Could not collect remote packet capture: {error}")
        if invalid_applied:
            report_logger.print_info(f"INFO: The invalid backhaul passphrase is still configured on {agent}; the test does not restore it. Restore it manually on the agent: "
                                     f"cp -f {AGENT_BACKHAUL_CONFIG_BACKUP} {AGENT_BACKHAUL_CONFIG} && sync; {AGENT_RESTART_COMMAND}")
        report_logger.print_test("Exiting test_backhaul_wireless_formation_negative_invalidcredentials")
