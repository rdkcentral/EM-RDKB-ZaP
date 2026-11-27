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

def test_topology_discovery_after_extender_reboots(initialize):
    """
    Reboot all Extenders and validate Topology Discovery after recovery.
    """
    report_logger.print_test("Entering test_topology_discovery_after_extender_reboots")
    capture_name = None
    capture_started = False

    try:
        # Find enabled Extenders and collect device AL MAC addresses for validation.
        report_logger.print_step("STEP 1: Identify enabled Extenders and collect device AL MAC addresses")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in infra.yaml")
            return
        expected_devices = device_utils.get_enabled_device_al_macs(initialize)
        report_logger.print_info(f"INFO: Found {len(extenders)} enabled Extenders: {extenders}")

        # Start the shared recovery timer and reboot all enabled Extenders concurrently.
        report_logger.print_step("STEP 2: Reboot all enabled Extenders concurrently")
        reboot_started_at = time.monotonic()
        reboot_errors = {}
        with ThreadPoolExecutor(max_workers=len(extenders)) as executor:
            futures = {
                executor.submit(
                    initialize.reboot_device, extender, method="cli"
                ): extender
                for extender in extenders
            }
            for future in as_completed(futures):
                extender = futures[future]
                try:
                    future.result()
                    report_logger.print_info(f"INFO: Reboot command completed for {extender}")
                except Exception as error:
                    reboot_errors[extender] = error
                    report_logger.print_error(f"FAIL: Reboot command failed for {extender}: {error}")
        # Allow reboot sessions to close before attempting recovery.
        time.sleep(30)

        # Recover rebooted Extenders concurrently against the shared recovery deadline.
        report_logger.print_step("STEP 3: Recover all enabled Extenders concurrently")
        recovery_results = {}
        with ThreadPoolExecutor(max_workers=len(extenders)) as executor:
            futures = [
                executor.submit(
                    recovery_utils.recover_device,
                    initialize,
                    extender,
                    reboot_started_at,
                    recovery_results,
                    recovery_type="agent",
                )
                for extender in extenders
                if extender not in reboot_errors
            ]
            for future in as_completed(futures):
                future.result()
        if reboot_errors:
            report_logger.print_error("FAIL: Extender reboot command failed for: " + ", ".join(reboot_errors))
            return
        failed_recovery = [extender for extender in extenders if not isinstance(recovery_results.get(extender), (int, float)) or isinstance(recovery_results.get(extender), bool)]
        if failed_recovery:
            report_logger.print_error("FAIL: Extender recovery failed for: " + ", ".join(failed_recovery))
            return

        # Start the Controller IEEE 1905 capture after all Extenders have recovered.
        capture_name = device_utils.start_capture(initialize, "controller", "topology_discovery_after_extender_reboots", step=4)
        capture_started = True

        # Capture IEEE 1905 traffic for the full Topology Discovery observation period.
        report_logger.print_step(f"STEP 5: Capture IEEE 1905 traffic for {TIME_DC // 60} minutes")
        time.sleep(TIME_DC)
        report_logger.print_info("INFO: Completed the IEEE 1905 capture period")

        # Stop the IEEE 1905 capture and download its PCAP for analysis.
        report_logger.print_step("STEP 6: Stop and collect the IEEE 1905 capture from the Controller")
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

        # Verify each enabled device's packet count and discovery interval.
        report_logger.print_step(f"STEP 8: Verify all {len(expected_devices)} enabled devices sent Topology Discovery packets and meet the interval limit")
        validate_topology_discovery_packets(details, expected_devices)
 
    finally:
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(
                    initialize, "controller", capture_name
                )
            except Exception as error:
                report_logger.print_error(f"FAIL: IEEE 1905 capture cleanup failed: {error}")
        report_logger.print_test("Exiting test_topology_discovery_after_extender_reboots")