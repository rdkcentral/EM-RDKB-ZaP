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
import time
from packet_analyzer.packet_dissector import check_message_presence, reassemble_packets
from rdkbmeshzap.common_utils import report_logger, device_utils
from rdkbmeshzap.common_utils.topology_utils import *

def test_topology_management_discovery_broadcast(initialize):
    """
    Verify that each enabled testbed device sends Topology Discovery packets.
    """
    report_logger.print_test("Entering test_topology_management_discovery_broadcast")
    capture_name = None
    capture_started = False
    
    try:
        # Use enabled testbed device AL MAC addresses to validate captured packets.
        report_logger.print_step("STEP 1: Collect enabled testbed device AL MAC addresses for packet validation")
        expected_devices = device_utils.get_enabled_device_al_macs(initialize)
        if not expected_devices:
            report_logger.print_error("FAIL: No enabled controller/extender devices found in the testbed")
            return
        num_devices = len(expected_devices)
        report_logger.print_info("INFO: Enabled testbed device AL MAC addresses collected for packet validation")

        # Capture IEEE 1905 traffic on the controller for discovery analysis.
        capture_name = device_utils.start_capture(initialize, "controller", "topology_management_discovery_broadcast", step="2")
        capture_started = True

        # Keep the capture running for the full observation period.
        report_logger.print_step(f"STEP 3: Capture IEEE 1905 traffic for {TIME_DC // 60} minutes")
        time.sleep(TIME_DC)
        report_logger.print_info("INFO: IEEE 1905 packet capture observation period completed")
        
        # Download the completed controller capture for local packet analysis.
        report_logger.print_step("STEP 4: Stop and collect the IEEE 1905 capture from the controller")
        pcap_file = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        if not pcap_file or not os.path.isfile(pcap_file):
            report_logger.print_error(f"FAIL: Captured PCAP was not downloaded: {pcap_file!r}")
            return
        
        # Reassemble packet fragments from the downloaded capture.
        report_logger.print_step("STEP 5: Reassemble and analyze the captured IEEE 1905 packets")
        reassembled_packets = reassemble_packets(pcap_file)
        if not reassembled_packets:
            report_logger.print_error("FAIL: No IEEE 1905 packets were found in the controller capture")
            return        
        report_logger.print_info(f"INFO: Reassembled {len(reassembled_packets)} IEEE 1905 packets from the controller capture")
        
        # Find Topology Discovery packets and extract details for device-level validation.
        report_logger.print_step("STEP 6: Find Topology Discovery packets and extract their details")
        discovery_payloads = check_message_presence(reassembled_packets, TOPOLOGY_DISCOVERY_TYPE)        
        if not discovery_payloads:
            report_logger.print_error("FAIL: No Topology Discovery packets were found in the capture")
            return
        discovery_details = extract_discovery_packet_details(reassembled_packets)
        if not discovery_details:
            report_logger.print_error("FAIL: Could not extract details from the captured Topology Discovery packets")
            return
        if len(discovery_details) != len(discovery_payloads):
            report_logger.print_error(f"FAIL: Topology Discovery packet count mismatch: found {len(discovery_payloads)} packets but extracted details for {len(discovery_details)}")
            return
        report_logger.print_success(f"PASS: Found and extracted details for {len(discovery_details)} Topology Discovery packets")
        
        # Verify that each enabled testbed device sent a Topology Discovery packet.
        report_logger.print_step(f"STEP 7: Verify all {num_devices} enabled devices sent Topology Discovery packets")
        devices_found = validate_all_devices_send_discovery(discovery_details, expected_devices)
        # Ignore packets from devices outside the enabled testbed list.
        expected_macs = {mac.lower() for mac in expected_devices.values()}
        testbed_discovery_details = [
            packet for packet in discovery_details
            if packet["al_mac"].lower() in expected_macs
        ]
        if not testbed_discovery_details:
            return
        if devices_found:
            report_logger.print_success(f"PASS: All {num_devices} enabled devices sent Topology Discovery packets")

        # Check each enabled device's packet count and discovery interval.
        report_logger.print_step("STEP 8: Verify Topology Discovery packet intervals for each enabled device")
        interval_results = analyze_discovery_intervals(testbed_discovery_details)
        min_interval = DISCOVERY_INTERVAL - DISCOVERY_INTERVAL_TOLERANCE
        max_interval = DISCOVERY_INTERVAL + DISCOVERY_INTERVAL_TOLERANCE
        for device, al_mac in expected_devices.items():
            result = interval_results.get(al_mac.lower())
            if result is None:
                continue
            if result["count"] < 2:
                report_logger.print_error(f"FAIL: {device} (AL MAC {al_mac}) sent fewer than two Topology Discovery packets; interval could not be verified")
                continue
            if result["count"] > MAX_DISCOVERY_PACKETS:
                report_logger.print_error(f"FAIL: {device} (AL MAC {al_mac}) sent {result['count']} Topology Discovery packets; the maximum is {MAX_DISCOVERY_PACKETS}")
                continue
            intervals = result["intervals"]
            if not result["valid"]:
                invalid = [
                    interval for interval in intervals
                    if not min_interval <= interval <= max_interval
                ]
                report_logger.print_error(
                    f"FAIL: {device} (AL MAC {al_mac}) sent packets at intervals outside "
                    f"the allowed range of {min_interval}-{max_interval}s: "
                    f"{', '.join(f'{interval:.3f}s' for interval in invalid)}"
                )
                continue
            report_logger.print_success(f"PASS: {device} has the expected Topology Discovery interval ({DISCOVERY_INTERVAL}±{DISCOVERY_INTERVAL_TOLERANCE}s)")
        
    finally:
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
            except Exception as cleanup_error:
                report_logger.print_error(f"FAIL: Capture cleanup failed: {cleanup_error}")
        report_logger.print_test("Exiting test_topology_management_discovery_broadcast")
