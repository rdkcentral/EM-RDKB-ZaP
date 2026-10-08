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
import pytest
from rdkbmeshzap.common_utils import report_logger

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
        report_logger.print_info(
            f"{device}: capture file was already removed from the device, skipping cleanup: {error}"
        )
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
        report_logger.print_error(f"Could not check services on {device} ({services}): the time limit expired before the first attempt")
    else:
        report_logger.print_error(f"Services on {device} are not active after {attempts} attempt(s). Services checked: {services}. Last error: {last_error}")
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
    return verify_services(
        initialize,
        extender,
        ("onewifi", "ieee1905_em_agent", "em_agent"),
        deadline,
    ) 

def get_extender_parent_device(initialize, extender, devices):
    """
    Syntax: get_extender_parent_device(initialize, extender, devices)
    Description: Identify the testbed device providing the extender's connected backhaul BSSID.
    Parameters: initialize - Testbed interface; extender - Extender name; devices - Candidate parent devices.
    Return Value: A tuple containing the parent device name and connected BSSID, or None values when unavailable.
    Example: get_extender_parent_device(initialize, "extender1", ["controller", "extender1"])
    """
    link_output = initialize.get_iw_dev_link_info(extender, "wifi1.3")
    match = re.search(r"Connected to\s+([0-9a-fA-F:]{17})", str(link_output), re.IGNORECASE)
    if not match:
        return None, None
    bssid = match.group(1).lower()
    for device in devices:
        try:
            output = initialize.get_iw_dev_interface_info(device, "wifi1.1")
        except Exception:
            continue
        if re.search(rf"\baddr\s+{re.escape(bssid)}\b", str(output), re.IGNORECASE):
            return device, bssid
    return None, bssid
