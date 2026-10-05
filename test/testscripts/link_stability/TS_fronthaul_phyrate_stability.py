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

def test_em_fronthaul_phyrate_stability(initialize):
    """
    Verify client TX/RX PHY rates remain within the allowed drop limit.
    """
    report_logger.print_test("Entering test_em_fronthaul_phyrate_stability")
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
        message = f"Unable to prepare fronthaul clients for PHY-rate monitoring: {err}"
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
        f"PASS: Connected clients before PHY-rate test: {', '.join(clients)}"
    )
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC

    report_logger.print_step(
        "STEP 2: Capture and validate baseline TX/RX PHY rates"
    )
    report_logger.print_info(
        f"INFO: Capturing baseline PHY rates for {len(clients)} client(s)"
    )
    baseline_rates = {}
    failures = []
    for client in clients:
        try:
            bssid = initialize.get_association_status(client, "cli")
            host = mesh_device_for_bssid(initialize, bssid)
            state = client_phy_rate(initialize, client, host)
            error = validate_phy_rate(state)
        except Exception as err:
            message = f"Unable to capture baseline PHY rate for '{client}': {err}"
            report_logger.print_error(message)
            failures.append(message)
            continue
        if error:
            message = f"Client '{client}' failed baseline PHY-rate validation: {error}"
            report_logger.print_error(message)
            failures.append(message)
            continue
        baseline_rates[client] = state
        report_logger.print_success(
            f"PASS: Client '{client}' baseline PHY rate: "
            f"TX {state['tx_mbps']:.1f} Mbps, RX {state['rx_mbps']:.1f} Mbps "
            f"on {state['host']}/{state['interface']}"
        )
    report_logger.print_info(
        f"INFO: Baseline captured for all {len(baseline_rates)} configured "
        "present WLAN client(s)"
    )

    report_logger.print_step(
        "STEP 3: Sample each client's TX/RX PHY rates and compare them with "
        "the baseline for the configured duration"
    )
    start_time = time.time()
    poll_count = 0
    while time.time() - start_time < test_duration_sec:
        poll_count += 1
        elapsed_sec = int(time.time() - start_time)
        poll_failures = []
        report_logger.print_step(
            "STEP 3: Sample client PHY rates"
        )
        report_logger.print_info(
            f"INFO: Poll #{poll_count} at {elapsed_sec}s elapsed"
        )
        for client in clients:
            try:
                bssid = initialize.get_association_status(client, "cli")
                host = mesh_device_for_bssid(initialize, bssid)
                state = client_phy_rate(initialize, client, host)
                error = validate_phy_rate(state, baseline_rates[client], PHY_RATE_DROP_PERCENT)
            except Exception as err:
                message = f"PHY-rate poll #{poll_count} failed for '{client}': {err}"
                report_logger.print_error(message)
                poll_failures.append(message)
                continue
            if error:
                message = f"Client '{client}' PHY-rate check failed: {error}"
                report_logger.print_error(message)
                poll_failures.append(message)
                continue
            report_logger.print_success(
                f"PASS: Client '{client}' PHY rate: TX {state['tx_mbps']:.1f} Mbps, "
                f"RX {state['rx_mbps']:.1f} Mbps on "
                f"{state['host']}/{state['interface']}"
            )
        if poll_failures:
            failures.extend(poll_failures)
        time.sleep(poll_interval_sec)
    report_logger.print_step(
        "STEP 4: Capture final per-client PHY rates and enforce the allowed "
        "drop limit"
    )
    for client in clients:
        try:
            bssid = initialize.get_association_status(client, "cli")
            host = mesh_device_for_bssid(initialize, bssid)
            state = client_phy_rate(initialize, client, host)
        except Exception as err:
            message = f"Final PHY-rate sample failed for '{client}': {err}"
            report_logger.print_error(message)
            failures.append(message)
            continue
        error = validate_phy_rate(state, baseline_rates[client], PHY_RATE_DROP_PERCENT)
        if error:
            message = f"Client '{client}' final PHY validation failed: {error}"
            report_logger.print_error(message)
            failures.append(message)
            continue
        report_logger.print_success(
            f"PASS: Client '{client}' final PHY rate: "
            f"TX {state['tx_mbps']:.1f} Mbps, "
            f"RX {state['rx_mbps']:.1f} Mbps on "
            f"{state['host']}/{state['interface']}"
        )
    if failures:
        pytest.fail("FRONTHAUL PHY-Rate Validation failed:\n- " + "\n- ".join(failures))
    report_logger.print_test("Exiting test_em_fronthaul_phyrate_stability")
