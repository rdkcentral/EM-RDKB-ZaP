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
import time
import uuid

from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.link_stability_utils import POLL_INTERVAL_SEC, TEST_DURATION_SEC, parse_iperf_throughput

# Time between scale setup stabilization checks.
STABILIZATION_POLL_INTERVAL_SEC = 30
# Time between reboot-transition checks.
REBOOT_TRANSITION_POLL_INTERVAL_SEC = 5
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
# Duration in seconds for each iperf throughput sample.
IPERF_SAMPLE_DURATION_SEC = 10
# Minimum acceptable throughput ratio compared with the baseline.
MIN_THROUGHPUT_RATIO = 0.8
# Remote log path used by the iperf server.
IPERF_SERVER_LOG = "/tmp/scale_client_traffic_server.log"
# Identifier used for the Controller device.
CONTROLLER_DEVICE = "controller"
# Supported SSID and operating-channel configuration parameters.
CONFIGURATION_PARAMETERS = ("ssid", "channel_2_4", "channel_5", "channel_6")
# Maximum time allowed for configuration propagation.
CONFIGURATION_PROPAGATION_TIMEOUT_SEC = 60
# Time between configuration propagation checks.
CONFIGURATION_POLL_INTERVAL_SEC = 5
# Mapping of channel parameters to bands, setters, and candidate channels.
CONFIGURATION_CHANNEL_BANDS = {
    "channel_2_4": (
        "2.4",
        "set_channel_preference_for_2_4_band",
        (1, 6),
    ),
    "channel_5": (
        "5",
        "set_channel_preference_for_5g_band",
        (42, 58, 106),
    ),
    "channel_6": (
        "6",
        "set_channel_preference_for_6g_band",
        (7, 23, 39),
    ),
}

