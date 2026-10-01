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

def test_multi_agent_onboarding_no_duplicate_entries(initialize):
    """
    Verify that no duplicate Agent entries are created in the Controller's topology after all 3 Agents complete onboarding.
    """
    report_logger.print_test("Entering EM Multi-Agent Onboarding No Duplicate Entries")
    report_logger.print_step("STEP 1: Get device-IDs of controller and all extenders from DataElements")
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
        ids = initialize.get_device_id("controller", index[i], "de")
        if not ids:
            report_logger.print_error(f"FAIL: Failed to get device ID for {device} from DataElements")
        else:
            device_ids[device] = ids
            report_logger.print_success(f"PASS: Device ID for {device} retrieved successfully: {ids}")
    report_logger.print_step("STEP 2: Check for duplicate AL MAC addresses")
    all_device_ids = list(device_ids.values())
    unique_device_ids = set(all_device_ids)
    if len(all_device_ids) == len(unique_device_ids):
        report_logger.print_success(f"PASS: No duplicate AL MAC addresses found. "f"Total devices: {len(all_device_ids)}, "f"Unique AL MAC addresses: {len(unique_device_ids)}")
    else:
        report_logger.print_error(f"FAIL: Duplicate AL MAC address(es) found")
    report_logger.print_step("STEP 3: Get DeviceNumberOfEntries for cross-checking from Controller DataElements")
    try:
        device_count = initialize.get_device_number_of_entries("controller", "de")
        if device_count is None:
            report_logger.print_error("Failed to get DeviceNumberOfEntries from Controller")
        else:
            report_logger.print_success(f"PASS: DeviceNumberOfEntries retrieved successfully: {device_count}")
    except Exception as e:
        report_logger.print_error(f"FAIL: Failed to query DeviceNumberOfEntries from Controller: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    # unique_device_count = len(unique_device_ids)
    print(f"DeviceNumberOfEntries: {device_count}, Unique AL MAC addresses: {len(unique_device_ids)}")
    if int(device_count) == len(unique_device_ids):
        report_logger.print_success(f"PASS: DeviceNumberOfEntries matches the number of unique AL MAC addresses: "f"{device_count} == {len(unique_device_ids)}")
    else:
        report_logger.print_error(f"FAIL: DeviceNumberOfEntries does not match the number of unique AL MAC addresses: "f"{device_count} != {len(unique_device_ids)}")
    report_logger.print_step("STEP 4: Reboot the extender and Requery device IDs from DataElements")
    initialize.reboot_device("extender1", "cli")
    initialize.close_connection("extender1")
    time.sleep(10)
    for i in range(1, 51):
        report_logger.log(f"FOR loop iteration : {i}")
        try:
            initialize.connect_with_device("extender1")
        except Exception:
            report_logger.print_error("FAIL: Connection FAILED with 'Extender1'", log_error=False)
        else:
            report_logger.print_success("PASS: Connection SUCCESS with 'Extender1'")
            break
        time.sleep(10)
    else:
        pytest.fail("Could not re-establish connection with - extender1")
    for i in range(len(index)):
            device = present_devices[i]
            ids = initialize.get_device_id("controller", index[i], "de")
            if not ids:
                report_logger.print_error(f"FAIL: Failed to get device IDs for controller and extenders from DataElements")
            else:
                device_ids[device] = ids
                report_logger.print_success(f"Device IDs for controller and extenders retrieved successfully: {device_ids}")
    if len(all_device_ids) == len(unique_device_ids):
            report_logger.print_success(f"PASS: No duplicate AL MAC addresses found. "f"Total devices: {len(all_device_ids)}, "f"Unique AL MAC addresses: {len(unique_device_ids)}")
    else:
        report_logger.print_error(f"FAIL: Duplicate AL MAC address(es) found")
    report_logger.print_step("STEP 5: Requery DeviceNumberOfEntries for cross-checking from Controller DataElements")
    try:
        final_device_count = initialize.get_device_number_of_entries("controller", "de")
        if final_device_count is None:
            report_logger.print_error("FAIL: Failed to get DeviceNumberOfEntries from Controller")
        else:
            report_logger.print_success(f"PASS: DeviceNumberOfEntries retrieved successfully: {final_device_count}")
    except Exception as e:
        report_logger.print_error(f"FAIL: Failed to query DeviceNumberOfEntries from Controller: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    if int(final_device_count) == len(unique_device_ids):
        report_logger.print_success(f"PASS: DeviceNumberOfEntries matches the number of unique AL MAC addresses: "f"{final_device_count} == {len(unique_device_ids)}")
    else:
        report_logger.print_error(f"FAIL: DeviceNumberOfEntries does not match the number of unique AL MAC addresses: "f"{final_device_count} != {len(unique_device_ids)}")