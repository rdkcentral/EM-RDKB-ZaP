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
from rdkbmeshzap.common_utils import device_utils, report_logger

# Polling interval (seconds) between consecutive stability checks.
POLL_INTERVAL_SEC = 600
# Total duration (seconds) for which stability monitoring is performed.
TEST_DURATION_SEC = 3600
# Maximum allowed percentage increase from the baseline metric value.
MAX_BASELINE_INCREASE_PERCENT = 20.0
# Minimum available memory percentage required for a healthy system.
AVAILABLE_MEMORY_PERCENT = 20.0
# Maximum memory utilization percentage allowed during the test.
MAX_USED_MEMORY_PERCENT = 80.0
# Number of consecutive samples required to detect monotonic memory growth.
MONOTONIC_GROWTH_SAMPLES = 3
# Minimum cumulative memory growth (MB) considered significant.
MIN_MONOTONIC_GROWTH_MB = 50.0
# Maximum allowed increase in used memory percentage from baseline.
MAX_BASELINE_USED_INCREASE_PERCENT = 20.0
# Maximum allowed PHY rate degradation relative to baseline (%).
PHY_RATE_DROP_PERCENT = 50
# Maximum allowed RSSI degradation from baseline (dB).
MAX_RSSI_DEGRADATION_DB = 10
# Minimum acceptable RSSI threshold (dBm) for a stable link.
MIN_RSSI_DBM = -80

def validate_memory_utilization_limits(snapshot: dict, used_history: list, baseline: dict | None = None):
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
        report_logger.print_error(f"FAIL: {device}: available memory {snapshot['available_percent']:.1f}% is at or below the {AVAILABLE_MEMORY_PERCENT:.1f}% limit")
    if snapshot["used_percent"] >= MAX_USED_MEMORY_PERCENT:
        report_logger.print_error(f"FAIL: {device}: used memory {snapshot['used_percent']:.1f}% is at or above the {MAX_USED_MEMORY_PERCENT:.1f}% limit")
    if baseline:
        increase = snapshot["used_percent"] - baseline["used_percent"]
        if increase > MAX_BASELINE_USED_INCREASE_PERCENT:
            message = (f"{device}: abnormal used-memory increase vs baseline: {increase:.1f} percentage points")
            raise Exception(message)    
    used_history.append(snapshot["used_mb"])
    recent = used_history[-MONOTONIC_GROWTH_SAMPLES:]
    if (len(recent) == MONOTONIC_GROWTH_SAMPLES
        and all(older < newer for older, newer in zip(recent, recent[1:]))
        and recent[-1] - recent[0] >= MIN_MONOTONIC_GROWTH_MB):
        report_logger.print_error(f"FAIL: {device}: used memory increased by {recent[-1] - recent[0]:.1f} MB across {MONOTONIC_GROWTH_SAMPLES} samples: {recent} MB")

def validate_cpu_utilization_limits(snapshot: dict, high_cpu_counts: dict, consecutive_limit: int, baseline: dict | None = None,):
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
    if idle_percent <= 20:
        report_logger.print_error(f"FAIL: {device}: CPU limit exceeded: idle={idle_percent:.1f}% (minimum 20.0%), utilization={snapshot['utilization_percent']:.1f}%")
    if baseline:
        increase = snapshot["utilization_percent"] - baseline["utilization_percent"]
        if increase > MAX_BASELINE_INCREASE_PERCENT:
            message = (f"{device}: abnormal utilization increase vs baseline: {increase:.1f} percentage points")
            raise Exception(message)                
    current_processes = set(snapshot["high_cpu_processes"])
    for process in list(high_cpu_counts):
        if process not in current_processes:
            del high_cpu_counts[process]
    for process in current_processes:
        high_cpu_counts[process] = high_cpu_counts.get(process, 0) + 1
        if high_cpu_counts[process] >= consecutive_limit:
            report_logger.print_error(f"FAIL: {device}: process exceeded 50% CPU for {high_cpu_counts[process]} consecutive samples: {process} ({snapshot['high_cpu_processes'][process]:.1f}%)")
            continue

