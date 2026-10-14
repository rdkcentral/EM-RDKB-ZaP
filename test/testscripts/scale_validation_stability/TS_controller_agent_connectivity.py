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
import time
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_controller_agent_stability(initialize):
    """
    Verify agent reachability and backhaul stability without MAC verification.
    """
    report_logger.print_test("Entering test_em_scale_controller_agent_stability")
    agents = device_utils.get_enabled_extenders(initialize)
    expected_agent_count = get_enabled_scale_setup(initialize)["expected_agent_count"]
    actual_agent_count = len(agents)
    report_logger.print_step("STEP 1: Validate that the configured scale-agent count matches the discovered count")
    if actual_agent_count < expected_agent_count:
        report_logger.print_error(f"Expected {expected_agent_count} configured scale agents, but found {actual_agent_count}: {agents}")
    report_logger.print_success(f"PASS: Found {actual_agent_count} configured scale agents")
    report_logger.print_step("STEP 2: Verify every scale agent is reachable and returns iw interface data")
    for agent_index, agent in enumerate(agents, start=1):
        report_logger.print_step(f"STEP 2.{agent_index}: Query iw interface data for scale agent '{agent}' and validate reachability")
        try:
            if not initialize.get_iw_dev_info(agent):
                report_logger.print_error(f"Device '{agent}' returned empty iw output")
            report_logger.print_success(f"PASS: Device '{agent}' is reachable")
        except Exception as err:
            report_logger.print_error(f"Device '{agent}' reachability check failed: {err}")
    report_logger.print_step("STEP 3: Capture baseline agent presence and validate the expected topology")
    baseline = get_extender_presence_snapshot(initialize, agents)
    report_logger.print_info(f"INFO: Baseline topology snapshot: {baseline}")
    baseline_mismatches = get_extender_presence_mismatches(
        expected_agent_count, baseline, baseline)
    if baseline_mismatches:
        report_logger.print_error(f"Baseline topology validation failed: {baseline_mismatches}")
    report_logger.print_step("STEP 4: Poll agent presence and report topology mismatches against the baseline")
    end_time = time.time() + TEST_DURATION_SEC
    poll_count = 0
    while time.time() < end_time:
        poll_count += 1
        current = get_extender_presence_snapshot(initialize, agents)
        mismatches = get_extender_presence_mismatches(
            expected_agent_count, baseline, current)
        report_logger.print_info(f"INFO: Poll #{poll_count} completed")
        if mismatches:
            report_logger.print_error(f"Topology mismatch at poll #{poll_count}: {mismatches}")
        remaining_time = end_time - time.time()
        if remaining_time > 0:
            time.sleep(min(POLL_INTERVAL_SEC, remaining_time))
    report_logger.print_step("STEP 5: Capture final agent presence and validate it against the baseline topology")
    final = get_extender_presence_snapshot(initialize, agents)
    final_mismatches = get_extender_presence_mismatches(
        expected_agent_count, baseline, final)
    if final_mismatches:
        report_logger.print_error(f"Final topology mismatch: {final_mismatches}")
    report_logger.print_test("Exiting test_em_scale_controller_agent_stability")
