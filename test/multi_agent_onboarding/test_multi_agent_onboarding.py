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
from zaero.utils import zi_logger

# ---------------------------------------------------------------------------
# Test Case-1: EM_Mutli_Agent_Onboarding_Topology_Device_Count
# ---------------------------------------------------------------------------

def test_multi_agent_onboarding_topology_device_count(initialize):
    zi_logger.print_step(
        "-------------------------------- EM Multi-Agent Onboarding Topology Device Count Test Case --------------------------------")
    zi_logger.print_step("Step 1: Get initial topology device count for controller from DataElements")
    try:
        device_count = initialize.get_device_number_of_entries("controller", "de")
        if device_count is None:
            zi_logger.print_error("FAIL: Failed to get device count for controller from DataElements")
        else:
            zi_logger.print_success(f"PASS: Device count for controller retrieved successfully: {device_count}")
    except Exception as e:
        zi_logger.print_error(f"Failed to query device count for controller: {e}")
    zi_logger.print_step("Step 2: Get device ID for controller and 3 extenders from DataElements")
    present_devices = []
    index = []
    if initialize.read_from_database("controller", "device_present"):
        controller_index = initialize.read_from_database("controller", "controller_device_index")
        present_devices.append("controller")
        index.append(controller_index)

    devices = initialize.get_enabled_extenders()
    zi_logger.print_success(f"{devices}")
    for device in devices:
        if initialize.read_from_database(device, "device_present"):
            present_devices.append(device)
            index.append(initialize.read_from_database("controller", f"{device}_device_index"))
        else:
            zi_logger.print_step(f"{device} is not present in the network. Skipping device ID retrieval.")
    print(present_devices)
    print(index)
    device_ids = {}
    for i in range(len(index)):
        device = present_devices[i]
        ids = initialize.get_device_id("controller", index[i],"de")
        if not ids:
            zi_logger.print_error(f"FAIL: Failed to get device ID for {device} from DataElements")
        else:
            device_ids[device] = ids
            zi_logger.print_success(f"PASS: Device ID for {device} retrieved successfully: {ids}")
    print(device_ids)
    zi_logger.print_step(f"Step 3: Cross-reference each returned AL MAC against the known MAC addresses for controller and 3 extenders from DataElements")
    for device in devices:
        if initialize.read_from_database(device, "device_present"):
            try:
                bssid = initialize.get_al_mac_address(device)
                if bssid == device_ids[device]:
                    zi_logger.print_success(f"{device} BSSID matches the device ID: {bssid}")
                else:
                    zi_logger.print_error(f"{device} BSSID does not match the device ID: {bssid} != {device_ids[device]}")
            except Exception as e:
                zi_logger.print_error(f"FAIL: Failed to query BSSID for {device}: {e}")
    zi_logger.print_step(f"Step 4: Get device radio count for each extender from DataElements")
    radio_counts = {}
    for extender in devices[1:]:  # Skip the controller
        if initialize.read_from_database(extender, "device_present"):
            try:
                radio_count = initialize.get_radioNumberofentries("controller", f"{extender}_device_index","de")
                radio_counts[extender] = radio_count
                if not radio_count:
                    zi_logger.print_error(f"FAIL: Failed to get device radio count for {extender} from DataElements")
                else:
                    zi_logger.print_success(f"PASS: Device radio count for {extender} retrieved successfully: {radio_count}")
            except Exception as e:
                    zi_logger.print_error(f"FAIL: Exception while getting radio count for {extender}: {e}")
    zi_logger.print_step(f"Step 5: Compare initial and updated device counts after short idle time")
    time.sleep(10)
    try:
        updated_device_count = initialize.get_device_number_of_entries("controller", "de")
        if updated_device_count != device_count:
            zi_logger.print_error(f"FAIL: Device count mismatch: Initial count {device_count}, Updated count {updated_device_count}")
        else:
            zi_logger.print_success(f"PASS: Device count verified successfully: {updated_device_count}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query updated device count for controller: {e}")
    
# ---------------------------------------------------------------------------
# Test Case-2: EM_Mutli_Agent_Onboarding_No_Duplicate_Entries
# ---------------------------------------------------------------------------

