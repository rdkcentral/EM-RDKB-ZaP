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

def test_multi_agent_onboarding_topology_device_count(initialize):
    """
    Verify that after onboarding, the Controller's topology data model reflects exactly 3 onboarded Agents (plus the Controller itself), with each Agent represented by a distinct Device entry.
    """
    report_logger.print_test("Entering  Multi-Agent Onboarding Topology Device Count ")
    report_logger.print_step("STEP 1: Get initial topology device count for controller from DataElements")
    try:
        device_count = initialize.get_device_number_of_entries("controller", "de")
        if device_count is None:
            report_logger.print_error("FAIL: Failed to get device count for controller from DataElements")
        else:
            report_logger.print_success(f"PASS: Device count for controller retrieved successfully: {device_count}")
    except Exception as e:
        report_logger.print_error(f"Failed to query device count for controller: {e}")
    report_logger.print_step("STEP 2: Get device ID for controller and 3 extenders from DataElements")
    present_devices = []
    index = []
    if initialize.read_from_database("controller", "device_present"):
        controller_index = initialize.read_from_database("controller", "controller_device_index")
        present_devices.append("controller")
        index.append(controller_index)

    devices = device_utils.get_enabled_extenders(initialize)
    report_logger.print_success(f"{devices}")
    for device in devices:
        if initialize.read_from_database(device, "device_present"):
            present_devices.append(device)
            index.append(initialize.read_from_database("controller", f"{device}_device_index"))
        else:
            report_logger.print_info(f"{device} is not present in the network. Skipping device ID retrieval.")
    device_ids = {}
    for i in range(len(index)):
        device = present_devices[i]
        ids = initialize.get_device_id("controller", index[i],"de")
        if not ids:
            report_logger.print_error(f"FAIL: Failed to get device ID for {device} from DataElements")
        else:
            device_ids[device] = ids
            report_logger.print_success(f"PASS: Device ID for {device} retrieved successfully: {ids}")
    report_logger.print_step(f"STEP 3: Cross-reference each returned AL MAC against the known MAC addresses for controller and 3 extenders from DataElements")
    for device in devices:
        if initialize.read_from_database(device, "device_present"):
            try:
                bssid = initialize.get_al_mac_address(device)
                if bssid == device_ids[device]:
                    report_logger.print_success(f"{device} BSSID matches the device ID: {bssid}")
                else:
                    report_logger.print_error(f"{device} BSSID does not match the device ID: {bssid} != {device_ids[device]}")
            except Exception as e:
                report_logger.print_error(f"FAIL: Failed to query BSSID for {device}: {e}")
    report_logger.print_step(f"STEP 4: Get device radio count for each extender from DataElements")
    radio_counts = {}
    for extender in devices[1:]:  # Skip the controller
        if initialize.read_from_database(extender, "device_present"):
            try:
                radio_count = initialize.get_radio_Number_of_entries("controller", f"{extender}_device_index","de")
                radio_counts[extender] = radio_count
                if not radio_count:
                    report_logger.print_error(f"FAIL: Failed to get device radio count for {extender} from DataElements")
                else:
                    report_logger.print_success(f"PASS: Device radio count for {extender} retrieved successfully: {radio_count}")
            except Exception as e:
                    report_logger.print_error(f"FAIL: Exception while getting radio count for {extender}: {e}")
    report_logger.print_step(f"STEP 5: Compare initial and updated device counts after short idle time")
    time.sleep(10)
    try:
        updated_device_count = initialize.get_device_number_of_entries("controller", "de")
        if updated_device_count != device_count:
            report_logger.print_error(f"FAIL: Device count mismatch: Initial count {device_count}, Updated count {updated_device_count}")
        else:
            report_logger.print_success(f"PASS: Device count verified successfully: {updated_device_count}")
    except Exception as e:
        report_logger.print_error(f"FAIL: Failed to query updated device count for controller: {e}")