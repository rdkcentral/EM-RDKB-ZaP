# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
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
"""Common helper utilities for Zaero-based tests."""

import re
import pytest
from rdkbmeshzap.common_utils import device_utils, report_logger
POLL_INTERVAL_SEC = 60
TEST_DURATION_SEC = 120

MAX_BASELINE_INCREASE_PERCENT = 20.0
AVAILABLE_MEMORY_PERCENT = 20.0
MAX_USED_MEMORY_PERCENT = 80.0
MONOTONIC_GROWTH_SAMPLES = 3
MIN_MONOTONIC_GROWTH_MB = 50.0
MAX_BASELINE_USED_INCREASE_PERCENT = 20.0

def parse_iw_dev_output(output: str, value: str) -> list:
    """
    Syntax : parse_iw_dev_output(output, value)
    Description : Extracts a requested value from raw `iw dev` output.
    Parameters :
        output - Raw output from an `iw dev` command.
        value - Value to extract: `interfaces`, `interface_records`, or `macs`.
    Return Value: A list of extracted values or interface-record tuples.
    """
    patterns = {
        "interfaces": (
            re.compile(r"^\s*Interface\s+(\S+)", re.MULTILINE),
            1,
        ),
        "interface_records": (
            re.compile(
                r"^\s*Interface\s+(?P<interface>\S+)"
                r"(?P<details>.*?)(?=^\s*Interface\s+|\Z)",
                re.MULTILINE | re.DOTALL,
            ),
            ("interface", "details"),
        ),
        "macs": (
            re.compile(
                r"^\s*addr\s+([0-9a-f:]{17})",
                re.MULTILINE | re.IGNORECASE,
            ),
            1,
        ),
    }
    if value not in patterns:
        raise ValueError(f"Unsupported iw dev value: {value}")
    pattern, groups = patterns[value]
    if isinstance(groups, tuple):
        return [
            tuple(match.group(group) for group in groups)
            for match in pattern.finditer(output)
        ]
    return [match.group(groups) for match in pattern.finditer(output)]

