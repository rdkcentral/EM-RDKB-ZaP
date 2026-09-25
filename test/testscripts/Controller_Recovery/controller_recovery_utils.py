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
import re
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import report_logger
from rdkbmeshzap.common_utils import device_utils

REBOOT_CYCLES = 5
RETRY_INTERVAL_SECONDS = 5

def get_controller_recovery_kpi(initialize):
    """
    Return the controller recovery KPI configured in YAML.
    """
    return int(
        initialize.read_from_database(
            "test_parameters", "controller_recovery_kpi_seconds"
        )
    )

def reconnect_device(initialize, device, step, started_at=None):
    """
    Reconnect a device within the configured recovery KPI window.
    """
    report_logger.print_step(f"STEP {step}: Wait for {device} SSH recovery")
    recovery_kpi = get_controller_recovery_kpi(initialize)
    max_retries = recovery_kpi // RETRY_INTERVAL_SECONDS
    deadline = time.monotonic() + recovery_kpi
    if started_at is not None:
        deadline = started_at + recovery_kpi
    for attempt in range(1, max_retries + 1):
        if time.monotonic() >= deadline:
            break
        initialize.close_connection(device)
        try:
            initialize.connect_with_device(device)
        except Exception as error:
            report_logger.print_info(f"{device} connect attempt {attempt} failed: {error}")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(RETRY_INTERVAL_SECONDS, remaining))
            continue
        if time.monotonic() > deadline:
            break
        report_logger.print_success(f"PASS: {device} connection restored on attempt {attempt}")
        return
    raise RuntimeError(
        f"Could not reconnect {device} within {recovery_kpi} seconds"
    )

def recover_device(initialize, device, started_at, results, step):
    """
    Reconnect a device, verify services, and record recovery time.
    """
    try:
        reconnect_device(initialize, device, step=step, started_at=started_at)
        recovery_kpi = get_controller_recovery_kpi(initialize)
        deadline = started_at + recovery_kpi
        if device == "controller":
            device_utils.verify_controller_services(initialize, deadline)
        else:
            device_utils.verify_extender_services(initialize, device, deadline)
        recovery_time = time.monotonic() - started_at
        if recovery_time >= recovery_kpi:
            raise RuntimeError(
            f"{device}: recovery exceeded {recovery_kpi} seconds"
            )
        results[device] = recovery_time
        report_logger.print_success(f"PASS: {device} connection restored in {recovery_time:.1f}s")
        return recovery_time
    except Exception as error:
        results[device] = error
        return error

def validate_topology_capture(packets, extender, extender_al_mac=None):
    """
    Require topology query and response messages in a recovery capture.
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
            report_logger.print_error(
                f"FAIL: {message_name} was not found in the recovery capture for "
                f"{extender}"
            )
        else:
            report_logger.print_success(
                f"PASS: {message_name} was found in the recovery capture for {extender}"
            )

def get_parent_device_by_backhaul_bssid(initialize, devices, bssid):
    """
    Return the device whose wifi1.1 interface owns the BSSID.
    """
    normalized_bssid = (bssid or "").lower()
    for device in devices:
        try:
            output = initialize.get_iw_dev_interface_info(device, "wifi1.1")
        except Exception:
            continue
        if re.search(
            rf"\baddr\s+{re.escape(normalized_bssid)}\b",
            str(output),
            re.IGNORECASE,
        ):
            return device
    return None

def get_extender_parent(initialize, extender, devices):
    """
    Return the parent device associated with the extender.
    """
    link_output = initialize.get_iw_dev_link_info(extender, "wifi1.3")
    match = re.search(
        r"Connected to\s+([0-9a-fA-F:]{17})", str(link_output), re.IGNORECASE
    )
    if not match:
        return None, None
    bssid = match.group(1).lower()
    return get_parent_device_by_backhaul_bssid(initialize, devices, bssid), bssid
