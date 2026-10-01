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

# Test Case: EM_Fronthaul_RSSI_Stability
# Validates RSSI stability for configured clients on the MLO fronthaul interface.

import time

import pytest

from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.client_utils import connect_wlan_clients

from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

MAX_RSSI_DEGRADATION_DB = 10

def test_em_fronthaul_rssi_stability(initialize):
    """
    Verify fronthaul client RSSI remains within the allowed degradation limit.
    """
    report_logger.print_test("Entering test_em_fronthaul_rssi_stability")
    report_logger.print_step(
        "Step 1: Discover present WLAN clients and connect each client to a "
        "present mesh-device BSSID"
    )
    present_clients = device_utils.get_enabled_clients(initialize)
    if not present_clients:
        pytest.fail("No fronthaul clients are marked present in the database")
    clients = connect_wlan_clients(
        initialize, present_clients, require_all=False
    )
    if not clients:
        pytest.fail("No present WLAN clients could be connected")
    skipped = [
        f"{client}: connection unavailable"
        for client in present_clients
        if client not in clients
    ]
    report_logger.print_success(
        f"PASS: Connected clients before RSSI test: {', '.join(clients)}"
    )
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC

    report_logger.print_step(
        f"Step 2: Capture and validate baseline RSSI for {len(clients)} client(s)"
    )
    baseline_rssi = {}
    for client in clients:
        try:
            state = client_rssi(initialize, client)
            error = validate_rssi(state)
        except Exception as err:
            skipped.append(f"{client}: baseline validation failed: {err}")
            report_logger.print_info(
                f"INFO: Skipping unreachable client '{client}' during baseline: {err}"
            )
            continue
        if error:
            skipped.append(f"{client}: baseline validation failed: {error}")
            report_logger.print_info(
                f"INFO: Skipping client '{client}' during baseline: {error}"
            )
            continue
        baseline_rssi[client] = state["rssi_dbm"]
        report_logger.print_success(
            f"PASS: Client '{client}' baseline RSSI: {state['rssi_dbm']} dBm "
            f"on {state['host']}/{state['interface']}"
        )
    clients = list(baseline_rssi)
    if not clients:
        pytest.fail("No WLAN clients were reachable for baseline validation")
    report_logger.print_step(
        f"STEP: Baseline captured for {len(clients)} client(s); "
        f"skipped {len(skipped)} present client(s)"
    )
    for item in skipped:
        report_logger.print_info(
            f"INFO: Present fronthaul client not monitored: {item}"
        )

    report_logger.print_step(
        "Step 3: Sample each client's RSSI and compare it with the baseline "
        "for the configured duration"
    )
    start_time = time.time()
    poll_count = 0
    while time.time() - start_time < test_duration_sec:
        poll_count += 1
        elapsed_sec = int(time.time() - start_time)
        report_logger.print_step(
            f"STEP: RSSI poll #{poll_count} at {elapsed_sec}s elapsed"
        )
        for client in clients:
            try:
                state = client_rssi(initialize, client)
                error = validate_rssi(state, baseline_rssi[client], MAX_RSSI_DEGRADATION_DB)
            except Exception as err:
                message = f"RSSI poll #{poll_count} failed for '{client}': {err}"
                report_logger.print_error(message)
                pytest.fail(message)
            if error:
                message = f"Client '{client}' RSSI check failed: {error}"
                report_logger.print_error(message)
                pytest.fail(message)
            report_logger.print_success(
                f"PASS: Client '{client}' RSSI is {state['rssi_dbm']} dBm "
                f"(baseline {baseline_rssi[client]} dBm)"
            )
        time.sleep(poll_interval_sec)

    report_logger.print_step(
        "Step 4: Capture final per-client RSSI and enforce the allowed "
        "degradation limit"
    )
    for client in clients:
        state = client_rssi(initialize, client)
        error = validate_rssi(state, baseline_rssi[client], MAX_RSSI_DEGRADATION_DB)
        if error:
            message = f"Client '{client}' final RSSI validation failed: {error}"
            report_logger.print_error(message)
            pytest.fail(message)
        report_logger.print_success(
            f"PASS: Client '{client}' final RSSI is {state['rssi_dbm']} dBm; "
            f"no degradation beyond {MAX_RSSI_DEGRADATION_DB} dB"
        )
    report_logger.print_test("Exiting test_em_fronthaul_rssi_stability")
