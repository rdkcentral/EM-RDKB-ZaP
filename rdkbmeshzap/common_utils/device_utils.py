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
from functools import wraps
import pytest
from rdkbmeshzap.common_utils import report_logger
from zaero.utils import zi_logger

def suppress_zaero_logs(function):
    """
    Syntax : suppress_zaero_logs(function)
    Description : Disables Zaero logging while the decorated function runs.
    Parameters :
        function - Function to run without Zaero log output.
    Return Value: The wrapped function with Zaero logging suppressed during execution.
    """
    @wraps(function)
    def wrapped(*args, **kwargs):
        previous_log_state = zi_logger.enable_log
        zi_logger.set_log_state(False)
        try:
            return function(*args, **kwargs)
        finally:
            zi_logger.set_log_state(previous_log_state)
    return wrapped

def get_device_cpu_utilization(initialize, device: str) -> dict:
    """
    Syntax : get_device_cpu_utilization(initialize, device)
    Description : Fetches and parses CPU utilization for a device.
    Parameters :
        initialize - Testbed initialization object exposing feature APIs.
        device - Name of the target device.
    Return Value: A dictionary containing idle, utilization, and high-CPU process data.
    """
    output = initialize.get_cpu_utilization(device)
    if output is None or not str(output).strip():
        raise RuntimeError(f"top returned no output on {device}")
    lines = [line.strip() for line in str(output).splitlines() if line.strip()]
    idle_match = re.search(
        r"(?:%?Cpu\([^)]*\).*?(?P<cpu>[\d.]+)\s*id|"
        r"\b(?P<idle>[\d.]+)%?\s*idle\b)",
        " ".join(lines),
        re.IGNORECASE,)
    if not idle_match:
        raise ValueError("Could not find CPU idle percentage in top output")
    idle_percent = float(idle_match.group("cpu") or idle_match.group("idle"))
    if not 0 <= idle_percent <= 100:
        raise ValueError(f"CPU idle percentage is outside 0-100: {idle_percent}")
    cpu_header = []
    for line in lines:
        fields = line.upper().split()
        if "%CPU" in fields:
            cpu_header = fields
            break
    high_cpu_processes = {}
    if cpu_header:
        cpu_column = cpu_header.index("%CPU")
        for line in lines:
            fields = line.split()
            if len(fields) <= cpu_column or not fields[0].isdigit():
                continue
            cpu_token = fields[cpu_column]
            if not re.fullmatch(r"\d+(?:\.\d+)?%?", cpu_token):
                continue
            cpu_value = float(cpu_token.rstrip("%"))
            if cpu_value <= 50:
                continue
            process_name = " ".join(fields[cpu_column + 1:]) or "unknown"
            high_cpu_processes[f"PID {fields[0]} ({process_name})"] = cpu_value
    return {
        "device": device,
        "idle_percent": idle_percent,
        "utilization_percent": 100.0 - idle_percent,
        "high_cpu_processes": high_cpu_processes,
    }

def get_device_memory_utilization(initialize, device: str) -> dict:
    """
    Syntax : get_device_memory_utilization(initialize, device)
    Description : Fetches and parses memory utilization for a device.
    Parameters :
        initialize - Testbed initialization object exposing feature APIs.
        device - Name of the target device.
    Return Value: A dictionary containing total, used, available, and percentage values.
    """
    output = initialize.get_memory_utilization(device)
    if output is None or not str(output).strip():
        raise RuntimeError(f"free returned no output on {device}")
    lines = [line.strip() for line in str(output).splitlines() if line.strip()]
    rows = [line.split() for line in lines]
    header = next((row for row in rows if row[0].lower() == "total"), None)
    values = next((row[1:] for row in rows if row[0].lower() == "mem:"), None)
    if not header or not values or len(values) < len(header):
        raise ValueError("Could not find a complete Mem row in free output")
    columns = {
        name.lower().rstrip(":"): float(value)
        for name, value in zip(header, values)}
    total = columns.get("total")
    used = columns.get("used")
    if total is None or used is None or total <= 0:
        raise ValueError("free output does not contain valid total and used values")
    available = columns.get("available", sum(columns.get(name, 0.0)for name in ("free", "buffers", "buff/cache", "cached")),)
    return {
        "device": device,
        "total_mb": total,
        "used_mb": used,
        "available_mb": available,
        "used_percent": used / total * 100.0,
        "available_percent": available / total * 100.0,
    }

def get_enabled_clients(initialize):
    """
    Syntax: get_enabled_clients(initialize)
    Description: Return enabled client devices from the configured testbed.
    Parameters: initialize - Testbed initialization and database interface.
    Return Value: A list of enabled client device names.
    Example: get_enabled_clients(initialize)
    """
    return [
        device
        for device in initialize.get_testbed_devices()
        if "_wlan_client_" in device
    ]

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
    initialize.stop_frame_capture(device)
    local_path = initialize.download_captured_pcap(device, capture_name)
    try:
        initialize.delete_captured_pcap(device, capture_name)
    except Exception as error:
        report_logger.print_info(f"INFO: {device}: capture file was already removed from the device, skipping cleanup: {error}")
    report_logger.print_success(
        f"PASS: Packet capture stopped on {device} and saved to: {local_path}"
    )
    return local_path

