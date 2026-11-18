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

import time
from packet_analyzer.packet_dissector import reassemble_packets
from rdkbmeshzap.common_utils import device_utils, report_logger
from backhaul_formation_utils import *

def test_backhaul_wireless_formation_negative_invalidcredentials(initialize):
    """
    EM_Backhaul_Wireless_Formation_Negative_InvalidCredentials: verify that an agent configured with an invalid backhaul
    passphrase does not form the wireless backhaul with the controller. All verification is done from the controller:
      - the Agent is not reachable from the Controller;
      - onboarding does not complete successfully (no AP Autoconfiguration WSC from the Controller to the Agent after the old session went down);
      - the Agent does not rejoin the active topology (final state and no topology messages from the Agent);
      - partial onboarding traffic may be present, but successful onboarding is not observed.
    The Controller station dump / station count is not used: on this platform it is not refreshed when an agent leaves.
    AP Autoconfiguration Search/Response/WSC traffic seen before the observation window, or an unanswered Search during
    it, is partial onboarding that is expected with invalid credentials; it is informational only and never a failure on
    its own. The capture is still validated (Topology Discovery from the Controller must be present).

    The invalid passphrase is written to the agent configuration over SSH while the backhaul is still up. The agent
    is then rebooted with the framework API initialize.reboot_device(agent, method="cli"), which sends a non-blocking
    reboot (the SSH connection is lost). It boots with the invalid credentials
    from /nvram and no old association, so the only way to form the backhaul is with the invalid credentials.

    The valid credentials are NOT restored by the test; restore them manually on the agent (a backup is kept):
        cp -f /nvram/EasymeshCfg.json.tc10.bak /nvram/EasymeshCfg.json && sync
        reboot, then confirm the agent is reachable from the controller

    Boot/association evidence: SSH to the agent is lost with the backhaul, so the test collects the new, timestamped
    controller OneWifi HAL log entries (CONTROLLER_WIFI_LOG_GLOB, rotated files included) written after the observation
    start. It requires "received auth frame" entries for the agent backhaul STA MAC (a join attempt) and Agent-specific
    WPA rejection / unauthorized-state entries for it (WPA_REJECTION_PATTERN); otherwise the missing traffic is not accepted
    as a pass. Entries are selected by timestamp, not by comparing total counts, so a log rotation cannot hide them.
    """
    report_logger.print_test("Entering test_backhaul_wireless_formation_negative_invalidcredentials")
    agent = None
    capture_name = None
    capture_started = False
    invalid_applied = False
    try:
        if APPLY_SETTLE_SECONDS < 120:
            report_logger.print_error(f"FAIL: apply_settle_seconds ({APPLY_SETTLE_SECONDS}s) must be at least 120s so the agent has rebooted before the observation starts")
            return
        agents = device_utils.get_enabled_extenders(initialize)
        agent = AGENT or (agents[0] if agents else None)
        if not agent or agent not in agents:
            report_logger.print_error(f"FAIL: Agent under test {agent!r} is not enabled in the infrastructure configuration; enabled extenders: {agents}")
            return

        report_logger.print_step(f"STEP 1 ({agent}): Verify the Agent is connected to the Controller and reachable before test execution")
        backhaul_iface = initialize.read_from_database(agent, "backhaul_interface")
        agent_ip = initialize.read_from_database(agent, "bridge_ip")
        capture_interface = device_utils.get_backhaul_capture_interface(initialize, "controller")
        capture_filter = initialize.read_from_database("controller", "filter_1905")
        if not backhaul_iface or not agent_ip or not capture_interface:
            report_logger.print_error(f"FAIL: Missing configuration for {agent}: backhaul_interface={backhaul_iface!r}, bridge_ip={agent_ip!r}, controller backhaul_capture_iface={capture_interface!r}")
            return
        if not initialize.get_wireless_backhaul_connection_status(agent, backhaul_iface):
            report_logger.print_error(f"FAIL: Precondition not met: {agent} is not connected on {backhaul_iface}; the test must start from a formed backhaul")
            return
        backhaul_mac = get_agent_backhaul_mac(initialize, agent, backhaul_iface)
        if not backhaul_mac:
            report_logger.print_error(f"FAIL: The backhaul MAC of {agent} ({backhaul_iface}) could not be read; boot and association attempts could not be verified")
            return
        agent_al_mac = initialize.get_al_mac_address(agent, "cli")
        controller_al_mac = initialize.get_al_mac_address("controller", "cli")
        report_logger.print_success(f"PASS: Agent: {agent}; backhaul interface: {backhaul_iface}; IP: {agent_ip}; AL MAC: {agent_al_mac}; Controller AL MAC: {controller_al_mac}")

        # The later "not reachable" check is only meaningful when the agent is reachable from the controller now.
        try:
            loss = ping_from_controller(initialize, agent_ip, OBSERVATION_PING_COUNT)
            reachable, ping_output = loss < 100.0, f"packet loss: {loss}%"
        except Exception as error:
            report_logger.print_error(f"FAIL: Precondition not met: the ping from the Controller to {agent} ({agent_ip}) could not be evaluated: {error}")
            return
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
        if last_line(ssh_exec(initialize, agent, f"grep -c {INVALID_PASSPHRASE} {AGENT_BACKHAUL_CONFIG}")) != "0":
            report_logger.print_error(f"FAIL: {AGENT_BACKHAUL_CONFIG} on {agent} already contains the invalid passphrase; restore it from {AGENT_BACKHAUL_CONFIG_BACKUP} first")
            return
        backup_check = ssh_exec(initialize, agent, f"cp -f {AGENT_BACKHAUL_CONFIG} {AGENT_BACKHAUL_CONFIG_BACKUP} && sync && grep -c Backhaul_KeyPassphrase {AGENT_BACKHAUL_CONFIG_BACKUP}")
        if last_line(backup_check) != "1":
            report_logger.print_error(f"FAIL: Could not back up {AGENT_BACKHAUL_CONFIG} on {agent} (or Backhaul_KeyPassphrase is missing in it): {backup_check!r}")
            return
        report_logger.print_success(f"PASS: Original {AGENT_BACKHAUL_CONFIG} backed up to {AGENT_BACKHAUL_CONFIG_BACKUP} on {agent}")
        # The old value is matched as a JSON string: any char except " and \, or a backslash escape (\" or \\), so an escaped quote cannot end the match early and break the JSON.
        sed_command = r"""sed -i 's/\("Backhaul_KeyPassphrase"[[:space:]]*:[[:space:]]*"\)\([^"\\]\|\\.\)*"/\1""" + INVALID_PASSPHRASE + '''"/' ''' + AGENT_BACKHAUL_CONFIG + " && sync"
        ssh_exec(initialize, agent, sed_command)
        invalid_applied = True
        applied = ssh_exec(initialize, agent, f"grep -c {INVALID_PASSPHRASE} {AGENT_BACKHAUL_CONFIG}")
        if last_line(applied) != "1":
            report_logger.print_error(f"FAIL: The invalid passphrase could not be written to {AGENT_BACKHAUL_CONFIG} on {agent}: {applied!r}")
            return
        reboot_sent = time.monotonic()
        try:
            # Existing framework API (as used by the recovery scripts): non-blocking reboot; the configuration was synced above.
            initialize.reboot_device(agent, method="cli")
        except Exception as error:
            report_logger.print_error(f"FAIL: The reboot command could not be sent to {agent}: {error}")
            return
        report_logger.print_success(f"PASS: Invalid backhaul passphrase configured on {agent} and reboot requested (initialize.reboot_device); it boots with the invalid credentials only")
        report_logger.print_info(f"INFO: Waiting {APPLY_SETTLE_SECONDS}s for {agent} to reboot and attempt the backhaul before the observation")
        # Confirmed reboot/link-down boundary: the old session (valid credentials) can still deliver a WSC until the link drops.
        link_down_at = wait_for_agent_link_down(initialize, agent_ip)
        if link_down_at is None:
            report_logger.print_error(f"FAIL: {agent} did not become unreachable within {LINK_DOWN_TIMEOUT_SECONDS}s after the reboot request; the end of the old backhaul session cannot be confirmed")
            return
        time.sleep(max(0, APPLY_SETTLE_SECONDS - (time.monotonic() - reboot_sent)))
        # Everything captured from here on is the final state: the old link is gone and only the invalid credentials remain.
        observation_start = get_controller_epoch(initialize)

        report_logger.print_step(f"STEP 4 ({agent}): Observe the Controller for {OBSERVATION_SECONDS}s: {agent} must stay unreachable from the Controller")
        samples = collect_ping_samples(initialize, agent, agent_ip)
        # End of the observation window (controller clock); later capture traffic is not part of the window.
        observation_end = get_controller_epoch(initialize)
        report_logger.print_success(f"PASS: Observation completed: {len(samples)} polls taken over {OBSERVATION_SECONDS}s")
        verify_agent_not_reachable(agent, agent_ip, samples)
        verify_agent_boot_attempts(initialize, agent, backhaul_mac, observation_start, observation_end, link_down_at)

        report_logger.print_step(f"STEP 5 ({agent}): Stop the packet capture on the Controller")
        local_path = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        packets = reassemble_packets(local_path)
        report_logger.print_success(f"PASS: Packet capture stopped and collected: {local_path}")

        report_logger.print_step(f"STEP 6 ({agent}): Analyze the IEEE 1905 traffic: onboarding not completed, Agent not in the active topology (partial onboarding informational)")
        before, during = verify_onboarding_not_completed(agent, agent_al_mac, controller_al_mac, packets, observation_start, observation_end, link_down_at)
        verify_not_in_active_topology(agent, agent_al_mac, during, samples, initialize)
        review_onboarding_traffic(agent, agent_al_mac, before, during, link_down_at, observation_start)
    finally:
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
            except Exception as error:
                report_logger.log(f"Could not collect remote packet capture: {error}")
        if invalid_applied:
            report_logger.print_info(f"INFO: The invalid backhaul passphrase is still configured on {agent}; the test does not restore it. Restore it manually on the agent: cp -f {AGENT_BACKHAUL_CONFIG_BACKUP} {AGENT_BACKHAUL_CONFIG} && sync; {AGENT_RESTART_COMMAND}")
        report_logger.print_test("Exiting test_backhaul_wireless_formation_negative_invalidcredentials")
