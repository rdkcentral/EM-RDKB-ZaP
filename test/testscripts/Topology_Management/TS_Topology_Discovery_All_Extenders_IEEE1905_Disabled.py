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
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.topology_utils import *

def test_topology_discovery_all_extenders_ieee1905_disabled(initialize):
    """
    Stop IEEE 1905 agents on all enabled Extenders and verify no discovery
    packets are sent by them during the IEEE 1905 capture.
    """
    report_logger.print_test("Entering test_topology_discovery_all_extenders_ieee1905_disabled")
    capture_name = None
    capture_started = False
    extenders_to_restore = []

    try:
        # Find enabled Extenders and cache their AL MAC addresses.
        report_logger.print_step("STEP 1: Discover enabled Extenders and collect device AL MACs")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in infra.yaml")
            return
        expected_devices = device_utils.get_enabled_device_al_macs(initialize)
        report_logger.print_info(f"INFO: Found {len(extenders)} enabled Extenders: {extenders}")
        ieee1905_agent_service = get_em_services(initialize, "extender", service="ieee1905_agent")

        # Stop the IEEE 1905 agent on every enabled Extender.
        report_logger.print_step(f"STEP 2: Stop {ieee1905_agent_service} on all enabled Extenders")
        stop_failures = []
        for extender in extenders:
            extenders_to_restore.append(extender)
            try:
                initialize.stop_service(extender, ieee1905_agent_service)
                report_logger.print_info(f"INFO: Issued a request to stop {ieee1905_agent_service} on {extender}")
            except Exception as error:
                stop_failures.append(extender)
                report_logger.print_error(f"FAIL: Could not stop {ieee1905_agent_service} on {extender}: {error}")

        report_logger.print_step(f"STEP 3: Verify {ieee1905_agent_service} is stopped on all Extenders")
        time.sleep(5)
        for extender in extenders:
            try:
                initialize.verify_service_status(extender, ieee1905_agent_service, expected_status="inactive")
                report_logger.print_success(f"PASS: {extender} {ieee1905_agent_service} is stopped")
            except Exception as error:
                stop_failures.append(extender)
                report_logger.print_error(f"FAIL: Could not verify {ieee1905_agent_service} is stopped on {extender}: {error}")
        if stop_failures:
            return

        # Start an IEEE 1905 capture after all targeted Extender agents are stopped.
        capture_name = device_utils.start_capture(initialize, "controller", "topology_discovery_all_extenders_ieee1905_disabled", step=4)
        capture_started = True

        # Capture IEEE 1905 traffic throughout the configured Discovery observation period.
        report_logger.print_step(f"STEP 5: Capture IEEE 1905 traffic for {TIME_DC // 60} minutes")
        time.sleep(TIME_DC)
        report_logger.print_info("INFO: Completed the IEEE 1905 capture period")

        # Stop and download the completed Controller IEEE 1905 capture.
        report_logger.print_step("STEP 6: Stop and collect the Controller IEEE 1905 capture")
        pcap_file = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        if not pcap_file or not os.path.isfile(pcap_file):
            report_logger.print_error(f"FAIL: Controller IEEE 1905 capture PCAP was not downloaded: {pcap_file!r}")
            return

        # Reassemble the IEEE 1905 capture and extract Topology Discovery packet details.
        report_logger.print_step("STEP 7: Extract Topology Discovery packet details from the IEEE 1905 capture")
        details = extract_topology_discovery_packet_details(pcap_file)
        if not details:
            report_logger.print_error("FAIL: No Topology Discovery packets were found in the captured IEEE 1905 traffic")
            return
        report_logger.print_success(f"PASS: Extracted details for {len(details)} Topology Discovery packet(s) from the IEEE 1905 capture data")

        # Check for Discovery packets from any Extender whose IEEE 1905 agent was stopped.
        report_logger.print_step("STEP 8: Verify no Topology Discovery packets came from the Extenders")
        discovery_counts = {
            extender: sum(
                packet["al_mac"].lower() == expected_devices[extender].lower()
                for packet in details
            )
            for extender in extenders
        }
        for extender, count in discovery_counts.items():
            if count:
                report_logger.print_error(f"FAIL: {extender} sent {count} Topology Discovery packet(s) while {ieee1905_agent_service} was stopped")
        if not any(discovery_counts.values()):
            report_logger.print_success("PASS: No Topology Discovery packets were detected from any Extender while its IEEE 1905 agent was stopped")

        # Confirm the Controller continues sending Topology Discovery packets.
        report_logger.print_step("STEP 9: Verify the Controller continued sending Topology Discovery packets while all Extender IEEE 1905 agents were stopped")
        validate_topology_discovery_packets(details, {"controller": expected_devices["controller"]})

    finally:
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(
                    initialize, "controller", capture_name
                )
            except Exception as error:
                report_logger.print_error(f"FAIL: IEEE 1905 capture cleanup failed: {error}")
        if extenders_to_restore:
            report_logger.print_title(f"CLEANUP: Restore {ieee1905_agent_service} on all attempted Extenders")
        for extender in extenders_to_restore:
            try:
                initialize.start_service(extender, ieee1905_agent_service, start_only=True)
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not start {ieee1905_agent_service} on {extender}: {error}")
            time.sleep(5)
            if device_utils.verify_services(initialize, extender, (ieee1905_agent_service,), deadline=time.monotonic() + SERVICE_RECOVERY_TIMEOUT):
                report_logger.print_success(f"PASS: {ieee1905_agent_service} is active on {extender}")
            else:
                report_logger.print_error(f"FAIL: Could not confirm {ieee1905_agent_service} is active on {extender}")
        report_logger.print_test("Exiting test_topology_discovery_all_extenders_ieee1905_disabled")
