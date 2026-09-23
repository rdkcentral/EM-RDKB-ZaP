"""Common helper utilities for Zaero-based tests."""

import re
import pytest
from rdkbmeshzap.bridge.feature_interface import FeatureInterface
from rdkbmeshzap.common_utils import report_logger


CPU_IDLE_PATTERNS = (
    re.compile(r"(?:%Cpu\([^)]*\)|Cpu\([^)]*\)).*?([\d.]+)\s*id", re.IGNORECASE),
    re.compile(r"\b([\d.]+)%?\s*idle\b", re.IGNORECASE),
)
CPU_TOKEN = re.compile(r"^\d+(?:\.\d+)?%?$")
MAX_BASELINE_INCREASE_PERCENT = 20.0
AVAILABLE_MEMORY_PERCENT = 20.0
MAX_USED_MEMORY_PERCENT = 80.0
MONOTONIC_GROWTH_SAMPLES = 3
MIN_MONOTONIC_GROWTH_MB = 50.0
MAX_BASELINE_USED_INCREASE_PERCENT = 20.0
STATION_MAC_PATTERN = re.compile(
    r"^Station\s+([0-9a-f:]{17})", re.MULTILINE | re.IGNORECASE
)
STATION_RECORD_PATTERN = re.compile(
    r"^Station\s+(?P<mac>[0-9a-f:]{17})\b(?P<details>.*?)(?=^Station |\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
LINK_BSSID_PATTERN = re.compile(
    r"^\s*Connected\s+to\s+([0-9a-f:]{17})", re.MULTILINE | re.IGNORECASE
)
LINK_SSID_PATTERN = re.compile(
    r"^\s*SSID:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE
)
LINK_SIGNAL_PATTERN = re.compile(
    r"^\s*signal:\s*(-?\d+)\s*dBm", re.MULTILINE | re.IGNORECASE
)
LINK_RATE_PATTERN = re.compile(
    r"^\s*(tx|rx) bitrate:\s*([\d.]+)\s+([MGK]Bit/s)",
    re.MULTILINE | re.IGNORECASE,
)


# Syntax : parse_cpu_top(output: str) -> dict
# Description : Parse CPU idle time and processes exceeding the CPU threshold.
# Parameters : output - raw `top` command output.
# Return Value : Dictionary containing idle, utilization, and high-CPU process data.
def parse_cpu_top(output: str) -> dict:
    """Return idle percentage and processes exceeding the per-process limit."""
    idle_percent = None
    for pattern in CPU_IDLE_PATTERNS:
        match = pattern.search(output)
        if match:
            idle_percent = float(match.group(1))
            break

    if idle_percent is None:
        raise ValueError("Could not find CPU idle percentage in top output")

    cpu_header = next(
        (line for line in output.splitlines() if "%CPU" in line.upper()), None
    )
    high_cpu_processes = {}
    if cpu_header:
        cpu_column = next(
            (index for index, value in enumerate(cpu_header.split())
             if value.upper() == "%CPU"),
            None,
        )
        if cpu_column is not None:
            for line in output.splitlines():
                fields = line.split()
                if len(fields) <= cpu_column or not fields[0].isdigit():
                    continue
                cpu_value = fields[cpu_column].rstrip("%")
                if not CPU_TOKEN.match(fields[cpu_column]):
                    continue
                if float(cpu_value) > 50:
                    process_name = " ".join(fields[cpu_column + 1:])
                    high_cpu_processes[
                        f"PID {fields[0]} ({process_name})"
                    ] = float(cpu_value)

    return {
        "idle_percent": idle_percent,
        "utilization_percent": 100.0 - idle_percent,
        "high_cpu_processes": high_cpu_processes,
    }


# Syntax : collect_cpu(zaero_obj, device: str) -> dict
# Description : Fetch and parse one CPU utilization snapshot for a device.
# Parameters : zaero_obj - Zaero object; device - target device name.
# Return Value : Parsed CPU snapshot with the device name.
def collect_cpu(zaero_obj, device: str) -> dict:
    """Collect one non-interactive CPU snapshot from a device."""
    output = FeatureInterface().get_cpu_utilization(device)
    if not output:
        raise RuntimeError(f"top returned no output on {device}")
    snapshot = parse_cpu_top(output)
    snapshot["device"] = device
    return snapshot


# Syntax : parse_free(output: str) -> dict
# Description : Parse memory totals and percentages from `free -m` output.
# Parameters : output - raw `free -m` command output.
# Return Value : Dictionary containing total, used, available, and percentage values.
def parse_free(output: str) -> dict:
    """Parse `free -m` output into memory totals and percentages."""
    header = values = None
    for line in output.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0].lower() == "total":
            header = fields
        elif fields[0].lower() == "mem:" and header:
            values = fields[1:]
            break
    if not header or not values or len(values) < len(header):
        raise ValueError("Could not find a complete Mem row in free output")

    columns = {
        name.lower().rstrip(":"): float(value)
        for name, value in zip(header, values)
    }
    total = columns.get("total")
    used = columns.get("used")
    if total is None or used is None or total <= 0:
        raise ValueError("free output does not contain valid total and used values")
    available = columns.get("available")
    if available is None:
        available = sum(
            columns.get(name, 0.0) for name in ("free", "buffers", "buff/cache", "cached")
        )
    return {
        "total_mb": total,
        "used_mb": used,
        "available_mb": available,
        "used_percent": used / total * 100.0,
        "available_percent": available / total * 100.0,
    }


