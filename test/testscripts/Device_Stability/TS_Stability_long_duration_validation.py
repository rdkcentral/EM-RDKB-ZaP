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
import os
import pytest
import time
from stability_config import LOG_PATHS
from stability_utils import *
from datetime import datetime
from rdkbmeshzap.common_utils import report_logger


def test_stability_long_duration_validation(initialize, common_setup):
    """
    Test to verify the stability of the system over a 24-hour period.
    """
    report_logger.print_test(f"[{get_timestamp()}] Entering test_stability_long_duration_validation")
    devices = common_setup
    report_logger.print_step(f"Step 1: retrieving time duration and local log directory details from configuration file")
    timeout = initialize.read_from_database("test_parameters", "device_stability", "Endurance_test_duration_in_seconds")
    if timeout <= 0:
        pytest.fail("long duration test timeout must be greater than 0. please update the configuration \"Endurance_test_duration_in_seconds\".")
    report_logger.print_info(f"Retrieved long duration stability test timeout: {timeout} seconds")

    ctrl_local_dir = initialize.read_from_database("controller", "local_log_directory")
    if ctrl_local_dir == "</replace/with/local/path>":
        pytest.fail("Local log directory  is not set. Please update the configuration \"local_log_directory\".")
    else:
        report_logger.print_info(f"Retrieved local_log_directory: {ctrl_local_dir}")
        
    if not os.path.exists(ctrl_local_dir):
        pytest.fail(f"Local log directory {ctrl_local_dir} does not exist. Please create it or update the configuration.")
    else:
        report_logger.print_info(f"Local log directory {ctrl_local_dir} exists.")
    report_logger.print_success("PASS: Successfully retrieved local log directory and test duration")

    report_logger.print_step("Step 2: Start monitoring script in controller")
    initialize.execute_command("controller", "python3 /nvram/monitoring_tool.py &")
    time.sleep(5)
    report_logger.print_success("PASS: Monitoring script started in controller")

    start_time = time.time()
    report_logger.print_step("Step 3: Starting long duration stability check loop for verifying core dump and backhaul status")
    step_count = 3
    sub_step_count = 1
    while (time.time() - start_time) < timeout:
        report_logger.print_info(f"Test duration: {timeout / 60:.2f} minutes. Elapsed time: {(time.time() - start_time) / 60:.2f} minutes")
        report_logger.print_step(f"Step {step_count}.{sub_step_count}: Checking for core dump files in controller")
        if initialize.get_file_presence_status("controller", "/tmp/*dmp"):
            report_logger.print_error(f"[{get_timestamp()}] controller: Core dump detected.")
            break
        else:
            report_logger.print_success(f"PASS: No core dump found on controller.")
        sub_step_count += 1

        for device in devices[:]:
            if device != "controller":
                report_logger.print_step(f"Step {step_count}.{sub_step_count}: Checking wireless backhaul status for {device}")
                sub_step_count += 1
                try:
                    if not initialize.get_wireless_backhaul_connection_status(device):
                        report_logger.print_error(f"[{get_timestamp()}] {device}: not connected to the backhaul.")
                        devices.remove(device)
                    else:
                        report_logger.print_success(f"PASS: {device} is connected to the backhaul.")
                except Exception as e:
                    report_logger.print_error(f"[{get_timestamp()}] {device}: Error occurred while checking backhaul status: {e}")
                    devices.remove(device)
        time.sleep(30)

    step_count += 1
    report_logger.print_step(f"Step {step_count}: Stopping monitoring script in controller")
    initialize.execute_command("controller", "pkill -f monitoring_tool.py")
    report_logger.print_success("PASS: Monitoring script stopped in controller")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ctrl_local_dir = os.path.join(ctrl_local_dir, "test_stability_long_duration_validation_" + str(timestamp))
    if not os.path.exists(ctrl_local_dir):
        os.makedirs(ctrl_local_dir)

    step_count += 1
    sub_step_count = 0
    available_log_files = []
    report_logger.print_step(f"Step {step_count}: Checking for presence of log files on controller")
    for log_file in LOG_PATHS:
        sub_step_count += 1
        report_logger.print_step(f"Step {step_count}.{sub_step_count}: checking presence of {log_file} on controller")
        if initialize.get_file_presence_status("controller", log_file):
            available_log_files.append(os.path.basename(log_file))
            report_logger.print_success(f"PASS: Log file found on controller.")
            report_logger.print_step(f"Step {step_count}.{sub_step_count}: Downloading log file locally and deleting remote file instance.")
            initialize.get_file("controller", log_file, ctrl_local_dir)
            initialize.execute_command("controller", f"rm -f {log_file}")
            report_logger.print_success(f"PASS: Log file downloaded and deleted the file from controller")
        else:
            report_logger.print_error(f"Controller: Log file not found : {log_file}")
    for log_file in available_log_files:
        step_count += 1
        log_file_path = os.path.join(ctrl_local_dir, log_file)
        log_analyzer(log_file_path, step_count)
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_long_duration_validation")
