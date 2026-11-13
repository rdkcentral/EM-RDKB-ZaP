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

import re
from typing import Any
from rdkbmeshzap.common_utils import device_utils, report_logger

# Match colon-delimited MAC addresses in UI tooltip text.
MAC_PATTERN = re.compile(r"\b[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}\b")

def collect_interface_details(initialize, devices: list[str]) -> dict[str, dict[str, dict[str, str]]] | None:
    """
    Syntax: collect_interface_details(initialize, devices)
    Description: Read one ``iw dev`` snapshot per device and normalize interfaces.
    Parameters:
        initialize : Testbed interface.
        devices : Controller and Extender device names.
    Return Value: Device-to-interface details mapping, or None if discovery fails.
    Example: collect_interface_details(initialize, ["controller", "extender1"])
    """
    interface_details_by_device = {}
    errors = []
    for device in devices:
        try:
            iw_dev_output = initialize.get_iw_dev_info(device)
            interface_names = device_utils.parse_iw_dev_output(iw_dev_output)
            # Reuse this snapshot for every interface on the device.
            interface_details_by_device[device] = {
                interface: initialize.get_iw_interface_details(
                    device, interface, iw_dev_output=iw_dev_output
                )
                for interface in interface_names
            }
        except Exception as error:
            errors.append(f"{device}: unable to read wireless interfaces: {error}")
    if errors:
        report_logger.print_error("FAIL: Interface discovery failed: " + "; ".join(errors))
        return None
    return interface_details_by_device

def collect_backhaul_macs(initialize, extenders: list[str], interface_details: dict[str, dict[str, dict[str, str]]]) -> dict[str, str] | None:
    """
    Syntax: collect_backhaul_macs(initialize, extenders, interface_details)
    Description: Map each configured Extender backhaul MAC to its owning Extender.
    Parameters:
        initialize : Testbed interface.
        extenders : Enabled Extender device names.
        interface_details : Normalized wireless interfaces by device.
    Return Value: Backhaul-MAC-to-Extender mapping, or None if discovery fails.
    Example: collect_backhaul_macs(initialize, extenders, interface_details)
    """
    backhaul_mac_to_agent = {}
    errors = []
    for extender in extenders:
        try:
            backhaul_iface = initialize.read_from_database(extender, "backhaul_interface")
        except Exception as error:
            errors.append(f"{extender}: unable to read backhaul_interface: {error}")
            continue
        if not backhaul_iface:
            errors.append(f"{extender}: backhaul_interface is not configured")
            continue
        backhaul_mac = (
            interface_details.get(extender, {})
            .get(backhaul_iface, {})
            .get("addr", "")
        )
        if not backhaul_mac:
            errors.append(f"{extender}: no MAC address found for {backhaul_iface}")
            continue
        # Index by MAC to detect duplicates while preserving Extender ownership.
        if backhaul_mac in backhaul_mac_to_agent:
            errors.append(f"Duplicate backhaul MAC {backhaul_mac} on {extender} and {backhaul_mac_to_agent[backhaul_mac]}")
            continue
        backhaul_mac_to_agent[backhaul_mac] = extender
        print(f"{extender}: backhaul interface={backhaul_iface}, MAC={backhaul_mac}")
    if errors:
        report_logger.print_error("FAIL: Backhaul MAC discovery failed: " + "; ".join(errors))
        return None
    return backhaul_mac_to_agent

