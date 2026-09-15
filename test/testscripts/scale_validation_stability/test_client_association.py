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

# Test Case: EM_Scale_Client_Association
# Scale: Small (1 Controller + 2 Agents + 5 Clients)
# Validates that all clients remain associated to their respective Agents
# throughout the test duration using iw dev station dump.

import pytest
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import EXPECTED_CLIENT_COUNT, POLL_INTERVAL_SEC, SCALE_AGENTS, TEST_DURATION_SEC
from utility import (
    collect_fronthaul_associations,
    compare_associations,
    device_present,
    execute_on_device,
    print_step,
    total_associations,
)


BH_IFACE_KEY = "2g_bh_iface_index"


def test_em_scale_client_association(initialize):
    """
    EM_Scale_Client_Association — Small scale: 1 Controller + 2 Agents + 5 Clients.

    Steps:
      1. Verify all Agents are reachable; capture baseline associations.
      2. Verify backhaul links are active on all Agents.
      3. Periodically verify the expected client count and associations.
      4. Capture final associations and assert they match the baseline.
    """
    agents = [
        agent for agent in SCALE_AGENTS
        if device_present(initialize, agent)
    ]
    expected_client_count = EXPECTED_CLIENT_COUNT
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC
    all_devices = ["controller"] + agents

    print_step("Step 1: Verify topology and capture baseline associations")
    for agent in agents:
        for attempt in range(1, 7):
            try:
                output, _ = execute_on_device(initialize, agent, "iw dev")
                if output:
                    print(f"SUCCESS: Agent '{agent}' is reachable")
                    break
            except Exception as err:
                print(f"Attempt {attempt}: '{agent}' not ready — {err}")
            time.sleep(10)
        else:
            pytest.fail(
                f"Agent '{agent}' did not become reachable before baseline capture"
            )

    baseline = collect_fronthaul_associations(initialize, all_devices)
    total_baseline = total_associations(baseline)
    if total_baseline != expected_client_count:
        pytest.fail(
            f"Baseline client count {total_baseline} != expected "
            f"{expected_client_count}. Snapshot: {baseline}"
        )
    print(
        f"SUCCESS: Baseline captured: {total_baseline} clients "
        f"across {len(all_devices)} devices"
    )

    print_step("Step 2: Verify backhaul connectivity on all Agents")
    for agent in agents:
        wifi_ifname = initialize.read_from_database(agent, "wifi_ifname")
        bh_idx = initialize.read_from_database(agent, BH_IFACE_KEY)
        bh_iface = f"{wifi_ifname}{bh_idx}"
        for attempt in range(1, 13):
            try:
                output, _ = execute_on_device(
                    initialize, agent, f"iw dev {bh_iface} link"
                )
                if "Connected" in output or "SSID" in output:
                    print(
                        f"SUCCESS: Agent '{agent}' backhaul active on {bh_iface}"
                    )
                    break
                raise RuntimeError("Backhaul link not yet established")
            except Exception as err:
                print(f"Attempt {attempt}: '{agent}' backhaul — {err}")
            time.sleep(10)
        else:
            pytest.fail(
                f"Agent '{agent}' backhaul on {bh_iface} not active at test start"
            )

    print_step("Step 3: Periodic association comparison")
    start_time = time.time()
    poll_count = 0
    while time.time() - start_time < test_duration_sec:
        elapsed_min = int((time.time() - start_time) / 60)
        poll_count += 1
        print(f"STEP: Poll #{poll_count} at ~{elapsed_min} min elapsed")

        current = collect_fronthaul_associations(initialize, all_devices)
        mismatches = compare_associations(
            baseline, current, expected_client_count
        )
        if mismatches:
            pytest.fail(
                f"Poll #{poll_count} ({elapsed_min} min): "
                f"Association mismatch — {mismatches}"
            )
        print(
            f"SUCCESS: Poll #{poll_count}: Associations match baseline "
            f"({total_associations(current)} clients)"
        )
        time.sleep(poll_interval_sec)

    print_step("Step 4: Final association comparison against baseline")
    final = collect_fronthaul_associations(initialize, all_devices)
    final_mismatches = compare_associations(
        baseline, final, expected_client_count
    )
    if final_mismatches:
        pytest.fail(f"Final associations do not match baseline: {final_mismatches}")
    print(
        f"SUCCESS: Final associations match baseline: "
        f"{total_associations(final)} clients — PASS"
    )
