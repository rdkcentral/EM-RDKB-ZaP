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
    timeout = initialize.read_from_database("test_parameters", "Endurance_test_duration_in_seconds")
    if timeout <= 0:
        pytest.fail("long duration test timeout must be greater than 0. please update the configuration \"Endurance_test_duration_in_seconds\" in platform.yaml")
    ctrl_local_dir = initialize.read_from_database("controller", "local_log_directory")
    if ctrl_local_dir == "</replace/with/local/path>":
        pytest.fail("Local log directory  is not set. Please update the configuration \"local_log_directory\" in platform.yaml")
    if not os.path.exists(ctrl_local_dir):
        pytest.fail(f"Local log directory {ctrl_local_dir} does not exist. Please create it or update the configuration in platform.yaml")

    report_logger.print_info("Starting monitoring script in controller")
    initialize.execute_command("controller", "python3 /nvram/monitoring_tool.py &")
    time.sleep(10)
    start_time = time.time()
    report_logger.print_step("STEP1: Starting long duration stability check loop for verifying core dump and backhaul status")
    while (time.time() - start_time) < timeout:
        report_logger.print_info(f"Test duration: {timeout / 60:.2f} minutes. Elapsed time: {(time.time() - start_time) / 60:.2f} minutes")
        report_logger.print_info("Checking core dump status in controller")
        if initialize.get_file_presence_status("controller", "/tmp/*dmp"):
            report_logger.print_error(f"[{get_timestamp()}] Core dump found on controller.")
            break
        else:
            report_logger.print_success("No core dump found on controller.")
        for device in devices[:]:
            if device != "controller":
                report_logger.print_info(f"Checking wireless backhaul status for {device}")
                if not initialize.get_wireless_backhaul_connection_status(device):
                    report_logger.print_error(f"[{get_timestamp()}] {device} is not connected to the backhaul.")
                    devices.remove(device)
                else:
                    report_logger.print_success(f"{device} is connected to the backhaul.")
        time.sleep(60)

    report_logger.print_info("Stopping monitoring script in controller")
    initialize.execute_command("controller", "pkill -f monitoring_tool.py")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ctrl_local_dir = os.path.join(ctrl_local_dir, "test_stability_long_duration_validation_" + str(timestamp))
    if not os.path.exists(ctrl_local_dir):
        os.makedirs(ctrl_local_dir)
    for log_file in LOG_PATHS:
        report_logger.print_info(f"checking presence of {log_file} on controller")
        if initialize.get_file_presence_status("controller", log_file):
            report_logger.print_info(f"Downloading log file locally and deleting remote file instance: {log_file}")
            initialize.get_file("controller", log_file, ctrl_local_dir)
            initialize.execute_command("controller", f"rm -f {log_file}")
            report_logger.print_step(f"STEP2: Analyzing downloaded log files in {ctrl_local_dir}")
            log_analyzer(ctrl_local_dir)
        else:
            report_logger.print_error(f"Log file not found on controller: {log_file}")
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_long_duration_validation")
