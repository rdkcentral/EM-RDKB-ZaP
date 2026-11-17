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

import time
from rdkbmeshzap.common_utils import device_utils, recovery_utils, report_logger
from rdkbmeshzap.common_utils.scale_validation_utils import *

def test_em_scale_controller_recovery_after_reboot(initialize):
    """Monitor recovery of the scale setup after repeated controller reboots."""
    report_logger.print_test(f"Entering test_em_scale_controller_recovery_after_reboot")
    try:
        agents = device_utils.get_enabled_extenders(initialize)
        if not agents:
            report_logger.print_error("No enabled extenders are available for scale validation")
            return
        expected_count = get_enabled_scale_setup(initialize)["expected_agent_count"]
        report_logger.print_step("STEP 1: Capture the initial scale setup baseline")
        baseline = get_extender_presence_snapshot(initialize, agents)
        baseline_mismatches = get_extender_presence_mismatches(
            expected_count, baseline, baseline)
        if baseline_mismatches:
            report_logger.print_error(f"FAIL: Initial scale setup is incomplete: {baseline_mismatches}")
            return
        recovery_kpi = recovery_utils.get_recovery_kpi(initialize, "controller")
        baseline_agents = set(baseline["agents"])
        test_end = time.monotonic() + TEST_DURATION_SEC
        next_cycle_at = time.monotonic()
        cycle = 0
        while next_cycle_at < test_end:
            wait_time = next_cycle_at - time.monotonic()
            if wait_time > 0:
                time.sleep(wait_time)
            if time.monotonic() >= test_end:
                break
            cycle += 1
            report_logger.print_step(f"STEP {cycle + 1}: Reboot controller and recover the scale setup (cycle {cycle}, scheduled every {POLL_INTERVAL_SEC} seconds)")
            cycle_started_at = time.monotonic()
            started_at = cycle_started_at
            try:
                initialize.reboot_device("controller", method="cli")
            except Exception as error:
                report_logger.print_error(f"FAIL: Controller cycle {cycle} reboot command failed: {error}")
                return
            report_logger.print_step(f"STEP {cycle + 1}.1: Wait for controller service recovery")
            recovery_results = {}
            try:
                recovery_utils.recover_device(initialize, "controller", started_at, recovery_results, recovery_type="controller")
            except Exception as error:
                recovery_results["controller"] = error
            recovery_time = recovery_results.get("controller")
            if (not isinstance(recovery_time, (int, float))or isinstance(recovery_time, bool)):
                report_logger.print_error(f"FAIL: Controller cycle {cycle} recovery result is unavailable or failed: {recovery_time}")
                return
            if recovery_time > recovery_kpi:
                report_logger.print_error(f"FAIL: Controller cycle {cycle} recovery took {recovery_time:.1f}s; limit is {recovery_kpi}s")
                return
            report_logger.print_success(f"PASS: Controller recovered in {recovery_time:.1f}s during cycle {cycle}, within the {recovery_kpi}s limit")
            report_logger.print_step(f"STEP {cycle + 1}.2: Wait for the scale setup to stabilize for up to {POLL_INTERVAL_SEC} seconds")
            stabilization_deadline = time.monotonic() + POLL_INTERVAL_SEC
            stabilized = False
            current = baseline
            while time.monotonic() < stabilization_deadline:
                current = get_extender_presence_snapshot(initialize, agents)
                mismatches = get_extender_presence_mismatches(
                    expected_count, baseline, current)
                current_agents = set(current["agents"])
                if current_agents != baseline_agents:
                    mismatches.append(f"Agent set changed: baseline={sorted(baseline_agents)} current={sorted(current_agents)}")
                if current["agent_count"] != expected_count:
                    mismatches.append(f"Agent count mismatch: expected={expected_count} current={current['agent_count']}")
                if not mismatches:
                    stabilized = True
                    break
                remaining = stabilization_deadline - time.monotonic()
                if remaining <= 0:
                    break
                report_logger.print_info(f"INFO: Scale setup is still converging; retrying in {STABILIZATION_POLL_INTERVAL_SEC} seconds: {mismatches}")
                time.sleep(min(STABILIZATION_POLL_INTERVAL_SEC, remaining))
            if not stabilized:
                mismatches = get_extender_presence_mismatches(
                    expected_count, baseline, current)
                report_logger.print_error(f"FAIL: Initial scale setup did not stabilize after controller cycle {cycle}: {mismatches}")
                return
            report_logger.print_success(f"PASS: Initial scale setup recovered with {current['agent_count']} connected agents after cycle {cycle}")
            next_cycle_at = cycle_started_at + POLL_INTERVAL_SEC
            if next_cycle_at < test_end:
                report_logger.print_info(f"INFO: Waiting for the next recovery cycle at the {POLL_INTERVAL_SEC}-second interval")
        report_logger.print_success(f"PASS: Initial scale setup recovery was verified across {cycle} scheduled controller recovery cycles during {TEST_DURATION_SEC} seconds")
    finally:
        report_logger.print_test(f"Exiting test_em_scale_controller_recovery_after_reboot")