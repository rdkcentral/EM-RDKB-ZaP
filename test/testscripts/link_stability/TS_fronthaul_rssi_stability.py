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

import time

import pytest

from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.client_utils import connect_wlan_clients

from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

MAX_RSSI_DEGRADATION_DB = 10

def test_em_fronthaul_rssi_stability(initialize):
    """
    Verify client RSSI remains within the allowed degradation limit, following
    each client's current serving mesh device.
    """
    report_logger.print_test("Entering test_em_fronthaul_rssi_stability")
    report_logger.print_step(
        "STEP 1: Discover present WLAN clients and attempt connection to "
        "their owning device"
    )
    present_clients = device_utils.get_enabled_clients(initialize)
    if not present_clients:
        message = "No fronthaul clients are marked present in the database"
        report_logger.print_error(message)
        pytest.fail(message)
    try:
        clients = connect_wlan_clients(
            initialize, present_clients, require_all=False
        )
    except Exception as err:
        message = f"Unable to prepare fronthaul clients for RSSI monitoring: {err}"
        report_logger.print_error(message)
        pytest.fail(message)
    unavailable = [
        f"{client}: connection unavailable"
        for client in present_clients
        if client not in clients
    ]
    if unavailable:
        message = (
            "Unable to establish or preserve a present-mesh association for "
            f"all configured WLAN clients: {unavailable}"
        )
        report_logger.print_error(message)
        pytest.fail(message)
    report_logger.print_success(
        f"PASS: Connected clients before RSSI test: {', '.join(clients)}"
    )
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC

    report_logger.print_step(
        "STEP 2: Capture and validate baseline RSSI"
    )
    report_logger.print_info(
        f"INFO: Capturing baseline RSSI for {len(clients)} client(s)"
    )
    baseline_rssi = {}
    for client in clients:
        try:
            state = client_rssi(initialize, client)
            error = validate_rssi(state)
        except Exception as err:
            message = f"Unable to capture baseline RSSI for '{client}': {err}"
            report_logger.print_error(message)
            pytest.fail(message)
        if error:
            message = f"Client '{client}' failed baseline RSSI validation: {error}"
            report_logger.print_error(message)
            pytest.fail(message)
        baseline_rssi[client] = state["rssi_dbm"]
        report_logger.print_success(
            f"PASS: Client '{client}' baseline RSSI: {state['rssi_dbm']} dBm "
            f"on {state['host']}/{state['interface']}"
        )
    report_logger.print_info(
        f"INFO: Baseline captured for all {len(baseline_rssi)} configured "
        "present WLAN client(s)"
    )

    report_logger.print_step(
        "STEP 3: Sample each client's RSSI and compare it with the baseline "
        "for the configured duration"
    )
    start_time = time.time()
    poll_count = 0
    while time.time() - start_time < test_duration_sec:
        poll_count += 1
        elapsed_sec = int(time.time() - start_time)
        report_logger.print_step(
            "STEP 3: Sample client RSSI"
        )
        report_logger.print_info(
            f"INFO: Poll #{poll_count} at {elapsed_sec}s elapsed"
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
                f"(baseline {baseline_rssi[client]} dBm) on "
                f"{state['host']}/{state['interface']}"
            )
        time.sleep(poll_interval_sec)

    report_logger.print_step(
        "STEP 4: Capture final per-client RSSI and enforce the allowed "
        "degradation limit"
    )
    for client in clients:
        try:
            state = client_rssi(initialize, client)
        except Exception as err:
            message = f"Final RSSI sample failed for '{client}': {err}"
            report_logger.print_error(message)
            pytest.fail(message)
        error = validate_rssi(state, baseline_rssi[client], MAX_RSSI_DEGRADATION_DB)
        if error:
            message = f"Client '{client}' final RSSI validation failed: {error}"
            report_logger.print_error(message)
            pytest.fail(message)
        report_logger.print_success(
            f"PASS: Client '{client}' final RSSI is {state['rssi_dbm']} dBm; "
            f"no degradation beyond {MAX_RSSI_DEGRADATION_DB} dB on "
            f"{state['host']}/{state['interface']}"
        )
    report_logger.print_test("Exiting test_em_fronthaul_rssi_stability")
