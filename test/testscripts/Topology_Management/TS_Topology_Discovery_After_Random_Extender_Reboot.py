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

def test_topology_discovery_after_random_extender_reboot(initialize):
    """
    Reboot a random Extender and validate peer topology discovery during its recovery.
    """
    report_logger.print_test("Entering test_topology_discovery_after_random_extender_reboot")
    capture_name = None
    capture_started = False
    selected_extender = None
    reboot_attempted = False

    try:
        # Identify enabled Extenders and collect device AL MAC addresses for validation.
        report_logger.print_step("STEP 1: Identify enabled Extenders and collect AL MAC addresses for all enabled devices")
        extenders = device_utils.get_enabled_extenders(initialize)
        expected_devices = device_utils.get_enabled_device_al_macs(initialize)
        if not extenders or not expected_devices:
            report_logger.print_error("FAIL: Enabled Controller and Extender devices are required")
            return
        report_logger.print_info(f"INFO: Found {len(extenders)} enabled Extenders: {extenders}")
        if "controller" not in expected_devices:
            report_logger.print_error("FAIL: Could not collect the Controller AL MAC address")
            return
        missing_al_macs = [extender for extender in extenders if extender not in expected_devices]
        if missing_al_macs:
            report_logger.print_error("FAIL: Could not collect AL MAC addresses for: " + ", ".join(missing_al_macs))
            return

        # Select one enabled Extender for reboot; packet validation will cover its peers only.
        report_logger.print_step("STEP 2: Select an Extender for reboot")
        selected_extender = random.choice(extenders)
        expected_other_devices = {
            device: al_mac
            for device, al_mac in expected_devices.items()
            if device != selected_extender
        }
        report_logger.print_info(f"INFO: Selected {selected_extender} for reboot")

        # Reboot the selected Extender before starting the Controller capture.
        report_logger.print_step(f"STEP 3: Reboot selected Extender {selected_extender}")
        reboot_attempted = True
        try:
            initialize.reboot_device(selected_extender, method="cli")
            report_logger.print_info(f"INFO: Reboot command completed for {selected_extender}")
        except Exception as error:
            report_logger.print_error(f"FAIL: Reboot command failed for {selected_extender}: {error}")
            return

        # Start capturing immediately after issuing the reboot, while the Extender recovers.
        capture_name = device_utils.start_capture(initialize, "controller", "topology_discovery_during_random_extender_reboot", step=4)
        capture_started = True
        capture_started_at = time.monotonic()

        # Allow the Extender to reboot before reconnecting.
        time.sleep(30)

        # Keep the capture open for the full observation period to validate peer intervals.
        remaining_capture_time = TIME_DC - (time.monotonic() - capture_started_at)
        if remaining_capture_time > 0:
            report_logger.print_info(f"INFO: Continue capturing IEEE 1905 traffic for {remaining_capture_time:.1f} more seconds")
            time.sleep(remaining_capture_time)
        report_logger.print_info("INFO: Completed the IEEE 1905 capture period")

        # Collect traffic captured while the Extender rebooted.
        report_logger.print_step("STEP 5: Stop and collect the Controller IEEE 1905 capture")
        reboot_pcap_file = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        if not reboot_pcap_file or not os.path.isfile(reboot_pcap_file):
            report_logger.print_error(f"FAIL: Controller IEEE 1905 capture PCAP was not downloaded: {reboot_pcap_file!r}")
            return

        report_logger.print_step("STEP 6: Extract Topology Discovery packet details from the reboot-period capture")
        reboot_details = extract_topology_discovery_packet_details(reboot_pcap_file)
        if not reboot_details:
            report_logger.print_error("FAIL: No Topology Discovery packets were found during the Extender reboot capture")
            return

        report_logger.print_step("STEP 7: Verify the remaining devices sent Topology Discovery packets during the reboot")
        validate_topology_discovery_packets(reboot_details, expected_other_devices)

    finally:
        # Stop and collect any IEEE 1905 capture left running after an early exit.
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
            except Exception as error:
                report_logger.print_error(f"FAIL: IEEE 1905 capture cleanup failed: {error}")
        if reboot_attempted and selected_extender:
            report_logger.print_step(f"STEP 8: Check the rebooted Extender {selected_extender} connection")
            try:
                if initialize.is_device_alive(selected_extender):
                    report_logger.print_success(f"PASS: Rebooted Extender {selected_extender} is reachable")
                else:
                    report_logger.print_error(f"FAIL: Rebooted Extender {selected_extender} is not reachable")
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not check the rebooted Extender {selected_extender} connection: {error}")
        report_logger.print_test("Exiting test_topology_discovery_after_random_extender_reboot")