def collect_bridge_station_interfaces(initialize, devices: list[str]) -> dict[str, list[str]] | None:
    """
    Syntax: collect_bridge_station_interfaces(initialize, devices)
    Description: Find wireless station interfaces attached to each device bridge.
    Parameters:
        initialize : Testbed interface.
        devices : Controller and Extender device names.
    Return Value: Device-to-station-interface mapping, or None if discovery fails.
    Example: collect_bridge_station_interfaces(initialize, ["controller", "extender1"])
    """
    station_interfaces_by_device = {}
    errors = []
    for device in devices:
        try:
            bridge_iface = initialize.read_from_database(device, "bridge_iface")
            if not bridge_iface:
                errors.append(f"{device}: bridge_iface is not configured")
                continue
            station_interfaces = initialize.get_bridge_station_interfaces(device, bridge_iface)
        except Exception as error:
            errors.append(f"{device}: unable to read bridge station interfaces: {error}")
            continue
        station_interfaces_by_device[device] = station_interfaces
        interfaces = ", ".join(station_interfaces) or "none"
        report_logger.print_info(f"INFO: {device} bridge station interfaces: {interfaces}")
    if errors:
        report_logger.print_error("FAIL: Bridge interface discovery failed: " + "; ".join(errors))
        return None
    return station_interfaces_by_device

def collect_station_macs(initialize, station_interfaces_by_device: dict[str, list[str]]) -> dict[str, set[str]] | None:
    """
    Syntax: collect_station_macs(initialize, station_interfaces_by_device)
    Description: Read associated station MAC addresses from each bridge station interface.
    Parameters:
        initialize : Testbed interface.
        station_interfaces_by_device : Device-to-station-interface mapping.
    Return Value: Device-to-set-of-associated-station-MACs mapping, or None if discovery fails.
    Example: collect_station_macs(initialize, station_interfaces_by_device)
    """
    station_macs_by_device = {}
    errors = []
    for device, station_interfaces in station_interfaces_by_device.items():
        station_macs_by_device[device] = set()
        if not station_interfaces:
            print(f"INFO: {device} bridge station table has no interfaces to read")
            continue
        # Merge station records from all bridge interfaces on this device.
        for station_iface in station_interfaces:
            try:
                station_macs = {
                    str(mac).lower()
                    for mac in initialize.get_iw_station_details(device, station_iface, "macs")
                }
            except Exception as error:
                errors.append(f"{device}: unable to read station MACs on {station_iface}: {error}")
                continue
            station_macs_by_device[device].update(station_macs)
            associated_macs = ", ".join(sorted(station_macs)) or "none"
            report_logger.print_info(f"INFO: {device} bridge station table on {station_iface} contains MACs: {associated_macs}")
    if errors:
        report_logger.print_error("FAIL: Station MAC discovery failed: " + "; ".join(errors))
        return None
    return station_macs_by_device

def validate_backhaul_associations(extenders: list[str], parent_by_agent: dict[str, str], backhaul_mac_to_agent: dict[str, str], station_macs_by_device: dict[str, set[str]]) -> bool:
    """
    Syntax: validate_backhaul_associations(extenders, parent_by_agent, backhaul_mac_to_agent, station_macs_by_device)
    Description: Verify each Extender's backhaul MAC appears in its mapped parent's station table.
    Parameters:
        extenders : Enabled Extender device names.
        parent_by_agent : Mapping from Extender names to their parent device names.
        backhaul_mac_to_agent : Mapping from backhaul MAC addresses to Extender names.
        station_macs_by_device : Device-to-set-of-associated-station-MACs mapping.
    Return Value: True when all backhaul associations are present; otherwise False.
    Example: validate_backhaul_associations(extenders, parent_by_agent, backhaul_mac_to_agent, station_macs_by_device)
    """
    errors = []
    agent_to_backhaul_mac = {
        agent: mac for mac, agent in backhaul_mac_to_agent.items()
    }
    for extender in extenders:
        parent = parent_by_agent[extender]
        backhaul_mac = agent_to_backhaul_mac.get(extender)
        if backhaul_mac not in station_macs_by_device.get(parent, set()):
            errors.append(f"{extender}: backhaul MAC {backhaul_mac} was not found in {parent}'s bridge station table")
            continue
        report_logger.print_info(f"INFO: {extender} backhaul MAC {backhaul_mac} appears in {parent}'s station table")
    if errors:
        report_logger.print_error("FAIL: Backhaul association validation failed: " + "; ".join(errors))
        return False
    return True