# Syntax : collect_memory(zaero_obj, device: str) -> dict
# Description : Fetch and parse one memory utilization snapshot for a device.
# Parameters : zaero_obj - Zaero object; device - target device name.
# Return Value : Parsed memory snapshot with the device name.
def collect_memory(zaero_obj, device: str) -> dict:
    """Collect one memory snapshot through the CLI feature interface."""
    output = FeatureInterface().get_memory_utilization(device)
    if not output:
        raise RuntimeError(f"free returned no output on {device}")
    snapshot = parse_free(output)
    snapshot["device"] = device
    return snapshot


# Syntax : assert_memory_limits(snapshot: dict, used_history: list, baseline: dict | None = None) -> None
# Description : Validate memory thresholds and detect sustained memory growth.
# Parameters : snapshot - current memory data; used_history - prior used-memory values; baseline - optional baseline data.
# Return Value : None; fails the test when a memory limit is exceeded.
def assert_memory_limits(snapshot: dict, used_history: list,
                         baseline: dict | None = None):
    """Enforce memory thresholds and detect sustained used-memory growth."""
    device = snapshot["device"]
    if snapshot["available_percent"] <= AVAILABLE_MEMORY_PERCENT:
        message = (f"{device}: available memory too low: "
                   f"{snapshot['available_percent']:.1f}%")
        print_error(message)
        pytest.fail(message)
    if snapshot["used_percent"] >= MAX_USED_MEMORY_PERCENT:
        message = (f"{device}: used memory too high: "
                   f"{snapshot['used_percent']:.1f}%")
        print_error(message)
        pytest.fail(message)
    if baseline:
        increase = snapshot["used_percent"] - baseline["used_percent"]
        if increase > MAX_BASELINE_USED_INCREASE_PERCENT:
            message = (f"{device}: abnormal used-memory increase vs baseline: "
                       f"{increase:.1f} percentage points")
            print_error(message)
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
        print_error(message)
        pytest.fail(message)


# Syntax : assert_cpu_limits(snapshot: dict, high_cpu_counts: dict, consecutive_limit: int, baseline: dict | None = None) -> None
# Description : Validate CPU thresholds and repeated high-CPU process usage.
# Parameters : snapshot - current CPU data; high_cpu_counts - process counters; consecutive_limit - failure threshold; baseline - optional baseline data.
# Return Value : None; fails the test when a CPU limit is exceeded.
def assert_cpu_limits(snapshot: dict, high_cpu_counts: dict,
                      consecutive_limit: int, baseline: dict | None = None):
    """Enforce idle/utilization limits and repeated high-CPU process usage."""
    device = snapshot["device"]
    idle_percent = snapshot["idle_percent"]
    if idle_percent <= 20 or snapshot["utilization_percent"] >= 80:
        message = (
            f"{device}: CPU limits exceeded: idle={idle_percent:.1f}%, "
            f"utilization={snapshot['utilization_percent']:.1f}%"
        )
        print_error(message)
        pytest.fail(message)
    if baseline:
        increase = snapshot["utilization_percent"] - baseline["utilization_percent"]
        if increase > MAX_BASELINE_INCREASE_PERCENT:
            message = (
                f"{device}: abnormal utilization increase vs baseline: "
                f"{increase:.1f} percentage points"
            )
            print_error(message)
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
            print_error(message)
            pytest.fail(message)


