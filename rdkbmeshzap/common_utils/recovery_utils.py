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

import time
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import device_utils, report_logger

# Number of consecutive reboot cycles to perform.
REBOOT_CYCLES = 5

# Interval in seconds between retry attempts.
RETRY_INTERVAL_SECONDS = 5

def get_recovery_kpi(initialize, recovery_type="controller"):
    """
    Syntax: get_recovery_kpi(initialize, recovery_type="controller")
    Description: Return the configured recovery KPI for the selected recovery type.
    Parameters:
        initialize : Testbed interface.
        recovery_type : "controller" or "agent".
    Return Value: Recovery KPI in seconds as an integer.
    Example: get_recovery_kpi(initialize, "agent")
    """
    parameter = {
        "agent": "agent_recovery_kpi_seconds",
        "controller": "controller_recovery_kpi_seconds",
    }.get(recovery_type)
    if parameter is None:
        raise ValueError(f"Unsupported recovery type: {recovery_type}")
    return int(initialize.read_from_database("test_parameters", parameter))

def print_recovery_summary(extenders, recovered_extenders, step="STEP 3", scope="after reboot", failed_cycles=None):
    """
    Syntax: print_recovery_summary(extenders, recovered_extenders, step="STEP 3", scope="after reboot", failed_cycles=None)
    Description: Print the final recovery status for each configured Extender.
    Parameters:
        extenders : Configured Extender names.
        recovered_extenders : Extenders that met the recovery criteria.
        step : Report step label.
        scope : Recovery period description.
        failed_cycles : Optional mapping of Extender names to their first failed cycle.
    Return Value: None.
    Example: print_recovery_summary(extenders, recovered_extenders, scope="across 2 reboot cycles")
    """
    report_logger.print_step(f"{step}: Final Extender recovery summary")
    for extender in extenders:
        if extender in recovered_extenders:
            report_logger.print_success(f"PASS: {extender} was reachable and met the recovery KPI {scope}")
        else:
            failure_cycle = (failed_cycles or {}).get(extender)
            if failure_cycle is not None:
                report_logger.print_error(f"FAIL: {extender} did not meet the recovery criteria in cycle {failure_cycle}")
            else:
                report_logger.print_error(f"FAIL: {extender} did not meet the recovery criteria {scope}")

def reconnect_device(initialize, device, started_at=None, recovery_type="controller"):
    """
    Syntax: reconnect_device(initialize, device, started_at=None, recovery_type="controller")
    Description: Reconnect a device within its configured recovery KPI window.
    Parameters:
        initialize : Testbed interface.
        device : Device name.
        started_at : Optional recovery start time.
        recovery_type : "controller" or "agent".
    Return Value: True on success; False when recovery times out.
    Example: reconnect_device(initialize, "extender1", recovery_type="agent")
    """
    report_logger.print_info(f"INFO: Waiting for {device} SSH recovery")
    recovery_kpi = get_recovery_kpi(initialize, recovery_type)
    max_retries = recovery_kpi // RETRY_INTERVAL_SECONDS
    # Use the shared recovery start time when one was provided by the caller.
    deadline = time.monotonic() + recovery_kpi
    if started_at is not None:
        deadline = started_at + recovery_kpi
    for attempt in range(1, max_retries + 1):
        if time.monotonic() >= deadline:
            break
        try:
            if recovery_type == "agent":
                # Restore controller connectivity before reconnecting an agent.
                if not initialize.is_device_alive("controller"):
                    initialize.close_connection("controller")
                    controller_connected = initialize.connect_with_device("controller")
                    if controller_connected is False:
                        raise RuntimeError("controller connection API returned False")
            initialize.close_connection(device)
            device_connected = initialize.connect_with_device(device)
            if device_connected is False:
                raise RuntimeError("device connection API returned False")
        except Exception as error:
            # Retry device connection until the recovery deadline expires.
            report_logger.print_info(f"INFO: {device} connect attempt {attempt} failed: {error}")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(RETRY_INTERVAL_SECONDS, remaining))
            continue
        if time.monotonic() >= deadline:
            break
        report_logger.print_success(f"PASS: {device} connection restored on attempt {attempt}")
        return True
    report_logger.print_error(f"FAIL: {device}: could not reconnect within {recovery_kpi} seconds")
    return False

