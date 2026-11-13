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

from concurrent.futures import ThreadPoolExecutor, as_completed
from rdkbmeshzap.common_utils import device_utils, recovery_utils, report_logger
from topology_management_utils import *
import time

def test_topology_management_after_extender_reboots(initialize):
    """
    Reboot enabled Extenders and validate the topology after recovery.
    """
    report_logger.print_test("Entering test_topology_management_after_extender_reboots")
    try:
        # Find the Extenders that participate in this topology test.
        report_logger.print_step("STEP 1: Discover all enabled Extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in infra.yaml")
            return
        report_logger.print_info(f"INFO: Found enabled Extenders: {extenders}")

        # Reboot all Extenders simultaneously.
        report_logger.print_step("STEP 2: Reboot all Extenders simultaneously")
        # Start the shared Extender recovery timer before rebooting the Extenders.
        reboot_started_at = time.monotonic()
        reboot_errors = {}
        with ThreadPoolExecutor(max_workers=len(extenders)) as executor:
            reboot_futures = {
                executor.submit(initialize.reboot_device, extender, method="cli"): extender
                for extender in extenders
            }
            for future in as_completed(reboot_futures):
                extender = reboot_futures[future]
                try:
                    future.result()
                except Exception as error:
                    reboot_errors[extender] = error
        for extender in extenders:
            if extender in reboot_errors:
                report_logger.print_error(f"FAIL: {extender}: reboot command failed: {reboot_errors[extender]}")
            else:
                report_logger.print_info(f"INFO: Reboot command executed for {extender}")

        # Allow reboot sessions to close before reconnecting.
        time.sleep(10)

        # Check all Extender recoveries concurrently against the shared deadline.
        report_logger.print_step("STEP 3: Recover all Extenders concurrently")
        recovery_results = {}
        with ThreadPoolExecutor(max_workers=len(extenders)) as executor:
            recovery_futures = [
                executor.submit(
                    recovery_utils.recover_device,
                    initialize,
                    extender,
                    reboot_started_at,
                    recovery_results,
                    recovery_type="agent",
                )
                for index, extender in enumerate(extenders, start=1)
            ]
            for future in as_completed(recovery_futures):
                future.result()

        # Report reboot errors after recovery is complete
        if reboot_errors:
            report_logger.print_error("FAIL: Extender reboot command failed for: " + ", ".join(reboot_errors))
            return

        # Require a numeric recovery duration for every Extender.
        failed_extenders = [
            extender
            for extender in extenders
            if not isinstance(recovery_results.get(extender), (int, float))
            or isinstance(recovery_results.get(extender), bool)
        ]
        if failed_extenders:
            report_logger.print_error("FAIL: Extender recovery failed for: " + ", ".join(failed_extenders))
            return
        report_logger.print_success("PASS: All Extenders recovered within the KPI")

        # Give the Controller time to refresh its topology view.
        report_logger.print_step("STEP 4: Wait for topology updates on the Controller")
        time.sleep(30)
        report_logger.print_success("PASS: Topology propagation wait completed")
        devices = ["controller", *extenders]

        # Read each device's wireless interfaces once and reuse the snapshots.
        report_logger.print_step("STEP 5: Read wireless interface details for each device")
        interface_details = collect_interface_details(initialize, devices)
        if interface_details is None:
            return
        report_logger.print_success("PASS: Wireless interface details collected")

        # Collect each Extender's configured backhaul MAC.
        report_logger.print_step("STEP 6: Read backhaul MAC addresses for each Extender")
        backhaul_data = collect_backhaul_macs(initialize, extenders, interface_details)
        if backhaul_data is None:
            return
        backhaul_mac_to_agent = backhaul_data
        report_logger.print_success("PASS: Extender backhaul MAC addresses collected")

        # Find bridge station interfaces used for backhaul association checks.
        report_logger.print_step("STEP 7: Discover bridge station interfaces for each device")
        station_interfaces_by_device = collect_bridge_station_interfaces(initialize, devices)
        if station_interfaces_by_device is None:
            return
        report_logger.print_success("PASS: Bridge station interfaces discovered")

        # Read associated station MACs from the discovered interfaces.
        report_logger.print_step("STEP 8: Read bridge station MAC addresses for each device")
        station_macs_by_device = collect_station_macs(initialize, station_interfaces_by_device)
        if station_macs_by_device is None:
            return
        report_logger.print_success("PASS: Bridge station MAC addresses collected")

        # Find each Extender's parent after recovery.
        report_logger.print_step("STEP 9: Find each Extender's parent device")
        parent_by_agent = {}
        failed_extenders = []
        for extender in extenders:
            parent, bssid = device_utils.get_extender_parent_device(initialize, extender, devices, iw_dev_snapshot=interface_details)
            if parent and parent != extender:
                parent_by_agent[extender] = parent
                report_logger.print_info(f"INFO: {extender} is connected to parent {parent} through backhaul BSSID {bssid}")
            else:
                failed_extenders.append(extender)
        if failed_extenders:
            report_logger.print_error("FAIL: Parent discovery failed after Extender reboots for: " + ", ".join(failed_extenders))
            return
        report_logger.print_success("PASS: Extender parent devices discovered")

        # Confirm each Extender's MAC is present in its parent's station table.
        report_logger.print_step("STEP 10: Confirm each Extender's backhaul MAC appears in its parent's station table")
        if not validate_backhaul_associations(extenders, parent_by_agent, backhaul_mac_to_agent, station_macs_by_device):
            return
        report_logger.print_success("PASS: Each Extender's backhaul MAC appears in its parent's station table")

        # Ensure every Extender's parent chain reaches the Controller without loops.
        report_logger.print_step("STEP 11: Confirm each Extender's parent chain reaches the Controller")
        if not validate_parent_chains(parent_by_agent):
            return
        report_logger.print_success("PASS: Every Extender's parent chain reaches the Controller without loops")

        # Classify the validated parent graph after the Extenders reboot.
        report_logger.print_step("STEP 12: Identify the topology type after Extender reboot")
        topology_type = classify_topology(devices, parent_by_agent)
        if topology_type is None:
            return
        report_logger.print_success(f"PASS: Detected {topology_type} topology after Extender recovery")
    finally:
        report_logger.print_test("Exiting test_topology_management_after_extender_reboots")
