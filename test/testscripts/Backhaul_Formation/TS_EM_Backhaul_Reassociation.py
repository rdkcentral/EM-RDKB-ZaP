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
from rdkbmeshzap.common_utils import report_logger
from rdkbmeshzap.common_utils.backhaul_utils import (
    AGENT,
    BACKHAUL_IFACE,
    CONTROLLER,
    DOWN_WAIT_SECONDS,
    LINK_CMD,
    PCAP_PATH,
    get_agent_ip,
    get_expected_ssid,
    parse_link,
    run_command,
    try_run_command,
    verify_eapol_handshake,
    wait_for_reconnect,
)

# PUBLIC_INTERFACE
def test_em_backhaul_reassociation(initialize):
    """
    Objective:
    Verify Agent backhaul reassociation after
    a controlled interface restart.

    Validation:
      - Existing association present
      - Interface restart occurs
      - Agent reassociates successfully
      - New EAPOL exchange observed
      - Controller regains connectivity
    """
    report_logger.print_test("EM_Backhaul_Reassociation")
    expected_ssid = get_expected_ssid(initialize)
    agent_ip = get_agent_ip(initialize)
    capture_pid = None
    try:
        report_logger.print_step("STEP 1: Verify current backhaul association")
        pre_output, _ = run_command(initialize, AGENT, LINK_CMD)
        pre_bssid, pre_ssid = parse_link(pre_output)
        assert pre_bssid, f"{AGENT}: Backhaul is not connected.\n{pre_output}"
        assert pre_ssid == expected_ssid, f"{AGENT}: Connected SSID {pre_ssid!r}, expected {expected_ssid!r}"
        report_logger.print_success(f"PASS: Connected to BSSID {pre_bssid}, SSID {pre_ssid}")

        report_logger.print_step("STEP 2: Start EAPOL packet capture")
        run_command(initialize, AGENT, f"rm -f {PCAP_PATH}")
        start_output, _ = run_command(
            initialize,
            AGENT,
            f"nohup tcpdump -i {BACKHAUL_IFACE} -w {PCAP_PATH} ether proto 0x888e > /dev/null 2>&1 & echo $!",
        )
        pid_match = re.search(r"^\s*(\d+)\s*$", start_output, re.MULTILINE)
        assert pid_match, f"Failed to obtain tcpdump PID:\n{start_output}"
        capture_pid = pid_match.group(1)
        time.sleep(2)
        _, rc = run_command(initialize, AGENT, f"kill -0 {capture_pid}", check=False)
        assert rc == 0, f"{AGENT}: tcpdump did not start"
        run_command(initialize, AGENT, f"ls -l {PCAP_PATH}")
        report_logger.print_success(f"PASS: Packet capture started (PID {capture_pid})")

        report_logger.print_step("STEP 3: Restart backhaul interface")
        restart_cmd = (
            f"setsid nohup sh -c 'ifconfig {BACKHAUL_IFACE} down; sleep {DOWN_WAIT_SECONDS}; ifconfig {BACKHAUL_IFACE} up' "
            f"> /dev/null 2>&1 < /dev/null &"
        )
        try_run_command(initialize, AGENT, restart_cmd)
        time.sleep(DOWN_WAIT_SECONDS)
        report_logger.print_success("PASS: Backhaul restart initiated")

        report_logger.print_step("STEP 4: Verify backhaul reconnection")
        post_bssid, post_output = wait_for_reconnect(initialize, expected_ssid)
        report_logger.print_success(f"PASS: Reconnected to BSSID {post_bssid}")

        report_logger.print_step("STEP 5: Verify EAPOL authentication sequence")
        try_run_command(initialize, AGENT, f"kill {capture_pid}")
        time.sleep(2)
        capture_pid = None
        dump_output, _ = run_command(initialize, AGENT, f"tcpdump -r {PCAP_PATH} -n")
        frame_count = verify_eapol_handshake(dump_output)
        report_logger.print_success(f"PASS: Captured {frame_count} EAPOL frame(s)")

        report_logger.print_step("STEP 6: Verify connectivity restoration")
        post_bssid_check, post_ssid = parse_link(post_output)
        assert post_bssid_check == post_bssid
        assert post_ssid == expected_ssid, f"Unexpected SSID after reassociation: {post_ssid}"
        report_logger.print_info(f"Pre-reassociation BSSID : {pre_bssid}")
        report_logger.print_info(f"Post-reassociation BSSID: {post_bssid}")

        ping_output, ping_rc = run_command(initialize, CONTROLLER, f"ping -c 5 {agent_ip}", check=False)
        assert ping_rc == 0, f"Ping command failed:\n{ping_output}"
        replies = re.findall(r"\d+\s+bytes\s+from", ping_output, re.IGNORECASE)
        assert len(replies) >= 3, (
            f"Connectivity not restored after reassociation. "
            f"Received only {len(replies)} successful ping replies.\n{ping_output}"
        )
        report_logger.print_success(
            f"PASS: Controller successfully reached Agent ({agent_ip}) with {len(replies)} successful ping replies"
        )
    finally:
        if capture_pid:
            try_run_command(initialize, AGENT, f"kill {capture_pid}")