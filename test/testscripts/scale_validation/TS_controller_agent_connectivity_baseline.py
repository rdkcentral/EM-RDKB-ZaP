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
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_controller_agent_connectivity(initialize):
    """
    Verify that the configured number of Agents is connected to the Controller.
    """
    report_logger.print_test("Entering test_em_scale_controller_agent_connectivity")
    report_logger.print_step("STEP 1: Read the controller's configured scale agent list from the platform database")
    agents = device_utils.get_enabled_extenders(initialize)
    report_logger.print_info(
        f"INFO: Discovered {len(agents)} configured scale devices: {agents}"
    )
    expected_agent_count = get_scale_setup(initialize)["expected_agent_count"]
    report_logger.print_step(
        "STEP 2: Validate the controller sees the expected scale devices"
    )
    report_logger.print_info(
        f"INFO: Expected result: Controller should report "
        f"{expected_agent_count} connected scale devices"
    )
    connected_agent_macs = get_backhaul_info(
        initialize, agents, controller="controller"
    )["agent_macs"]
    actual_agent_count = len(connected_agent_macs)
    report_logger.print_info(
        f"INFO: Observed result: Controller station dump reported "
        f"{actual_agent_count} connected device MACs: {sorted(connected_agent_macs)}"
    )
    if actual_agent_count < expected_agent_count:
        msg = (
            f"Expected scale devices are not present. Expected {expected_agent_count} "
            f"devices, but only {actual_agent_count} were connected. "
            f"Found connected MACs: {sorted(connected_agent_macs)}"
        )
        report_logger.print_error(msg)
        pytest.fail(msg)
    report_logger.print_success(
        f"PASS: Expected scale devices are present. "
        f"Expected {expected_agent_count} devices and controller sees {actual_agent_count} connected device MACs: "
        f"{sorted(connected_agent_macs)}"
    )
    report_logger.print_test("Exiting test_em_scale_controller_agent_connectivity")
