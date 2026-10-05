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
import pytest
from rdkbmeshzap.common_utils import report_logger

def parse_cpu_utilization_output(output: str) -> dict:
    """
    Syntax : parse_cpu_utilization_output(output)
    Description : Parses CPU idle time and processes exceeding the CPU threshold.
    Parameters :
        output - Raw output from the `top` command.
    Return Value: A dictionary containing idle, utilization, and high-CPU process data.
    """
    idle_match = re.search(
        r"(?:%?Cpu\([^)]*\).*?(?P<cpu>[\d.]+)\s*id|"
        r"\b(?P<idle>[\d.]+)%?\s*idle\b)",
        output,
        re.IGNORECASE,
    )
    if not idle_match:
        raise ValueError("Could not find CPU idle percentage in top output")
    idle_percent = float(idle_match.group("cpu") or idle_match.group("idle"))

    lines = output.splitlines()
    cpu_header = next(
        (
            fields
            for line in lines
            if "%CPU" in (fields := [value.upper() for value in line.split()])
        ),
        [],
    )
    high_cpu_processes = {}
    if cpu_header:
        cpu_column = next(
            index for index, value in enumerate(cpu_header)
            if value.upper() == "%CPU"
        )
        for line in lines:
            fields = line.split()
            if len(fields) <= cpu_column or not fields[0].isdigit():
                continue
            cpu_token = fields[cpu_column]
            if not re.fullmatch(r"\d+(?:\.\d+)?%?", cpu_token):
                continue
            cpu_value = float(cpu_token.rstrip("%"))
            if cpu_value > 50:
                process_name = " ".join(fields[cpu_column + 1:])
                high_cpu_processes[
                    f"PID {fields[0]} ({process_name})"
                ] = cpu_value

    return {
        "idle_percent": idle_percent,
        "utilization_percent": 100.0 - idle_percent,
        "high_cpu_processes": high_cpu_processes,
    }

def get_device_cpu_utilization_output(initialize, device: str) -> str:
    """
    Syntax : get_device_cpu_utilization_output(initialize, device)
    Description : Fetches raw CPU utilization output for a device.
    Parameters :
        initialize - Testbed initialization object exposing feature APIs.
        device - Name of the target device.
    Return Value: Raw output from the device CPU utilization command.
    """
    if output := initialize.get_cpu_utilization(device):
        return output
    raise RuntimeError(f"top returned no output on {device}")

def parse_memory_utilization_output(output: str) -> dict:
    """
    Syntax : parse_memory_utilization_output(output)
    Description : Parses memory totals and percentages from `free -m` output.
    Parameters :
        output - Raw output from the `free -m` command.
    Return Value: A dictionary containing total, used, available, and percentage values.
    """
    rows = [line.split() for line in output.splitlines() if line.split()]
    header = next((row for row in rows if row[0].lower() == "total"), None)
    values = next((row[1:] for row in rows if row[0].lower() == "mem:"), None)
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
    available = columns.get(
        "available",
        sum(
            columns.get(name, 0.0)
            for name in ("free", "buffers", "buff/cache", "cached")
        ),
    )
    return {
        "total_mb": total,
        "used_mb": used,
        "available_mb": available,
        "used_percent": used / total * 100.0,
        "available_percent": available / total * 100.0,
    }

def get_device_memory_utilization_output(initialize, device: str) -> str:
    """
    Syntax : get_device_memory_utilization_output(initialize, device)
    Description : Fetches raw memory utilization output for a device.
    Parameters :
        initialize - Testbed initialization object exposing feature APIs.
        device - Name of the target device.
    Return Value: Raw output from the device memory utilization command.
    """
    if output := initialize.get_memory_utilization(device):
        return output
    raise RuntimeError(f"free returned no output on {device}")

