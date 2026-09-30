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
from stability_config import LOG_PATHS, SSID_UPDATE_WAITING_TIME
from stability_utils import *
from datetime import datetime
from rdkbmeshzap.common_utils import report_logger


def test_stability_ssid_update_stress(initialize, common_setup):
    """
    Test to verify the stability of SSID updates over multiple iterations and ensure that all devices correctly reflect the updated SSID.
    """
    report_logger.print_test(f"[{get_timestamp()}] Entering test_stability_ssid_update_stress")
    devices = common_setup
    ssid_update_max_count = initialize.read_from_database("test_parameters", "ssid_update_max_count")
    if ssid_update_max_count <= 0:
        pytest.fail("ssid_update_max_count must be greater than 0. please update the configuration \"ssid_update_max_count\"in platform.yaml")

    ctrl_local_dir = initialize.read_from_database("controller", "local_log_directory")
    if ctrl_local_dir == "</replace/with/local/path>":
        pytest.fail("Local log directory  is not set. Please update the configuration \"local_log_directory\" in platform.yaml")
    if not os.path.exists(ctrl_local_dir):
        pytest.fail(f"Local log directory {ctrl_local_dir} does not exist. Please create it or update the configuration in platform.yaml")

    report_logger.print_info("Starting monitor_service in controller")
    initialize.execute_command("controller", "python3 /nvram/monitoring_tool.py &")
    ssid_update_current_count = 0
    report_logger.print_step("Step1: Fetching initial SSID from controller")
    try:
        initial_ssid = initialize.get_ssid("controller", "2g_ssid_index", 'de')
    except Exception as ERR:
        pytest.fail(f"Failed to get initial SSID from controller: {ERR}")

    report_logger.print_step("Step2: Starting SSID update procedure")
    while ssid_update_current_count < ssid_update_max_count:
        ssid_update_current_count += 1
        ssid = initialize.get_random_ssid()
        report_logger.print_info(f"Iteration: {ssid_update_current_count}")
        report_logger.print_info(f"Updating SSID to {ssid}")
        initialize.set_ssid("controller", "mld_iface_index", ssid, 'gui')
        time.sleep(SSID_UPDATE_WAITING_TIME)
        for device in devices[:]:
            try:
                report_logger.print_info(f"Checking SSID on {device}")
                initialize.check_ssid(device, "mld_iface_index", ssid, 'cli')
            except Exception as ERR:
                report_logger.print_error(f"Iteration: {ssid_update_current_count} check_ssid failed in {device}: {ERR}")
                devices.remove(device)
            else:
                report_logger.print_success(f"SSID matched successfully in {device}")
        if not devices:
            break
    report_logger.print_info("Stopping monitor_service in controller")
    initialize.execute_command("controller", "pkill -f monitoring_tool.py")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ctrl_local_dir = os.path.join(ctrl_local_dir, "test_stability_ssid_update_stress_" + str(timestamp))
    if not os.path.exists(ctrl_local_dir):
        os.makedirs(ctrl_local_dir)

    log_file_presence_status = False
    for log_file in LOG_PATHS:
        report_logger.print_info(f"checking presence of {log_file} on controller")
        if initialize.get_file_presence_status("controller", log_file):
            report_logger.print_info(f"Downloading log file locally and deleting remote file instance: {log_file}")
            initialize.get_file("controller", log_file, ctrl_local_dir)
            initialize.execute_command("controller", f"rm -f {log_file}")
            log_file_presence_status = True
        else:
            report_logger.print_error(f"Log file not found on controller: {log_file}")

    if log_file_presence_status:
        log_file_presence_status = False
        report_logger.print_step(f"Step3: Analyzing downloaded log files in {ctrl_local_dir}")
        log_analyzer(ctrl_local_dir)

    report_logger.print_step("Step4: Reverting SSID to initial value")
    initialize.set_ssid("controller", "mld_iface_index", initial_ssid, 'gui')
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_ssid_update_stress")
