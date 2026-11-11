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
from rdkbmeshzap.common_utils import report_logger
from rdkbmeshzap.common_utils.client_utils import *
import time

def test_wifi_security_wpa2_personal_propagation(initialize):
    """
    Test case for verifying WPA2 Personal security propagation.
    """
    device_bssids = {}
    verified_devices = {}
    report_logger.print_test(f"Entering test_wifi_security_wpa2_personal_propagation")
    report_logger.print_step("STEP 1: Getting Current fronthaul security mode")
    try:
        initial_security_mode = initialize.get_security_mode("controller")
        report_logger.print_info(f"INFO: Current fronthaul security mode is: {initial_security_mode}")
    except Exception as e:
        report_logger.print_error(f"ERROR: Failed to get fronthaul security mode: {e}")
        return
    
    if initial_security_mode == "WPA2 Personal":
        report_logger.print_info("INFO: Security mode is already WPA2 Personal, skipping the steps 2 to 3")
    else:
        report_logger.print_step("STEP 2: Getting supported security modes")
        try:
            supported_sec_modes = initialize.get_supported_security_modes("controller")
            report_logger.print_info(f"INFO: Supported security modes: {supported_sec_modes}")
        except Exception as e:
            report_logger.print_error(f"ERROR: Failed to get supported security modes: {e}")
            return
        report_logger.print_step("STEP 2.1: Verifying if WPA2 Personal is supported")
        if "WPA2 Personal" not in supported_sec_modes:
            report_logger.print_info("INFO: WPA2 Personal is not supported, skipping the test")
            return
        else:
            report_logger.print_info("INFO: WPA2 Personal security is supported")

        report_logger.print_step(f"STEP 3: setting security mode to : WPA2 Personal")
        try:
            initialize.set_security_mode("controller", "WPA2 Personal")
            report_logger.print_success(f"PASS: Successfully set security mode to WPA2 Personal")
        except Exception as e:
            report_logger.print_error(f"ERROR: Failed to set security mode: {e}")
            return

    report_logger.print_step("STEP 4: Retrieving the wifi scanner device details")
    try:
        report_logger.print_step("STEP 4.1: Reading wifi scanner device from database")
        wifi_client_device =  initialize.read_from_database("test_parameters", "wifi_scanner_device")
        report_logger.print_info(f"INFO: Wifi scanner device read from database: {wifi_client_device}")
        report_logger.print_step("STEP 4.2: Checking if wifi scanner device is present")
        device_present = initialize.read_from_database(wifi_client_device, "device_present")
        if not device_present:
            report_logger.print_error(f"ERROR: Wifi scanner device is not present")
            return
        else:
            report_logger.print_info(f"INFO: Wifi scanner device is present: {wifi_client_device}")
    except Exception as e:
        report_logger.print_error(f"ERROR: Failed to retrieve wifi scanner device details: {e}")
        return
    
    devices = initialize.get_testbed_devices()
    for device in devices:
        if device == "controller" or re.match(r"^extender\d+$", device.strip()):
            device_bssids[device] = {}
            device_bssids[device]["2g_radio_mac"] = initialize.read_from_database(device, "2g_radio_mac")
            device_bssids[device]["5g_radio_mac"] = initialize.read_from_database(device, "5g_radio_mac")
    step_index = 1
    for device, bssids in device_bssids.items():
        for radio_type, target_bssid in bssids.items():
            #add step inside the print_step
            report_logger.print_step(f"STEP 5.{step_index}: Verifying security mode for {device} ({radio_type}) - {target_bssid}")
            step_index += 1
            for attempt in range(1, NMCLI_SCAN_RETRY_LIMIT):
                    try:
                        nmcli_scan_output = initialize.get_nmcli_scan_output(wifi_client_device)
                        report_logger.print_info(f"INFO: Scan attempt {attempt} for {target_bssid} completed.")
                    except Exception as error:
                        if attempt < NMCLI_SCAN_RETRY_LIMIT - 1:
                            report_logger.print_info(f"INFO: exception occurred: {error}")
                            report_logger.print_info(f"INFO: Scan attempt {attempt} failed for {target_bssid}. Retrying({attempt})...")
                            time.sleep(10)
                            continue
                        else:
                            report_logger.print_error(f"FAIL: Scan attempt {attempt} failed for {target_bssid}. Error: {error}")
                            break
                    try:
                        result, actual_security_mode = verify_security_mode(nmcli_scan_output,target_bssid,"WPA2")
                        if result:
                            report_logger.print_success(f"PASS: {device} ({radio_type}) security mode verified successfully: {actual_security_mode}")
                            verified_devices.setdefault(device, {})[radio_type] = target_bssid
                            break
                        if not result and attempt < NMCLI_SCAN_RETRY_LIMIT - 1:
                            report_logger.print_info(f"INFO: Security mode verification invalid. Retrying({attempt})... ")
                            time.sleep(10)
                            continue
                        else:
                            report_logger.print_error(f"FAIL: {device} ({radio_type}) security mode verification failed. Expected: 'WPA2', Actual: '{actual_security_mode}'")
                        # Success or verification completed
                    except Exception as error:
                        if attempt < NMCLI_SCAN_RETRY_LIMIT - 1:
                            report_logger.print_info(f"INFO: exception occurred: {error}")
                            report_logger.print_info(f"INFO: security mode verification failed for attempt {attempt} for {target_bssid}. Retrying({attempt})...")
                            time.sleep(5)
                            continue
                        else:
                            report_logger.print_error(f"FAIL: Failed to verify security mode for {device} ({radio_type}) [{target_bssid}] after {NMCLI_SCAN_RETRY_LIMIT - 1} attempts: {error}")

    report_logger.print_info("INFO: retrieving ssid and password from controller")
    try:
        ssid = initialize.get_ssid("controller", "2g_ssid_index", 'de')
        password = initialize.get_fronthaul_password("controller","gui")
    except Exception as ERR:
        report_logger.print_error(f"FAIL: Failed to get SSID or password from controller: {ERR}")
        return
    step_index = 1
    if verified_devices:
        for device, radios in verified_devices.items():
            for radio_type, bssid in radios.items():
                report_logger.print_step(f"STEP 6.{step_index}: Connecting {wifi_client_device} to SSID {ssid} of {device} through {radio_type} radio ({bssid})")
                step_index += 1
                try:
                    report_logger.print_info(f"INFO: Removing Existing conneections for {wifi_client_device}")
                    initialize.remove_all_wifi_connections(wifi_client_device)
                except Exception as ERR:
                    report_logger.print_error(f"FAIL: Failed to remove all WiFi connections for {wifi_client_device}: {ERR}")
                    continue
                for attempt in range(1, NMCLI_SCAN_RETRY_LIMIT):
                    try:
                        initialize.connect_client_to_ssid(wifi_client_device,ssid,password,bssid)
                        time.sleep(10)
                        report_logger.print_success(f"PASS: {wifi_client_device} connected to SSID {ssid} of {device} through {radio_type} radio ({bssid})")
                        break
                    except Exception as ERR:
                        if attempt < NMCLI_SCAN_RETRY_LIMIT - 1:
                            report_logger.print_info(f"INFO: exception occurred: {ERR}")
                            report_logger.print_info(f"INFO: Connection attempt {attempt} failed for {wifi_client_device}. Retrying({attempt})...")
                            time.sleep(2)
                            try:
                                initialize.remove_all_wifi_connections(wifi_client_device)
                            except Exception as ERR:
                                report_logger.print_error(f"FAIL: Failed to remove all WiFi connections for {wifi_client_device}: {ERR}")
                                continue
                        else:
                            report_logger.print_info(f"INFO: exception occurred: {error}")
                            report_logger.print_error(f"FAIL: Failed to connect {wifi_client_device} to SSID {ssid} of {device} through {radio_type} radio ({bssid}) after {NMCLI_SCAN_RETRY_LIMIT - 1} attempts: {ERR}")
    report_logger.print_test("Exiting test_wifi_security_wpa2_personal_propagation")