def validate_device_accessibility(initialize):
    """
    Validate SSH accessibility for every configured testbed device.
    Parameters: initialize - Testbed initialization and device interface.
    Return Value: A list of devices that failed accessibility validation.
    Example: validate_device_accessibility(initialize)
    """
    devices = initialize.get_testbed_devices()
    failures = []
    report_logger.print_info(
        f"INFO: Validating accessibility of {len(devices)} configured devices"
    )
    for device in devices:
        report_logger.print_info(f"INFO: Connecting to {device}")
        try:
            connected = initialize.connect_with_device(device)
            if connected is False:
                raise RuntimeError("connection API returned False")
        except Exception as error:
            failures.append(device)
            report_logger.print_error(
                f"{device} accessibility validation failed: {error}"
            )
        else:
            report_logger.print_success(
                f"{device} is accessible over SSH"
            )
    return failures

def get_enabled_clients(initialize):
    """
    Syntax: get_enabled_clients(initialize)
    Description: Return enabled client devices from the configured testbed.
    Parameters: initialize - Testbed initialization and database interface.
    Return Value: A list of enabled client device names.
    Example: get_enabled_clients(initialize)
    """
    enabled_clients = []
    for device in initialize.get_testbed_devices():
        if "_wlan_client_" not in device:
            continue
        present = initialize.read_from_database(device, "device_present")
        if present is None or (
            isinstance(present, str)
            and present.strip().lower() in {"true", "yes", "1", "on"}
        ) or (not isinstance(present, str) and bool(present)):
            enabled_clients.append(device)
    return enabled_clients

def normalize_security( value: str) -> str:
    """
    Syntax: normalize_security(value)
    Description: Normalize AKM/key management values from DataElements or wpa_cli
                 into a common security family for comparison.
    Parameters: value - AKM/key management value obtained from DataElements or wpa_cli.
    Return Value: A normalized security family such as WPA2, WPA3,
                  WPA2/WPA3-Transition, or UNKNOWN(value).
    Example: normalize_security("sae")
    """
    value = value.lower()
    wpa3_values = ["sae", "dpp", "dpp+sae", "eap-sha256", "eap-sha384"]
    wpa2_values = ["psk", "wpa2-psk", "eap", "dot1x", "wpa-eap"]
    transition_values = ["psk+sae"]
    if value in wpa3_values:
        return "WPA3"
    elif value in wpa2_values:
        return "WPA2"
    elif value in transition_values:
        return "WPA2/WPA3-Transition"
    else:
        return f"UNKNOWN({value})"   

def get_enabled_extenders(initialize):
    """
    Syntax: get_enabled_extenders(initialize)
    Description: Return enabled extender devices from the configured testbed.
    Parameters: initialize - Testbed initialization and database interface.
    Return Value: A list of enabled extender device names.
    Example: get_enabled_extenders(initialize)
    """
    return [
        device
        for device in initialize.get_testbed_devices()
        if (
            device.startswith("extender")
            and "_client_" not in device
            and initialize.read_from_database(device, "device_present")
        )
    ]

def get_enabled_device_al_macs(initialize):
    """
    Syntax: get_enabled_device_al_macs(initialize)
    Description: Return AL MAC addresses for enabled controller and extender devices.
    Parameters: initialize - Testbed initialization and device database interface.
    Return Value: A device-to-AL-MAC dictionary.
    Example: get_enabled_device_al_macs(initialize)
    """
    devices = [
        device
        for device in initialize.get_testbed_devices()
        if device == "controller"
        or (device.startswith("extender") and "_client_" not in device)
    ]
    devices = [
        device
        for device in devices
        if initialize.read_from_database(device, "device_present")
    ]
    return {
        device: initialize.get_al_mac_address(device, "cli").lower()
        for device in devices
    }

def create_capture_name(prefix, device=None, extension="pcapng"):
    """
    Syntax: create_capture_name(prefix, device=None, extension="pcapng")
    Description: Create a timestamped packet-capture filename.
    Parameters: prefix - Capture name prefix; device - Optional device name; extension - File extension.
    Return Value: A unique capture filename string.
    Example: create_capture_name("recovery", "extender1")
    """
    device_suffix = f"_{device}" if device else ""
    return f"{prefix}{device_suffix}_{time.time_ns()}.{extension}"