def get_enabled_scale_setup(initialize, scale: str | None = None) -> dict:
    """
    Syntax : get_scale_setup(initialize, scale=None)
    Description : Reads the requested or enabled scale settings from platform YAML.
    Parameters :
        initialize - Testbed initialization and database interface.
        scale - Optional scale name such as `small`, `medium`, or `large`.
    Return Value: A dictionary containing the selected scale configuration.
    """
    scale_setups = initialize.read_from_database(
        "test_parameters", "scalesetup")
    if not isinstance(scale_setups, dict):
        raise ValueError("Scale setups are missing from test_parameters in platform YAML")
    if scale:
        setup = scale_setups.get(scale)
        if not isinstance(setup, dict):
            raise ValueError(
                f"Scale setup '{scale}' is missing from test_parameters.scalesetup in platform YAML")
        return setup
    setups = [scale_setups.get(name) for name in ("small", "medium", "large")]
    if not all(isinstance(setup, dict) for setup in setups):
        raise ValueError("One or more scale setups are missing from test_parameters.scalesetup in platform YAML")
    enabled_setups = [setup for setup in setups if setup.get("enabled", False) is True]
    if len(enabled_setups) > 1:
        raise ValueError("Multiple scale setups are enabled in platform YAML")
    if not enabled_setups:
        raise ValueError("No scale setup is enabled in platform YAML")
    return enabled_setups[0]

def get_fronthaul_station_macs_by_device(initialize, devices: list) -> dict:
    """
    Syntax : get_fronthaul_station_macs_by_device(initialize, devices)
    Description : Collects fronthaul station MACs grouped by mesh device.
    Parameters :
        initialize - Testbed initialization and database interface.
        devices - Names of the mesh devices to inspect.
    Return Value: A mapping of device names to associated station MAC sets.
    """
    associations = {}
    for device in devices:
        try:
            interface = device_utils.get_fronthaul_interface(initialize, device)
            station_macs = set(
                initialize.get_iw_station_details(device, interface, "macs"))
            associations[device] = station_macs
            observed = ", ".join(sorted(station_macs))
            observation = observed or "no clients currently connected"
            report_logger.print_info(f"INFO: Stations associated with the fronthaul of {device}: {observation}")
        except Exception as err:
            report_logger.print_error(f"Fronthaul station dump failed on {device}: {err}")
            associations[device] = set()
    return associations

def get_client_association_mismatches(baseline: dict, current: dict) -> list:
    """
    Syntax : get_client_association_mismatches(baseline, current)
    Description : Compares current client associations with a baseline snapshot.
    Parameters :
        baseline - Initial mapping of device names to station MAC sets.
        current - Current mapping of device names to station MAC sets.
    Return Value: A list of client-count and per-device mismatch descriptions.
    """
    mismatches = []
    baseline_total = len(set().union(*baseline.values())) if baseline else 0
    current_total = len(set().union(*current.values())) if current else 0
    if current_total != baseline_total:
        mismatches.append(
            f"Total client count changed: baseline={baseline_total} current={current_total}")
    for device in sorted(set(baseline) | set(current)):
        baseline_macs = baseline.get(device, set())
        current_macs = current.get(device, set())
        missing_macs = sorted(baseline_macs - current_macs)
        if missing_macs:
            mismatches.append(f"{device} client association mismatch")
    return mismatches

def get_extender_presence_snapshot(initialize, agents: list) -> dict:
    """
    Syntax : get_extender_presence_snapshot(initialize, agents)
    Description : Captures extender presence information.
    Parameters :
        initialize - Testbed initialization and database interface.
        agents - Names of extender devices included in the topology.
    Return Value: Dictionary containing the connected agents and agent count.
    """
    connected_agents = set()
    for agent in agents:
        try:
            stored_interface = initialize.read_from_database(
                agent, "backhaul_interface")
            if not stored_interface:
                report_logger.print_error(f"FAIL: {agent}: backhaul_interface is missing from platform.yaml")
                continue
            if initialize.get_wireless_backhaul_connection_status(agent, stored_interface):
                connected_agents.add(agent)
            else:
                report_logger.print_info(
                    f"INFO: {agent}: no active backhaul connection")
        except Exception as err:
            report_logger.print_error(
                f"Backhaul presence check failed on {agent}: {err}")
            continue
    connected_agents = set(connected_agents)
    report_logger.print_info(f"INFO: Connected agents: {sorted(connected_agents)} (count={len(connected_agents)})")
    return {
        "agent_count": len(connected_agents),
        "agents": connected_agents,
    }

