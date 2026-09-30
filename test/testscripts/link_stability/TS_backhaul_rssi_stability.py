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
"""Validate managed backhaul RSSI stability using iw only."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdkbmeshzap.common_utils import  report_logger
from utility import (
    backhaul_interfaces, backhaul_state, get_present_agents,
    get_test_parameters,
)


MAX_RSSI_DEGRADATION_DB = 10
MIN_RSSI_DBM = -80


def test_em_backhaul_rssi_stability(initialize):
    """Verify backhaul RSSI stays above threshold and near its baseline."""
    report_logger.print_test("Entering test_em_backhaul_rssi_stability")
    agents = get_present_agents(initialize)
    if not agents:
        pytest.fail("No backhaul agents are marked present in the database")
    test_parameters = get_test_parameters(initialize)
    interval = test_parameters["poll_interval_sec"]
    duration = test_parameters["test_duration_sec"]
    baseline = {}
    skipped = []

    report_logger.print_step("Step 1: Capture baseline backhaul RSSI")
    for agent in agents:
        try:
            interfaces = backhaul_interfaces(initialize, agent)
        except Exception as err:
            skipped.append(f"{agent}: interface discovery failed: {err}")
            report_logger.print_info(
                f"Skipping unreachable agent '{agent}': interface discovery failed: {err}"
            )
            continue
        if not interfaces:
            skipped.append(f"{agent}: no managed backhaul interface found")
            report_logger.print_info(
                f"Skipping agent '{agent}': no managed backhaul interface found"
            )
            continue
        for interface in interfaces:
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                skipped.append(f"{agent}/{interface}: state collection failed: {err}")
                report_logger.print_info(
                    f"Skipping unreachable link '{agent}/{interface}': {err}"
                )
                continue
            report_logger.print_step(f"Baseline {agent}/{interface}: {state}")
            if not state["connected"] or state["rssi_dbm"] is None:
                skipped.append(f"{agent}/{interface}: RSSI unavailable at baseline")
                report_logger.print_info(
                    f"Skipping unavailable link '{agent}/{interface}': RSSI unavailable"
                )
                continue
            if state["rssi_dbm"] < MIN_RSSI_DBM:
                skipped.append(
                    f"{agent}/{interface}: baseline RSSI {state['rssi_dbm']} dBm "
                    f"below {MIN_RSSI_DBM} dBm"
                )
                report_logger.print_info(
                    f"Skipping link '{agent}/{interface}': baseline RSSI "
                    f"{state['rssi_dbm']} dBm below {MIN_RSSI_DBM} dBm"
                )
                continue
            baseline[(agent, interface)] = state["rssi_dbm"]
    if not baseline:
        pytest.fail("No reachable backhaul links were available for baseline validation")
    report_logger.print_step(
        f"Baseline captured for {len(baseline)} link(s); "
        f"skipped {len(skipped)} present link/agent item(s)"
    )
    for item in skipped:
        report_logger.print_info(f"Present backhaul item not monitored: {item}")

    report_logger.print_step("Step 2: Monitor backhaul RSSI")
    start = time.time()
    latest = {}
    while time.time() - start < duration:
        failures = []
        for (agent, interface), initial_rssi in baseline.items():
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                failures.append(f"{agent}/{interface}: state collection failed: {err}")
                continue
            latest[(agent, interface)] = state
            report_logger.print_step(f"RSSI poll {agent}/{interface}: {state}")
            if not state["connected"] or state["rssi_dbm"] is None:
                failures.append(f"{agent}/{interface}: RSSI unavailable: {state}")
                continue
            if state["rssi_dbm"] < MIN_RSSI_DBM:
                failures.append(
                    f"{agent}/{interface}: RSSI {state['rssi_dbm']} dBm "
                    f"below {MIN_RSSI_DBM} dBm"
                )
                continue
            if initial_rssi - state["rssi_dbm"] > MAX_RSSI_DEGRADATION_DB:
                failures.append(
                    f"RSSI degraded by more than {MAX_RSSI_DEGRADATION_DB} dB "
                    f"for '{agent}/{interface}': {initial_rssi} -> {state['rssi_dbm']} dBm"
                )
        if failures:
            message = "Backhaul RSSI failures:\n- " + "\n- ".join(failures)
            report_logger.print_error(message)
            pytest.fail(message)
        time.sleep(interval)
    report_logger.print_step("Final baseline-versus-latest backhaul RSSI comparison")
    final_failures = []
    for (agent, interface), initial_rssi in baseline.items():
        try:
            state = backhaul_state(initialize, agent, interface)
        except Exception as err:
            final_failures.append(f"{agent}/{interface}: final state collection failed: {err}")
            continue
        latest[(agent, interface)] = state
        current_rssi = state["rssi_dbm"]
        if not state["connected"] or current_rssi is None:
            final_failures.append(f"{agent}/{interface}: latest RSSI unavailable: {state}")
        elif current_rssi < MIN_RSSI_DBM:
            final_failures.append(
                f"{agent}/{interface}: latest RSSI {current_rssi} dBm below {MIN_RSSI_DBM} dBm"
            )
        elif initial_rssi - current_rssi > MAX_RSSI_DEGRADATION_DB:
            final_failures.append(
                f"{agent}/{interface}: baseline RSSI {initial_rssi} -> "
                f"latest RSSI {current_rssi} dBm"
            )
    if final_failures:
        message = "Final backhaul RSSI comparison failed:\n- " + "\n- ".join(final_failures)
        report_logger.print_error(message)
        pytest.fail(message)
    report_logger.print_test("Exiting test_em_backhaul_rssi_stability")