def get_backhaul_capture_interface(initialize, device):
    """
    Syntax: get_backhaul_capture_interface(initialize, device)
    Description: Return the backhaul capture interface configured in platform YAML.
    Parameters: initialize - Testbed interface; device - Device name.
    Return Value: The configured interface name.
    Example: get_backhaul_capture_interface(initialize, "extender1")
    """
    capture_interface = initialize.read_from_database(device, "backhaul_capture_iface")
    if not capture_interface:
        pytest.fail(
            f"{device}: backhaul_capture_iface is missing from platform YAML"
        )
    return capture_interface

def start_capture(initialize, device, capture_prefix, step, include_device=False):
    """
    Syntax: start_capture(initialize, device, capture_prefix, step, include_device=False)
    Description: Start an IEEE 1905 capture on a device backhaul interface.
    Parameters: initialize - Testbed interface; device - Device name; capture_prefix - Name prefix;
                step - Report step; include_device - Include device in filename.
    Return Value: The capture filename.
    Example: start_capture(initialize, "extender1", "recovery", 1)
    """
    capture_device = device if include_device else None
    capture_name = create_capture_name(capture_prefix, capture_device)
    capture_interface = get_backhaul_capture_interface(initialize, device)
    capture_filter = initialize.read_from_database(device, "filter_1905")
    report_logger.print_step(
        f"STEP {step}: Start packet capture on {device}"
    )
    initialize.start_frame_capture(
        device, capture_interface, capture_filter, capture_name
    )
    report_logger.print_success(
        f"PASS: Capture started in {device}; capture name: {capture_name}; "
        f"interface: {capture_interface}"
    )
    return capture_name

def stop_and_collect_capture(initialize, device, capture_name):
    """
    Syntax: stop_and_collect_capture(initialize, device, capture_name)
    Description: Stop, download, and remove a device capture.
    Parameters: initialize - Testbed interface; device - Device name; capture_name - Remote capture filename.
    Return Value: The local capture path.
    Example: stop_and_collect_capture(initialize, "extender1", capture_name)
    """
    report_logger.print_step(f"Stop and collect packet capture from {device}")
    initialize.stop_frame_capture(device)
    local_path = initialize.download_captured_pcap(device, capture_name)
    try:
        initialize.delete_captured_pcap(device, capture_name)
    except Exception as error:
        report_logger.print_info(
            f"{device}: capture already unavailable during cleanup: {error}"
        )
    report_logger.print_success(
        f"PASS: Capture stopped and collected successfully for {device}: {local_path}"
    )
    return local_path

def verify_services(initialize, device, service_names, deadline=None):
    """
    Syntax: verify_services(initialize, device, service_names, deadline=None)
    Description: Verify required services with retries bounded by an optional deadline.
    Parameters: initialize - Testbed interface; device - Device name; service_names - Services to verify;
                deadline - Optional monotonic deadline.
    Return Value: None when all services are active; raises pytest failure otherwise.
    Example: verify_services(initialize, "controller", ("onewifi",))
    """
    if not service_names:
        pytest.fail(f"{device}: no services were configured for validation")

    if deadline is None:
        deadline = time.monotonic() + 2
    last_error = None
    attempts = 0
    while time.monotonic() < deadline:
        attempts += 1
        try:
            for service_name in service_names:
                initialize.verify_service_status(device, service_name)
            return
        except Exception as error:
            last_error = error
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(2, remaining))
    if attempts == 0:
        pytest.fail(f"{device}: service validation deadline expired before an attempt")
    pytest.fail(f"{device}: services did not become active after {attempts} attempts: {last_error}")

def verify_controller_services(initialize, deadline=None):
    """
    Syntax: verify_controller_services(initialize, deadline=None)
    Description: Verify controller services after recovery.
    Parameters: initialize - Testbed interface; deadline - Optional monotonic deadline.
    Return Value: None when controller services are active.
    Example: verify_controller_services(initialize)
    """
    verify_services(
        initialize,
        "controller",
        ("onewifi", "ieee1905_em_agent", "ieee1905_em_ctrl", "em_ctrl"),
        deadline,
    )

