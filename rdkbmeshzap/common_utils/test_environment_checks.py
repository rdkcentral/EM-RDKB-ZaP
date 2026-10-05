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

from rdkbmeshzap.common_utils import device_utils, report_logger

def validate_device_accessibility(initialize):
    """
    Validate SSH accessibility for every configured testbed device.
    Parameters: initialize - Testbed initialization and device interface.
    Return Value: True when all configured devices are accessible.
    Example: validate_device_accessibility(initialize)
    """
    devices = initialize.get_testbed_devices()
    validation_result = True
    report_logger.print_title(f"Validating accessibility of {len(devices)} configured devices")
    for device in devices:
        report_logger.print_info(f"INFO: Connecting to {device}")
        try:
            connected = initialize.connect_with_device(device)
            if connected is False:
                raise RuntimeError("connection API returned False")
        except Exception as error:
            validation_result = False
            report_logger.print_error(
                f"{device} accessibility validation failed: {error}"
            )
        else:
            report_logger.print_success(f"{device} is accessible over SSH")
    return validation_result

def validate_mld0_vap_configurations(initialize):
    """
    Syntax: validate_mld0_vap_configurations(initialize)
    Description: Validate the mld0 interface and default SSID on all enabled devices.
    Parameters: initialize - Testbed initialization and device interface.
    Return Value: True when all enabled devices have the expected mld0 configuration.
    Example: validate_mld0_vap_configurations(initialize)
    """
    report_logger.print_title("Environment Check 1: Validate mld0 VAP configurations on all enabled devices")
    validation_result = True
    expected_ssid = initialize.read_from_database("controller", "default_ssid")
    if not expected_ssid:
        report_logger.print_error("FAIL: controller: default_ssid is missing or empty")
        return False
    for device in ["controller"] + device_utils.get_enabled_extenders(initialize):
        device_failed = False
        try:
            info = initialize.get_iw_interface_details(device, "mld0")
            missing = info["lines"][:1] != ["Interface mld0"] or info["ssid"] != str(expected_ssid).strip()
            if missing:
                validation_result = False
                device_failed = True
                report_logger.print_error(f"FAIL: {device}: Invalid mld0 VAP configuration")
        except Exception as error:
            validation_result = False
            device_failed = True
            report_logger.print_error(f"FAIL: {device}: mld0 check failed: {error}")
        if not device_failed:
            report_logger.print_success(f"PASS: {device}: Valid mld0 VAP configuration")
    if validation_result:
        report_logger.print_success("PASS: mld0 interface validation completed for all enabled devices")
    return validation_result

def validate_mesh_and_iot_vap_configurations(initialize):
    """
    Syntax: validate_mesh_and_iot_vap_configurations(initialize)
    Description: Validate mesh and IoT VAP interfaces and SSIDs on all enabled devices.
    Parameters: initialize - Testbed initialization and device interface.
    Return Value: True when all expected mesh and IoT VAPs are valid.
    Example: validate_mesh_and_iot_vap_configurations(initialize)
    """
    report_logger.print_title("Environment Check 2: Validate mesh and IoT VAP configurations on all enabled devices")
    devices = ["controller"] + device_utils.get_enabled_extenders(initialize)
    mesh_ssid = initialize.read_from_database("controller", "mesh_backhaul_ssid")
    iot_ssid = initialize.read_from_database("controller", "iot_ssids")
    for name, ssid in (("mesh_backhaul_ssid", mesh_ssid), ("iot_ssids", iot_ssid)):
        if not isinstance(ssid, str) or not ssid.strip():
            report_logger.print_error(f"FAIL: {name} is missing or empty in platform.yaml")
            return False
    mesh_ssid, iot_ssid = mesh_ssid.strip(), iot_ssid.strip()
    validation_result = True
    for device in devices:
        device_failed = False
        try:
            for radio in range(3):
                for suffix, expected, label in ((".1", mesh_ssid, "mesh"), (".2", iot_ssid, "IoT")):
                    interface = f"wifi{radio}{suffix}"
                    info = initialize.get_iw_interface_details(device, interface)
                    if not info["exists"] or info["ssid"] != expected:
                        validation_result = False
                        device_failed = True
                        report_logger.print_error(f"FAIL: {device}: {label} interface {interface} is missing or has incorrect SSID")
        except Exception as error:
            validation_result = False
            device_failed = True
            report_logger.print_error(f"FAIL: {device}: VAP validation failed: {error}")
        if not device_failed:
            report_logger.print_success(f"PASS: {device}: All mesh and IoT VAP interfaces are valid")
    return validation_result