def test_multi_agent_onborading_no_duplicate_entries(initialize):
    zi_logger.print_step("-------------------------------- EM Multi-Agent Onboarding No Duplicate Entries Test Case --------------------------------")
    zi_logger.print_step("Step 1: Get device-IDs of controller and all extenders from DataElements")
    present_devices = []
    index = []
    if initialize.read_from_database("controller", "device_present"):
        controller_index = initialize.read_from_database("controller", "controller_device_index")
        present_devices.append("controller")
        index.append(controller_index)

    devices = initialize.get_enabled_extenders()
    zi_logger.print_success(f"{devices}")
    for device in devices:
        if initialize.read_from_database(device, "device_present"):
            present_devices.append(device)
            index.append(initialize.read_from_database("controller", f"{device}_device_index"))
        else:
            zi_logger.print_step(f"{device} is not present in the network. Skipping device ID retrieval.")
    print(present_devices)
    print(index)
    device_ids = {}
    for i in range(len(index)):
        device = present_devices[i]
        ids = initialize.get_device_id("controller", index[i], "de")
        if not ids:
            zi_logger.print_error(f"FAIL: Failed to get device ID for {device} from DataElements")
        else:
            device_ids[device] = ids
            zi_logger.print_success(f"PASS: Device ID for {device} retrieved successfully: {ids}")
    print(device_ids)
    zi_logger.print_step("Step 2: Check for duplicate AL MAC addresses")
    all_device_ids = list(device_ids.values())
    unique_device_ids = set(all_device_ids)
    if len(all_device_ids) == len(unique_device_ids):
        zi_logger.print_success(f"PASS: No duplicate AL MAC addresses found. "f"Total devices: {len(all_device_ids)}, "f"Unique AL MAC addresses: {len(unique_device_ids)}")
    else:
        zi_logger.print_error(f"FAIL: Duplicate AL MAC address(es) found")
    zi_logger.print_step("Step 3: Get DeviceNumberOfEntries for cross-checking from Controller DataElements")
    try:
        device_count = initialize.get_device_number_of_entries("controller", "de")
        if device_count is None:
            zi_logger.print_error("Failed to get DeviceNumberOfEntries from Controller")
        else:
            zi_logger.print_success(f"PASS: DeviceNumberOfEntries retrieved successfully: {device_count}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query DeviceNumberOfEntries from Controller: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    # unique_device_count = len(unique_device_ids)
    print(f"DeviceNumberOfEntries: {device_count}, Unique AL MAC addresses: {len(unique_device_ids)}")
    if int(device_count) == len(unique_device_ids):
        zi_logger.print_success(f"PASS: DeviceNumberOfEntries matches the number of unique AL MAC addresses: "f"{device_count} == {len(unique_device_ids)}")
    else:
        zi_logger.print_error(f"FAIL: DeviceNumberOfEntries does not match the number of unique AL MAC addresses: "f"{device_count} != {len(unique_device_ids)}")
    zi_logger.print_step("Step 4: Reboot the extender and Requery device IDs from DataElements")
    initialize.reboot_device("extender1", "cli")
    initialize.close_connection("extender1")
    time.sleep(10)
    for i in range(1, 51):
        zi_logger.log(f"FOR loop iteration : {i}")
        try:
            initialize.connect_with_device("extender1")
        except Exception:
            zi_logger.print_error("FAIL: Connection FAILED with 'Extender1'", log_error=False)
        else:
            zi_logger.print_success("PASS: Connection SUCCESS with 'Extender1'")
            break
        time.sleep(10)
    else:
        pytest.fail("Could not re-establish connection with - extender1")
    for i in range(len(index)):
            device = present_devices[i]
            ids = initialize.get_device_id("controller", index[i], "de")
            if not ids:
                zi_logger.print_error(f"FAIL: Failed to get device IDs for controller and extenders from DataElements")
            else:
                device_ids[device] = ids
                zi_logger.print_success(f"Device IDs for controller and extenders retrieved successfully: {device_ids}")

            print(device_ids)
    if len(all_device_ids) == len(unique_device_ids):
            zi_logger.print_success(f"PASS: No duplicate AL MAC addresses found. "f"Total devices: {len(all_device_ids)}, "f"Unique AL MAC addresses: {len(unique_device_ids)}")
    else:
        zi_logger.print_error(f"FAIL: Duplicate AL MAC address(es) found")
    zi_logger.print_step("Step 5: Requery DeviceNumberOfEntries for cross-checking from Controller DataElements")
    try:
        final_device_count = initialize.get_device_number_of_entries("controller", "de")
        if final_device_count is None:
            zi_logger.print_error("FAIL: Failed to get DeviceNumberOfEntries from Controller")
        else:
            zi_logger.print_success(f"PASS: DeviceNumberOfEntries retrieved successfully: {final_device_count}")
    except Exception as e:
        zi_logger.print_error(f"FAIL: Failed to query DeviceNumberOfEntries from Controller: {e}")
        pytest.fail(f"DataElements query failed: {e}")
    if int(final_device_count) == len(unique_device_ids):
        zi_logger.print_success(f"PASS: DeviceNumberOfEntries matches the number of unique AL MAC addresses: "f"{final_device_count} == {len(unique_device_ids)}")
    else:
        zi_logger.print_error(f"FAIL: DeviceNumberOfEntries does not match the number of unique AL MAC addresses: "f"{final_device_count} != {len(unique_device_ids)}")