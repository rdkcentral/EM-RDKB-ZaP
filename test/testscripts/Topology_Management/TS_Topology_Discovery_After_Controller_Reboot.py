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
from concurrent.futures import ThreadPoolExecutor, as_completed
from rdkbmeshzap.common_utils import device_utils, recovery_utils, report_logger
from rdkbmeshzap.common_utils.topology_utils import *

def test_topology_discovery_after_controller_reboot(initialize):
    """
    Reboot the Controller and validate Topology Discovery after recovery.
    """
    report_logger.print_test("Entering test_topology_discovery_after_controller_reboot")
    capture_name = None
    capture_started = False
    capture_started_at = None

    try:
        report_logger.print_step("STEP 1: Discover all enabled Extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in infra.yaml")
            return
        report_logger.print_info(f"INFO: Enabled Extenders for this recovery test: {extenders}")

        # Record enabled-device AL MACs for post-reboot packet validation.
        report_logger.print_step("STEP 2: Collect enabled device AL MAC addresses")
        expected_devices = device_utils.get_enabled_device_al_macs(initialize)
        if "controller" not in expected_devices:
            report_logger.print_error("FAIL: Could not collect the Controller AL MAC address")
            return
        missing_al_macs = [extender for extender in extenders if extender not in expected_devices]
        if missing_al_macs:
            report_logger.print_error("FAIL: Could not collect AL MAC addresses for: " + ", ".join(missing_al_macs))
            return
        report_logger.print_success("PASS: Collected AL MAC addresses for all enabled devices")

        # Share the reboot timestamp across Controller and Extender recovery checks.
        report_logger.print_step("STEP 3: Reboot the Controller")
        reboot_started_at = time.monotonic()
        try:
            initialize.reboot_device("controller", method="cli")
        except Exception as error:
            report_logger.print_error(f"FAIL: Controller reboot command failed: {error}")
            return
        report_logger.print_info("INFO: Controller reboot command executed")
        # Allow the Controller to reboot before reconnecting.
        time.sleep(30)

        # Verify the Controller is reachable and its services recover within the KPI.
        report_logger.print_step("STEP 4: Recover the Controller after reboot")
        recovery_results = {}
        try:
            recovery_utils.recover_device(initialize, "controller", reboot_started_at, recovery_results)
        except Exception as error:
            report_logger.print_error(f"FAIL: Controller recovery failed: {error}")
            return
        controller_result = recovery_results.get("controller")
        if isinstance(controller_result, Exception):
            report_logger.print_error(f"FAIL: Controller recovery failed: {controller_result}")
            return
        if controller_result is False or controller_result is None:
            report_logger.print_error("FAIL: Controller recovery result is unavailable")
            return
        report_logger.print_success("PASS: Controller recovered successfully")

        # Capture Controller IEEE 1905 traffic while Extender recovery is checked concurrently.
        report_logger.print_step("STEP 5: Start IEEE 1905 packet capture on the Controller after recovery")
        capture_name = device_utils.start_capture(initialize, "controller", "topology_management_discovery_after_controller_reboot", step=5)
        capture_started = True
        capture_started_at = time.monotonic()

        # Check each Extender's reachability and services concurrently during the IEEE 1905 capture.
        report_logger.print_step("STEP 6: Capture IEEE 1905 traffic while validating Extender recovery in parallel")
        recovery_times = {}
        with ThreadPoolExecutor(max_workers=len(extenders)) as executor:
            futures = {
                executor.submit(
                    recovery_utils.recover_device,
                    initialize,
                    extender,
                    reboot_started_at,
                    recovery_times,
                    recovery_type="agent",
                ): extender
                for extender in extenders
            }
            for future in as_completed(futures):
                future.result()
        for extender in extenders:
            result = recovery_times.get(extender)
            if isinstance(result, BaseException):
                report_logger.print_error(f"FAIL: {extender} recovery failed: {result}")
            elif result is False or result is None:
                report_logger.print_error(f"FAIL: {extender} recovery result is unavailable")
            elif not initialize.is_device_alive(extender):
                report_logger.print_error(f"FAIL: {extender} is not reachable after Controller reboot")
            else:
                report_logger.print_success(f"PASS: {extender} recovered within the KPI in {result:.1f}s")
        # Keep the Controller IEEE 1905 capture running for the full observation period.
        remaining_capture_time = TIME_DC - (time.monotonic() - capture_started_at)
        if remaining_capture_time > 0:
            report_logger.print_info(f"INFO: Continuing the Controller IEEE 1905 capture for {remaining_capture_time:.1f} more seconds")
            time.sleep(remaining_capture_time)

        # Stop the IEEE 1905 capture and retrieve its PCAP file for analysis.
        report_logger.print_step("STEP 7: Stop and collect the Controller IEEE 1905 capture")
        pcap_file = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        if not pcap_file or not os.path.isfile(pcap_file):
            report_logger.print_error(f"FAIL: Controller IEEE 1905 capture PCAP was not downloaded: {pcap_file!r}")
            return

        # Extract Topology Discovery packets from the Controller IEEE 1905 capture.
        report_logger.print_step("STEP 8: Extract Topology Discovery packet details from the IEEE 1905 capture")
        details = extract_topology_discovery_packet_details(pcap_file)
        if not details:
            report_logger.print_error("FAIL: No Topology Discovery packets were found in the captured IEEE 1905 traffic")
            return
        report_logger.print_success(f"PASS: Extracted details for {len(details)} Topology Discovery packet(s) from the IEEE 1905 capture data")

        # Confirm every enabled device transmitted Discovery packets at valid intervals.
        report_logger.print_step(f"STEP 9: Verify all {len(expected_devices)} enabled devices sent Topology Discovery packets and meet the interval limit")
        validate_topology_discovery_packets(details, expected_devices)

    finally:
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not stop Controller IEEE 1905 capture during cleanup: {error}")
        report_logger.print_test("Exiting test_topology_discovery_after_controller_reboot")
