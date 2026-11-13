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

from rdkbmeshzap.common_utils import device_utils, report_logger
from topology_management_utils import *

def test_topology_management_dynamic_topology(initialize):
    """
    Discover and validate the live Controller and Extender topology.
    """
    report_logger.print_test("Entering test_topology_management_dynamic_topology")
    try:
        # Find the Extenders included in this topology check.
        report_logger.print_step("STEP 1: Discover all enabled Extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in infra.yaml")
            return
        report_logger.print_info(f"INFO: Found enabled Extenders: {extenders}")

        devices = ["controller", *extenders]
        # Read each device's wireless interfaces once and reuse the snapshots.
        report_logger.print_step("STEP 2: Read wireless interface details for each device")
        interface_details = collect_interface_details(initialize, devices)
        if interface_details is None:
            return
        report_logger.print_success("PASS: Wireless interface details collected")

        # Collect each Extender's configured backhaul MAC.
        report_logger.print_step("STEP 3: Read backhaul MAC addresses for each Extender")
        backhaul_data = collect_backhaul_macs(initialize, extenders, interface_details)
        if backhaul_data is None:
            return
        backhaul_mac_to_agent = backhaul_data
        report_logger.print_success("PASS: Extender backhaul MAC addresses collected")

        # Find bridge station interfaces used for backhaul association checks.
        report_logger.print_step("STEP 4: Discover bridge station interfaces for each device")
        station_interfaces_by_device = collect_bridge_station_interfaces(initialize, devices)
        if station_interfaces_by_device is None:
            return
        report_logger.print_success("PASS: Bridge station interfaces discovered")

        # Read associated station MACs from the discovered interfaces.
        report_logger.print_step("STEP 5: Read bridge station MAC addresses for each device")
        station_macs_by_device = collect_station_macs(initialize, station_interfaces_by_device)
        if station_macs_by_device is None:
            return
        report_logger.print_success("PASS: Bridge station MAC addresses collected")

        # Resolve each Extender's parent using its connected backhaul BSSID.
        report_logger.print_step("STEP 6: Find Extender parent devices")
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
            report_logger.print_error("FAIL: Extender parent discovery failed for: " + ", ".join(failed_extenders))
            return
        report_logger.print_success("PASS: Extender parent devices discovered")

        # Confirm each Extender MAC is present in its parent's station table.
        report_logger.print_step("STEP 7: Confirm each Extender's backhaul MAC appears in its parent's station table")
        if not validate_backhaul_associations(extenders, parent_by_agent, backhaul_mac_to_agent, station_macs_by_device):
            return
        report_logger.print_success("PASS: Each Extender's backhaul MAC appears in its parent's station table")

        # Ensure every Extender's parent chain reaches the Controller without loops.
        report_logger.print_step("STEP 8: Confirm each Extender's parent chain reaches the Controller")
        if not validate_parent_chains(parent_by_agent):
            return
        report_logger.print_success("PASS: Every Extender's parent chain reaches the Controller without loops")

        # Classify the validated parent graph.
        report_logger.print_step("STEP 9: Identify the testbed topology type")
        topology_type = classify_topology(devices, parent_by_agent)
        if topology_type is None:
            return
        report_logger.print_success(f"PASS: Detected {topology_type} topology")
    finally:
        report_logger.print_test("Exiting test_topology_management_dynamic_topology")