def parse_link_output(output: str, value: str) -> list:
    """
    Syntax : parse_link_output(output, value)
    Description : Extracts a requested value from raw `iw link` output.
    Parameters :
        output - Raw output from an `iw link` command.
        value - Value to extract: `bssid`, `ssid`, `signal`, or `rates`.
    Return Value: A list of extracted values or rate tuples.
    """
    patterns = {
        "bssid": (
            re.compile(
                r"^\s*Connected\s+to\s+([0-9a-f:]{17})",
                re.MULTILINE | re.IGNORECASE,
            ),
            1,
        ),
        "ssid": (
            re.compile(r"^\s*SSID:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE),
            1,
        ),
        "signal": (
            re.compile(
                r"^\s*signal:\s*(-?\d+)\s*dBm",
                re.MULTILINE | re.IGNORECASE,
            ),
            1,
        ),
        "rates": (
            re.compile(
                r"^\s*(tx|rx) bitrate:\s*([\d.]+)\s+([MGK]Bit/s)",
                re.MULTILINE | re.IGNORECASE,
            ),
            (1, 2, 3),
        ),
    }
    if value not in patterns:
        raise ValueError(f"Unsupported iw link value: {value}")
    pattern, groups = patterns[value]
    if isinstance(groups, tuple):
        return [
            tuple(match.group(group) for group in groups)
            for match in pattern.finditer(output)
        ]
    return [match.group(groups) for match in pattern.finditer(output)]

def parse_station_output(output: str, value: str) -> list:
    """
    Syntax : parse_station_output(output, value)
    Description : Extracts a requested value from raw `iw station dump` output.
    Parameters :
        output - Raw output from an `iw station dump` command.
        value - Value to extract: `records`, `macs`, `connected_time`,
                `signal`, `tx_rate`, or `rx_rate`.
    Return Value: A list of extracted values or station-record/rate tuples.
    """
    patterns = {
        "records": (
            re.compile(
                r"^Station\s+(?P<mac>[0-9a-f:]{17})\b"
                r"(?P<details>.*?)(?=^Station |\Z)",
                re.MULTILINE | re.DOTALL | re.IGNORECASE,
            ),
            ("mac", "details"),
        ),
        "macs": (
            re.compile(
                r"^Station\s+([0-9a-f:]{17})",
                re.MULTILINE | re.IGNORECASE,
            ),
            1,
        ),
        "connected_time": (
            re.compile(r"^\s*connected time:\s*(\d+) seconds", re.MULTILINE),
            1,
        ),
        "signal": (
            re.compile(
                r"^\s*signal:\s*(-?\d+)\s*dBm\s*$",
                re.MULTILINE | re.IGNORECASE,
            ),
            1,
        ),
        "tx_rate": (
            re.compile(
                r"^\s*tx bitrate:\s*([\d.]+)\s+([MGK]Bit/s)",
                re.MULTILINE | re.IGNORECASE,
            ),
            (1, 2),
        ),
        "rx_rate": (
            re.compile(
                r"^\s*rx bitrate:\s*([\d.]+)\s+([MGK]Bit/s)",
                re.MULTILINE | re.IGNORECASE,
            ),
            (1, 2),
        ),
    }
    if value not in patterns:
        raise ValueError(f"Unsupported iw station value: {value}")
    pattern, groups = patterns[value]
    if isinstance(groups, tuple):
        return [
            tuple(match.group(group) for group in groups)
            for match in pattern.finditer(output)
        ]
    return [match.group(groups) for match in pattern.finditer(output)]

def collect_device_cpu_utilization(zaero_obj, device: str) -> dict:
    """
    Syntax : collect_device_cpu_utilization(zaero_obj, device)
    Description : Collects one parsed CPU utilization snapshot for a device.
    Parameters :
        zaero_obj - Testbed initialization object exposing feature APIs.
        device - Name of the target device.
    Return Value: A parsed CPU snapshot containing the device name.
    """
    output = device_utils.get_device_cpu_utilization_output(zaero_obj, device)
    snapshot = device_utils.parse_cpu_utilization_output(output)
    snapshot["device"] = device
    return snapshot

def collect_device_memory_utilization(zaero_obj, device: str) -> dict:
    """
    Syntax : collect_device_memory_utilization(zaero_obj, device)
    Description : Collects one parsed memory utilization snapshot for a device.
    Parameters :
        zaero_obj - Testbed initialization object exposing feature APIs.
        device - Name of the target device.
    Return Value: A parsed memory snapshot containing the device name.
    """
    output = device_utils.get_device_memory_utilization_output(zaero_obj, device)
    snapshot = device_utils.parse_memory_utilization_output(output)
    snapshot["device"] = device
    return snapshot

def validate_memory_utilization_limits(
    snapshot: dict, used_history: list, baseline: dict | None = None
):
    """
    Syntax : validate_memory_utilization_limits(snapshot, used_history, baseline=None)
    Description : Validates memory thresholds and detects sustained memory growth.
    Parameters :
        snapshot - Current parsed memory data.
        used_history - Previously observed used-memory values.
        baseline - Optional baseline memory snapshot used for comparison.
    Return Value: None. The current test fails when a memory limit is exceeded.
    """
    device = snapshot["device"]
    if snapshot["available_percent"] <= AVAILABLE_MEMORY_PERCENT:
        message = (f"{device}: available memory too low: "
                   f"{snapshot['available_percent']:.1f}%")
        report_logger.print_error(message)
        pytest.fail(message)
    if snapshot["used_percent"] >= MAX_USED_MEMORY_PERCENT:
        message = (f"{device}: used memory too high: "
                   f"{snapshot['used_percent']:.1f}%")
        report_logger.print_error(message)
        pytest.fail(message)
    if baseline:
        increase = snapshot["used_percent"] - baseline["used_percent"]
        if increase > MAX_BASELINE_USED_INCREASE_PERCENT:
            message = (f"{device}: abnormal used-memory increase vs baseline: "
                       f"{increase:.1f} percentage points")
            report_logger.print_error(message)
            pytest.fail(message)

    used_history.append(snapshot["used_mb"])
    recent = used_history[-MONOTONIC_GROWTH_SAMPLES:]
    if (
        len(recent) == MONOTONIC_GROWTH_SAMPLES
        and all(older < newer for older, newer in zip(recent, recent[1:]))
        and recent[-1] - recent[0] >= MIN_MONOTONIC_GROWTH_MB
    ):
        message = (f"{device}: used memory increased monotonically across "
               f"{MONOTONIC_GROWTH_SAMPLES} samples by "
               f"{recent[-1] - recent[0]:.1f} MB: {recent} MB")
        report_logger.print_error(message)
        pytest.fail(message)

def validate_cpu_utilization_limits(
    snapshot: dict,
    high_cpu_counts: dict,
    consecutive_limit: int,
    baseline: dict | None = None,
):
    """
    Syntax : validate_cpu_utilization_limits(snapshot, high_cpu_counts, consecutive_limit, baseline=None)
    Description : Validates CPU thresholds and repeated high-CPU process usage.
    Parameters :
        snapshot - Current parsed CPU data.
        high_cpu_counts - Consecutive high-CPU counters keyed by process.
        consecutive_limit - Number of consecutive samples allowed before failure.
        baseline - Optional baseline CPU snapshot used for comparison.
    Return Value: None. The current test fails when a CPU limit is exceeded.
    """
    device = snapshot["device"]
    idle_percent = snapshot["idle_percent"]
    if idle_percent <= 20 or snapshot["utilization_percent"] >= 80:
        message = (
            f"{device}: CPU limits exceeded: idle={idle_percent:.1f}%, "
            f"utilization={snapshot['utilization_percent']:.1f}%"
        )
        report_logger.print_error(message)
        pytest.fail(message)
    if baseline:
        increase = snapshot["utilization_percent"] - baseline["utilization_percent"]
        if increase > MAX_BASELINE_INCREASE_PERCENT:
            message = (
                f"{device}: abnormal utilization increase vs baseline: "
                f"{increase:.1f} percentage points"
            )
            report_logger.print_error(message)
            pytest.fail(message)

    current_processes = set(snapshot["high_cpu_processes"])
    for process in list(high_cpu_counts):
        if process not in current_processes:
            del high_cpu_counts[process]
    for process in current_processes:
        high_cpu_counts[process] = high_cpu_counts.get(process, 0) + 1
        if high_cpu_counts[process] >= consecutive_limit:
            message = (
                f"{device}: process continuously exceeded 50% CPU: {process} "
                f"({snapshot['high_cpu_processes'][process]:.1f}%)"
            )
            report_logger.print_error(message)
            pytest.fail(message)

def get_scale_setup(zaero_obj, scale: str = None) -> dict:
    """
    Syntax : get_scale_setup(zaero_obj, scale=None)
    Description : Reads the requested or enabled scale settings from platform YAML.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        scale - Optional scale name such as `small`, `medium`, or `large`.
    Return Value: A dictionary containing the selected scale configuration.
    """
    scale_setups = zaero_obj.read_from_database(
        "test_parameters", "scalesetup"
    )
    if not isinstance(scale_setups, dict):
        raise ValueError(
            "Scale setups are missing from test_parameters in platform YAML"
        )
    scale_names = (scale,) if scale else ("small", "medium", "large")
    enabled_setup = None
    for scale_name in scale_names:
        setup = scale_setups.get(scale_name)
        if not isinstance(setup, dict):
            raise ValueError(
                f"Scale setup '{scale_name}' is missing from "
                "test_parameters.scalesetup in platform YAML"
            )
        if scale:
            return setup
        enabled = setup.get("enabled", False)
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() in {"true", "yes", "1", "on"}
        if enabled:
            if enabled_setup is not None:
                raise ValueError("Multiple scale setups are enabled in platform YAML")
            enabled_setup = setup
    if enabled_setup is None:
        raise ValueError("No scale setup is enabled in platform YAML")
    return enabled_setup

def fronthaul_interface(zaero_obj, device: str) -> str:
    """
    Syntax : fronthaul_interface(zaero_obj, device)
    Description : Builds the configured MLD fronthaul interface name.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        device - Name of the target mesh device.
    Return Value: The configured fronthaul interface name.
    """
    mld_ifname = zaero_obj.read_from_database(device, "mld_ifname")
    mld_iface_index = zaero_obj.read_from_database(device, "mld_iface_index")
    if not mld_ifname or mld_iface_index is None:
        raise ValueError(f"Missing MLD interface configuration for {device}")
    return f"{mld_ifname}{mld_iface_index}"

def all_interfaces(zaero_obj, device: str) -> list:
    """
    Syntax : all_interfaces(zaero_obj, device)
    Description : Returns non-MLD wireless interfaces reported by `iw dev`.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        device - Name of the target mesh device.
    Return Value: A list of wireless interface names used for topology checks.
    """
    interfaces = parse_iw_dev_output(
        zaero_obj.get_iw_dev_info(device), "interfaces"
    )
    return [iface for iface in interfaces if not iface.lower().startswith("mld")]

def backhaul_interfaces(zaero_obj, device: str) -> list:
    """
    Syntax : backhaul_interfaces(zaero_obj, device)
    Description : Finds non-MLD wireless interfaces operating in managed mode.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        device - Name of the target mesh device.
    Return Value: A list of managed backhaul interface names.
    """
    output = zaero_obj.get_iw_dev_info(device)
    return [
        interface
        for interface, details in parse_iw_dev_output(output, "interface_records")
        if re.search(
            r"^\s*type\s+managed\s*$",
            details,
            re.MULTILINE | re.IGNORECASE,
        )
        and not interface.lower().startswith("mld")
    ]

def backhaul_state(zaero_obj, device: str, interface: str) -> dict:
    """
    Syntax : backhaul_state(zaero_obj, device, interface)
    Description : Collects link and station metrics for a backhaul interface.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        device - Name of the target mesh device.
        interface - Name of the managed backhaul interface.
    Return Value: A dictionary containing connection, signal, rate, and station data.
    """
    link = zaero_obj.get_iw_dev_link_info(device, interface)
    station = zaero_obj.get_iw_dev_sta_dump(device, interface)
    bssids = parse_link_output(link, "bssid")
    signals = parse_link_output(link, "signal")
    ssids = parse_link_output(link, "ssid")
    state = {
        "device": device,
        "interface": interface,
        "connected": bool(bssids),
        "bssid": bssids[0] if bssids else None,
        "ssid": ssids[0].strip() if ssids else None,
        "rssi_dbm": int(signals[0]) if signals else None,
        "tx_mbps": None,
        "rx_mbps": None,
        "connected_time": None,
    }
    for direction, rate, unit in parse_link_output(link, "rates"):
        state[f"{direction.lower()}_mbps"] = rate_to_mbps(rate, unit)
    records = parse_station_output(station, "records")
    if records:
        connected_times = parse_station_output(records[0][1], "connected_time")
        state["connected_time"] = (
            int(connected_times[0]) if connected_times else None
        )
    return state

def all_stations(zaero_obj, device: str) -> set:
    """
    Syntax : all_stations(zaero_obj, device)
    Description : Collects station MACs across all relevant device interfaces.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        device - Name of the target mesh device.
    Return Value: A set of associated station MAC addresses.
    """
    macs: set = set()
    for iface in all_interfaces(zaero_obj, device):
        try:
            output = zaero_obj.get_iw_dev_sta_dump(device, iface)
            macs.update(parse_station_output(output, "macs"))
        except Exception as err:
            report_logger.print_error(f"station dump failed on {device}/{iface}: {err}")
    return macs

def collect_fronthaul_associations(zaero_obj, devices: list) -> dict:
    """
    Syntax : collect_fronthaul_associations(zaero_obj, devices)
    Description : Collects fronthaul station MACs for each mesh device.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        devices - Names of the mesh devices to inspect.
    Return Value: A mapping of device names to associated station MAC sets.
    """
    associations = {}
    for device in devices:
        interface = fronthaul_interface(zaero_obj, device)
        try:
            output = zaero_obj.get_iw_dev_sta_dump(device, interface)
            associations[device] = set(parse_station_output(output, "macs"))
            report_logger.print_step(
                f"STEP: Observed {device}/{interface} fronthaul client MACs: "
                f"{sorted(associations[device])}"
            )
        except Exception as err:
            report_logger.print_error(
                f"Fronthaul station dump failed on "
                f"{device}/{interface}: {err}"
            )
            associations[device] = set()
    return associations

def total_associations(associations: dict) -> int:
    """
    Syntax : total_associations(associations)
    Description : Counts all associated clients in a topology snapshot.
    Parameters :
        associations - Mapping of device names to station MAC sets.
    Return Value: The total number of associated clients.
    """
    return sum(len(macs) for macs in associations.values())

def compare_associations(baseline: dict, current: dict) -> list:
    """
    Syntax : compare_associations(baseline, current)
    Description : Compares current client associations with a baseline snapshot.
    Parameters :
        baseline - Initial mapping of device names to station MAC sets.
        current - Current mapping of device names to station MAC sets.
    Return Value: A list of client-count and per-device mismatch descriptions.
    """
    mismatches = []
    baseline_total = total_associations(baseline)
    current_total = total_associations(current)
    if current_total != baseline_total:
        mismatches.append(
            f"Total client count changed: baseline={baseline_total} "
            f"current={current_total}"
        )
    for device in sorted(set(baseline) | set(current)):
        baseline_macs = baseline.get(device, set())
        current_macs = current.get(device, set())
        missing_macs = sorted(baseline_macs - current_macs)
        unexpected_macs = sorted(current_macs - baseline_macs)
        if missing_macs or unexpected_macs:
            mismatches.append(
                f"{device} client association mismatch: "
                f"missing={missing_macs}, unexpected={unexpected_macs}"
            )
    return mismatches

def backhaul_active(zaero_obj, device: str) -> bool:
    """
    Syntax : backhaul_active(zaero_obj, device)
    Description : Checks whether any device interface has an associated station.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        device - Name of the target mesh device.
    Return Value: True when at least one station is associated; otherwise False.
    """
    return bool(all_stations(zaero_obj, device))

def capture_topology(zaero_obj, agents: list) -> dict:
    """
    Syntax : capture_topology(zaero_obj, agents)
    Description : Captures controller and agent station topology using `iw` data.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        agents - Names of extender devices included in the topology.
    Return Value: A dictionary containing controller-side agent MACs and agent-side client MACs.
    """
    agent_macs = all_stations(zaero_obj, "controller")

    client_macs = set()
    for agent in agents:
        client_macs.update(all_stations(zaero_obj, agent))

    topology = {"agent_macs": agent_macs, "client_macs": client_macs}
    report_logger.print_step(f"Topology snapshot: agents={topology['agent_macs']}, "
               f"clients={len(topology['client_macs'])}")
    return topology

def compare_agent_presence(expected_count: int, baseline: dict, current: dict) -> list:
    """
    Syntax : compare_agent_presence(expected_count, baseline, current)
    Description : Validates controller-side agent count and presence.
    Parameters :
        expected_count - Required number of connected agents.
        baseline - Initial topology snapshot.
        current - Current topology snapshot.
    Return Value: A list of agent-presence mismatch descriptions.
    """
    mismatches = []
    current_agents = current["agent_macs"]

    if len(current_agents) != expected_count:
        mismatches.append(
            f"Agent count changed: expected={expected_count} "
            f"current={len(current_agents)}"
        )

    missing_agents = baseline["agent_macs"] - current_agents
    if missing_agents:
        mismatches.append(f"Missing agents vs baseline: {missing_agents}")

    return mismatches

def client_host(client: str) -> str:
    """
    Syntax : client_host(client)
    Description : Determines the mesh-device host encoded in a WLAN client name.
    Parameters :
        client - WLAN client name using the `<device>_wlan_client_<number>` format.
    Return Value: The controller or extender name associated with the client.
    """
    match = re.match(r"^(.+)_wlan_client_\d+$", client)
    if not match:
        raise ValueError(f"Cannot determine AP for client '{client}': unexpected naming")
    return match.group(1)

def station_flags(details: str) -> dict:
    """
    Syntax : station_flags(details)
    Description : Extracts authorization and association flags from station details.
    Parameters :
        details - Raw details from one `iw` station record.
    Return Value: A dictionary of boolean authorization, authentication, and association flags.
    """
    return {
        state: bool(
            re.search(
                rf"^\s*{state}:\s*yes\s*$",
                details,
                re.MULTILINE | re.IGNORECASE,
            )
        )
        for state in ("authorized", "authenticated", "associated")
    }

def client_wifi_macs(zaero_obj, client: str) -> set:
    """
    Syntax : client_wifi_macs(zaero_obj, client)
    Description : Finds the MAC addresses of a client's wireless interfaces.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        client - Name of the WLAN client device.
    Return Value: A set of lowercase wireless-interface MAC addresses.
    """
    return {
        mac.lower()
        for mac in parse_iw_dev_output(
            zaero_obj.get_iw_dev_info(client), "macs"
        )
    }

def station_validation_error(state, missing_message: str):
    """
    Syntax : station_validation_error(state, missing_message)
    Description : Validates required station authorization and association flags.
    Parameters :
        state - Station-state dictionary to validate.
        missing_message - Error text returned when station state is unavailable.
    Return Value: An error message, or None when the station state is valid.
    """
    if state is None:
        return missing_message
    if not all(state[field] for field in ("authorized", "authenticated", "associated")):
        return f"invalid station state: {state}"
    return None

def validate_client(zaero_obj, client: str, gateway_ip: str):
    """
    Syntax : validate_client(zaero_obj, client, gateway_ip)
    Description : Validates client association and controller gateway reachability.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        client - Name of the WLAN client device.
        gateway_ip - Controller gateway IP address to validate.
    Return Value: A tuple containing station state and an optional error message.
    """
    interface = zaero_obj.read_from_database(client, "data_iface")
    try:
        bssid = zaero_obj.get_association_status(client, "cli")
    except RuntimeError:
        return None, "client interface is not associated to any BSSID"
    station = {
        "interface": interface,
        "bssid": bssid.lower(),
    }
    if zaero_obj.ping_ipv4(client, gateway_ip, "3") != 0:
        return None, f"cannot reach controller gateway {gateway_ip}"
    return station, None

def rate_to_mbps(rate: str, unit: str) -> float:
    """
    Syntax : rate_to_mbps(rate, unit)
    Description : Converts a parsed `iw` bitrate to megabits per second.
    Parameters :
        rate - Numeric bitrate value returned by the parser.
        unit - Bitrate unit returned by the parser.
    Return Value: The bitrate in Mbps.
    """
    rate = float(rate)
    unit = unit.lower()
    if unit == "gbit/s":
        return rate * 1000
    if unit == "kbit/s":
        return rate / 1000
    return rate

def client_phy_rate(zaero_obj, client: str):
    """
    Syntax : client_phy_rate(zaero_obj, client)
    Description : Reads a client's primary transmit and receive PHY rates.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        client - Name of the configured WLAN client.
    Return Value: A PHY-rate state dictionary, or None when no station matches.
    """
    host = client_host(client)
    client_macs = client_wifi_macs(zaero_obj, client)
    interface = fronthaul_interface(zaero_obj, host)
    output = zaero_obj.get_iw_dev_sta_dump(host, interface)

    for station_mac, details in parse_station_output(output, "records"):
        station_mac = station_mac.lower()
        if station_mac not in client_macs:
            continue
        tx_rates = parse_station_output(details, "tx_rate")
        rx_rates = parse_station_output(details, "rx_rate")
        return {
            "client": client,
            "host": host,
            "interface": interface,
            "mac": station_mac,
            **station_flags(details),
            "tx_mbps": rate_to_mbps(*tx_rates[0]) if tx_rates else None,
            "rx_mbps": rate_to_mbps(*rx_rates[0]) if rx_rates else None,
        }
    return None

def validate_phy_rate(state, baseline=None, drop_percent_limit=50):
    """
    Syntax : validate_phy_rate(state, baseline=None, drop_percent_limit=50)
    Description : Validates station PHY rates and optional baseline degradation.
    Parameters :
        state - Current PHY-rate state dictionary.
        baseline - Optional baseline PHY-rate state.
        drop_percent_limit - Maximum allowed rate reduction percentage.
    Return Value: An error message, or None when the sample is valid.
    """
    error = station_validation_error(
        state, "client MAC is not associated on the configured fronthaul interface"
    )
    if error:
        return error
    if state["tx_mbps"] is None or state["rx_mbps"] is None:
        return f"station record has no TX/RX PHY rate: {state}"
    if baseline is not None:
        for direction in ("tx_mbps", "rx_mbps"):
            baseline_rate = baseline[direction]
            current_rate = state[direction]
            drop_percent = (baseline_rate - current_rate) / baseline_rate * 100
            if drop_percent > drop_percent_limit:
                return (
                    f"{direction[:-5].upper()} PHY rate dropped by "
                    f"{drop_percent:.1f}% from {baseline_rate:.1f} to "
                    f"{current_rate:.1f} Mbps"
                )
    return None

def client_rssi(zaero_obj, client: str):
    """
    Syntax : client_rssi(zaero_obj, client)
    Description : Reads a client's fronthaul RSSI and station state.
    Parameters :
        zaero_obj - Testbed initialization and database interface.
        client - Name of the configured WLAN client.
    Return Value: An RSSI state dictionary, or None when no station matches.
    """
    host = client_host(client)
    interface = fronthaul_interface(zaero_obj, host)
    client_macs = client_wifi_macs(zaero_obj, client)
    output = zaero_obj.get_iw_dev_sta_dump(host, interface)

    for station_mac, details in parse_station_output(output, "records"):
        station_mac = station_mac.lower()
        if station_mac not in client_macs:
            continue
        signals = parse_station_output(details, "signal")
        return {
            "client": client,
            "host": host,
            "interface": interface,
            "mac": station_mac,
            **station_flags(details),
            "rssi_dbm": int(signals[0]) if signals else None,
        }
    return None

def validate_rssi(client_state, previous_rssi=None, max_rssi_degradation_db=10):
    """
    Syntax : validate_rssi(client_state, previous_rssi=None, max_rssi_degradation_db=10)
    Description : Validates station association and RSSI degradation.
    Parameters :
        client_state - Current RSSI state dictionary.
        previous_rssi - Optional baseline or previous RSSI value in dBm.
        max_rssi_degradation_db - Maximum allowed RSSI degradation in dB.
    Return Value: An error message, or None when the sample is valid.
    """
    error = station_validation_error(
        client_state,
        "client MAC is not associated on the configured fronthaul interface",
    )
    if error:
        return error
    if client_state["rssi_dbm"] is None:
        return "station record has no primary signal value"
    if previous_rssi is not None:
        degradation = previous_rssi - client_state["rssi_dbm"]
        if degradation > max_rssi_degradation_db:
            return (
                f"RSSI degraded by {degradation} dB from {previous_rssi} dBm "
                f"to {client_state['rssi_dbm']} dBm"
            )
    return None

