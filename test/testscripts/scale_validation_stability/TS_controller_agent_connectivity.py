# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
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

# Test Case: EM_Scale_ControllerAgent_Stability
# Topology: 1 Controller + N Agents (agent list driven by platform DB scale_agents)
# Validates that, once the expected EasyMesh scale topology has formed, it stays
# stable over test_duration_sec, polling every poll_interval_sec, using iw
# station dump / link (no Data Elements / rbuscli involved). For a one-time
# "did the topology form" check, see test_controller_agent_connectivity.py.

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import POLL_INTERVAL_SEC, SCALE_AGENTS, TEST_DURATION_SEC
from utility import (
    device_present, capture_topology, compare_agent_presence, backhaul_active,
    print_step, print_success, print_error, print_test, get_iw_dev_info,
)

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
    print_test("Entering test_em_scale_controller_agent_stability")
    configured_agents = SCALE_AGENTS
    AGENTS = [
        agent for agent in configured_agents
        if device_present(initialize, agent)
    ]
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC

    # ------------------------------------------------------------------
    # Step 1 — Verify onboarding and capture baseline topology
    # ------------------------------------------------------------------
    print_step("Step 1: Verify onboarding and capture baseline topology")

    expected_agent_count = len(AGENTS)

    # Verify each Agent is reachable (basic iw command check)
    for agent in AGENTS:
        for attempt in range(1, 7):
            try:
                output = get_iw_dev_info(initialize, agent)
                if output:
                    print_success(f"Agent '{agent}' is reachable")
                    break
            except Exception as err:
                print_step(f"Attempt {attempt}: Agent '{agent}' not ready — {err}")
            time.sleep(10)
        else:
            msg = f"Agent '{agent}' did not become reachable before baseline capture"
            print_error(msg)
            pytest.fail(msg)

    baseline = capture_topology(initialize, AGENTS)
    print_step(f"BASELINE TOPOLOGY: {baseline}")

    if len(baseline["agent_macs"]) != expected_agent_count:
        msg = (
            f"Baseline agent count {len(baseline['agent_macs'])} "
            f"!= expected {expected_agent_count}. "
            f"Found: {baseline['agent_macs']}"
        )
        print_error(msg)
        pytest.fail(msg)

    print_success(
        f"Baseline captured: {len(baseline['agent_macs'])} agents"
    )

    # ------------------------------------------------------------------
    # Step 2 — Confirm initial network stability
    # ------------------------------------------------------------------
    print_step("Step 2: Confirm initial network stability")

    for agent in AGENTS:
        for attempt in range(1, 13):
            try:
                if backhaul_active(initialize, agent):
                    print_success(f"Agent '{agent}' backhaul active")
                    break
                raise RuntimeError("Backhaul link not yet established")
            except Exception as err:
                print_step(
                    f"Attempt {attempt}: Agent '{agent}' backhaul not yet stable — {err}"
                )
            time.sleep(10)
        else:
            msg = f"Agent '{agent}' backhaul is not stable at test start"
            print_error(msg)
            pytest.fail(msg)

    # ------------------------------------------------------------------
    # Step 3 — Periodic topology checks
    # ------------------------------------------------------------------
    print_step("Step 3: Periodic agent presence checks")

    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < test_duration_sec:
        elapsed_min = int((time.time() - start_time) / 60)
        poll_count += 1
        print_step(f"Poll #{poll_count} at ~{elapsed_min} min elapsed")

        current = capture_topology(initialize, AGENTS)
        mismatches = compare_agent_presence(
            expected_agent_count, baseline, current
        )
        if mismatches:
            msg = (
                f"Poll #{poll_count} ({elapsed_min} min): "
                f"Agent presence mismatch — {mismatches}"
            )
            print_error(msg)
            pytest.fail(msg)
        print_success(
            f"Poll #{poll_count}: Expected {expected_agent_count} agents "
            "remain present"
        )

        time.sleep(poll_interval_sec)

    # ------------------------------------------------------------------
    # Step 4 — Final topology comparison against baseline
    # ------------------------------------------------------------------
    print_step("Step 4: Final agent presence check")

    final = capture_topology(initialize, AGENTS)
    print_step(f"FINAL TOPOLOGY: {final}")
    final_mismatches = compare_agent_presence(
        expected_agent_count, baseline, final
    )

    if final_mismatches:
        msg = f"Final agent presence does not match baseline: {final_mismatches}"
        print_error(msg)
        pytest.fail(msg)

    # Verify each Agent's backhaul is still active
    for agent in AGENTS:
        try:
            if not backhaul_active(initialize, agent):
                msg = f"Agent '{agent}' backhaul is down at end of test"
                print_error(msg)
                pytest.fail(msg)
        except Exception as err:
            msg = f"Agent '{agent}' backhaul check failed at end of test: {err}"
            print_error(msg)
            pytest.fail(msg)

    print_success(
        f"Final agent presence matches baseline: "
        f"{len(final['agent_macs'])} agents"
    )
    print_test("Exiting test_em_scale_controller_agent_stability")
