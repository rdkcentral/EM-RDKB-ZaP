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

def test_topology_management_ui_topology(initialize):
    """
    Compare the Controller topology UI with the discovered live parent graph.
    """
    report_logger.print_test("Entering test_topology_management_ui_topology")
    try:
        # Find enabled Extenders and build the device list.
        report_logger.print_step("STEP 1: Find enabled Extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in infra.yaml")
            return
        report_logger.print_info(f"INFO: Found enabled Extenders: {extenders}")
        devices = ["controller", *extenders]

        # Collect wireless interface details from every device.
        report_logger.print_step("STEP 2: Collect wireless interface details for each device")
        interface_details = collect_interface_details(initialize, devices)
        if interface_details is None:
            return
        report_logger.print_success("PASS: Wireless interface details collected")

        # Find each Extender's backhaul MAC address.
        report_logger.print_step("STEP 3: Find backhaul MAC addresses for each Extender")
        backhaul_mac_to_agent = collect_backhaul_macs(initialize, extenders, interface_details)
        if backhaul_mac_to_agent is None:
            return
        report_logger.print_success("PASS: Extender backhaul MAC addresses collected")

        # Find bridge station interfaces on every device.
        report_logger.print_step("STEP 4: Find bridge station interfaces for each device")
        station_interfaces_by_device = collect_bridge_station_interfaces(initialize, devices)
        if station_interfaces_by_device is None:
            return
        report_logger.print_success("PASS: Bridge station interfaces discovered")

        # Read associated station MACs from the bridge interfaces.
        report_logger.print_step("STEP 5: Collect bridge station MAC addresses for each device")
        station_macs_by_device = collect_station_macs(initialize, station_interfaces_by_device)
        if station_macs_by_device is None:
            return
        report_logger.print_success("PASS: Bridge station MAC addresses collected")

        # Find the parent device for each Extender.
        report_logger.print_step("STEP 6: Find each Extender's parent device")
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
            report_logger.print_error("FAIL: Extender parent discovery failed for: "+ ", ".join(failed_extenders))
            return
        report_logger.print_success("PASS: Extender parent devices discovered")

        # Check that each parent lists its Extender's backhaul MAC.
        report_logger.print_step("STEP 7: Check Extender backhaul MACs in parent station tables")
        if not validate_backhaul_associations(extenders, parent_by_agent, backhaul_mac_to_agent, station_macs_by_device):
            return
        report_logger.print_success("PASS: Each Extender's backhaul MAC appears in its parent's station table")

        # Ensure every parent chain reaches the Controller.
        report_logger.print_step("STEP 8: Check that parent chains reach the Controller")
        if not validate_parent_chains(parent_by_agent):
            return
        report_logger.print_success("PASS: Every Extender's parent chain reaches the Controller without loops")

        # Classify the discovered parent relationships.
        report_logger.print_step("STEP 9: Classify the discovered topology")
        live_topology_type = classify_topology(devices, parent_by_agent)
        if live_topology_type is None:
            return
        report_logger.print_success(f"PASS: Detected {live_topology_type} topology")

        # Navigate to the Controller's Network Topology page.
        report_logger.print_step("STEP 10: Navigate to the Controller Network Topology page")
        try:
            initialize.ui_navigate_to_home_page("controller")
            initialize.ui_navigate_to_required_page("controller", "Network Topology")
            ui_module = initialize.get_ui_platform_obj("controller")
            if ui_module._page is None:
                raise RuntimeError("Controller UI page is not open")
            report_logger.print_info("INFO: Controller Network Topology page is accessible")
            page = ui_module._page
            ui_graph = read_ui_topology_graph(page)
        except Exception as error:
            report_logger.print_error(f"FAIL: Could not inspect the Controller Network Topology UI: {error}")
            return

        # Identify the root and match UI nodes to devices.
        report_logger.print_step("STEP 11: Match UI nodes to configured devices")
        errors = [str(ui_graph["error"])] if ui_graph.get("error") else []
        ui_nodes = ui_graph.get("nodes", [])
        # IDs are SVG child indices; labels are display-only and can repeat.
        ui_node_ids = {node["id"] for node in ui_nodes}
        ui_node_labels = {node["id"]: node["label"] for node in ui_nodes}
        root_id = ui_graph.get("root")
        if root_id is None or root_id not in ui_node_ids:
            errors.append("Could not identify the root node in the Network Topology UI")
        # Mapping values are node IDs, matching root and edge endpoints in ui_graph.
        device_to_ui_node, mapping_errors = map_ui_nodes_to_devices(page, ui_nodes, devices, interface_details, root_id)
        errors.extend(mapping_errors)
        controller_ui_node = device_to_ui_node.get("controller")
        if controller_ui_node is None:
            errors.append("Could not map a UI node to the Controller by its radio MACs")
        if errors:
            for error in errors:
                report_logger.print_error(error)
            return

        # Check that every configured device was mapped to a UI node.
        report_logger.print_step("STEP 12: Verify every configured device has a UI node")
        missing_devices = set(devices) - set(device_to_ui_node)
        if missing_devices:
            report_logger.print_error(f"FAIL: Configured devices missing from UI: {sorted(missing_devices)}")
            return
        report_logger.print_success("PASS: Every configured device has a UI node")

        # Verify UI connections and report success after all topology checks pass.
        report_logger.print_step("STEP 13: Verify UI links match the discovered topology")
        # Compare links by node ID so repeated display labels cannot merge distinct nodes.
        expected_edges = set()
        if root_id is not None and root_id != controller_ui_node:
            expected_edges.add(tuple(sorted((root_id, controller_ui_node))))
        for extender, parent in parent_by_agent.items():
            child_node = device_to_ui_node.get(extender)
            parent_node = device_to_ui_node.get(parent)
            if child_node is None or parent_node is None:
                report_logger.print_error(f"FAIL: Cannot compare the UI link for {parent} -> {extender}: a device has no mapped UI node")
                return
            expected_edges.add(tuple(sorted((parent_node, child_node))))
        actual_edges = set()
        for edge in ui_graph.get("edges", []):
            source = edge.get("source")
            target = edge.get("target")
            if source not in ui_node_ids or target not in ui_node_ids:
                report_logger.print_error(f"FAIL: UI contains an edge with unknown endpoints: {source} ({ui_node_labels.get(source, 'unknown')}) -> {target} ({ui_node_labels.get(target, 'unknown')})")
                return
            actual_edges.add(tuple(sorted((source, target))))
        missing_edges = expected_edges - actual_edges
        unexpected_edges = actual_edges - expected_edges
        if missing_edges or unexpected_edges:
            for status, edges in (("Missing", missing_edges), ("Unexpected", unexpected_edges)):
                for source, target in sorted(edges):
                    report_logger.print_error(
                        f"FAIL: UI parent-link mismatch: {status} link "
                        f"{ui_node_labels[source]} (node {source}) -> "
                        f"{ui_node_labels[target]} (node {target})"
                    )
            return
        report_logger.print_success(f"PASS: Network Topology UI nodes and parent links match the live {live_topology_type} topology")
    finally:
        report_logger.print_test("Exiting test_topology_management_ui_topology")
