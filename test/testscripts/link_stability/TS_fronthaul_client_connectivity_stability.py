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

# Test Case: EM_FronthaulLinkStability
# Topology: Normal setup (1 Controller [+ Agents], each with its own fronthaul
# WiFi client — not a scale setup). Validates that each configured, present
# fronthaul client (controller_wlan_client_1, extender1_wlan_client_1, ...)
# stays associated on its AP's fronthaul interface for the configured test
# duration, using iw station dump (no Data Elements / rbuscli involved).

import sys
from pathlib import Path
import pytest
import re
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import FRONTHAUL_CLIENTS, POLL_INTERVAL_SEC, TEST_DURATION_SEC
from utility import (
    client_host, client_reachable, client_station_info, device_present,
    fronthaul_interface, print_step, print_success, print_error, print_test,
    validate_client,
)


def test_em_fronthaul_link_stability(initialize):
    """
    EM_FronthaulLinkStability — normal (non-scale) setup.

    Steps:
            1. Capture baseline fronthaul station state and client gateway reachability.
            2. Validate state, connected-time continuity, and ping at each interval.
            3. Perform one final validation at the end of the observation period.
    """
    print_test("Entering test_em_fronthaul_link_stability")
    configured_clients = FRONTHAUL_CLIENTS
    CLIENTS = [
        client for client in configured_clients
        if device_present(initialize, client)
    ]
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC
    gateway_ip = initialize.read_from_database("controller", "bridge_ip")

    if not CLIENTS:
        pytest.skip("No fronthaul clients are marked present in the database")

    # ------------------------------------------------------------------
    # Step 1 — Capture baseline fronthaul state and connectivity
    # ------------------------------------------------------------------
    print_step("Step 1: Capture baseline fronthaul state and client connectivity")

    baseline_connected_time = {}
    for client in CLIENTS:
        station, error = validate_client(initialize, client, gateway_ip)
        if error:
            msg = f"Client '{client}' baseline validation failed: {error}"
            print_error(msg)
            pytest.fail(msg)
        baseline_connected_time[client] = station["connected_time"]
        print_success(
            f"Client '{client}' connected on '{station['host']}/{station['interface']}' "
            f"with connected time {station['connected_time']}s"
        )

    # ------------------------------------------------------------------
    # Step 2 — Periodic fronthaul link checks
    # ------------------------------------------------------------------
    print_step("Step 2: Periodic fronthaul link stability check")

    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < test_duration_sec:
        elapsed_min = int((time.time() - start_time) / 60)
        poll_count += 1
        print_step(f"Poll #{poll_count} at ~{elapsed_min} min elapsed")

        for client in CLIENTS:
            try:
                station, error = validate_client(
                    initialize, client, gateway_ip, baseline_connected_time[client]
                )
            except Exception as err:
                msg = f"Poll #{poll_count}: Validation failed for '{client}': {err}"
                print_error(msg)
                pytest.fail(msg)
            if error:
                msg = f"Poll #{poll_count} ({elapsed_min} min): Client '{client}' failed: {error}"
                print_error(msg)
                pytest.fail(msg)
            baseline_connected_time[client] = station["connected_time"]
            print_success(
                f"Poll #{poll_count}: Client '{client}' healthy on "
                f"'{station['host']}/{station['interface']}' "
                f"({station['connected_time']}s connected)"
            )

        time.sleep(poll_interval_sec)

    # ------------------------------------------------------------------
    # Step 3 — Final fronthaul connectivity check
    # ------------------------------------------------------------------
    print_step("Step 3: Final fronthaul connectivity check")

    for client in CLIENTS:
        try:
            station, error = validate_client(
                initialize, client, gateway_ip, baseline_connected_time[client]
            )
        except Exception as err:
            msg = f"Final validation failed for '{client}': {err}"
            print_error(msg)
            pytest.fail(msg)
        if error:
            msg = f"Client '{client}' failed final validation: {error}"
            print_error(msg)
            pytest.fail(msg)
        print_success(
            f"Client '{client}' healthy on '{station['host']}/{station['interface']}' "
            f"at end of test ({station['connected_time']}s connected)"
        )
    print_test("Exiting test_em_fronthaul_link_stability")
