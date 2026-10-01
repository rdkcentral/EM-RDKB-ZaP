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

import zaero
import pytest
import time
from rdkbmeshzap.common_utils import device_utils, report_logger

def test_client_association_discovery_easymesh_ssid(initialize):
    """
    Verify that  Wi-Fi client devices can discover and see the EasyMesh SSID broadcast by the mesh network (Controller and all 3 Agent devices)
    """    
    report_logger.print_test("Entering EM_Client_Association_Discovery_EasyMesh_SSID")
    report_logger.print_step("STEP 1: Get SSID from DataElements")
    ssid = initialize.get_ssid("controller", "controller_device_index", 'de')
    report_logger.print_success(f"PASS: Retrieved SSID: {ssid}")
    report_logger.print_step("STEP 2: Wait for some time for SSID propagation")
    time.sleep(10)
    report_logger.print_step("STEP 3: Initiate WiFi scan on each wlan client of the devices")
    clients = device_utils.get_enabled_clients(initialize)
    for client in clients:
        if initialize.read_from_database(client, "device_present"):
            output = []
            try:
                output = initialize.get_ap_ssid_visibility(client, ssid, 'cli')
                time.sleep(20)
                report_logger.print_success(f"PASS: WiFi scan initiated successfully on {client} with SSID: {ssid} and output: {output}")
                report_logger.print_step(f"STEP 4: Count SSID occurrences for {client}")
                if len(output) >= 2:
                    report_logger.print_success(f"PASS: {client}: SSID Count: {len(output)}")
                else:
                    report_logger.print_error(f"FAIL: {client}: SSID count: {len(output)}")
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to initiate WiFi scan on {client}: {e}")
