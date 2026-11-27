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
import random
import time
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.topology_utils import *

def test_topology_discovery_extender_isolation_resilience(initialize):
    """
    Stop one Extender's IEEE 1905 agent and validate discovery from other devices.
    """
    report_logger.print_test("Entering test_topology_discovery_extender_isolation_resilience")
    capture_name = None
    capture_started = False
    isolated_extender = None
    service_may_be_stopped = False

    try:
        # Identify enabled Extenders and collect all device AL MAC addresses.
        report_logger.print_step("STEP 1: Identify enabled Extenders and collect AL MAC addresses for all enabled devices")
        extenders = device_utils.get_enabled_extenders(initialize)
        expected_devices = device_utils.get_enabled_device_al_macs(initialize)
        if not extenders or "controller" not in expected_devices:
            report_logger.print_error("FAIL: Enabled Controller and Extender devices are required")
            return
        missing_al_macs = [extender for extender in extenders if extender not in expected_devices]
        if missing_al_macs:
            report_logger.print_error("FAIL: Could not collect AL MAC addresses for: " + ", ".join(missing_al_macs))
            return
        core_dump_check_timestamp = time.time()
        report_logger.print_info(f"INFO: Found {len(extenders)} enabled Extenders: {extenders}")
        ieee1905_agent_service = get_em_services(initialize, "extender", service="ieee1905_agent")

        # Select one Extender for the IEEE 1905 service isolation check.
        report_logger.print_step("STEP 2: Select an Extender for the isolation test")
        isolated_extender = random.choice(extenders)
        isolated_al_mac = expected_devices[isolated_extender].lower()
        expected_active_devices = {
            device: al_mac
            for device, al_mac in expected_devices.items()
            if device != isolated_extender
        }
        report_logger.print_info(f"INFO: Selected {isolated_extender} (AL MAC {isolated_al_mac})")

        # Stop only the IEEE 1905 agent on the selected Extender.
        report_logger.print_step(f"STEP 3: Stop {ieee1905_agent_service} on {isolated_extender}")
        service_may_be_stopped = True
        try:
            initialize.stop_service(isolated_extender, ieee1905_agent_service)
            report_logger.print_info(f"INFO: Issued a request to stop {ieee1905_agent_service} on {isolated_extender}")
        except Exception as error:
            report_logger.print_error(f"FAIL: Could not stop {ieee1905_agent_service} on {isolated_extender}: {error}")
            return

        # Confirm the selected Extender service is inactive before observing traffic.
        report_logger.print_step(f"STEP 4: Verify {ieee1905_agent_service} is stopped on {isolated_extender}")
        time.sleep(5)
        try:
            initialize.verify_service_status(isolated_extender, ieee1905_agent_service, expected_status="inactive")
        except Exception as error:
            report_logger.print_error(f"FAIL: Could not verify {ieee1905_agent_service} is stopped on {isolated_extender}: {error}")
            return
        report_logger.print_success(f"PASS: {isolated_extender} {ieee1905_agent_service} is stopped")

        # Check the isolated Extender for core dumps created after its IEEE 1905 agent was stopped.
        report_logger.print_step(f"STEP 5: Check {isolated_extender} for core dumps after its IEEE 1905 agent is stopped")
        core_dump_files = initialize.get_core_dump_status(isolated_extender, core_dump_check_timestamp)
        if core_dump_files:
            report_logger.print_error(f"FAIL: Core dump(s) found on {isolated_extender}: {', '.join(core_dump_files)}")
            return
        report_logger.print_success(f"PASS: No new core dumps found on {isolated_extender}")

        # Start the Controller capture after confirming the selected Extender service is stopped.
        capture_name = device_utils.start_capture(initialize, "controller", "topology_discovery_extender_isolation_resilience", step=6)
        capture_started = True

        # Capture IEEE 1905 traffic for the full Topology Discovery observation period.
        report_logger.print_step(f"STEP 7: Capture IEEE 1905 traffic for {TIME_DC // 60} minutes")
        time.sleep(TIME_DC)
        report_logger.print_info("INFO: The IEEE 1905 capture interval is complete")

        # Stop and collect the completed Controller IEEE 1905 capture.
        report_logger.print_step("STEP 8: Stop and collect the IEEE 1905 capture from the Controller")
        pcap_file = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        if not pcap_file or not os.path.isfile(pcap_file):
            report_logger.print_error(f"FAIL: Controller IEEE 1905 capture PCAP was not downloaded: {pcap_file!r}")
            return

        # Reassemble the IEEE 1905 capture and extract Topology Discovery packet details.
        report_logger.print_step("STEP 9: Extract Topology Discovery packet details from the IEEE 1905 capture")
        details = extract_topology_discovery_packet_details(pcap_file)
        if not details:
            report_logger.print_error("FAIL: No Topology Discovery packets were found in the captured IEEE 1905 traffic")
            return
        report_logger.print_success(f"PASS: Extracted details for {len(details)} Topology Discovery packet(s) from the IEEE 1905 capture data")

        # Confirm the isolated Extender sent no Discovery packets while its service was stopped.
        report_logger.print_step("STEP 10: Verify no Topology Discovery packets came from the isolated Extender")
        isolated_packets = [packet for packet in details if packet["al_mac"].lower() == isolated_al_mac]
        if isolated_packets:
            report_logger.print_error(f"FAIL: {isolated_extender} sent {len(isolated_packets)} Topology Discovery packet(s) while {ieee1905_agent_service} was stopped")
        else:
            report_logger.print_success(f"PASS: No Topology Discovery packets were detected from {isolated_extender} while its IEEE 1905 agent was stopped")

        # Verify the Controller and other enabled Extenders continue sending Discovery.
        report_logger.print_step("STEP 11: Verify active-device Topology Discovery packets and intervals")
        validate_topology_discovery_packets(details, expected_active_devices)

    finally:
        # Stop and collect the Controller capture if it remains active.
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
            except Exception as error:
                report_logger.print_error(f"FAIL: IEEE 1905 capture cleanup failed: {error}")
        if service_may_be_stopped:
            # Restore and verify only the IEEE 1905 service stopped by the test.
            report_logger.print_title(f"CLEANUP: Restore {ieee1905_agent_service} on {isolated_extender}")
            try:
                initialize.start_service(isolated_extender, ieee1905_agent_service, start_only=True)
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not start {ieee1905_agent_service} on {isolated_extender}: {error}")
            time.sleep(5)
            if device_utils.verify_services(initialize, isolated_extender, (ieee1905_agent_service,), deadline=time.monotonic() + SERVICE_RECOVERY_TIMEOUT):
                report_logger.print_success(f"PASS: {isolated_extender} {ieee1905_agent_service} is active")
            else:
                report_logger.print_error(f"FAIL: Could not confirm {ieee1905_agent_service} is active on {isolated_extender}")
        report_logger.print_test("Exiting test_topology_discovery_extender_isolation_resilience")
