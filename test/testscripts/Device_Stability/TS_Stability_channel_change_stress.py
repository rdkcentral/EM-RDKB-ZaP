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

import pytest
import time
from stability_config import CHANNEL_UPDATE_WAITING_TIME
from stability_utils import *
from datetime import datetime
from rdkbmeshzap.common_utils import report_logger


def test_stability_channel_change_stress(initialize, common_setup):
    """
    Test to verify the stability of channel updates over multiple iterations and ensure that all devices correctly reflect the updated channel.
    """
    report_logger.print_test(f"[{get_timestamp()}] Entering test_stability_channel_change_stress")
    initial_channel_number = None
    report_logger.print_step("Step 1: Retrieving test parameter")
    channel_update_max_count = initialize.read_from_database("test_parameters", "device_stability", "channel_update_max_count")
    if channel_update_max_count <= 0:
        pytest.fail("channel_update_max_count must be greater than 0. please update the configuration \"channel_update_max_count\".")
    report_logger.print_info(f"Channel update max count: {channel_update_max_count}")
    report_logger.print_success("PASS: Successfully retrieved test parameter")
    
    devices = common_setup
    channel_update_current_count = 0
    report_logger.print_step("Step 2: Starting channel update procedure")
    step_count = 2
    sub_step_count = 0
    while channel_update_current_count < channel_update_max_count:
        sub_step_count += 1
        report_logger.print_info(f"Iteration: {channel_update_current_count + 1}")
        report_logger.print_step(f"Step{step_count}.{sub_step_count}: Fetching current operating channel from the controller")
        try:
            operating_channel = initialize.get_operating_channel("controller", "2.4")
        except Exception as e:
            report_logger.print_error(f"Failed to retrieve current operating channel from the controller: {e}")
            pytest.fail(f"Failed to retrieve current operating channel from the controller: {e}")
        report_logger.print_success(f"PASS: Retrieved current operating channel from the controller: {operating_channel}")
        
        sub_step_count += 1
        if initial_channel_number is None:
            initial_channel_number = operating_channel

        operating_channel_to_set = 6 if operating_channel != 6 else 1
        report_logger.print_step(f"Step{step_count}.{sub_step_count}: Setting operating channel to {operating_channel_to_set}")
        try:
            initialize.set_channel_preference_for_2_4_band("controller", uncheck_channel=operating_channel, check_channel=operating_channel_to_set, priority=14)
        except Exception as e:
            report_logger.print_error(f"Failed to set operating channel to {operating_channel_to_set}: {e}")
        else:
            report_logger.print_success(f"PASS: Successfully set operating channel to {operating_channel_to_set}")
            

        channel_update_current_count += 1
        time.sleep(CHANNEL_UPDATE_WAITING_TIME)
        for device in devices[:]:
            sub_step_count += 1
            report_logger.print_step(f"Step {step_count}.{sub_step_count}: Fetching current operating channel from the device {device}")
            try:
                current_operating_channel = initialize.get_operating_channel(device, "2.4")
                if current_operating_channel != operating_channel_to_set:
                    report_logger.print_error(f"{device}: Iteration: {channel_update_current_count} Channel update failed in {device}: expected {operating_channel_to_set}, got {current_operating_channel}")
                    devices.remove(device)
                else:
                    report_logger.print_success(f"PASS: Channel updated successfully in {device} to {current_operating_channel}")
            except Exception as e:
                report_logger.print_error(f"Failed to retrieve current operating channel from the device {device}: {e}")
                devices.remove(device)
        if not devices:
            break

    step_count += 1
    sub_step_count=1
    report_logger.print_step(f"Step {step_count}: Reverting channel number")
    try:
        report_logger.print_step(f"Step {step_count}.{sub_step_count}: Fetching current operating channel from the controller")
        operating_channel = initialize.get_operating_channel("controller", "2.4")
    except Exception as e:
        report_logger.print_error(f"Failed to fetch current operating channel from the controller: {e}")
    else:
        report_logger.print_success(f"PASS: Fetched current operating channel from the controller: {operating_channel}")

    sub_step_count += 1
    if initial_channel_number is not None and initial_channel_number != operating_channel:
        try:
                report_logger.print_step(f"Step {step_count}.{sub_step_count}: Reverting operating channel to {initial_channel_number}")
                initialize.set_channel_preference_for_2_4_band("controller", uncheck_channel=operating_channel, check_channel=initial_channel_number, priority=14)
        except Exception as e:
            report_logger.print_error(f"Failed to revert operating channel: {e}")
        else:
            report_logger.print_success(f"PASS: Successfully reverted operating channel to {initial_channel_number}")
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_channel_change_stress")