def verify_extender_services(initialize, extender, deadline=None):
    """
    Syntax: verify_extender_services(initialize, extender, deadline=None)
    Description: Verify extender services after recovery.
    Parameters: initialize - Testbed interface; extender - Extender name; deadline - Optional monotonic deadline.
    Return Value: None when extender services are active.
    Example: verify_extender_services(initialize, "extender1")
    """
    verify_services(
        initialize,
        extender,
        ("onewifi", "ieee1905_em_agent", "em_agent"),
        deadline,
    ) 

def discover_macs(initialize):
    """
    Syntax: discover_macs(initialize)
    Description:
        Discover 2G, 5G, and 6G fronthaul BSSIDs for the controller
        and all enabled extenders.
        Compare every BSSID returned by get_fronthaul_bssids()
        against the MAC addresses of wifi0, wifi1 and wifi2.
        The order of BSSIDs returned by get_fronthaul_bssids()
        is not assumed to match the interface order.
        Store the validated MAC addresses in the database.
    Parameters:
        initialize - Testbed interface used to access devices.
    Return Value:
        None when radio MAC discovery is successful.
    """
    report_logger.print_info("Discovering radio MACs for controller and extenders")
    try:
        # Controller
        devices = ["controller"]
        # Enabled extenders
        devices.extend(get_enabled_extenders(initialize))
        report_logger.print_info(f"Devices found for MAC discovery: {devices}")
        interfaces = ["wifi0", "wifi1", "wifi2"]
        radio_db_keys = {
            "wifi0": "2g_radio_mac",
            "wifi1": "5g_radio_mac",
            "wifi2": "6g_radio_mac"
        }
        for device in devices:
            report_logger.print_info(f"Getting fronthaul BSSIDs for {device}")
            bssids = initialize.get_fronthaul_bssids(device,"cli")
            if len(bssids) < 3:
                raise RuntimeError(f"Expected 3 BSSIDs for {device}, but found {len(bssids)}: {bssids}")
            report_logger.print_info(f"{device} BSSIDs: {bssids}")
            # Normalize BSSIDs
            bssids = [
                mac.strip().lower()
                for mac in bssids]
            interface_macs = {}
            for iface in interfaces:
                iw_output = initialize.get_iw_dev_interface_info(device,iface)
                actual_mac = None
                for line in iw_output.splitlines():
                    line = line.strip()
                    if line.startswith("addr "):
                        actual_mac = line.split()[1].strip().lower()
                        break
                if actual_mac is None:
                    raise RuntimeError(f"Could not find MAC address for {device} interface {iface}")
                interface_macs[iface] = actual_mac
            matched = {}
            for bssid in bssids:
                matching_interface = None
                for iface, interface_mac in interface_macs.items():
                    if bssid == interface_mac:
                        matching_interface = iface
                        break
                if matching_interface is None:
                    raise RuntimeError(f"{device}: BSSID {bssid} was not found in any radio interface. Interface MACs: {interface_macs}")
                matched[matching_interface] = bssid
            if len(matched) != 3:
                raise RuntimeError(f"{device}: Expected 3 unique radio MAC matches, but found {len(matched)}. Matches: {matched}")
            initialize.db_obj.write_into_database(device,"2g_radio_mac",matched["wifi0"])
            initialize.db_obj.write_into_database(device,"5g_radio_mac",matched["wifi1"])
            initialize.db_obj.write_into_database(device,"6g_radio_mac", matched["wifi2"])
            report_logger.print_info(f"{device} 2G MAC: {matched['wifi0']}")
            report_logger.print_info(f"{device} 5G MAC: {matched['wifi1']}")
            report_logger.print_info(f"{device} 6G MAC: {matched['wifi2']}")
    except Exception as e:
        report_logger.print_error(f"Failed to discover radio MACs: {e}")
        pytest.fail(f"Radio MAC discovery failed: {e}") 