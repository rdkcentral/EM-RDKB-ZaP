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

def test_topology_discovery_controller_isolation_resilience(initialize):
    """
    Stop the Controller's IEEE 1905 control service and validate discovery from Extenders.
    """
    report_logger.print_test("Entering test_topology_discovery_controller_isolation_resilience")
    captures = {}
    controller_service_stop_attempted = False

    try:
        # Identify enabled Extenders and collect their AL MAC addresses.
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
        expected_extender_devices = {
            extender: expected_devices[extender] for extender in extenders
        }
        report_logger.print_info(f"INFO: Found {len(extenders)} enabled Extenders: {extenders}")
        controller_ieee1905_service = get_em_services(initialize, "controller", service="ieee1905_controller")

        # Stop the Controller's IEEE 1905 service.
        report_logger.print_step(f"STEP 2: Stop {controller_ieee1905_service} on the Controller")
        controller_service_stop_attempted = True
        try:
            initialize.stop_service("controller", controller_ieee1905_service)
            report_logger.print_info(f"INFO: Issued a request to stop {controller_ieee1905_service} on the Controller")
        except Exception as error:
            report_logger.print_error(f"FAIL: Could not stop {controller_ieee1905_service} on the Controller: {error}")
            return

        # Confirm the Controller service is inactive before starting Extender captures.
        report_logger.print_step(f"STEP 3: Verify {controller_ieee1905_service} is stopped on the Controller")
        time.sleep(5)
        try:
            initialize.verify_service_status("controller", controller_ieee1905_service, expected_status="inactive")
        except Exception as error:
            report_logger.print_error(f"FAIL: Could not verify {controller_ieee1905_service} is stopped on the Controller: {error}")
            return
        report_logger.print_success(f"PASS: Controller {controller_ieee1905_service} is stopped")

        # Start IEEE 1905 captures on all enabled Extenders after confirming the Controller service is stopped.
        report_logger.print_step("STEP 4: Start IEEE 1905 captures on all Extenders")
        for index, extender in enumerate(extenders, start=1):
            captures[extender] = device_utils.start_capture(initialize, extender, "topology_discovery_controller_isolation_resilience", step=f"4.{index}", include_device=True)

        # Capture IEEE 1905 traffic throughout the configured Discovery interval.
        report_logger.print_step(f"STEP 5: Capture IEEE 1905 traffic for {TIME_DC // 60} minutes")
        time.sleep(TIME_DC)
        report_logger.print_info("INFO: The IEEE 1905 capture interval is complete")

        # Collect each Extender's IEEE 1905 capture for packet validation.
        report_logger.print_step("STEP 6: Stop and collect Extender IEEE 1905 captures")
        details_by_extender = {}
        all_details = []
        failed_captures = []
        for extender, capture_name in list(captures.items()):
            try:
                pcap_file = device_utils.stop_and_collect_capture(initialize, extender, capture_name)
                del captures[extender]
                if not pcap_file or not os.path.isfile(pcap_file):
                    failed_captures.append(extender)
                    report_logger.print_error(f"FAIL: Extender IEEE 1905 capture PCAP was not downloaded: {pcap_file!r}")
                    continue
                extender_details = extract_topology_discovery_packet_details(pcap_file)
                details_by_extender[extender] = extender_details
                all_details.extend(extender_details)
            except Exception as error:
                failed_captures.append(extender)
                report_logger.print_error(f"FAIL: Could not collect or analyze the IEEE 1905 capture from {extender}: {error}")
        if failed_captures:
            return
        if not all_details:
            report_logger.print_error("FAIL: No Topology Discovery packets were found in the captured IEEE 1905 traffic")
            return
        report_logger.print_success(f"PASS: Extracted details for {len(all_details)} Topology Discovery packet(s) from the IEEE 1905 capture data")

        # Validate each Extender only against packets from its own capture.
        report_logger.print_step("STEP 7: Verify all Extenders sent Topology Discovery packets and meet the interval limit")
        for extender, extender_details in details_by_extender.items():
            validate_topology_discovery_packets(extender_details, {extender: expected_extender_devices[extender]})

        # Check all Extender captures for Controller packets while its IEEE 1905 service was stopped.
        report_logger.print_step("STEP 8: Verify the Controller sent no Topology Discovery packets")
        controller_al_mac = expected_devices["controller"].lower()
        controller_packet_count = sum(packet["al_mac"].lower() == controller_al_mac for packet in all_details)
        if controller_packet_count:
            report_logger.print_error(f"FAIL: Controller sent {controller_packet_count} Topology Discovery packet(s) while {controller_ieee1905_service} was stopped")
        else:
            report_logger.print_success(f"PASS: No Topology Discovery packets were detected from the Controller while {controller_ieee1905_service} was stopped")

    finally:
        # Stop and collect any Extender capture left running after an early exit.
        for extender, capture_name in list(captures.items()):
            try:
                device_utils.stop_and_collect_capture(initialize, extender, capture_name)
            except Exception as error:
                report_logger.print_error(f"FAIL: {extender} IEEE 1905 capture cleanup failed: {error}")
        if controller_service_stop_attempted:
            # Restore and verify only the Controller IEEE 1905 service stopped by the test.
            report_logger.print_title(f"CLEANUP: Restore {controller_ieee1905_service} on the Controller")
            try:
                initialize.start_service("controller", controller_ieee1905_service, start_only=True)
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not start {controller_ieee1905_service} on the Controller: {error}")
            time.sleep(5)
            if device_utils.verify_services(initialize, "controller", (controller_ieee1905_service,), deadline=time.monotonic() + SERVICE_RECOVERY_TIMEOUT):
                report_logger.print_success(f"PASS: Controller {controller_ieee1905_service} is active")
            else:
                report_logger.print_error(f"FAIL: Could not confirm Controller {controller_ieee1905_service} is active")
        report_logger.print_test("Exiting test_topology_discovery_controller_isolation_resilience")