def recover_device(initialize, device, started_at, results, recovery_type="controller"):
    """
    Syntax: recover_device(initialize, device, started_at, results, recovery_type="controller")
    Description: Reconnect a device, verify services, and record its recovery time.
    Parameters:
        initialize : Testbed interface.
        device : Device name.
        started_at : Recovery start time.
        results : Result dictionary.
        recovery_type : "controller" or "agent".
    Return Value: Recovery time in seconds, False when recovery fails, or the captured exception.
    Example: recover_device(initialize, "extender1", started_at, results, "agent")
    """
    try:
        reconnected = reconnect_device(initialize, device, started_at=started_at, recovery_type=recovery_type)
        if reconnected is False:
            results[device] = False
            return False
        recovery_kpi = get_recovery_kpi(initialize, recovery_type)
        deadline = started_at + recovery_kpi
        report_logger.print_info(f"INFO: Verify services on {device}")
        if device == "controller":
            services_active = device_utils.verify_controller_services(initialize, deadline)
        else:
            services_active = device_utils.verify_extender_services(initialize, device, deadline)
        if not services_active:
            results[device] = False
            return False
        recovery_time = time.monotonic() - started_at
        if recovery_time >= recovery_kpi:
            results[device] = False
            report_logger.print_error(f"FAIL: {device}: recovery exceeded {recovery_kpi} seconds")
            return False
        results[device] = recovery_time
        report_logger.print_success(f"PASS: {device} connection restored in {recovery_time:.1f}s")
        return recovery_time
    except Exception as error:
        results[device] = error
        report_logger.print_error(f"FAIL: {device}: recovery failed with error: {error}")
        return error

def validate_topology_capture(packets, extender, extender_al_mac=None):
    """
    Syntax: validate_topology_capture(packets, extender, extender_al_mac=None)
    Description: Require topology query and response messages in a recovery capture.
    Parameters:
        packets : Decoded packets.
        extender : Extender name.
        extender_al_mac : Optional AL MAC filter.
    Return Value: None; reports missing or present topology messages.
    Example: validate_topology_capture(packets, "extender1")
    """
    for message_type, message_name in (
        (MSG_TYPE_AP_TOPOLOGY_QUERY, "Topology Query"),
        (MSG_TYPE_AP_TOPOLOGY_RESPONSE, "Topology Response"),
    ):
        if extender_al_mac:
            present = check_message_presence(
                packets, message_type, src_mac=extender_al_mac
            ) or check_message_presence(packets, message_type, dst_mac=extender_al_mac)
        else:
            present = check_message_presence(packets, message_type) or []
        if not present:
            report_logger.print_error(f"FAIL: {message_name} was not found in the recovery capture for {extender}")
        else:
            report_logger.print_success(f"PASS: {message_name} was found in the recovery capture for {extender}")

def monitor_device_reachability(initialize, device, stop_event, interval_seconds=5, status_context="during recovery", poll_failure_event=None):
    """
    Syntax: monitor_device_reachability(initialize, device, stop_event, interval_seconds=5, status_context="during recovery")
    Description: Poll reachability until stopped, logging each result and signaling failures.
    Parameters:
        initialize : Testbed interface.
        device : Device name.
        stop_event : Event used to stop the monitor.
        interval_seconds : Seconds between checks.
        status_context : Text describing the activity during monitoring.
        poll_failure_event : Optional Event set when a reachability poll fails.
    Return Value: None; sets poll_failure_event when a poll fails.
    Example: monitor_device_reachability(initialize, "extender1", stop_event)
    """
    poll_count = 0
    while not stop_event.wait(interval_seconds):
        poll_count += 1
        try:
            if not initialize.is_device_alive(device):
                failure = "not reachable"
            else:
                report_logger.print_info(f"INFO: Poll #{poll_count} {device} reachable ({status_context})")
                continue
        except Exception as error:
            failure = f"reachability check failed: {error}"
        report_logger.print_error(f"FAIL: Poll #{poll_count} {device} {failure} ({status_context})")
        if poll_failure_event is not None:
            poll_failure_event.set()
