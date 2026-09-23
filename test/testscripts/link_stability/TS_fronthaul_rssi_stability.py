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

# Test Case: EM_Fronthaul_RSSI_Stability
# Validates RSSI stability for configured clients on the MLO fronthaul interface.

import re
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import FRONTHAUL_CLIENTS, POLL_INTERVAL_SEC, TEST_DURATION_SEC
from utility import (
    client_rssi,
    device_present,
    print_error,
    print_step,
    print_success,
    print_test,
    validate_rssi,
)

MAX_RSSI_DEGRADATION_DB = 10


def test_em_fronthaul_rssi_stability(initialize):
    """Verify fronthaul client RSSI remains within the allowed degradation limit."""
    print_test("Entering test_em_fronthaul_rssi_stability")
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

    print_step(f"Step 1: Capture baseline RSSI for {len(clients)} client(s)")
    baseline_rssi = {}
    for client in clients:
        state = client_rssi(initialize, client)
        error = validate_rssi(state)
        if error:
            message = f"Client '{client}' baseline RSSI validation failed: {error}"
            print_error(message)
            pytest.fail(message)
        baseline_rssi[client] = state["rssi_dbm"]
        print_success(
            f"Client '{client}' baseline RSSI: {state['rssi_dbm']} dBm "
            f"on {state['host']}/{state['interface']}"
        )

    print_step("Step 2: Monitor fronthaul RSSI for the configured duration")
    start_time = time.time()
    poll_count = 0
    while time.time() - start_time < test_duration_sec:
        poll_count += 1
        elapsed_sec = int(time.time() - start_time)
        print_step(f"RSSI poll #{poll_count} at {elapsed_sec}s elapsed")
        for client in clients:
            try:
                state = client_rssi(initialize, client)
                error = validate_rssi(state, baseline_rssi[client], MAX_RSSI_DEGRADATION_DB)
            except Exception as err:
                message = f"RSSI poll #{poll_count} failed for '{client}': {err}"
                print_error(message)
                pytest.fail(message)
            if error:
                message = f"Client '{client}' RSSI check failed: {error}"
                print_error(message)
                pytest.fail(message)
            print_success(
                f"Client '{client}' RSSI is {state['rssi_dbm']} dBm "
                f"(baseline {baseline_rssi[client]} dBm)"
            )
        time.sleep(poll_interval_sec)

    print_step("Step 3: Final fronthaul RSSI validation")
    for client in clients:
        state = client_rssi(initialize, client)
        error = validate_rssi(state, baseline_rssi[client], MAX_RSSI_DEGRADATION_DB)
        if error:
            message = f"Client '{client}' final RSSI validation failed: {error}"
            print_error(message)
            pytest.fail(message)
        print_success(
            f"Client '{client}' final RSSI is {state['rssi_dbm']} dBm; "
            f"no degradation beyond {MAX_RSSI_DEGRADATION_DB} dB"
        )
    print_test("Exiting test_em_fronthaul_rssi_stability")
