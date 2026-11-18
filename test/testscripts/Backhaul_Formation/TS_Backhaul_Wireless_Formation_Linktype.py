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
from packet_analyzer.ieee1905_utils import MSG_TYPE_TOPOLOGY_DISCOVERY, MSG_TYPE_TOPOLOGY_NOTIFICATION, MSG_TYPE_AP_AUTOCONFIG_SEARCH
from packet_analyzer.packet_dissector import reassemble_packets, check_message_presence
from rdkbmeshzap.common_utils import device_utils, recovery_utils, report_logger
from zaero.utils import zi_logger
from backhaul_formation_utils import *

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
            report_logger.print_info(f"INFO: Verifying wireless backhaul formation for {agent}")
            capture_name = None
            capture_started = False
            try:
                report_logger.print_step(f"STEP 1 ({agent}): Start the IEEE 1905 packet capture on the controller")
                backhaul_iface = initialize.read_from_database(agent, "backhaul_interface")
                agent_ip = initialize.read_from_database(agent, "bridge_ip")
                expected_ssid = initialize.read_from_database("controller", "mesh_backhaul_ssid")
                capture_interface = device_utils.get_backhaul_capture_interface(initialize, "controller")
                if not backhaul_iface or not agent_ip or not expected_ssid or not capture_interface:
                    report_logger.print_error(f"FAIL: Missing configuration for {agent}: backhaul_interface={backhaul_iface!r}, bridge_ip={agent_ip!r}, mesh_backhaul_ssid={expected_ssid!r}, controller backhaul_capture_iface={capture_interface!r}")
                    continue
                agent_al_mac = initialize.get_al_mac_address(agent, "cli")
                if not agent_al_mac or not MAC_PATTERN.match(str(agent_al_mac).strip()):
                    report_logger.print_error(f"FAIL: Could not read a valid AL MAC address for {agent}: {agent_al_mac!r}; the IEEE 1905 messages cannot be verified")
                    continue
                agent_al_mac = str(agent_al_mac).strip().lower()
                controller_al_mac = initialize.get_al_mac_address("controller", "cli")
                if not controller_al_mac or not MAC_PATTERN.match(str(controller_al_mac).strip()):
                    report_logger.print_error(f"FAIL: Could not read a valid controller AL MAC address: {controller_al_mac!r}; the backhaul link type cannot be verified")
                    continue
                controller_al_mac = str(controller_al_mac).strip().lower()
                report_logger.print_info(f"INFO: Agent: {agent}; backhaul interface: {backhaul_iface}; IP: {agent_ip}; AL MAC: {agent_al_mac}; expected backhaul SSID: {expected_ssid}")
                capture_name = device_utils.create_capture_name(f"test_backhaul_wireless_formation_linktype_{agent}")
                capture_filter = initialize.read_from_database("controller", "filter_1905")
                initialize.start_frame_capture("controller", capture_interface, capture_filter, capture_name)
                capture_started = True
                report_logger.print_success(f"PASS: Packet capture started on the controller; capture name: {capture_name}; interface: {capture_interface}")

                report_logger.print_step(f"STEP 2 ({agent}): Reboot {agent} to trigger wireless backhaul onboarding and wait for it to come back online")
                reboot_start = time.monotonic()
                try:
                    initialize.reboot_device(agent, method="cli")
                except Exception as error:
                    report_logger.print_error(f"FAIL: The reboot command could not be sent to {agent}: {error}")
                    continue
                report_logger.print_info(f"INFO: {agent} reboot command executed; waiting for it to recover")
                # Confirm the old session is gone before recovery, so recovery cannot succeed against the old boot.
                link_down_at = wait_for_agent_link_down(initialize, agent_ip)
                if link_down_at is None:
                    report_logger.print_error(f"FAIL: {agent} ({agent_ip}) did not become unreachable within {LINK_DOWN_TIMEOUT_SECONDS}s after the reboot request; the reboot cannot be verified")
                    continue
                report_logger.print_info(f"INFO: {agent} link down confirmed at controller epoch {link_down_at:.3f}; waiting for it to recover")
                # Existing recovery API: reconnects the agent and verifies its services within the agent recovery KPI.
                recovery_times = {}
                recovery_result = recovery_utils.recover_device(initialize, agent, reboot_start, recovery_times, "agent")
                if recovery_result is False or isinstance(recovery_result, BaseException) or recovery_result is None:
                    report_logger.print_error(f"FAIL: {agent} did not recover within the agent recovery KPI after the reboot")
                    continue
                # Drop the connection errors logged while the device was still booting; recovery succeeded.
                zi_logger.clear_error_logs()
                if not wait_until(lambda: initialize.get_wireless_backhaul_connection_status(agent, backhaul_iface)):
                    report_logger.print_error(f"FAIL: {agent} did not re-establish the wireless backhaul on {backhaul_iface} within {ONBOARDING_TIMEOUT_SECONDS}s")
                    continue
                report_logger.print_success(f"PASS: {agent} rebooted, recovered in {recovery_result:.1f}s and started the wireless backhaul re-establishment")

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
                fdb_ports, fdb_output = wait_for_fdb_ports(initialize, agent, controller_al_mac, ONBOARDING_SETTLE_SECONDS * 2)
                report_logger.print_info(f"INFO: Bridge FDB entries for the controller AL MAC:\n{fdb_output}")
                if not fdb_ports:
                    report_logger.print_error(f"FAIL: Controller AL MAC {controller_al_mac} is not learned in the {agent} bridge; the backhaul link type cannot be determined")
                else:
                    wifi_ports = [port for port in fdb_ports if port == backhaul_iface or port.startswith(f"{backhaul_iface}.")]
                    other_ports = [port for port in fdb_ports if port not in wifi_ports]
                    if wifi_ports and not other_ports:
                        report_logger.print_success(f"PASS: Backhaul link type is Wi-Fi: controller AL MAC is learned only on the wireless backhaul interface {backhaul_iface} (ports: {fdb_ports})")
                    elif wifi_ports:
                        report_logger.print_error(f"FAIL: Controller AL MAC is learned on the wireless backhaul interface {backhaul_iface} and also on other port(s) {other_ports}; the backhaul link type is not exclusively Wi-Fi")
                    else:
                        report_logger.print_error(f"FAIL: Backhaul link type is not Wi-Fi: controller AL MAC is learned on {fdb_ports}, not on the wireless backhaul interface {backhaul_iface}")

                report_logger.print_step(f"STEP 5 ({agent}): Ping {agent} ({agent_ip}) from the controller (ping -c {PING_COUNT})")
                try:
                    loss = ping_from_controller(initialize, agent_ip, PING_COUNT)
                    reachable, ping_output = loss < 100.0, f"packet loss: {loss}%"
                except Exception as error:
                    reachable, ping_output = False, f"ping could not be executed: {error}"
                report_logger.print_info(f"INFO: Ping result:\n{ping_output}")
                if reachable:
                    report_logger.print_success(f"PASS: {agent} ({agent_ip}) responds to ping from the controller")
                else:
                    report_logger.print_error(f"FAIL: {agent} ({agent_ip}) did not respond to ping from the controller")

                report_logger.print_step(f"STEP 6 ({agent}): Stop the capture after the IEEE 1905 onboarding exchange and verify Topology Discovery, AP Autoconfiguration Search and a completed Topology Query/Response exchange for {agent} AL MAC {agent_al_mac} (Topology Notification informational)")
                report_logger.print_info(f"INFO: Waiting {ONBOARDING_SETTLE_SECONDS}s for the IEEE 1905 onboarding messages")
                time.sleep(ONBOARDING_SETTLE_SECONDS)
                local_path = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
                capture_started = False
                packets = reassemble_packets(local_path)
                packets = [pkt for pkt in packets if float(pkt.time) >= link_down_at]
                report_logger.print_success(f"PASS: Packet capture stopped and collected: {local_path}")

                _, agent_messages = get_agent_1905_messages(packets, agent_al_mac, float("-inf"))
                for message_type, message_name in ((MSG_TYPE_TOPOLOGY_DISCOVERY, "Topology Discovery"), (MSG_TYPE_AP_AUTOCONFIG_SEARCH, "AP Autoconfiguration Search")):
                    present = [entry for entry in agent_messages if entry[0] == message_type]
                    if present:
                        report_logger.print_success(f"PASS: {message_name} observed for {agent} (AL MAC {agent_al_mac}); count: {len(present)}")
                    else:
                        report_logger.print_error(f"FAIL: {message_name} was not observed for {agent} (AL MAC {agent_al_mac}) in the post-reboot capture")

                verify_topology_exchange(agent, agent_al_mac, controller_al_mac, packets)
                verify_onboarding_message_order(agent, agent_al_mac, packets, link_down_at)

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
    finally:
        report_logger.print_test("Exiting test_backhaul_wireless_formation_linktype")