# Syntax : get_iw_dev_info(zaero_obj, device: str, method: str = "cli") -> str
# Description : Fetch `iw dev` output for a device.
# Parameters : zaero_obj - Zaero object; device - target device; method - feature-interface method.
# Return Value : Raw command output as a string.
def get_iw_dev_info(zaero_obj, device: str, method: str = "cli") -> str:
    """Run `iw dev` using the feature interface."""
    return FeatureInterface().get_iw_dev_info(device, method)


# Syntax : get_iw_dev_sta_dump(zaero_obj, device: str, iface: str, method: str = "cli") -> str
# Description : Fetch `iw dev <iface> station dump` output.
# Parameters : zaero_obj - Zaero object; device - target device; iface - interface; method - feature-interface method.
# Return Value : Raw command output as a string.
def get_iw_dev_sta_dump(
    zaero_obj, device: str, iface: str, method: str = "cli"
) -> str:
    """Run `iw dev <iface> station dump` using the feature interface."""
    return FeatureInterface().get_iw_dev_sta_dump(device, iface, method)


# Syntax : get_iw_dev_link_info(zaero_obj, device: str, iface: str, method: str = "cli") -> str
# Description : Fetch `iw dev <iface> link` output.
# Parameters : zaero_obj - Zaero object; device - target device; iface - interface name; method - feature-interface method.
# Return Value : Raw link output as a string.
def get_iw_dev_link_info(
    zaero_obj, device: str, iface: str, method: str = "cli"
) -> str:
    """Run `iw dev <iface> link` using the CLI feature interface."""
    return FeatureInterface().get_iw_dev_link_info(device, iface, method)


# Syntax : execute_on_device(zaero_obj, device: str, command: str)
# Description : Execute a command after selecting the device connection.
# Parameters : zaero_obj - Zaero object; device - target device; command - shell command.
# Return Value : Command output and standard-error result from the connection module.
def execute_on_device(zaero_obj, device: str, command: str):
    """Run a command on a device after selecting its configured connection."""
    connection = zaero_obj.read_from_database(device, "connection")
    connection_obj = zaero_obj.get_connection_module_object(connection)
    connection_obj.switch_connection(device)
    return connection_obj.execute_command(command, return_stderr=True)


# Syntax : print_step(message: str)
# Description : Print and log a test step message.
# Parameters : message - step text.
# Return Value : Result returned by the report logger.
def print_step(message: str):
    """Print and log a step so pytest-html captures it in test details."""
    return report_logger.print_step(message)


# Syntax : print_test(message: str)
# Description : Print and log a test boundary message.
def print_test(message: str):
    """Print and log a test name for the pytest-html report."""
    return report_logger.print_test(message)


# Syntax : print_info(message: str)
# Description : Print and log an informational test message.
def print_info(message: str):
    """Print and log informational text for the pytest-html report."""
    return report_logger.print_info(message)


# Syntax : print_success(message: str)
# Description : Print and log a successful test message.
# Parameters : message - success text.
# Return Value : Result returned by the Zaero success logger.
def print_success(message: str):
    """Print and log a passing check for the pytest-html report."""
    report_message = f"PASS: {message}"
    return report_logger.print_success(report_message)


# Syntax : print_error(message: str)
# Description : Print and log a failed test message.
# Parameters : message - error text.
# Return Value : Result returned by the Zaero error logger.
def print_error(message: str):
    """Print and log a failing check for the pytest-html report."""
    report_message = f"FAIL: {message}"
    return report_logger.print_error(report_message)


# Syntax : device_present(zaero_obj, device: str) -> bool
# Description : Check whether a device is configured as present.
# Parameters : zaero_obj - Zaero object; device - device name.
# Return Value : True when the device is present or no setting is defined.
def device_present(zaero_obj, device: str) -> bool:
    """Return True unless the database explicitly marks a device absent."""
    value = zaero_obj.read_from_database(device, "device_present")
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "on"}
    return bool(value)


