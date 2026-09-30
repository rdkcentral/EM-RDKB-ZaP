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
from stability_config import FRONTHAUL_TOGGLE_WAITING_TIME
from stability_utils import *
from datetime import datetime
from rdkbmeshzap.common_utils import report_logger


def test_stability_fronthaul_toggle_stress(initialize, common_setup):
    """
    Test to verify the stability of fronthaul network profile toggles over multiple iterations and ensure that all devices correctly reflect the updated MLD status.
    """
    report_logger.print_test(f"[{get_timestamp()}] Entering test_stability_fronthaul_toggle_stress")
    initial_mld_status = None
    devices = common_setup
    fronthaul_toggle_max_count = initialize.read_from_database("test_parameters", "fronthaul_toggle_max_count")
    if fronthaul_toggle_max_count <= 0:
        pytest.fail("fronthaul_toggle_max_count must be greater than 0. please update the configuration \"fronthaul_toggle_max_count\" in platform.yaml")
    fronthaul_toggle_current_count = 0
    report_logger.print_step("Step1: Starting fronthaul toggle procedure")
    while fronthaul_toggle_current_count < fronthaul_toggle_max_count:
        report_logger.print_info(f"Iteration: {fronthaul_toggle_current_count + 1}")
        report_logger.print_info("Fetching current MLD status from the controller")
        current_mld_status = initialize.get_mld_status("controller")
        if initial_mld_status is None:
            initial_mld_status = current_mld_status
        report_logger.print_info(f"Current MLD status from the controller: {current_mld_status}")
        set_mld_status = not current_mld_status
        report_logger.print_info(f"Setting MLD status to: {set_mld_status}")
        initialize.set_fronthaul_network_state("controller", "Home Network", enable=set_mld_status)
        fronthaul_toggle_current_count += 1
        time.sleep(FRONTHAUL_TOGGLE_WAITING_TIME)
        for device in devices[:]:
            report_logger.print_info(f"Fetching current MLD status from the device {device}")
            mld_status = initialize.get_mld_status(device)
            if mld_status != set_mld_status:
                report_logger.print_error(f"Iteration: {fronthaul_toggle_current_count} Fronthaul network profile toggle failed in {device}: expected {set_mld_status}, got {mld_status}")
                devices.remove(device)
            else:
                report_logger.print_success(f"Iteration: {fronthaul_toggle_current_count} Fronthaul network profile toggle succeeded in {device}")
        if not devices:
            break

    report_logger.print_step("Step2: Enabling MLD status for clearing any previous toggles")
    initialize.set_fronthaul_network_state("controller", "Home Network", enable=True)
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_fronthaul_toggle_stress")
