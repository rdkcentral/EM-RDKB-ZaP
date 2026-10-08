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

def retrieve_and_store_radio_macs(initialize):
    """
    Syntax: retrieve_and_store_radio_macs(initialize)
    Description:
        Discover 2G, 5G, and 6G fronthaul BSSIDs for the controller
        and all enabled extenders.
        Match every BSSID returned by get_fronthaul_bssids() against
        the MAC addresses of wifi0, wifi1, and wifi2, then store the
        validated radio MAC addresses in the database.
    Parameters:
        initialize - Testbed interface used to access devices.
    Return Value:
        None on success; False when retrieval or validation fails.
    """
    report_logger.print_title("Update the database with radio MAC addresses for the controller and enabled extenders")
    try:
        # Controller
        devices = ["controller"]
        # Enabled extenders
        devices.extend(device_utils.get_enabled_extenders(initialize))
        report_logger.print_title(f"Radio MAC retrieval and storage started for {len(devices)} device(s): {', '.join(devices)}")
        interfaces = ["wifi0", "wifi1", "wifi2"]
        radio_db_keys = {
            "wifi0": "2g_radio_mac",
            "wifi1": "5g_radio_mac",
            "wifi2": "6g_radio_mac"
        }
        for device in devices:
            report_logger.print_info(f"[{device}] Retrieving 2G, 5G, and 6G fronthaul BSSIDs")
            bssids = initialize.get_fronthaul_bssids(device, "cli")
            if len(bssids) < 3:
                report_logger.print_error(f"Expected 3 fronthaul BSSIDs for {device}, but found {len(bssids)}: {bssids}")
                return False
            report_logger.print_info(f"[{device}] Fronthaul BSSIDs received: {bssids}")
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
            report_logger.print_success(f"[{device}] Stored 2g_radio_mac = {matched['wifi0']}")
            report_logger.print_success(f"[{device}] Stored 5g_radio_mac = {matched['wifi1']}")
            report_logger.print_success(f"[{device}] Stored 6g_radio_mac = {matched['wifi2']}")
        report_logger.print_success(f"Successfully retrieved and stored radio MAC addresses in the database for {len(devices)} device(s)")
    except Exception as e:
        report_logger.print_error(f"Radio MAC retrieval and storage failed: {e}")
        return False

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
    report_logger.print_info("INFO: Validating services on controller")
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

def retrieve_and_store_device_indexes(initialize):
    report_logger.print_title("Update the database with device indexes for the controller and enabled extenders")
    # Device Index
    devices = ["controller"] + device_utils.get_enabled_extenders(initialize)
    for device in devices:
        al_mac = initialize.get_al_mac_address(device)
        report_logger.print_step(f"{device} AL MAC: {al_mac}")
        device_index = None
        if device == "controller":
            for i in range(1, 10):
                controller_al_mac_de = initialize.get_controller_id("controller", "de")
                if al_mac.lower() == controller_al_mac_de.lower():
                    device_index = i
                    break
        else:
            for i in range(1, 10):
                extender_al_mac_de = initialize.get_device_id("controller", str(i), "de")
                if al_mac.lower() == extender_al_mac_de.lower():
                    device_index = i
                    break
        if device_index is None:
            report_logger.print_error(f"ERROR: AL MAC {al_mac} not found")
        else:
            initialize.write_into_database("controller",f"{device}_device_index",str(device_index))
            report_logger.print_success(f"PASS: {device} Device Index = {device_index}")