# Syntax : fronthaul_interface(zaero_obj, device: str) -> str
# Description : Build the configured MLD fronthaul interface name.
# Parameters : zaero_obj - Zaero object; device - device name.
# Return Value : Fronthaul interface name.
def fronthaul_interface(zaero_obj, device: str) -> str:
    """Return the configured MLD fronthaul interface for a device."""
    mld_ifname = zaero_obj.read_from_database(device, "mld_ifname")
    mld_iface_index = zaero_obj.read_from_database(device, "mld_iface_index")
    if not mld_ifname or mld_iface_index is None:
        raise ValueError(f"Missing MLD interface configuration for {device}")
    return f"{mld_ifname}{mld_iface_index}"


# Syntax : all_interfaces(zaero_obj, device: str) -> list
# Description : Return non-MLD wireless interfaces reported by `iw dev`.
# Parameters : zaero_obj - Zaero object; device - device name.
# Return Value : List of wireless interface names.
def all_interfaces(zaero_obj, device: str) -> list:
    """Return Wi-Fi interfaces used for agent/backhaul topology checks.

    Ignore MLD interfaces because they are fronthaul-only and are validated by the
    dedicated fronthaul client tests, not by agent/backhaul scale checks.
    """
    interfaces = re.findall(
        r"^\s*Interface\s+(\S+)", get_iw_dev_info(zaero_obj, device), re.MULTILINE
    )
    return [iface for iface in interfaces if not iface.lower().startswith("mld")]


# Syntax : backhaul_interfaces(zaero_obj, device: str) -> list
# Description : Find non-MLD wireless interfaces operating in managed mode.
# Parameters : zaero_obj - Zaero object; device - device name.
# Return Value : List of backhaul interface names.
def backhaul_interfaces(zaero_obj, device: str) -> list:
    """Return non-MLD wireless interfaces operating in managed mode."""
    output, _ = execute_on_device(zaero_obj, device, "iw dev")
    blocks = re.split(r"(?=^\s*Interface\s+)", output, flags=re.MULTILINE)
    return [
        match.group(1)
        for block in blocks
        if re.search(r"^\s*type\s+managed\s*$", block, re.MULTILINE | re.IGNORECASE)
        and (match := re.search(r"^\s*Interface\s+(\S+)", block, re.MULTILINE))
        and not match.group(1).lower().startswith("mld")
    ]


# Syntax : backhaul_state(zaero_obj, device: str, interface: str) -> dict
# Description : Collect link and station metrics for a backhaul interface.
# Parameters : zaero_obj - Zaero object; device - device name; interface - interface name.
# Return Value : Dictionary containing connection, signal, rate, and station data.
def backhaul_state(zaero_obj, device: str, interface: str) -> dict:
    """Return link and station metrics for one managed backhaul interface."""
    link = get_iw_dev_link_info(zaero_obj, device, interface)
    station = get_iw_dev_sta_dump(zaero_obj, device, interface)
    bssid_match = LINK_BSSID_PATTERN.search(link)
    signal_match = LINK_SIGNAL_PATTERN.search(link)
    ssid_match = LINK_SSID_PATTERN.search(link)
    state = {
        "device": device,
        "interface": interface,
        "connected": bssid_match is not None,
        "bssid": bssid_match.group(1) if bssid_match else None,
        "ssid": ssid_match.group(1).strip() if ssid_match else None,
        "rssi_dbm": signal_match.group(1) if signal_match else None,
        "tx_mbps": None,
        "rx_mbps": None,
        "connected_time": None,
    }
    for direction, rate, unit in LINK_RATE_PATTERN.findall(link):
        state[f"{direction.lower()}_mbps"] = rate_to_mbps(
            re.match(r"(?P<rate>[\d.]+)\s+(?P<unit>[MGK]Bit/s)", f"{rate} {unit}")
        )
    record = next(iter(STATION_RECORD_PATTERN.finditer(station)), None)
    if record:
        match = re.search(r"^\s*connected time:\s*(\d+) seconds", record.group("details"), re.MULTILINE)
        state["connected_time"] = int(match.group(1)) if match else None
    if state["rssi_dbm"] is not None:
        state["rssi_dbm"] = int(state["rssi_dbm"])
    return state