def get_extender_presence_mismatches(expected_count: int, baseline: dict, current: dict) -> list:
    """
    Syntax : get_extender_presence_mismatches(expected_count, baseline, current)
    Description : Validates controller-side agent count and presence.
    Parameters :
        expected_count - Required number of connected agents.
        baseline - Initial topology snapshot.
        current - Current topology snapshot.
    Return Value: A list of agent-presence mismatch descriptions.
    """
    mismatches = []
    baseline_agents = set(baseline.get("agents", set()))
    current_agents = set(current.get("agents", set()))
    current_agent_count = len(current_agents)
    if current_agent_count < expected_count:
        mismatches.append(f"Agent count below minimum: expected={expected_count} current={current_agent_count}")
    if current_agent_count != len(baseline_agents):
        mismatches.append(f"Agent count changed: baseline={len(baseline_agents)} current={current_agent_count}")
    missing_agents = baseline_agents - current_agents
    if missing_agents:
        mismatches.append(f"Missing agents: {sorted(missing_agents)}")
    return mismatches

def get_device_advertising_bssid(initialize, bssid: str):
    """
    Syntax : get_device_advertising_bssid(initialize, bssid)
    Description : Identifies the mesh device advertising the specified fronthaul BSSID.
    Parameters :
        initialize - Testbed initialization and database interface.
        bssid - BSSID to locate within the mesh network.
    Return Value: Device name advertising the BSSID, or None if not found.
    """
    connected_bssid = str(bssid or "").strip().lower()
    if not connected_bssid:
        report_logger.print_error(
            "FAIL: Cannot identify the mesh device because the BSSID is empty")
        return None
    if not re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", connected_bssid):
        report_logger.print_error(f"Invalid BSSID format: {bssid}")
        return None
    devices = ["controller", *device_utils.get_enabled_extenders(initialize)]
    for device in devices:
        try:
            bssids = {
                str(device_bssid).strip().lower()
                for device_bssid in initialize.get_fronthaul_bssids(device)
                if device_bssid
            }
        except Exception as err:
            report_logger.print_info(
                f"INFO: Could not read fronthaul BSSIDs from '{device}': {err}")
            continue
        if connected_bssid in bssids:
            return device
    report_logger.print_info(
        f"INFO: No mesh device advertises fronthaul BSSID {connected_bssid}")
    return None

def rate_to_mbps(rate: str | float, unit: str) -> float:
    """
    Syntax : rate_to_mbps(rate, unit)
    Description : Converts a parsed `iw` bitrate to megabits per second.
    Parameters :
        rate - Numeric bitrate value returned by the parser.
        unit - Bitrate unit returned by the parser.
    Return Value: The bitrate in Mbps.
    """
    rate_mbps = float(rate)
    unit = unit.lower()
    if unit == "gbit/s":
        return rate_mbps * 1000
    if unit == "kbit/s":
        return rate_mbps / 1000
    return rate_mbps

def get_client_phy_rates(initialize, client: str, host: str | None) -> dict | None:
    """
    Syntax : get_client_phy_rates(initialize, client, host)
    Description : Reads a client's primary transmit and receive PHY rates.
    Parameters :
        initialize - Testbed initialization and database interface.
        client - Name of the configured WLAN client.
        host - Present mesh device advertising the client's associated BSSID.
    Return Value: A PHY-rate state dictionary, or None when no station matches.
    """
    if host is None:
        return None
    client_mac = initialize.read_from_database(client, "mac").lower()
    interface = device_utils.get_fronthaul_interface(initialize, host)
    for station_mac, _ in initialize.get_iw_station_details(host, interface, "records"):
        station_mac = station_mac.lower()
        if station_mac != client_mac:
            continue
        tx_rates = initialize.get_iw_station_details(host, interface, "tx_rate")
        rx_rates = initialize.get_iw_station_details(host, interface, "rx_rate")
        return {
            "host": host,
            "interface": interface,
            "tx_mbps": rate_to_mbps(*tx_rates[0]) if tx_rates else None,
            "rx_mbps": rate_to_mbps(*rx_rates[0]) if rx_rates else None,
        }
    return None