def verify_services(initialize, device, service_names, deadline=None):
    """
    Syntax: verify_services(initialize, device, service_names, deadline=None)
    Description: Verify required services with retries bounded by an optional deadline.
    Parameters: initialize - Testbed interface; device - Device name; service_names - Services to verify;
                deadline - Optional monotonic deadline.
    Return Value: True when all services are active, otherwise False after logging the error.
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
            return True
        except Exception as error:
            last_error = error
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(2, remaining))
    services = ", ".join(service_names)
    if attempts == 0:
        report_logger.print_error(f"FAIL: Could not check services on {device} ({services}): the time limit expired before the first attempt")
    else:
        report_logger.print_error(f"FAIL: Services on {device} are not active after {attempts} attempt(s). Services checked: {services}. Last error: {last_error}")
    return False

def verify_controller_services(initialize, deadline=None):
    """
    Syntax: verify_controller_services(initialize, deadline=None)
    Description: Verify controller services after recovery.
    Parameters: initialize - Testbed interface; deadline - Optional monotonic deadline.
    Return Value: None when controller services are active.
    Example: verify_controller_services(initialize)
    """
    return verify_services(
        initialize,
        "controller",
        ("onewifi", "ieee1905_em_agent", "ieee1905_em_ctrl", "em_ctrl", "em_agent"),
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
    return verify_services(
        initialize,
        extender,
        ("onewifi", "ieee1905_em_agent", "em_agent"),
        deadline,
    ) 

def get_extender_parent_device(initialize, extender, devices, iw_dev_snapshot=None):
    """
    Syntax: get_extender_parent_device(initialize, extender, devices)
    Description: Find the device hosting the mesh-backhaul AP connected to the extender.
    Parameters: initialize - Testbed interface; extender - Extender name; devices - Candidate parent devices.
    Return Value: A tuple containing the parent device name and connected BSSID, or None values when unavailable.
    Example: get_extender_parent_device(initialize, "extender1", ["controller", "extender1"])
    """
    try:
        backhaul_interface = initialize.read_from_database(extender, "backhaul_interface")
    except Exception as error:
        report_logger.print_error(f"FAIL: {extender}: unable to read backhaul_interface: {error}")
        return None, None
    if not backhaul_interface:
        return None, None
    try:
        bssids = initialize.get_iw_link_details(extender, backhaul_interface, "bssid")
    except Exception as error:
        report_logger.print_error(f"FAIL: {extender}: unable to read backhaul BSSID on {backhaul_interface}: {error}")
        return None, None
    if not bssids:
        return None, None
    bssid = str(bssids[0]).lower()
    mesh_backhaul_ssid = initialize.read_from_database("controller", "mesh_backhaul_ssid").strip()

    for device in devices:
        try:
            interface_details = (
                iw_dev_snapshot.get(device, {})
                if iw_dev_snapshot is not None
                else parse_iw_dev_output(initialize.get_iw_dev_info(device))
            )
        except Exception as error:
            report_logger.print_info(f"INFO: {device}: unable to read wireless interfaces: {error}")
            continue
        if any(
            details["addr"] == bssid
            and details["ssid"] == mesh_backhaul_ssid
            and details["type"].lower() == "ap"
            for details in interface_details.values()
        ):
            return device, bssid
    return None, bssid

def get_fronthaul_interface(initialize, device: str) -> str:
    """
    Syntax : get_fronthaul_interface(initialize, device)
    Description : Builds the configured MLD fronthaul interface name.
    Parameters :
        initialize - Testbed initialization and database interface.
        device - Name of the target mesh device.
    Return Value: The configured fronthaul interface name.
    """
    mld_ifname = initialize.read_from_database(device, "mld_ifname")
    mld_iface_index = initialize.read_from_database(device, "mld_iface_index")
    if not mld_ifname or mld_iface_index is None:
        raise ValueError(f"Missing MLD interface configuration for {device}")
    return f"{mld_ifname}{mld_iface_index}"

def retrieve_and_store_device_index(initialize, device, device_mac):
    """
    Syntax: retrieve_and_store_device_index(initialize, device, device_mac)
    Description: Retrieve the device index for a given device and its MAC address, and store it in the database.
    Parameters: initialize - Testbed interface; device - Device name; device_mac - Device MAC address.
    Return Value: The retrieved device index.
    Example: retrieve_and_store_device_index(initialize, "controller", "00:11:22:33:44:55")
    """
    index = initialize.get_device_index("controller", device_mac, "de")
    initialize.db_obj.write_into_database("controller", f"{device}_device_index",index)
    return index

def parse_iw_dev_output(output: str) -> dict[str, dict[str, str]]:
    """
    Syntax: parse_iw_dev_output(output)
    Description: Parse ``iw dev`` output into interface address, SSID, and type details.
    Parameters: output - Raw output from the ``iw dev`` command.
    Return Value: A dictionary keyed by interface name, with address, SSID, and type fields.
    Example: parse_iw_dev_output(iw_dev_output)
    """
    interfaces = {}
    current_interface = None
    for line in str(output or "").splitlines():
        line = line.strip()
        if line.startswith("Interface "):
            fields = line.split(maxsplit=1)
            if len(fields) != 2:
                current_interface = None
                continue
            current_interface = fields[1]
            interfaces[current_interface] = {"addr": "", "ssid": "", "type": ""}
        elif current_interface and " " in line:
            key, value = line.split(maxsplit=1)
            if key in {"addr", "ssid", "type"}:
                interfaces[current_interface][key] = (
                    value.strip().lower() if key == "addr" else value.strip()
                )
    return interfaces

def retrieve_and_store_radio_index(initialize, device, band, radio_mac):
    """
    Syntax: retrieve_and_store_radio_index(initialize, device, band, radio_mac)
    Description: Retrieve the radio index using its MAC address and store it in the corresponding database field.
    Parameters:
        initialize - Initialization object used to access radio index and database utilities.
        device - Device name for which the radio index is retrieved.
        band - Radio frequency band (2G, 5G, or 6G).
        radio_mac - MAC address of the radio.
    Return Value: The retrieved radio index.
    Example: retrieve_and_store_radio_index(initialize, "controller", "2g", radio_mac)
    """
    index = initialize.get_radio_index("controller", radio_mac, "de")
    initialize.db_obj.write_into_database("controller", f"{device}_{band}_radio_index", index)
    return index

def retrieve_and_store_bss_index(initialize, device, band, bss_mac):
    """
    Syntax: retrieve_and_store_bss_index(initialize, device, band, bss_mac)
    Description: Retrieve the BSS index using its MAC address and store it in the corresponding database field.
    Parameters:
        initialize - Initialization object used to access BSS index and database utilities.
        device - Device name for which the BSS index is retrieved.
        band - Radio frequency band (2G, 5G, or 6G).
        bss_mac - MAC address of the BSS.
    Return Value: The retrieved BSS index.
    Example: retrieve_and_store_bss_index(initialize, "controller", "2g", bss_mac)
    """
    index = initialize.get_bss_index("controller", bss_mac, "de")
    initialize.db_obj.write_into_database("controller", f"{device}_{band}_radio_bss_index", index)
    return index

def retrieve_and_store_all_indexes(initialize):
    """
    Syntax: retrieve_and_store_all_indexes(initialize)
    Description: Retrieve and store device, radio, and BSS indexes for the controller and all enabled extenders.
    Parameters:
        initialize - Initialization object used to access device information and database utilities.
    Return Value: True if all available device, radio, and BSS indexes are retrieved and stored successfully; otherwise, False.
    Example: retrieve_and_store_all_indexes(initialize)
    """
    all_passed = True
    devices = ["controller"] + get_enabled_extenders(initialize)
    # Retrieve and store device indexes
    for device in devices:
        try:
            device_mac = initialize.read_from_database(device, "2g_radio_mac")
            if not device_mac:
                report_logger.print_error(f"FAIL: 2.4 GHz radio MAC not found for {device}")
                all_passed = False
                continue
            device_index = retrieve_and_store_device_index(initialize, device, device_mac)
            if device_index is None:
                report_logger.print_error(f"FAIL: Device index not found for {device}")
                all_passed = False
            else:
                report_logger.print_info(f"INFO: Device index for {device}: {device_index}")
        except Exception as e:
            report_logger.print_error(f"FAIL: Failed to retrieve device index for {device}: {e}")
            all_passed = False
    # Retrieve and store radio indexes
    for device in devices:
        for band in ("2g", "5g", "6g"):
            try:
                radio_mac = initialize.read_from_database(device, f"{band}_radio_mac")
                if not radio_mac:
                    report_logger.print_info(f"INFO: Skipping {band} radio for {device}: Radio MAC not found")
                    continue
                radio_index = retrieve_and_store_radio_index(initialize, device, band, radio_mac)
                if radio_index is None:
                    report_logger.print_error(f"FAIL: Radio index not found for {device} ({band})")
                    all_passed = False
                else:
                    report_logger.print_info(f"INFO: Radio index for {device} {band}: {radio_index}")
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to retrieve {band} radio index for {device}: {e}")
                all_passed = False
    # Retrieve and store BSS indexes
    for device in devices:
        for band in ("2g", "5g", "6g"):
            try:
                radio_mac = initialize.read_from_database(device, f"{band}_radio_mac")
                if not radio_mac:
                    report_logger.print_info(f"INFO: Skipping {band} radio for {device}: radio MAC not found")
                    continue
                bss_index = retrieve_and_store_bss_index(initialize, device, band, radio_mac)
                if bss_index is None:
                    report_logger.print_error(f"FAIL: BSS index not found for {device} ({band})")
                    all_passed = False
                else:
                    report_logger.print_info(f"INFO: BSS index for {device} {band}: {bss_index}")
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to retrieve {band} BSS index for {device}: {e}")
                all_passed = False
    return all_passed