# Syntax : station_macs(output: str) -> set
# Description : Extract station MAC addresses from an `iw` station dump.
# Parameters : output - raw station-dump output.
# Return Value : Set of station MAC addresses.
def station_macs(output: str) -> set:
    """Extract associated station MACs from an iw station dump."""
    return set(STATION_MAC_PATTERN.findall(output))


# Syntax : all_stations(zaero_obj, device: str) -> set
# Description : Collect station MACs across all relevant device interfaces.
# Parameters : zaero_obj - Zaero object; device - device name.
# Return Value : Set of associated station MAC addresses.
def all_stations(zaero_obj, device: str) -> set:
    """Run station dump on every relevant interface and union the MACs."""
    macs: set = set()
    for iface in all_interfaces(zaero_obj, device):
        try:
            output = get_iw_dev_sta_dump(zaero_obj, device, iface)
            macs.update(station_macs(output))
        except Exception as err:
            print_error(f"station dump failed on {device}/{iface}: {err}")
    return macs


# Syntax : collect_fronthaul_associations(zaero_obj, devices: list) -> dict
# Description : Collect fronthaul station MACs for each device.
# Parameters : zaero_obj - Zaero object; devices - device names to inspect.
# Return Value : Mapping of device names to station MAC sets.
def collect_fronthaul_associations(zaero_obj, devices: list) -> dict:
    """Collect client MACs from the fronthaul interface on each device."""
    associations = {}
    for device in devices:
        interface = fronthaul_interface(zaero_obj, device)
        try:
            output = get_iw_dev_sta_dump(zaero_obj, device, interface)
            associations[device] = station_macs(output)
            print_step(
                f"Observed {device} fronthaul clients: "
                f"{sorted(associations[device])}"
            )
        except Exception as err:
            print_error(
                f"Fronthaul station dump failed on "
                f"{device}/{interface}: {err}"
            )
            associations[device] = set()
    return associations


# Syntax : total_associations(associations: dict) -> int
# Description : Count all associated clients in a topology snapshot.
# Parameters : associations - mapping of devices to station MAC sets.
# Return Value : Total number of associated clients.
def total_associations(associations: dict) -> int:
    """Return the total number of associated clients in a topology snapshot."""
    return sum(len(macs) for macs in associations.values())


# Syntax : compare_associations(baseline: dict, current: dict, expected_count: int = None) -> list
# Description : Compare station associations with a baseline and expected total.
# Parameters : baseline - initial associations; current - current associations; expected_count - optional required total.
# Return Value : List of association mismatch descriptions.
def compare_associations(
    baseline: dict, current: dict, expected_count: int = None
) -> list:
    """Return association and optional expected-count differences."""
    mismatches = []
    for device, baseline_macs in baseline.items():
        missing = baseline_macs - current.get(device, set())
        if missing:
            mismatches.append(f"{device}: clients absent vs baseline {missing}")

    baseline_total = total_associations(baseline)
    current_total = total_associations(current)
    required_total = expected_count if expected_count is not None else baseline_total
    if current_total != required_total:
        mismatches.append(
            f"Total client count changed: expected={required_total} "
            f"current={current_total}"
        )
    return mismatches


# Syntax : backhaul_active(zaero_obj, device: str) -> bool
# Description : Check whether any device interface has an associated station.
# Parameters : zaero_obj - Zaero object; device - device name.
# Return Value : True when at least one station is associated.
def backhaul_active(zaero_obj, device: str) -> bool:
    """Backhaul is considered active if any interface from `iw dev` has a station."""
    return bool(all_stations(zaero_obj, device))


# Syntax : capture_topology(zaero_obj, agents: list) -> dict
# Description : Capture controller and agent station topology.
# Parameters : zaero_obj - Zaero object; agents - agent device names.
# Return Value : Dictionary containing agent and client MAC sets.
def capture_topology(zaero_obj, agents: list) -> dict:
    """
    Capture topology snapshot purely via iw commands, scanning every interface
    reported by `iw dev` (not just the config-indexed fronthaul/backhaul ones):
    - agent_macs: stations seen across all of the Controller's interfaces
    - client_macs: stations seen across all of each Agent's interfaces
    """
    agent_macs = all_stations(zaero_obj, "controller")

    client_macs = set()
    for agent in agents:
        client_macs.update(all_stations(zaero_obj, agent))

    topology = {"agent_macs": agent_macs, "client_macs": client_macs}
    print_step(f"Topology snapshot: agents={topology['agent_macs']}, "
               f"clients={len(topology['client_macs'])}")
    return topology


