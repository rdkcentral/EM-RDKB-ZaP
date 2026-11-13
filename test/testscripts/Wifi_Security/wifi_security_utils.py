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
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.client_utils import verify_security_mode
import pytest

NMCLI_SCAN_RETRY_LIMIT = 6

@pytest.fixture(autouse=True)
def common_setup(initialize):
    """
    Syntax: common_setup(initialize)
    Description: Collect common Wi-Fi security test data from the controller,
                 enabled client, and mesh devices.
    Parameters: initialize - Testbed initialization and database interface.
    Yield Value: A tuple containing the controller's current security mode,
                 supported security modes, selected Wi-Fi client device, and
                 controller/extender 2.4 GHz and 5 GHz BSSIDs. Restores the
                 initial controller security mode during teardown if changed.
    Example: common_setup(initialize)
    """
    try:
        report_logger.print_info("INFO: getting current security mode")
        current_security_mode = initialize.get_security_mode("controller")
        report_logger.print_success(f"PASS: Current security mode retrieved successfully: {current_security_mode}")
        report_logger.print_info("INFO: getting supported security modes")
        supported_security_modes = initialize.get_supported_security_modes("controller")
        report_logger.print_success(f"PASS: Supported security modes retrieved successfully: {supported_security_modes}")
        report_logger.print_info("INFO: getting enabled Wi-Fi clients")
        enabled_clients = device_utils.get_enabled_clients(initialize)
        if not enabled_clients:
            raise RuntimeError("No enabled Wi-Fi client devices found")
        report_logger.print_success(f"PASS: Enabled Wi-Fi clients retrieved successfully: {enabled_clients}")
        device_bssids = {}
        report_logger.print_info("INFO: getting test bed BSSIDs")
        for device in initialize.get_testbed_devices():
            if device == "controller" or re.fullmatch(r"extender\d+", device.strip()):
                device_bssids[device] = {
                    "2g_radio_mac": initialize.read_from_database(device, "2g_radio_mac"),
                    "5g_radio_mac": initialize.read_from_database(device, "5g_radio_mac"),
                }
        if not device_bssids:
            raise RuntimeError("No BSSIDs found for test bed devices")
        report_logger.print_success(f"PASS: BSSIDs for test bed devices retrieved successfully")
        yield (
            current_security_mode,
            supported_security_modes,
            enabled_clients[0],
            device_bssids,
        )
    finally:
        try:
            final_security_mode = initialize.get_security_mode("controller")
        except Exception as error:
            report_logger.print_error(f"ERROR: Failed to get security mode during cleanup: {error}")
            raise
        if final_security_mode != current_security_mode:
            report_logger.print_info("INFO: Reverting security mode to initial value")
            try:
                initialize.set_security_mode("controller", current_security_mode)
                report_logger.print_info(f"INFO: Successfully set security mode to "f"{current_security_mode}")
            except Exception as error:
                report_logger.print_error(f"ERROR: Failed to revert security mode: {error}")
                raise

