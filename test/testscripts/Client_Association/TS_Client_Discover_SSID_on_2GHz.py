# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
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
import pytest
import time
from rdkbmeshzap.common_utils import device_utils, report_logger

def test_client_association_discover_ssid_on_2_4GHz(initialize):
    """
    Verify that Wi-Fi client devices can specifically discover and see the EasyMesh SSID on the 2.4 GHz band, broadcast by the Controller and all 3 Agents.
    """
    report_logger.print_test("Entering test_client_association_discover_ssid_on_2_4GHz")
    try:
        report_logger.print_step("STEP 1: Verifying client's Wi-Fi generation")
        clients = device_utils.get_enabled_clients(initialize)
        for client in clients:
            if initialize.read_from_database(client, "device_present"):
                client_generation = initialize.get_wifi_generation(client, 'cli')
                report_logger.print_info(f"INFO: {client} is a {client_generation} client")
            else:
                report_logger.print_info(f"INFO: {client} is not present, skipping generation check.")
        report_logger.print_step("STEP 2: Retrieve and store device indexes, radio indexes, and BSS indexes for controller and enabled extenders")
        if not device_utils.retrieve_and_store_all_indexes(initialize):
            pytest.fail("Failed to retrieve and store the required indexes")
        report_logger.print_success(
            "PASS: Device indexes, Radio indexes, and BSS indexes "
            "retrieved and stored successfully for the controller "
            "and enabled extenders."
        )
        report_logger.print_step("STEP 3: Verify 2.4 GHz Radio enabled on Controller and all enabled extenders")
        step_passed = True
        devices = ["controller"] + device_utils.get_enabled_extenders(initialize)
        for device in devices:
            device_index = initialize.read_from_database("controller", f"{device}_device_index")
            radio_index = initialize.read_from_database("controller", f"{device}_2g_radio_index")
            radio_status = initialize.get_radio_enabled_status("controller", device_index, radio_index)
            if radio_status != "true":
                report_logger.print_error(f"FAIL: 2.4 GHz Radio is not enabled on {device}. Status: {radio_status}")
                step_passed = False
            else:
                report_logger.print_info(f"INFO: 2.4 GHz Radio is enabled on {device}. Status: {radio_status}")
        if step_passed:
            report_logger.print_success("PASS: 2.4 GHz Radio is enabled on controller and all enabled extenders.")
        else:
            pytest.fail("2.4 GHz Radio is not enabled on one or more devices.")
        report_logger.print_step("STEP 4:Query SSID on 2.4 GHz Radio/BSS on controller and all enabled extenders")
        step_passed = True
        for device in devices:
            device_index = initialize.read_from_database("controller", f"{device}_device_index")
            radio_index = initialize.read_from_database("controller", f"{device}_2g_radio_index")
            bss_index = initialize.read_from_database("controller", f"{device}_2g_radio_bss_index")
            ssid = initialize.get_ssid_for_each_radio("controller", device_index, radio_index, bss_index, "de")
            if not ssid:
                report_logger.print_error(f"FAIL: Failed to query SSID on 2.4 GHz Radio/BSS for {device}")
                step_passed = False
            else:
                report_logger.print_info(f"INFO: SSID on 2.4 GHz Radio/BSS for {device}: {ssid}")
        if step_passed:
            report_logger.print_success("PASS: SSID on 2.4 GHz Radio/BSS queried successfully for controller and all enabled extenders.")
        else:
            pytest.fail("Failed to query 2.4 GHz SSID for one or more devices.")
        report_logger.print_step("STEP 5: Verify Operating Radio Details on 2.4 GHz Radio for controller and all enabled extenders")
        step_passed = True
        for device in devices:
            operating_radio_details = initialize.get_operating_radio_details(device, "2.4", "cli")
            if not operating_radio_details:
                report_logger.print_error(f"FAIL: Failed to retrieve operating radio details for {device} on 2.4 GHz Radio")
                step_passed = False
            else:
                report_logger.print_info(f"INFO: Operating Radio Details for {device} on 2.4 GHz Radio: {operating_radio_details}")
        if step_passed:
            report_logger.print_success("PASS: Operating radio details retrieved successfully for controller and all enabled extenders.")
        else:
            report_logger.print_error("FAIL: Failed to retrieve operating radio details for one or more devices.")
        report_logger.print_step("STEP 6: Wait 5 seconds for SSID propagation")
        time.sleep(5)
        report_logger.print_info("INFO: Waited 5 seconds for SSID propagation to ensure that the SSID is visible to all connected clients.")
        report_logger.print_step("STEP 7: Initiate WiFi scan and count occurrences on 2.4 GHz band on the enabled client devices")
        step_passed = True
        clients = device_utils.get_enabled_clients(initialize)
        for client in clients:
            if initialize.read_from_database(client, "device_present"):
                output = []
                try:
                    report_logger.print_info(f"INFO: Count SSID occurrences for {client}")
                    output = initialize.get_ap_ssid_visibility(client, ssid, 'cli')
                    time.sleep(10)
                    report_logger.print_info(f"INFO: WiFi scan initiated successfully on {client} with SSID: {ssid} and output: {output}")
                    frequencies = re.findall(r'(\d+)\s*MHz', output)
                    ssid_occurrences = [frequency for frequency in frequencies
                        if 2400 <= int(frequency) <= 2500]                
                    frequency_count = len(ssid_occurrences)
                    if frequency_count >= 1:
                        report_logger.print_success(f"PASS: {client}: SSID Count: {frequency_count}")
                    else:
                        report_logger.print_error(f"FAIL: {client}: SSID count: {frequency_count}")
                        step_passed = False
                except Exception as e:
                    report_logger.print_error(f"FAIL: Failed to initiate WiFi scan on {client}: {e}")
                    step_passed = False
        if step_passed:
            report_logger.print_success("PASS: All connected clients can discover and see the 2.4 GHz SSID broadcast by the mesh network.")
        else:
            report_logger.print_error("FAIL: One or more clients could not discover the 2.4 GHz SSID.")
            pytest.fail("2.4 GHz SSID discovery failed for one or more clients.")
    finally:
        report_logger.print_test("Exiting test_client_association_discover_ssid_on_2_4GHz")