def validate_mld0_links_to_private_vaps(initialize):
    """
    Syntax: validate_mld0_links_to_private_vaps(initialize)
    Description: Validate mld0 link IDs and map each link MAC to a private VAP.
    Parameters: initialize - Testbed initialization and device interface.
    Return Value: True when all mld0 links map to private VAPs on enabled devices.
    Example: validate_mld0_links_to_private_vaps(initialize)
    """
    report_logger.print_title("Environment Check 3: Validate mld0 links mapped to private VAPs on all enabled devices")
    expected_link_ids = {0, 1, 2}
    validation_result = True
    for device in ["controller"] + device_utils.get_enabled_extenders(initialize):
        device_failed = False
        try:
            mld_info = initialize.get_iw_interface_details(device, "mld0")
            if mld_info["link_ids"] != expected_link_ids:
                validation_result = False
                device_failed = True
                report_logger.print_error(f"FAIL: {device}: expected mld0 link IDs {sorted(expected_link_ids)}, found {sorted(mld_info['link_ids'])}")
                continue
            wifi_macs = {
                f"wifi{radio}": initialize.get_iw_interface_details(
                    device, f"wifi{radio}"
                )["addr"]
                for radio in range(3)
            }
            mac_to_wifi = {mac: interface for interface, mac in wifi_macs.items() if mac}
            for link_id in sorted(expected_link_ids):
                mld_mac = mld_info["link_macs"].get(link_id, "")
                mapped_interface = mac_to_wifi.get(mld_mac)
                if not mld_mac or not mapped_interface:
                    validation_result = False
                    device_failed = True
                    report_logger.print_error(f"FAIL: {device}: link ID {link_id} MAC {mld_mac} does not map to a private VAP")
                else:
                    report_logger.print_info(f"INFO: {device}: link ID {link_id} maps to {mapped_interface}")
        except Exception as error:
            validation_result = False
            device_failed = True
            report_logger.print_error(f"FAIL: {device}: mld0 private VAP link validation failed: {error}")
        if not device_failed:
            report_logger.print_success(f"PASS: {device}: mld0 links correctly mapped to private VAPs")
    if validation_result:
        report_logger.print_success("PASS: mld0 links map correctly to private VAPs in all enabled devices")
    return validation_result

def verify_mesh_backhaul_interfaces(initialize):
    """
    Syntax: verify_mesh_backhaul_interfaces(initialize)
    Description: Validate mesh backhaul interface presence, type, and 4-address mode.
    Parameters: initialize - Testbed initialization and device interface.
    Return Value: True when mesh backhaul interfaces are valid on all enabled devices.
    Example: verify_mesh_backhaul_interfaces(initialize)
    """
    report_logger.print_title("Environment Check 4: Validate mesh backhaul interfaces on all enabled devices")
    extenders = device_utils.get_enabled_extenders(initialize)
    validation_result = True
    if not extenders:
        validation_result = False
        report_logger.print_error("FAIL: No enabled Extenders are configured")
    for device in ["controller"] + extenders:
        interface = "wifi1.3"
        device_failed = False
        try:
            info = initialize.get_iw_interface_details(device, interface)
            if not info["exists"] or info["type"] != "managed" or info["four_addr"] != "on":
                validation_result = False
                device_failed = True
                report_logger.print_error(f"FAIL: {device}: {interface} is missing or has invalid interface data")
        except Exception as error:
            validation_result = False
            device_failed = True
            report_logger.print_error(f"FAIL: {device}: {interface} validation failed: {error}")
        if not device_failed:
            report_logger.print_success(f"PASS: {device}: Valid mesh backhaul interface")
    if validation_result:
        report_logger.print_success("PASS: Mesh backhaul interfaces are valid on all enabled devices")
    return validation_result

def validate_extender_parent_connections(initialize):
    """
    Syntax: validate_extender_parent_connections(initialize)
    Description: Validate that every enabled extender is connected to a testbed parent device.
    Parameters: initialize - Testbed initialization and device interface.
    Return Value: True when all enabled extenders have a matching parent device.
    Example: validate_extender_parent_connections(initialize)
    """
    report_logger.print_title("Environment Check 5: Validate parent-device connections for all enabled extenders")
    devices = ["controller"] + device_utils.get_enabled_extenders(initialize)
    validation_result = True
    for extender in device_utils.get_enabled_extenders(initialize):
        parent, bssid = device_utils.get_extender_parent_device(initialize, extender, devices)
        if not parent:
            validation_result = False
            report_logger.print_error(f"FAIL: {extender} is not connected to a testbed device (BSSID: {bssid or 'unknown'})")
        else:
            report_logger.print_success(f"{extender} is connected to {parent} through {bssid}")
    if validation_result:
        report_logger.print_success("All enabled extenders are connected within testbed devices")
    return validation_result

def validate_mesh_service_status(initialize):
    """
    Syntax: validate_mesh_service_status(initialize)
    Description: Validate required mesh services on the controller and enabled extenders.
    Parameters: initialize - Testbed initialization and device interface.
    Return Value: True when mesh service validation completes successfully.
    Example: validate_mesh_service_status(initialize)
    """
    report_logger.print_title("Environment Check 6: Validate mesh services on all enabled devices")
    validation_result = True
    report_logger.print_info("INFO: Validating controller services")
    if device_utils.verify_controller_services(initialize) is False:
        validation_result = False
    else:
        report_logger.print_success("PASS: controller mesh services are active")
    for extender in device_utils.get_enabled_extenders(initialize):
        report_logger.print_info(f"INFO: Validating services on {extender}")
        if device_utils.verify_extender_services(initialize, extender) is False:
            validation_result = False
        else:
            report_logger.print_success(f"PASS: {extender} mesh services are active")
    if validation_result:
        report_logger.print_success("PASS: Mesh services validated on all enabled devices")
    return validation_result