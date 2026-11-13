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

from rdkbmeshzap.common_utils import report_logger
from rdkbmeshzap.common_utils.client_utils import *
import time
from wifi_security_utils import *

def test_wifi_security_wpa3_personal_propagation(initialize, common_setup):
    """
    Test case for verifying WPA3 Personal security propagation.
    """
    step_index = 1
    security_mode_to_verify = "WPA3"
    report_logger.print_test(f"Entering test_wifi_security_wpa3_personal_propagation")
    try:
        try:
            (initial_security_mode, supported_sec_modes, wifi_client_device,
             device_bssids) = common_setup
        except Exception as error:
            report_logger.print_error(
                f"ERROR: Failed to unpack Wi-Fi security test setup: {error}")
            return
        if initial_security_mode == "WPA3 Personal":
            report_logger.print_info("INFO: Security mode is already WPA3 Personal.")
        else:
            if "WPA3 Personal" not in supported_sec_modes:
                report_logger.print_info("INFO: WPA3 Personal security is not supported, skipping the test")
                return
            else:
                report_logger.print_info("INFO: WPA3 Personal security is supported")
            step_index += 1
            report_logger.print_step(f"STEP {step_index}: setting security mode to : WPA3 Personal")
            try:
                initialize.set_security_mode("controller", "WPA3 Personal")
                report_logger.print_success(f"PASS: Successfully set security mode to WPA3 Personal")
            except Exception as e:
                report_logger.print_error(f"ERROR: Failed to set security mode: {e}")
                return
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Verifying security mode propagation for WPA3 Personal security")
        verified_bssid = verify_security_mode_propagation(initialize, device_bssids, security_mode_to_verify, wifi_client_device, step_index)
        if not verified_bssid:
            report_logger.print_error("ERROR: no devices updated with WPA3 Personal security mode.")
            return
        else:
            step_index += 1
            report_logger.print_step(f"STEP {step_index}: Connecting Wi-Fi client to WPA3 Personal network")
            connect_client_to_bssid(initialize, wifi_client_device, verified_bssid, step_index)    
    finally:
        report_logger.print_test("Exiting test_wifi_security_wpa3_personal_propagation")