# Syntax : compare_topologies(baseline: dict, current: dict) -> list
# Description : Compare current topology against a baseline topology.
# Parameters : baseline - initial topology; current - current topology.
# Return Value : List of topology mismatch descriptions.
def compare_topologies(baseline: dict, current: dict) -> list:
    """Return a list of mismatch descriptions; empty list means topologies match."""
    mismatches = []

    missing_agents = baseline["agent_macs"] - current["agent_macs"]
    if missing_agents:
        mismatches.append(f"Missing agents vs baseline: {missing_agents}")

    missing_clients = baseline["client_macs"] - current["client_macs"]
    if missing_clients:
        mismatches.append(f"Missing clients vs baseline: {missing_clients}")

    return mismatches


# Syntax : compare_agent_presence(expected_count: int, baseline: dict, current: dict) -> list
# Description : Validate controller-side agent count and presence.
# Parameters : expected_count - required agent count; baseline - initial topology; current - current topology.
# Return Value : List of agent-presence mismatch descriptions.
def compare_agent_presence(expected_count: int, baseline: dict, current: dict) -> list:
    """Return mismatches for the expected controller-side agent topology."""
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


# Syntax : client_host(client: str) -> str
# Description : Determine the access-point host for a configured WLAN client.
# Parameters : client - WLAN client configuration name.
# Return Value : Access-point host name.
def client_host(client: str) -> str:
    """Return the AP device a `*_wlan_client_N` config entry is associated with,
    e.g. 'extender1_wlan_client_1' -> 'extender1', 'controller_wlan_client_1' -> 'controller'."""
    match = re.match(r"^(.+)_wlan_client_\d+$", client)
    if not match:
        raise ValueError(f"Cannot determine AP for client '{client}': unexpected naming")
    return match.group(1)


# Syntax : client_mac(zaero_obj, client: str) -> str
# Description : Read and normalize a client's configured MAC address.
# Parameters : zaero_obj - Zaero object; client - client configuration name.
# Return Value : Lowercase client MAC address.
def client_mac(zaero_obj, client: str) -> str:
    """Return the configured MAC address of a wlan client from the database."""
    mac = zaero_obj.read_from_database(client, "mac")
    if not mac:
        raise ValueError(f"No 'mac' configured for client '{client}'")
    return mac.lower()


# Syntax : fronthaul_client_connected(zaero_obj, client: str) -> bool
# Description : Check whether a client is associated on its fronthaul interfaces.
# Parameters : zaero_obj - Zaero object; client - client configuration name.
# Return Value : True when the client's MAC is associated.
def fronthaul_client_connected(zaero_obj, client: str) -> bool:
    """Return True if the client's MAC is associated on its AP's fronthaul interfaces."""
    host = client_host(client)
    mac = client_mac(zaero_obj, client)
    print_step(f"Checking client '{client}' (MAC {mac}) on host '{host}'")
    return mac in {station.lower() for station in all_stations(zaero_obj, host)}


# Syntax : fronthaul_interfaces(zaero_obj, host: str) -> list
# Description : Return the configured fronthaul interfaces for a host.
# Parameters : zaero_obj - Zaero object; host - access-point host name.
# Return Value : List containing the host's fronthaul interface.
def fronthaul_interfaces(zaero_obj, host: str) -> list:
    """Return the configured fronthaul interfaces for an AP host."""
    return [fronthaul_interface(zaero_obj, host)]


# Syntax : execute_on_host(zaero_obj, host: str, command: str)
# Description : Execute a command after selecting the host connection.
# Parameters : zaero_obj - Zaero object; host - target host; command - shell command.
# Return Value : Command output and standard-error result.
def execute_on_host(zaero_obj, host: str, command: str):
    """Run a command after selecting the configured connection for the host."""
    return execute_on_device(zaero_obj, host, command)


# Syntax : station_flags(details: str) -> dict
# Description : Extract authorization and association flags from station details.
# Parameters : details - station record details.
# Return Value : Dictionary of boolean station-state flags.
def station_flags(details: str) -> dict:
    """Return the common authorization state fields from a station record."""
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


