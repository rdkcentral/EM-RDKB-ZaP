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
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import get_scale_setup

def test_em_scale_controller_agent_connectivity(initialize):
    """
    Verify that the configured number of scale agents is present.
    """
    report_logger.print_test("Entering test_em_scale_controller_agent_connectivity")
    report_logger.print_step(
        "STEP 1: Read the configured scale agent list from the platform database"
    )
    agents = device_utils.get_enabled_extenders(initialize)
    report_logger.print_info(
        f"INFO: Discovered {len(agents)} configured scale devices: {agents}"
    )
    expected_agent_count = get_scale_setup(initialize)["expected_agent_count"]
    actual_agent_count = len(agents)
    report_logger.print_step("STEP 2: Validate the configured scale device count")
    report_logger.print_info(
        f"INFO: Expected result: {expected_agent_count} configured scale devices"
    )
    report_logger.print_info(
        f"INFO: Observed result: {actual_agent_count} configured scale devices"
    )
    if actual_agent_count != expected_agent_count:
        message = (
            f"Expected {expected_agent_count} configured scale devices, "
            f"but found {actual_agent_count}: {agents}"
        )
        report_logger.print_error(message)
    else:
        report_logger.print_success(
            f"PASS: Found the expected {actual_agent_count} configured scale devices"
        )
    report_logger.print_test("Exiting test_em_scale_controller_agent_connectivity")