def validate_client_phy_rates(current_rates: dict | None, baseline_rates: dict | None = None, drop_percent_limit: float = PHY_RATE_DROP_PERCENT,) -> str | None:
    """
    Syntax : validate_client_phy_rates(current_rates, baseline_rates=None, drop_percent_limit=PHY_RATE_DROP_PERCENT)
    Description : Validates PHY rates and optional baseline degradation.
    Parameters :
        current_rates - Current PHY-rate dictionary.
        baseline_rates - Optional baseline PHY-rate dictionary.
        drop_percent_limit - Maximum allowed rate reduction percentage.
    Return Value: An error message, or None when the sample is valid.
    """
    if current_rates is None:
        return "client PHY-rate sample is unavailable"
    if current_rates["tx_mbps"] is None or current_rates["rx_mbps"] is None:
        return f"station record has no TX/RX PHY rate: {current_rates}"
    if baseline_rates is not None:
        for direction in ("tx_mbps", "rx_mbps"):
            baseline_rate = baseline_rates[direction]
            current_rate = current_rates[direction]
            if baseline_rate <= 0:
                continue
            drop_percent = (baseline_rate - current_rate) / baseline_rate * 100
            if drop_percent > drop_percent_limit:
                return (f"{direction[:-5].upper()} PHY rate dropped by {drop_percent:.1f}% from {baseline_rate:.1f} to {current_rate:.1f} Mbps")
    return None

def get_client_rssi(initialize, client: str, host: str | None) -> dict | None:
    """
    Syntax : get_client_rssi(initialize, client, host)
    Description : Reads a client's fronthaul RSSI and station state.
    Parameters :
        initialize - Testbed initialization and database interface.
        client - Name of the configured WLAN client.
        host - Present mesh device advertising the client's associated BSSID.
    Return Value: An RSSI state dictionary, or None when no station matches.
    """
    if host is None:
        return None
    interface = device_utils.get_fronthaul_interface(initialize, host)
    client_mac = initialize.read_from_database(client, "mac").lower()
    for station_mac, details in initialize.get_iw_station_details(
        host, interface, "records"):
        station_mac = station_mac.lower()
        if station_mac != client_mac:
            continue
        signal = re.search(
            r"^\s*signal:\s*(-?\d+)\s*dBm\s*$",
            details,
            re.IGNORECASE | re.MULTILINE)
        return {
            "host": host,
            "interface": interface,
            "rssi_dbm": int(signal.group(1)) if signal else None,
        }
    return None

def validate_client_rssi(current_rssi: dict | None, baseline_rssi: int | None = None, max_rssi_degradation_db: int = MAX_RSSI_DEGRADATION_DB,) -> str | None:
    """
    Syntax : validate_client_rssi(current_rssi, baseline_rssi=None, max_rssi_degradation_db=MAX_RSSI_DEGRADATION_DB)
    Description : Validates RSSI data and degradation.
    Parameters :
        current_rssi - Current RSSI dictionary.
        baseline_rssi - Optional baseline RSSI value in dBm.
        max_rssi_degradation_db - Maximum allowed RSSI degradation in dB.
    Return Value: An error message, or None when the sample is valid.
    """
    if current_rssi is None:
        return "client RSSI sample is unavailable"
    if current_rssi["rssi_dbm"] is None:
        return "station record has no primary signal value"
    if baseline_rssi is not None:
        degradation = baseline_rssi - current_rssi["rssi_dbm"]
        if degradation > max_rssi_degradation_db:
            return (f"RSSI degraded by {degradation} dB from {baseline_rssi} dBm to {current_rssi['rssi_dbm']} dBm")
    return None