# Syntax : matching_station_records(output: str, client_macs: set)
# Description : Iterate over station records matching client MAC addresses.
# Parameters : output - station-dump output; client_macs - MAC addresses to match.
# Return Value : Iterator of matching MAC and station-detail pairs.
def matching_station_records(output: str, client_macs: set):
    """Yield station records whose MAC belongs to the client."""
    for record in STATION_RECORD_PATTERN.finditer(output):
        station_mac = record.group("mac").lower()
        if station_mac in client_macs:
            yield station_mac, record.group("details")


# Syntax : client_wifi_macs(zaero_obj, client: str) -> set
# Description : Find the MAC addresses of a client's wireless interfaces.
# Parameters : zaero_obj - Zaero object; client - client host name.
# Return Value : Set of lowercase wireless MAC addresses.
def client_wifi_macs(zaero_obj, client: str) -> set:
    """Return the MAC addresses of the client's own wireless interfaces."""
    output, _ = execute_on_host(zaero_obj, client, "iw dev")
    return {mac.lower() for mac in re.findall(
        r"^\s*addr\s+([0-9a-f:]{17})", output, re.MULTILINE | re.IGNORECASE
    )}


# Syntax : client_station_info(zaero_obj, client: str)
# Description : Find the client's matching fronthaul station record.
# Parameters : zaero_obj - Zaero object; client - client configuration name.
# Return Value : Station-state dictionary, or None when no record matches.
def client_station_info(zaero_obj, client: str):
    """Return the fronthaul station record for a configured client, if present."""
    host = client_host(client)
    macs = client_wifi_macs(zaero_obj, client)
    print_step(f"Host: {host}")
    print_step(f"Client '{client}' wireless MACs: {sorted(macs)}")
    for interface in fronthaul_interfaces(zaero_obj, host):
        output = get_iw_dev_sta_dump(zaero_obj, host, interface)
        print_step(f"Station dump for '{host}/{interface}':\n{output}")
        for station_mac, details in matching_station_records(output, macs):
            connected_time = re.search(r"^\s*connected time:\s*(\d+) seconds", details, re.MULTILINE)
            return {
                "host": host,
                "interface": interface,
                "mac": station_mac,
                **station_flags(details),
                "connected_time": int(connected_time.group(1)) if connected_time else None,
            }
    return None


# Syntax : client_reachable(zaero_obj, client: str, gateway_ip: str) -> bool
# Description : Check whether a client can reach the controller gateway.
# Parameters : zaero_obj - Zaero object; client - client host name; gateway_ip - gateway address.
# Return Value : True when all ping packets reach the gateway.
def client_reachable(zaero_obj, client: str, gateway_ip: str) -> bool:
    """Return whether the client can reach the controller gateway."""
    output, _ = execute_on_host(
        zaero_obj, client, f"ping -c 3 -W 2 {gateway_ip}"
    )
    loss = re.search(r"(\d+)% packet loss", output)
    return loss is not None and int(loss.group(1)) == 0


# Syntax : station_validation_error(state, missing_message: str)
# Description : Validate required station authorization and association flags.
# Parameters : state - station-state dictionary; missing_message - message for missing state.
# Return Value : Error message, or None when the state is valid.
def station_validation_error(state, missing_message: str):
    """Return a common station-state error, or None when the state is valid."""
    if state is None:
        return missing_message
    if not all(state[field] for field in ("authorized", "authenticated", "associated")):
        return f"invalid station state: {state}"
    return None


# Syntax : validate_client(zaero_obj, client: str, gateway_ip: str, previous_connected_time=None)
# Description : Validate station state, session continuity, and gateway reachability.
# Parameters : zaero_obj - Zaero object; client - client name; gateway_ip - gateway address; previous_connected_time - prior session time.
# Return Value : Tuple containing station state and an error message.
def validate_client(zaero_obj, client: str, gateway_ip: str, previous_connected_time=None):
    """Validate fronthaul state, session continuity, and gateway reachability."""
    station = client_station_info(zaero_obj, client)
    error = station_validation_error(
        station,
        f"none of the client's wireless MACs are associated on the "
        f"fronthaul interface of '{client_host(client)}'",
    )
    if error:
        return None, error
    if station["connected_time"] is None:
        return None, "station record has no connected time"
    if previous_connected_time is not None and station["connected_time"] < previous_connected_time:
        return None, (
            f"connected time reset from {previous_connected_time}s "
            f"to {station['connected_time']}s"
        )
    if not client_reachable(zaero_obj, client, gateway_ip):
        return None, f"cannot reach controller gateway {gateway_ip}"
    return station, None