def validate_parent_chains(parent_by_agent: dict[str, str]) -> bool:
    """
    Syntax: validate_parent_chains(parent_by_agent)
    Description: Ensure each Extender's parent chain reaches the Controller without cycles.
    Parameters:
        parent_by_agent : Mapping from Extender names to their parent device names.
    Return Value: True when every chain reaches the Controller; otherwise False.
    Example: validate_parent_chains({"extender1": "controller"})
    """
    errors = []
    for extender in parent_by_agent:
        current = extender
        # A repeated device in this path means the parent links contain a loop.
        visited = set()
        chain_valid = True
        while current != "controller":
            if current in visited:
                errors.append(f"Topology loop detected while tracing {extender}")
                chain_valid = False
                break
            visited.add(current)
            parent = parent_by_agent.get(current)
            if parent is None:
                errors.append(f"{extender}: parent chain ends at {current}, not controller")
                chain_valid = False
                break
            current = parent
        if chain_valid:
            report_logger.print_info(f"INFO: {extender}'s parent chain reaches the Controller without loops")
    if errors:
        report_logger.print_error("FAIL: Parent-chain validation failed: " + "; ".join(errors))
        return False
    return True

def classify_topology(devices: list[str], extender_to_parent_map: dict[str, str]) -> str | None:
    """
    Syntax: classify_topology(devices, extender_to_parent_map)
    Description: Classify a validated parent graph as star, daisy-chain, or hybrid.
    Parameters:
        devices : Controller and Extender device names.
        extender_to_parent_map : Mapping of each Extender to its parent device.
    Return Value: Topology type, or None when the parent graph is not a supported shape.
    Example: classify_topology(devices, extender_to_parent_map)
    """
    children = {device: set() for device in devices}
    for extender, parent in extender_to_parent_map.items():
        children[parent].add(extender)
    # Separate flat stars and single chains from topologies with mixed branching.
    if all(parent == "controller" for parent in extender_to_parent_map.values()):
        topology_type = "star"
    elif len(children["controller"]) == 1 and all(
        len(device_children) <= 1 for device_children in children.values()
    ):
        topology_type = "daisy"
    else:
        has_star_component = any(len(device_children) > 1 for device_children in children.values())
        has_daisy_component = any(parent != "controller" for parent in extender_to_parent_map.values())
        topology_type = "hybrid" if has_star_component and has_daisy_component else None
    if topology_type is None:
        report_logger.print_error("FAIL: Invalid topology: parent relationships do not form a star, daisy-chain, or hybrid (star + daisy-chain) topology")
        return None
    return topology_type

def read_ui_topology_graph(page) -> dict[str, Any]:
    """
    Syntax: read_ui_topology_graph(page)
    Description: Read unique node IDs, display labels, the root, and links from the rendered graph.
        Each ID is the node's SVG child index for this graph snapshot; labels may repeat.
    Parameters:
        page : Controller Network Topology page.
    Return Value: Mapping containing the root ID, nodes as ``{id, label}``, and edges as ID pairs.
    Example: read_ui_topology_graph(page)
    """
    page.wait_for_function(
        """() => {
            const nodes = document.querySelectorAll("svg .nodes > *");
            return nodes.length > 0 && Array.from(nodes).every(node =>
                Array.from(node.querySelectorAll("text"))
                    .some(label => (label.textContent || "").trim()) &&
                node.transform.baseVal.consolidate()
            );
        }""",
        timeout=15000,
    )
    return page.evaluate(
        """() => {
            const nodeGroup = document.querySelector("svg .nodes");
            const svg = nodeGroup?.ownerSVGElement;
            if (!svg) {
                return { error: "Network Topology SVG was not found", nodes: [], edges: [] };
            }
            // Use each SVG child's index as a unique ID, even when labels repeat.
            const nodes = Array.from(nodeGroup.children, (node, id) => {
                const labels = Array.from(node.querySelectorAll("text"))
                    .map(label => (label.textContent || "").trim())
                    .filter(Boolean);
                const transform = node.transform.baseVal.consolidate();
                return labels.length && transform ? {
                    id,
                    label: labels[labels.length - 1],
                    x: transform.matrix.e,
                    y: transform.matrix.f,
                    isRoot: node.querySelectorAll("circle").length === 0
                } : null;
            }).filter(Boolean);
            const roots = nodes.filter(node => node.isRoot);

            // Resolve edge endpoints to node IDs so duplicate labels stay distinct.
            const nearestNode = point => nodes.reduce((closest, candidate) => {
                const distance = Math.hypot(candidate.x - point.x, candidate.y - point.y);
                return !closest || distance < closest.distance
                    ? { id: candidate.id, distance }
                    : closest;
            }, null)?.id ?? null;
            const edges = Array.from(svg.querySelectorAll(".edges > path"), path => {
                const length = path.getTotalLength();
                return length ? {
                    source: nearestNode(path.getPointAtLength(0)),
                    target: nearestNode(path.getPointAtLength(length))
                } : null;
            }).filter(Boolean);
            return {
                root: roots.length === 1 ? roots[0].id : null,
                nodes: nodes.map(({ id, label }) => ({ id, label })),
                edges
            };
        }"""
    )

