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

from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_controller_agent_connectivity(initialize):
    """
    Verify that the configured number of scale extenders is present.
    """
    report_logger.print_test("Entering test_em_scale_controller_agent_connectivity")
    try:
        report_logger.print_step("STEP 1: Read the configured extender list and capture current active extenders")
        agents = device_utils.get_enabled_extenders(initialize)
        report_logger.print_info(f"INFO: Discovered {len(agents)} configured active extenders: {agents}")
        expected_agent_count = get_enabled_scale_setup(initialize)["expected_agent_count"]
        presence = get_extender_presence_snapshot(initialize, agents)
        actual_agent_count = presence["agent_count"]
        report_logger.print_step("STEP 2: Validate that the connected active extender count matches the configured count")
        if actual_agent_count < expected_agent_count:
            report_logger.print_error(f"Expected at least {expected_agent_count} connected active extenders, but found {actual_agent_count}: {sorted(presence['agents'])}")
        else:
            report_logger.print_success(f"PASS: Expected {expected_agent_count} active extenders, found {actual_agent_count}")
    finally:
        report_logger.print_test("Exiting test_em_scale_controller_agent_connectivity")