def get_enabled_scale_setup(initialize, scale: str | None = None) -> dict:
    """
    Syntax : get_enabled_scale_setup(initialize, scale=None)
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

def get_extender_presence_snapshot(initialize, agents: list, nonfatal_query_errors: bool = False) -> dict:
    """
    Syntax : get_extender_presence_snapshot(initialize, agents, nonfatal_query_errors=False)
    Description : Captures Controller-side Agent presence and parent relationships.
    Parameters :
        initialize - Testbed initialization and database interface.
        agents - Names of extender devices included in the topology.
        nonfatal_query_errors - Suppress transient query errors until stabilization times out.
    Return Value: Dictionary containing presence, topology, and query error details.
    """
    connected_agents = set()
    parent_by_agent = {}
    query_errors = []
    configuration_errors = []
    topology_devices = [CONTROLLER_DEVICE, *agents]
    for agent in agents:
        try:
            stored_interface = initialize.read_from_database(agent, "backhaul_interface")
            if not stored_interface:
                error = f"{agent}: backhaul_interface is missing from platform.yaml"
                configuration_errors.append(error)
                report_logger.print_error(f"FAIL: {error}")
                continue
            if initialize.get_wireless_backhaul_connection_status(agent, stored_interface):
                connected_agents.add(agent)
                parent, _ = device_utils.get_extender_parent_device(
                    initialize, agent, topology_devices)
                parent_by_agent[agent] = parent
                if parent:
                    report_logger.print_info(f"INFO: {agent} is connected to parent {parent}")
                else:
                    report_logger.print_error(f"FAIL: {agent}: Controller-side parent relationship is unavailable")
            else:
                report_logger.print_info(f"INFO: {agent}: no active backhaul connection")
        except Exception as err:
            error = f"{agent}: backhaul presence check failed: {err}"
            query_errors.append(error)
            if not nonfatal_query_errors:
                report_logger.print_error(f"FAIL: {error}")
            continue
    report_logger.print_info(f"INFO: Connected agents: {sorted(connected_agents)} (count={len(connected_agents)})")
    return {
        "agent_count": len(connected_agents),
        "agents": connected_agents,
        "parent_by_agent": parent_by_agent,
        "query_errors": query_errors,
        "configuration_errors": configuration_errors,
    }

def wait_for_device_reboot(initialize, device: str, deadline: float) -> bool:
    """
    Syntax : wait_for_device_reboot(initialize, device, deadline)
    Description : Waits for device shutdown and a subsequent connection.
    Parameters :
        initialize - Testbed initialization and database interface.
        device - Device being monitored.
        deadline - Monotonic deadline for the transition check.
    Return Value: True when shutdown and reconnection are observed, otherwise False.
    """
    shutdown_observed = False
    while time.monotonic() < deadline:
        try:
            if not initialize.is_device_alive(device):
                shutdown_observed = True
                break
        except Exception as error:
            shutdown_observed = True
            report_logger.print_info(f"INFO: {device} shutdown transition observed: {error}")
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(REBOOT_TRANSITION_POLL_INTERVAL_SEC, remaining))
    if not shutdown_observed:
        report_logger.print_error(f"FAIL: {device}: shutdown transition was not observed before the recovery deadline")
        return False
    while time.monotonic() < deadline:
        try:
            initialize.close_connection(device)
            connected = initialize.connect_with_device(device)
            if connected is False:
                raise RuntimeError("device connection API returned False")
            report_logger.print_info(f"INFO: {device} post-reboot connection was restored")
            return True
        except Exception as error:
            report_logger.print_info(f"INFO: {device} post-reboot connection is waiting: {error}")
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(REBOOT_TRANSITION_POLL_INTERVAL_SEC, remaining))
    report_logger.print_error(f"FAIL: {device}: post-reboot connection was not restored before the recovery deadline")
    return False

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
    baseline_parents = baseline.get("parent_by_agent", {})
    current_parents = current.get("parent_by_agent", {})
    current_agent_count = len(current_agents)
    current_query_errors = current.get("query_errors", [])
    current_configuration_errors = current.get("configuration_errors", [])
    for error in current_configuration_errors:
        mismatches.append(f"Configuration error: {error}")
    for error in current_query_errors:
        mismatches.append(f"Transient presence query error: {error}")
    if current_agent_count < expected_count:
        mismatches.append(f"Agent count below minimum: expected={expected_count} current={current_agent_count}")
    if current_agent_count != len(baseline_agents):
        mismatches.append(f"Agent count changed: baseline={len(baseline_agents)} current={current_agent_count}")
    missing_agents = baseline_agents - current_agents
    if missing_agents:
        mismatches.append(f"Missing agents: {sorted(missing_agents)}")
    for agent in sorted(baseline_agents):
        baseline_parent = baseline_parents.get(agent)
        current_parent = current_parents.get(agent)
        if not baseline_parent:
            mismatches.append(f"Missing baseline parent relationship for {agent}")
        if agent in current_agents and not current_parent:
            mismatches.append(f"Missing Controller-side parent relationship for {agent}")
        elif current_parent != baseline_parent:
            mismatches.append(
                f"Parent relationship changed for {agent}: "
                f"baseline={baseline_parent} current={current_parent}")
    return mismatches

def collect_client_iperf_samples(initialize, client_targets: dict, sample_duration_sec: int) -> dict:
    """
    Syntax : collect_client_iperf_samples(initialize, client_targets, sample_duration_sec)
    Description : Collects parallel iperf3 throughput samples from WLAN clients.
    Parameters :
        initialize - Testbed initialization and database interface.
        client_targets - Mapping of client names to iperf3 destination IP addresses.
        sample_duration_sec - Duration of each iperf3 sample in seconds.
    Return Value: A mapping of clients with successful samples to Mbps throughput.
    """
    results = {}
    for client, target_ip in client_targets.items():
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", client)
        remote_log = (f"/tmp/scale_client_traffic_{safe_name}_{uuid.uuid4().hex}.log")
        connection_obj = None
        try:
            bind_ip = initialize.get_wlan_ip_address(client, "cli")
            if not bind_ip:
                raise ValueError("client has no assigned IPv4 address")
            connection = initialize.read_from_database(client, "connection")
            connection_obj = initialize.get_connection_module_object(connection)
            connection_obj.execute_command(client, f"rm -f {remote_log}")
            initialize.start_iperf_client(client, target_ip, bind_ip, "tcp", remote_log, time=sample_duration_sec)
            output = connection_obj.execute_command(
                client, f"cat {remote_log}", return_stderr=True)
            if isinstance(output, tuple):
                output, error = output
                if error and not output:
                    error_text = str(error).strip() or repr(error)
                    raise ValueError(
                        f"unable to read iperf3 log {remote_log}: {error_text}")
            output_text = str(output)
            if not output_text.strip():
                raise ValueError(
                    f"iperf3 log {remote_log} is empty; the client command "
                    "did not produce throughput output")
            throughput = parse_iperf_throughput(output_text)
            if throughput <= 0:
                raise ValueError(f"iperf3 reported non-positive throughput: {throughput} Mbps")
            results[client] = throughput
        except Exception as error:
            report_logger.print_error(f"{client}: unable to collect iperf3 sample: {error!r}")
        finally:
            if connection_obj is not None:
                try:
                    connection_obj.execute_command(client, f"rm -f {remote_log}")
                except Exception:
                    pass
    return results

def validate_client_associations(initialize, devices: list, clients: list, baseline: dict) -> list:
    """
    Syntax : validate_client_associations(initialize, devices, clients, baseline)
    Description : Validates baseline client associations against current station data.
    Parameters :
        initialize - Testbed initialization and database interface.
        devices - Mesh devices whose fronthaul associations should be checked.
        clients - WLAN clients expected on their owning devices.
        baseline - Baseline station MAC mapping grouped by device.
    Return Value: A list of association mismatch descriptions.
    """
    current = get_fronthaul_station_macs_by_device(initialize, devices)
    mismatches = get_client_association_mismatches(baseline, current)
    for client in clients:
        owner = client.rsplit("_wlan_client_", 1)[0]
        if owner not in devices:
            owner = None
        client_mac = str(initialize.read_from_database(client, "mac")).lower()
        if owner and client_mac not in current.get(owner, set()):
            mismatches.append(
                f"{client}: expected association with {owner} is missing")
    return mismatches

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

def get_scale_configuration_parameter(initialize, device: str, parameter: str):
    """
    Syntax : get_scale_configuration_parameter(initialize, device, parameter)
    Description : Reads a supported SSID or operating-channel configuration parameter.
    Parameters :
        initialize - Testbed initialization and database interface.
        device - Mesh device name, such as `controller` or an extender.
        parameter - Configuration name from CONFIGURATION_PARAMETERS.
    Return Value: The current parameter value.
    """
    if parameter == "ssid":
        ssid = initialize.get_ssid(device, "2g_ssid_index", "cli")
        if ssid is None or not str(ssid).strip():
            raise ValueError(f"Unable to capture a non-empty SSID for {device}")
        return ssid
    if parameter in CONFIGURATION_CHANNEL_BANDS:
        band = CONFIGURATION_CHANNEL_BANDS[parameter][0]
        return initialize.get_operating_channel(device, band)
    raise ValueError(f"Unsupported propagation parameter: {parameter}")

def set_controller_scale_configuration_parameter(initialize, parameter: str, current_value):
    """
    Syntax : set_controller_scale_configuration_parameter(initialize, parameter, current_value)
    Description : Changes a supported Controller SSID or operating channel to the next test value.
    Parameters :
        initialize - Testbed initialization and database interface.
        parameter - Configuration name from CONFIGURATION_PARAMETERS.
        current_value - Current Controller value used to select the next value.
    Return Value: The target value applied to the Controller.
    """
    if parameter == "ssid":
        target_value = initialize.get_random_ssid()
        initialize.set_ssid("controller", "mld_iface_index", target_value, "gui")
        return target_value
    if parameter in CONFIGURATION_CHANNEL_BANDS:
        try:
            current_channel = int(current_value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid current channel for {parameter}: {current_value!r}") from error
        band, setter_name, channel_candidates = CONFIGURATION_CHANNEL_BANDS[parameter]
        if current_channel in channel_candidates:
            current_index = channel_candidates.index(current_channel)
            target_value = channel_candidates[(current_index + 1) % len(channel_candidates)]
        else:
            target_value = channel_candidates[0]
        getattr(initialize, setter_name)("controller",uncheck_channel=current_channel,check_channel=target_value,priority=14,)
        return target_value
    raise ValueError(f"Unsupported propagation parameter: {parameter}")

def get_scale_configuration_mismatches(initialize, agents: list, parameter: str, expected_value):
    """
    Syntax : get_scale_configuration_mismatches(initialize, agents, parameter, expected_value)
    Description : Compares an expected Controller configuration value with all extenders.
    Parameters :
        initialize - Testbed initialization and database interface.
        agents - Extender device names to check.
        parameter - Configuration name from CONFIGURATION_PARAMETERS.
        expected_value - Value expected on every extender.
    Return Value: A tuple containing mismatch descriptions and observed values.
    """
    mismatches = []
    observed = {}
    for agent in agents:
        try:
            if parameter == "ssid":
                initialize.check_ssid(agent, "mld_iface_index", str(expected_value), "cli")
                observed[agent] = expected_value
            else:
                current_value = get_scale_configuration_parameter(initialize, agent, parameter)
                observed[agent] = current_value
                if str(current_value) != str(expected_value):
                    mismatches.append(f"{agent}: expected={expected_value},observed={current_value}")
        except Exception as error:
            failure = f"{agent}: read failed: {error}"
            mismatches.append(failure)
            observed[agent] = failure
    return mismatches, observed

def wait_for_scale_configuration_propagation(initialize, agents: list, parameter: str, expected_value):
    """
    Syntax : wait_for_scale_configuration_propagation(initialize, agents, parameter, expected_value)
    Description : Checks whether a configuration value has propagated to all extenders.
    Parameters :
        initialize - Testbed initialization and database interface.
        agents - Extender device names to check.
        parameter - Configuration name from CONFIGURATION_PARAMETERS.
        expected_value - Value expected on every extender.
    Return Value: A tuple containing the propagation status and observed values.
    """
    deadline = time.monotonic() + CONFIGURATION_PROPAGATION_TIMEOUT_SEC
    observed = {}
    while True:
        mismatches, observed = get_scale_configuration_mismatches(initialize, agents, parameter, expected_value)
        if not mismatches:
            return True, observed
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False, observed
        time.sleep(min(CONFIGURATION_POLL_INTERVAL_SEC, remaining))

def wait_for_controller_scale_configuration_update(initialize, parameter: str, expected_value):
    """
    Syntax : wait_for_controller_scale_configuration_update(initialize, parameter, expected_value)
    Description : Checks whether the Controller reports the requested configuration value.
    Parameters :
        initialize - Testbed initialization and database interface.
        parameter - Configuration name from CONFIGURATION_PARAMETERS.
        expected_value - Value expected on the Controller.
    Return Value: A tuple containing the update status and observed value.
    """
    deadline = time.monotonic() + CONFIGURATION_PROPAGATION_TIMEOUT_SEC
    observed = None
    while True:
        if parameter == "ssid":
            try:
                initialize.check_ssid("controller", "mld_iface_index", str(expected_value), "cli")
                return True, expected_value
            except Exception as error:
                observed = f"SSID check failed: {error}"
        else:
            try:
                observed = get_scale_configuration_parameter(initialize, "controller", parameter)
            except Exception as error:
                observed = f"Channel read failed: {error}"
        if str(observed) == str(expected_value):
            return True, observed
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False, observed
        time.sleep(min(CONFIGURATION_POLL_INTERVAL_SEC, remaining))

def restore_controller_scale_configuration_parameter(initialize, parameter: str, original_value):
    """
    Syntax : restore_controller_scale_configuration_parameter(initialize, parameter, original_value)
    Description : Restores a Controller SSID or operating channel to its original value.
    Parameters :
        initialize - Testbed initialization and database interface.
        parameter - Configuration name from CONFIGURATION_PARAMETERS.
        original_value - Original value to restore.
    Return Value: None.
    """
    if parameter == "ssid":
        initialize.set_ssid("controller", "mld_iface_index", original_value, "gui")
        return
    try:
        current_value = get_scale_configuration_parameter(initialize, "controller", parameter)
    except Exception as error:
        report_logger.print_error(f"Unable to read current {parameter} before restoration: {error}")
        return
    if str(current_value) == str(original_value):
        return
    if parameter in CONFIGURATION_CHANNEL_BANDS:
        band, setter_name = (
            CONFIGURATION_CHANNEL_BANDS[parameter][0],
            CONFIGURATION_CHANNEL_BANDS[parameter][1],)
        getattr(initialize, setter_name)("controller",uncheck_channel=current_value,check_channel=original_value,priority=14,)