def map_ui_nodes_to_devices(page, ui_nodes, devices, interface_details, root_id):
    """
    Syntax: map_ui_nodes_to_devices(page, ui_nodes, devices, interface_details, root_id)
    Description: Map UI node IDs to devices using live interface MACs from ``iw dev``.
    Parameters:
        page : Controller Network Topology page.
        ui_nodes : Rendered topology nodes with SVG child-index ``id`` values and display ``label`` values.
        devices : Controller and Extender device names.
        interface_details : Normalized wireless interfaces by device.
        root_id : SVG child-index ID of the root node, matching the IDs in ``ui_nodes``.
    Return Value: Device-to-node-ID mapping and any mapping errors; labels are for diagnostics only.
    Example: map_ui_nodes_to_devices(page, ui_nodes, devices, interface_details, root_id)
    """
    node_locator = page.locator("svg .nodes").first.locator(":scope > *")
    tooltip_locator = page.locator("#custom-tooltip")
    device_radio_macs = {
        device: {
            str(interface.get("addr", "")).strip().lower()
            for interface in interface_details.get(device, {}).values()
            if interface.get("addr")
        }
        for device in devices
    }
    # Key device mappings by node ID; use labels only in diagnostics.
    device_to_ui_node = {}
    node_labels = {node["id"]: node["label"] for node in ui_nodes}
    errors = []
    for node in ui_nodes:
        node_id = node["id"]
        label = node["label"]
        try:
            # The ID is the SVG child index, so it selects the matching rendered node.
            node_locator.nth(node_id).hover()
            tooltip_locator.wait_for(state="visible", timeout=5000)
            tooltip_text = tooltip_locator.inner_text(timeout=5000)
        except Exception as error:
            if node_id != root_id:
                errors.append(f"Could not inspect UI node {label}: {error}")
            continue
        displayed_radio_macs = {
            match.group(0).lower()
            for match in MAC_PATTERN.finditer(tooltip_text)
        }
        matching_devices = [
            device
            for device, radio_macs in device_radio_macs.items()
            if displayed_radio_macs & radio_macs
        ]
        if not matching_devices and node_id == root_id:
            continue
        if len(matching_devices) != 1:
            errors.append(f"UI node {label} maps to {len(matching_devices)} configured devices by its displayed radio MACs {sorted(displayed_radio_macs)}")
            continue
        device = matching_devices[0]
        if device in device_to_ui_node:
            previous_node_id = device_to_ui_node[device]
            errors.append(f"Configured device {device} appears under multiple UI nodes: {previous_node_id} ({node_labels[previous_node_id]}) and {node_id} ({label})")
            continue
        device_to_ui_node[device] = node_id
        report_logger.print_info(f"INFO: UI node {label} maps to {device}")
    return device_to_ui_node, errors