def verify_security_mode_propagation(initialize, device_bssids, expected_security_mode, wifi_client_device,step_index):
    """
    Syntax : verify_security_mode_propagation(initialize, device_bssids, expected_security_mode, wifi_client_device, step_index)
    Description : Verifies the propagation of the expected security mode for the specified devices and BSSIDs.
    Parameters :
        initialize : Initialization object for interacting with the test bed.
        device_bssids : Dictionary containing devices and their corresponding BSSIDs.
        expected_security_mode : The expected security mode to verify.
        wifi_client_device : The Wi-Fi client device used for scanning.
        step_index : The current step index for logging purposes.
    Return Value: Dictionary of verified devices and their BSSIDs if successful, None otherwise.
    """
    sub_step_index = 0
    verified_devices = {}
    for device, bssids in device_bssids.items():
        for radio_type, target_bssid in bssids.items():
            sub_step_index += 1
            report_logger.print_step(f"STEP {step_index}.{sub_step_index}: Verifying security mode propagation for {device} ({radio_type}) - {target_bssid}")
            for attempt in range(1, NMCLI_SCAN_RETRY_LIMIT):
                    try:
                        nmcli_scan_output = initialize.get_nmcli_scan_output(wifi_client_device)
                    except Exception as error:
                        if attempt < NMCLI_SCAN_RETRY_LIMIT - 1:
                            report_logger.print_info(f"INFO: exception occurred: {error}.  Retrying({attempt})...")
                            initialize.set_client_radio_state(wifi_client_device,0)
                            time.sleep(3)
                            initialize.set_client_radio_state(wifi_client_device,1)
                            time.sleep(60)
                            continue
                        else:
                            report_logger.print_error(f"FAIL: Scan attempt {attempt} failed for {target_bssid}. Error: {error}")
                            break
                    try:
                        result, actual_security_mode = verify_security_mode(nmcli_scan_output,target_bssid,expected_security_mode)
                        if result:
                            report_logger.print_success(f"PASS: {device} ({radio_type}) security mode verified successfully: {actual_security_mode}")
                            verified_devices.setdefault(device, {})[radio_type] = target_bssid
                            break
                        if attempt < NMCLI_SCAN_RETRY_LIMIT - 1:
                            report_logger.print_info(f"INFO: Security mode verification invalid. Retrying({attempt})... ")
                            initialize.set_client_radio_state(wifi_client_device,0)
                            time.sleep(3)
                            initialize.set_client_radio_state(wifi_client_device,1)
                            time.sleep(60)
                            continue
                        else:
                            report_logger.print_error(f"FAIL: {device} ({radio_type}) security mode verification failed. Expected: '{expected_security_mode}', Actual: '{actual_security_mode}'")
                        # Success or verification completed
                    except Exception as error:
                        if attempt < NMCLI_SCAN_RETRY_LIMIT - 1:
                            report_logger.print_info(f"INFO: exception occurred: {error}. Retrying({attempt})...")
                            initialize.set_client_radio_state(wifi_client_device,0)
                            time.sleep(3)
                            initialize.set_client_radio_state(wifi_client_device,1)
                            time.sleep(60)
                            continue
                        else:
                            report_logger.print_error(f"FAIL: Failed to verify security mode for {device} ({radio_type}) [{target_bssid}] after {NMCLI_SCAN_RETRY_LIMIT - 1} attempts: {error}")
    if verified_devices:
        return verified_devices
    else:
        return None

def connect_client_to_bssid(initialize, wifi_client_device, device_bssids, step_index):
    """
    Syntax: connect_client_to_bssid(initialize, wifi_client_device, device_bssids, step_index)
    Description: Connects a WiFi client to the specified BSSID of a device and verifies the connection.
    Parameters:
        initialize : Test initialization object.
        wifi_client_device : Client device name.
        device_bssids : Dictionary containing device BSSIDs organized by radio type.
        step_index : Step index for logging purposes.
    Return Value: None
    """
    sub_step_index = 1
    report_logger.print_step(f"STEP {step_index}.{sub_step_index}: retrieving ssid and password from controller")
    try:
        ssid = initialize.get_ssid("controller", "2g_ssid_index", 'de')
        password = initialize.get_fronthaul_password("controller","gui")
        report_logger.print_info(f"INFO: Retrieved SSID: {ssid} and password from controller")
    except Exception as ERR:
        report_logger.print_error(f"FAIL: Failed to get SSID or password from controller: {ERR}")
        return
    for device, radios in device_bssids.items():
        for radio_type, bssid in radios.items():
            sub_step_index += 1
            report_logger.print_step(f"STEP {step_index}.{sub_step_index}: Connecting {wifi_client_device} to SSID {ssid} of {device} through {radio_type} radio ({bssid})")
            try:
                report_logger.print_info(f"INFO: Removing Existing connections for {wifi_client_device}")
                initialize.remove_all_wifi_connections(wifi_client_device)
            except Exception as ERR:
                report_logger.print_error(f"FAIL: Failed to remove all WiFi connections for {wifi_client_device}: {ERR}")
                continue
            for attempt in range(1, NMCLI_SCAN_RETRY_LIMIT):
                try:
                    initialize.connect_client_to_ssid(wifi_client_device,ssid,password,bssid)
                    report_logger.print_success(f"PASS: {wifi_client_device} connected to SSID {ssid} of {device} through {radio_type} radio ({bssid})")
                    break
                except Exception as ERR:
                    if attempt < NMCLI_SCAN_RETRY_LIMIT - 1:
                        report_logger.print_info(f"INFO: exception occurred: {ERR}")
                        report_logger.print_info(f"INFO: Connection attempt {attempt} failed for {wifi_client_device}. Retrying({attempt})...")
                        time.sleep(10)
                        try:
                            initialize.remove_all_wifi_connections(wifi_client_device)
                        except Exception as ERR:
                            report_logger.print_error(f"FAIL: Failed to remove all WiFi connections for {wifi_client_device}: {ERR}")
                            continue
                    else:
                        report_logger.print_info(f"INFO: exception occurred: {ERR}")
                        report_logger.print_error(f"FAIL: Failed to connect {wifi_client_device} to SSID {ssid} of {device} through {radio_type} radio ({bssid}) after {NMCLI_SCAN_RETRY_LIMIT - 1} attempts: {ERR}")

