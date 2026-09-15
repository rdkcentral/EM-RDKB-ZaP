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

# Test Case: EM_Fronthaul_PHYRate_Stability
# Validates client TX/RX PHY-rate stability on the MLO fronthaul interface.

import re
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import FRONTHAUL_CLIENTS, POLL_INTERVAL_SEC, TEST_DURATION_SEC
from utility import (
    client_phy_rate,
    device_present,
    print_error,
    print_step,
    print_success,
    validate_phy_rate,
)

PHY_RATE_DROP_PERCENT = 50


def test_em_fronthaul_phyrate_stability(initialize):
    """Verify client TX/RX PHY rates remain within the allowed drop limit."""
    configured_clients = FRONTHAUL_CLIENTS
    clients = [
        client
        for client in configured_clients
        if device_present(initialize, client)
    ]
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC

    if not clients:
        pytest.skip("No fronthaul clients are marked present in the database")

    print_step(f"Step 1: Capture baseline PHY rates for {len(clients)} client(s)")
    baseline_rates = {}
    for client in clients:
        state = client_phy_rate(initialize, client)
        error = validate_phy_rate(state)
        if error:
            print_error(f"Client '{client}' baseline PHY validation failed: {error}")
            pytest.fail(f"Client '{client}' baseline PHY validation failed: {error}")
        baseline_rates[client] = state
        print_success(
            f"Client '{client}' baseline PHY rate: "
            f"TX {state['tx_mbps']:.1f} Mbps, RX {state['rx_mbps']:.1f} Mbps "
            f"on {state['host']}/{state['interface']}"
        )

    print_step("Step 2: Monitor fronthaul PHY rates for the configured duration")
    start_time = time.time()
    poll_count = 0
    while time.time() - start_time < test_duration_sec:
        poll_count += 1
        elapsed_sec = int(time.time() - start_time)
        print_step(f"PHY-rate poll #{poll_count} at {elapsed_sec}s elapsed")
        for client in clients:
            try:
                state = client_phy_rate(initialize, client)
                error = validate_phy_rate(state, baseline_rates[client], PHY_RATE_DROP_PERCENT)
            except Exception as err:
                pytest.fail(f"PHY-rate poll #{poll_count} failed for '{client}': {err}")
            if error:
                print_error(f"Client '{client}' PHY-rate check failed: {error}")
                pytest.fail(f"Client '{client}' PHY-rate check failed: {error}")
            print_success(
                f"Client '{client}' PHY rate: TX {state['tx_mbps']:.1f} Mbps, "
                f"RX {state['rx_mbps']:.1f} Mbps"
            )
        time.sleep(poll_interval_sec)

    print_step("Step 3: Final fronthaul PHY-rate validation")
    for client in clients:
        state = client_phy_rate(initialize, client)
        error = validate_phy_rate(state, baseline_rates[client], PHY_RATE_DROP_PERCENT)
        if error:
            print_error(f"Client '{client}' final PHY validation failed: {error}")
            pytest.fail(f"Client '{client}' final PHY validation failed: {error}")
        print_success(
            f"Client '{client}' final PHY rate: TX {state['tx_mbps']:.1f} Mbps, "
            f"RX {state['rx_mbps']:.1f} Mbps"
        )
