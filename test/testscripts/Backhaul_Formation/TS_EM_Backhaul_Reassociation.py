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
from contextlib import suppress
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.backhaul_utils import (
    DOWN_WAIT_SECONDS,
    EAPOL_CAPTURE_FILTER,
    verify_eapol_handshake,
    wait_for_reconnect,
    verify_bssid_owned_by_controller
)

# PUBLIC_INTERFACE
def test_em_backhaul_reassociation(initialize):
    """
    Objective:
    Verify Agent backhaul reassociation after a controlled interface restart.

    Validation:
      - Existing association present
      - Interface restart occurs
      - Link disconnect is observed
      - Agent reassociates successfully
      - New EAPOL exchange observed
      - Controller regains connectivity
    """
    controller = "controller"
    capture_running = False
    capture_name = None
    agent = None
    report_logger.print_test("Entering test_em_backhaul_reassociation")
    try:
        agent = device_utils.get_enabled_extenders(initialize)[0]
        capture_name = device_utils.create_capture_name("backhaul_reassoc", agent)
        expected_ssid = initialize.read_from_database(controller, "mesh_backhaul_ssid")
        agent_ip = initialize.read_from_database(agent, "bridge_ip")
        backhaul_iface = initialize.read_from_database(agent, "backhaul_interface")

        report_logger.print_step("STEP 1: Verify current backhaul association")
        pre_bssid, pre_ssid = initialize.get_backhaul_link_details(agent, backhaul_iface)
        assert pre_bssid, f"{agent}: Backhaul is not connected on {backhaul_iface}."
        assert pre_ssid == expected_ssid, f"{agent}: Connected SSID {pre_ssid!r}, expected {expected_ssid!r}"
        verify_bssid_owned_by_controller(initialize, agent, pre_bssid)
        report_logger.print_success(f"PASS: Connected to Controller BSSID {pre_bssid}, SSID {pre_ssid}")

        report_logger.print_step("STEP 2: Start EAPOL packet capture")
        initialize.start_frame_capture(agent, backhaul_iface, EAPOL_CAPTURE_FILTER, capture_name)
        capture_running = True
        time.sleep(2)
        report_logger.print_success(f"PASS: Packet capture started ({capture_name})")

        report_logger.print_step("STEP 3: Restart backhaul interface")
        restart_cmd = (
            f"setsid nohup sh -c 'ifconfig {backhaul_iface} down; "
            f"sleep {DOWN_WAIT_SECONDS:g}; ifconfig {backhaul_iface} up' "
            f"> /dev/null 2>&1 < /dev/null &"
        )
        try:
            initialize.execute_command(agent, restart_cmd)
        except Exception as exc:
            report_logger.print_info(f"Expected interruption during restart: {exc}")

        report_logger.print_step("STEP 3A: Verify disconnect occurred")
        disconnect_seen = False
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                connected = initialize.get_wireless_backhaul_connection_status(agent, backhaul_iface)
            except Exception as exc:
                if not initialize.is_device_alive(agent):
                    report_logger.print_info(f"{agent}: Device unreachable during restart: {exc}")
                    disconnect_seen = True
                    break
                report_logger.print_info(f"{agent}: Unable to read link status, retrying: {exc}")
                time.sleep(2)
                continue
            if not connected:
                disconnect_seen = True
                break
            time.sleep(2)
        assert disconnect_seen, f"{agent}: Backhaul interface never entered disconnected state"
        report_logger.print_success("PASS: Disconnect observed")

        report_logger.print_step("STEP 4: Verify backhaul reconnection")
        reconnect = wait_for_reconnect(initialize, agent, backhaul_iface, expected_ssid)
        assert reconnect, f"{agent}: Backhaul did not reconnect to {expected_ssid!r}"
        post_bssid, post_ssid = reconnect
        report_logger.print_success(f"PASS: Reconnected to BSSID {post_bssid}, SSID {post_ssid}")

        report_logger.print_step("STEP 5: Verify EAPOL authentication sequence")
        local_pcap = device_utils.stop_and_collect_capture(initialize, agent, capture_name)
        capture_running = False
        frame_count = verify_eapol_handshake(local_pcap)
        report_logger.print_success(f"PASS: Captured {frame_count} EAPOL-Key frame(s)")

        report_logger.print_step("STEP 6: Verify connectivity restoration")
        report_logger.print_info(f"Pre-reassociation : BSSID {pre_bssid}, SSID {pre_ssid}")
        report_logger.print_info(f"Post-reassociation: BSSID {post_bssid}, SSID {post_ssid}")
        assert post_ssid == pre_ssid == expected_ssid, f"{agent}: Backhaul SSID changed after reassociation (pre {pre_ssid!r}, post {post_ssid!r}, expected {expected_ssid!r})"
        verify_bssid_owned_by_controller(initialize, agent, post_bssid)
        if post_bssid != pre_bssid:
            report_logger.print_info(f"INFO: {agent} moved between Controller BSSs ({pre_bssid} -> {post_bssid})")
        report_logger.print_success(f"PASS: {agent} is associated with a Controller BSS (SSID {post_ssid})")
        replies = []
        ping_output = ""
        for attempt in range(1, 4):
            ping_output, ping_rc = initialize.execute_command(controller, f"ping -c 3 -W 2 {agent_ip}", return_rc=True)
            replies = re.findall(r"\d+\s+bytes\s+from", ping_output, re.IGNORECASE)
            if ping_rc == 0 and len(replies) == 3:
                break
            report_logger.print_info(f"Ping attempt {attempt}/3: {len(replies)} of 3 replies, retrying")
            time.sleep(5)
        assert len(replies) == 3, f"Connectivity not restored after reassociation. Received {len(replies)} of 3 ping replies in the last attempt.\n{ping_output}"
        report_logger.print_success(f"PASS: Controller reached Agent ({agent_ip}) with {len(replies)} of 3 ping replies")
    except Exception as exc:
        report_logger.print_error(f"FAIL: test_em_backhaul_reassociation: {exc}")
        raise
    finally:
        if capture_running:
            with suppress(Exception):
                device_utils.stop_and_collect_capture(initialize, agent, capture_name)
        report_logger.print_test("Exiting test_em_backhaul_reassociation")