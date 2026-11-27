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
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.topology_utils import *

def test_topology_discovery_after_em_service_restart(initialize):
    """
    Restart Controller and Extender EM services and validate Topology Discovery.
    """
    report_logger.print_test("Entering test_topology_discovery_after_em_service_restart")
    capture_name = None
    capture_started = False

    try:
        # Identify enabled Extenders and collect all device AL MAC addresses.
        report_logger.print_step("STEP 1: Identify enabled Extenders and collect AL MAC addresses for all enabled devices")
        extenders = device_utils.get_enabled_extenders(initialize)
        expected_devices = device_utils.get_enabled_device_al_macs(initialize)
        if not extenders or not expected_devices:
            report_logger.print_error("FAIL: Enabled Controller and Extender devices are required")
            return
        # Load the Controller and Extender service lists from test parameters.
        controller_em_services = get_em_services(initialize, "controller")
        extender_em_services = get_em_services(initialize, "extender")
        report_logger.print_info(f"INFO: Found {len(extenders)} enabled Extenders: {extenders}")

        # Restart each configured Controller EM service.
        report_logger.print_step("STEP 2: Restart Controller EM services")
        controller_failures = []
        for service in controller_em_services:
            try:
                report_logger.print_info(f"INFO: Restarting {service} on controller")
                initialize.restart_service("controller", service)
                report_logger.print_success(f"PASS: Restarted {service} on controller")
            except Exception as error:
                controller_failures.append(f"{service}: {error}")
                report_logger.print_error(f"FAIL: Could not restart {service} on controller: {error}")
        if controller_failures:
            report_logger.print_error("FAIL: Controller service restart failures: " + "; ".join(controller_failures))
            return

        # Verify all Controller EM services are active after restart.
        report_logger.print_step("STEP 3: Verify Controller EM service recovery")
        time.sleep(5)
        controller_services_active = device_utils.verify_services(initialize, "controller", controller_em_services, deadline=time.monotonic() + SERVICE_RECOVERY_TIMEOUT,)
        if not controller_services_active:
            report_logger.print_error("FAIL: Controller EM services did not recover")
            return
        report_logger.print_success("PASS: All Controller EM services recovered")

        # Check Controller SSH reachability after EM service restarts.
        report_logger.print_step("STEP 4: Verify Controller SSH connectivity after EM service restart")
        if not initialize.is_device_alive("controller"):
            report_logger.print_error("FAIL: Controller SSH is not reachable after service recovery")
            return
        report_logger.print_success("PASS: Controller SSH is reachable after EM service restart")

        # Restart Extender services after Controller service recovery.
        report_logger.print_step("STEP 5: Restart Extender EM services")
        extender_failures = {}
        for extender in extenders:
            for service in extender_em_services:
                try:
                    report_logger.print_info(f"INFO: Restarting {service} on {extender}")
                    initialize.restart_service(extender, service)
                    report_logger.print_success(f"PASS: Restarted {service} on {extender}")
                except Exception as error:
                    extender_failures.setdefault(extender, []).append(f"{service}: {error}")
                    report_logger.print_error(f"FAIL: Could not restart {service} on {extender}: {error}")
        if extender_failures:
            for extender, failures in extender_failures.items():
                report_logger.print_error(f"FAIL: {extender} service restart failures: " + "; ".join(failures))
            return

        # Verify all restarted Extender services are active.
        report_logger.print_step("STEP 6: Verify Extender EM service recovery")
        time.sleep(5)
        extender_status = {}
        with ThreadPoolExecutor(max_workers=len(extenders)) as executor:
            futures = {
                executor.submit(
                    device_utils.verify_services,
                    initialize,
                    extender,
                    extender_em_services,
                    time.monotonic() + SERVICE_RECOVERY_TIMEOUT,
                ): extender
                for extender in extenders
            }
            for future in as_completed(futures):
                extender = futures[future]
                extender_status[extender] = future.result()
                if extender_status[extender]:
                    report_logger.print_success(f"PASS: EM services recovered on {extender}")
        failed_extenders = [
            extender for extender, active in extender_status.items() if not active
        ]
        if failed_extenders:
            report_logger.print_error("FAIL: EM services are not active on: " + ", ".join(sorted(failed_extenders)))
            return

        # Check each Extender's SSH connectivity after service recovery.
        report_logger.print_step("STEP 7: Verify Extender SSH connectivity after EM service restarts")
        unreachable_extenders = []
        for extender in extenders:
            if initialize.is_device_alive(extender):
                report_logger.print_success(f"PASS: SSH is reachable on {extender}")
            else:
                unreachable_extenders.append(extender)
                report_logger.print_error(f"FAIL: SSH is not reachable on {extender}")
        if unreachable_extenders:
            return

        # Start IEEE 1905 capture once all Controller and Extender services have recovered.
        capture_name = device_utils.start_capture(initialize, "controller", "topology_discovery_after_em_service_restart", step=8)
        capture_started = True

        # Capture IEEE 1905 traffic for the full Topology Discovery observation period.
        report_logger.print_step(f"STEP 9: Capture IEEE 1905 traffic for {TIME_DC // 60} minutes")
        time.sleep(TIME_DC)
        report_logger.print_info("INFO: Completed the IEEE 1905 capture period")

        # Stop and download the completed Controller IEEE 1905 capture.
        report_logger.print_step("STEP 10: Stop and collect the IEEE 1905 capture from the Controller")
        pcap_file = device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
        capture_started = False
        if not pcap_file or not os.path.isfile(pcap_file):
            report_logger.print_error(f"FAIL: Controller IEEE 1905 capture PCAP was not downloaded: {pcap_file!r}")
            return

        # Reassemble the IEEE 1905 capture and extract Topology Discovery packet details.
        report_logger.print_step("STEP 11: Extract Topology Discovery packet details from the IEEE 1905 capture")
        details = extract_topology_discovery_packet_details(pcap_file)
        if not details:
            report_logger.print_error("FAIL: No Topology Discovery packets were found in the captured IEEE 1905 traffic")
            return
        report_logger.print_success(f"PASS: Extracted details for {len(details)} Topology Discovery packet(s) from the IEEE 1905 capture data")

        # Verify all enabled devices sent Discovery packets at valid intervals.
        report_logger.print_step(f"STEP 12: Verify all {len(expected_devices)} enabled devices sent Topology Discovery packets and meet the interval limit")
        validate_topology_discovery_packets(details, expected_devices)
    finally:
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(initialize, "controller", capture_name)
            except Exception as error:
                report_logger.print_error(f"FAIL: IEEE 1905 capture cleanup failed: {error}")
        report_logger.print_test("Exiting test_topology_discovery_after_em_service_restart")