# Syntax : rate_to_mbps(match)
# Description : Convert a bitrate match to megabits per second.
# Parameters : match - regular-expression bitrate match or None.
# Return Value : Bitrate in Mbps, or None when no match exists.
def rate_to_mbps(match):
    """Convert an iw bitrate match to Mbps."""
    if match is None:
        return None
    rate = float(match.group("rate"))
    unit = match.group("unit").lower()
    if unit == "gbit/s":
        return rate * 1000
    if unit == "kbit/s":
        return rate / 1000
    return rate


# Syntax : client_phy_rate(zaero_obj, client: str)
# Description : Read the client's primary TX and RX PHY rates.
# Parameters : zaero_obj - Zaero object; client - client configuration name.
# Return Value : PHY-rate dictionary, or None when no station matches.
def client_phy_rate(zaero_obj, client: str):
    """Return the primary station TX/RX PHY rates for a configured client."""
    host = client_host(client)
    client_macs = client_wifi_macs(zaero_obj, client)
    interface = fronthaul_interface(zaero_obj, host)
    output, stderr = execute_on_host(
        zaero_obj, host, f"iw dev {interface} station dump"
    )
    if not output and stderr:
        raise RuntimeError(f"{host}: station dump failed on {interface}: {stderr}")

    for station_mac, details in matching_station_records(output, client_macs):
        tx_match = re.search(
            r"^\s*tx bitrate:\s*(?P<rate>[\d.]+)\s+(?P<unit>[MGK]Bit/s)",
            details,
            re.MULTILINE | re.IGNORECASE,
        )
        rx_match = re.search(
            r"^\s*rx bitrate:\s*(?P<rate>[\d.]+)\s+(?P<unit>[MGK]Bit/s)",
            details,
            re.MULTILINE | re.IGNORECASE,
        )
        return {
            "client": client,
            "host": host,
            "interface": interface,
            "mac": station_mac,
            **station_flags(details),
            "tx_mbps": rate_to_mbps(tx_match),
            "rx_mbps": rate_to_mbps(rx_match),
        }
    return None


# Syntax : validate_phy_rate(state, baseline=None, drop_percent_limit=50)
# Description : Validate station PHY rates and optional baseline degradation.
# Parameters : state - current PHY-rate state; baseline - optional baseline; drop_percent_limit - allowed drop percentage.
# Return Value : Error message, or None when the sample is valid.
def validate_phy_rate(state, baseline=None, drop_percent_limit=50):
    """Return a PHY-rate validation error, or None for a healthy sample."""
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


# Syntax : client_rssi(zaero_obj, client: str)
# Description : Read the client's fronthaul RSSI and station state.
# Parameters : zaero_obj - Zaero object; client - client configuration name.
# Return Value : RSSI state dictionary, or None when no station matches.
def client_rssi(zaero_obj, client: str):
    """Return the client's configured fronthaul RSSI and association state."""
    host = client_host(client)
    interface = fronthaul_interface(zaero_obj, host)
    client_macs = client_wifi_macs(zaero_obj, client)
    output = get_iw_dev_sta_dump(zaero_obj, host, interface)

    for station_mac, details in matching_station_records(output, client_macs):
        signal_match = re.search(
            r"^\s*signal:\s*(-?\d+)\s*dBm\s*$",
            details,
            re.MULTILINE | re.IGNORECASE,
        )
        return {
            "client": client,
            "host": host,
            "interface": interface,
            "mac": station_mac,
            **station_flags(details),
            "rssi_dbm": int(signal_match.group(1)) if signal_match else None,
        }
    return None


# Syntax : validate_rssi(client_state, previous_rssi=None, max_rssi_degradation_db=10)
# Description : Validate station association and RSSI degradation.
# Parameters : client_state - current RSSI state; previous_rssi - prior RSSI; max_rssi_degradation_db - allowed degradation.
# Return Value : Error message, or None when the sample is valid.
def validate_rssi(client_state, previous_rssi=None, max_rssi_degradation_db=10):
    """Return an RSSI validation error, or None when the sample is healthy."""
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

