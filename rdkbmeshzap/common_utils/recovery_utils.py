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
    Parameters: initialize - Testbed interface; recovery_type - "controller" or "agent".
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

def reconnect_device(initialize, device, step, started_at=None, recovery_type="controller"):
    """
    Syntax: reconnect_device(initialize, device, step, started_at=None, recovery_type="controller")
    Description: Reconnect a device within its configured recovery KPI window.
    Parameters: initialize - Testbed interface; device - Device name; step - Report step;
                started_at - Optional recovery start time; recovery_type - "controller" or "agent".
    Return Value: True on success; False when recovery times out.
    Example: reconnect_device(initialize, "extender1", 1, recovery_type="agent")
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
                    initialize.connect_with_device("controller")
            initialize.close_connection(device)
            initialize.connect_with_device(device)
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

def recover_device(initialize, device, started_at, results, step, recovery_type="controller"):
    """
    Syntax: recover_device(initialize, device, started_at, results, step, recovery_type="controller")
    Description: Reconnect a device, verify services, and record its recovery time.
    Parameters: initialize - Testbed interface; device - Device name; started_at - Recovery start time;
                results - Result dictionary; step - Report step; recovery_type - "controller" or "agent".
    Return Value: Recovery time in seconds, False when recovery fails, or the captured exception.
    Example: recover_device(initialize, "extender1", started_at, results, 1, "agent")
    """
    try:
        reconnected = reconnect_device(
            initialize, device, step=f"{step}.1", started_at=started_at, recovery_type=recovery_type
        )
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
            report_logger.print_error(f"{device}: recovery exceeded {recovery_kpi} seconds")
            return False
        results[device] = recovery_time
        report_logger.print_success(f"PASS: {device} connection restored in {recovery_time:.1f}s")
        return recovery_time
    except Exception as error:
        results[device] = error
        report_logger.print_error(f"{device}: recovery failed with error: {error}")
        return error

def validate_topology_capture(packets, extender, extender_al_mac=None):
    """
    Syntax: validate_topology_capture(packets, extender, extender_al_mac=None)
    Description: Require topology query and response messages in a recovery capture.
    Parameters: packets - Decoded packets; extender - Extender name; extender_al_mac - Optional AL MAC filter.
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
