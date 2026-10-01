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

import time

def test_em_scale_controller_agent_stability(initialize):
    """
    EM_Scale_ControllerAgent_Stability — 1 Controller + N Agents.

    Steps:
            1. Verify all Agents are onboarded; capture baseline topology.
      2. Confirm network stability at the start of the test duration.
            3. Periodically verify the expected agents remain present for
                 test_duration_sec, every poll_interval_sec.
            4. Capture the final agent topology and verify it against the baseline.
    """
    report_logger.print_test("Entering test_em_scale_controller_agent_stability")
    AGENTS = device_utils.get_enabled_extenders(initialize)
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC

    # ------------------------------------------------------------------
    # Step 1 — Verify onboarding and capture baseline topology
    # ------------------------------------------------------------------
    report_logger.print_step(
        "STEP 1: Verify every configured device responds to an iw interface query"
    )

    expected_agent_count = get_scale_setup(initialize)["expected_agent_count"]

    # Verify each device is reachable (basic iw command check)
    for agent in AGENTS:
        for attempt in range(1, 7):
            try:
                output = initialize.get_iw_dev_info(agent)
                if output:
                    report_logger.print_success(
                        f"PASS: Device '{agent}' is reachable"
                    )
                    break
            except Exception as err:
                report_logger.print_info(
                    f"INFO: Attempt {attempt}: Device '{agent}' not ready — {err}"
                )
            time.sleep(10)
        else:
            msg = f"Device '{agent}' did not become reachable before baseline capture"
            report_logger.print_error(msg)
            pytest.fail(msg)

    report_logger.print_step(
        "STEP 2: Capture controller and agent station MACs for the baseline topology"
    )
    baseline = capture_topology(initialize, AGENTS)
    report_logger.print_info(f"INFO: Baseline topology snapshot: {baseline}")

    if len(baseline["agent_macs"]) != expected_agent_count:
        msg = (
            f"Baseline agent count {len(baseline['agent_macs'])} "
            f"!= expected {expected_agent_count}. "
            f"Found: {baseline['agent_macs']}"
        )
        report_logger.print_error(msg)
        pytest.fail(msg)

    report_logger.print_success(
        f"PASS: Baseline captured: {len(baseline['agent_macs'])} agents"
    )

    # ------------------------------------------------------------------
    # Step 2 — Confirm initial network stability
    # ------------------------------------------------------------------
    report_logger.print_step(
        "STEP 3: Confirm every agent has an active backhaul before monitoring"
    )

    for agent in AGENTS:
        for attempt in range(1, 13):
            try:
                if backhaul_active(initialize, agent):
                    report_logger.print_success(
                        f"PASS: Device '{agent}' backhaul active"
                    )
                    break
                raise RuntimeError("Backhaul link not yet established")
            except Exception as err:
                report_logger.print_info(
                    f"INFO: Attempt {attempt}: Device '{agent}' backhaul "
                    f"not yet stable — {err}"
                )
            time.sleep(10)
        else:
            msg = f"Device '{agent}' backhaul is not stable at test start"
            report_logger.print_error(msg)
            pytest.fail(msg)

    # ------------------------------------------------------------------
    # Step 3 — Periodic topology checks
    # ------------------------------------------------------------------
    report_logger.print_step(
        "STEP 4: Periodically compare agent presence with the baseline topology"
    )

    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < test_duration_sec:
        elapsed_min = int((time.time() - start_time) / 60)
        poll_count += 1
        report_logger.print_step(
            "STEP 4: Compare current topology with the baseline"
        )
        report_logger.print_info(
            f"INFO: Topology poll #{poll_count} at ~{elapsed_min} min elapsed"
        )

        current = capture_topology(initialize, AGENTS)
        mismatches = compare_agent_presence(
            expected_agent_count, baseline, current
        )
        if mismatches:
            msg = (
                f"Poll #{poll_count} ({elapsed_min} min): "
                f"Agent presence mismatch — {mismatches}"
            )
            report_logger.print_error(msg)
            pytest.fail(msg)
        report_logger.print_success(
            f"PASS: Poll #{poll_count}: Expected {expected_agent_count} agents "
            "remain present"
        )

        time.sleep(poll_interval_sec)

    # ------------------------------------------------------------------
    # Step 4 — Final topology comparison against baseline
    # ------------------------------------------------------------------
    report_logger.print_step(
        "STEP 5: Capture final agent presence and verify every backhaul remains active"
    )

    final = capture_topology(initialize, AGENTS)
    report_logger.print_info(f"INFO: Final topology snapshot: {final}")
    final_mismatches = compare_agent_presence(
        expected_agent_count, baseline, final
    )

    if final_mismatches:
        msg = f"Final agent presence does not match baseline: {final_mismatches}"
        report_logger.print_error(msg)
        pytest.fail(msg)

    # Verify each Agent's backhaul is still active
    for agent in AGENTS:
        try:
            if not backhaul_active(initialize, agent):
                msg = f"Device '{agent}' backhaul is down at end of test"
                report_logger.print_error(msg)
                pytest.fail(msg)
        except Exception as err:
            msg = f"Device '{agent}' backhaul check failed at end of test: {err}"
            report_logger.print_error(msg)
            pytest.fail(msg)

    report_logger.print_success(
        f"PASS: Final agent presence matches baseline: "
        f"{len(final['agent_macs'])} agents"
    )
    report_logger.print_test("Exiting test_em_scale_controller_agent_stability")
