"""Validate managed backhaul RSSI stability using iw only."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import POLL_INTERVAL_SEC, SCALE_AGENTS, TEST_DURATION_SEC
from utility import (
    backhaul_interfaces, backhaul_state, device_present,
    print_error, print_step, print_test,
)


MAX_RSSI_DEGRADATION_DB = 10
MIN_RSSI_DBM = -80


def test_em_backhaul_rssi_stability(initialize):
    """Verify backhaul RSSI stays above threshold and near its baseline."""
    print_test("Entering test_em_backhaul_rssi_stability")
    agents = [
        agent for agent in SCALE_AGENTS
        if device_present(initialize, agent)
    ]
    interval = POLL_INTERVAL_SEC
    duration = TEST_DURATION_SEC
    baseline = {}

    print_step("Step 1: Capture baseline backhaul RSSI")
    failures = []
    for agent in agents:
        try:
            interfaces = backhaul_interfaces(initialize, agent)
        except Exception as err:
            failures.append(f"{agent}: interface discovery failed: {err}")
            continue
        if not interfaces:
            failures.append(f"{agent}: no managed backhaul interface found")
            continue
        for interface in interfaces:
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                failures.append(f"{agent}/{interface}: state collection failed: {err}")
                continue
            print_step(f"Baseline {agent}/{interface}: {state}")
            if not state["connected"] or state["rssi_dbm"] is None:
                failures.append(f"{agent}/{interface}: RSSI unavailable: {state}")
                continue
            if state["rssi_dbm"] < MIN_RSSI_DBM:
                failures.append(
                    f"{agent}/{interface}: baseline RSSI {state['rssi_dbm']} dBm "
                    f"below {MIN_RSSI_DBM} dBm"
                )
                continue
            baseline[(agent, interface)] = state["rssi_dbm"]
    if failures:
        message = "Backhaul RSSI baseline failures:\n- " + "\n- ".join(failures)
        print_error(message)
        pytest.fail(message)

    print_step("Step 2: Monitor backhaul RSSI")
    start = time.time()
    while time.time() - start < duration:
        failures = []
        for (agent, interface), initial_rssi in baseline.items():
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                failures.append(f"{agent}/{interface}: state collection failed: {err}")
                continue
            print_step(f"RSSI poll {agent}/{interface}: {state}")
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
            print_error(message)
            pytest.fail(message)
        time.sleep(interval)
    print_test("Exiting test_em_backhaul_rssi_stability")
