"""Validate managed backhaul connectivity and association continuity."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import POLL_INTERVAL_SEC, SCALE_AGENTS, TEST_DURATION_SEC
from utility import backhaul_interfaces, backhaul_state, device_present, print_step


def _agents(initialize):
    return [
        agent for agent in SCALE_AGENTS
        if device_present(initialize, agent)
    ]


def test_em_backhaul_link_stability(initialize):
    """Verify every agent stays connected to the same parent BSSID."""
    agents = _agents(initialize)
    interval = POLL_INTERVAL_SEC
    duration = TEST_DURATION_SEC
    interfaces = {}

    print_step("Step 1: Discover and capture managed backhaul links")
    baseline = {}
    failures = []
    for agent in agents:
        try:
            interfaces[agent] = backhaul_interfaces(initialize, agent)
        except Exception as err:
            failures.append(f"{agent}: interface discovery failed: {err}")
            continue
        if not interfaces[agent]:
            failures.append(f"{agent}: no managed backhaul interface found")
            continue
        for interface in interfaces[agent]:
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                failures.append(f"{agent}/{interface}: state collection failed: {err}")
                continue
            print_step(f"Baseline {agent}/{interface}: {state}")
            if not state["connected"] or state["bssid"] is None:
                failures.append(f"{agent}/{interface}: not connected: {state}")
                continue
            if state["connected_time"] is None:
                failures.append(
                    f"{agent}/{interface}: connected time unavailable: {state}"
                )
                continue
            baseline[(agent, interface)] = state
    if failures:
        pytest.fail("Backhaul baseline failures:\n- " + "\n- ".join(failures))

    print_step("Step 2: Monitor backhaul connection continuity")
    start = time.time()
    poll = 0
    while time.time() - start < duration:
        poll += 1
        failures = []
        for key, initial in baseline.items():
            agent, interface = key
            try:
                current = backhaul_state(initialize, agent, interface)
            except Exception as err:
                failures.append(f"{agent}/{interface}: state collection failed: {err}")
                continue
            print_step(f"Poll #{poll} {agent}/{interface}: {current}")
            if not current["connected"]:
                failures.append(f"Poll #{poll}: '{agent}/{interface}' disconnected")
                continue
            if current["bssid"] != initial["bssid"]:
                failures.append(
                    f"Poll #{poll}: '{agent}/{interface}' parent BSSID changed "
                    f"from {initial['bssid']} to {current['bssid']}"
                )
            if current["connected_time"] is None:
                failures.append(
                    f"Poll #{poll}: '{agent}/{interface}' connected time unavailable"
                )
            elif current["connected_time"] < initial["connected_time"]:
                failures.append(f"Poll #{poll}: '{agent}/{interface}' connected time reset")
        if failures:
            pytest.fail("Backhaul link failures:\n- " + "\n- ".join(failures))
        time.sleep(interval)
