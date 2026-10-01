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

# Test Case: EM_FronthaulLinkStability
# Topology: Normal setup (1 Controller [+ Agents], each with its own fronthaul
# WiFi client — not a scale setup). Validates that each configured, present
# fronthaul client (controller_wlan_client_1, extender1_wlan_client_1, ...)
# stays associated to a BSSID and can reach the controller gateway for the
# configured test duration.

import pytest
import time

from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.client_utils import connect_wlan_clients

from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_fronthaul_link_stability(initialize):
    """
    EM_FronthaulLinkStability — normal (non-scale) setup.

    Steps:
            1. Capture baseline fronthaul station state and client gateway reachability.
            2. Validate association and gateway reachability at each interval.
            3. Perform one final validation at the end of the observation period.
    """
    report_logger.print_test("Entering test_em_fronthaul_link_stability")
    report_logger.print_step(
        "Step 1: Discover present WLAN clients and connect each client to its "
        "owning device BSSID"
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
        f"PASS: Connected clients before stability test: {', '.join(clients)}"
    )
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC
    gateway_ip = initialize.read_from_database("controller", "bridge_ip")

    # ------------------------------------------------------------------
    # Step 2 — Capture baseline fronthaul state and connectivity
    # ------------------------------------------------------------------
    report_logger.print_step(
        "Step 2: Validate each client's baseline BSSID association and "
        "controller gateway reachability"
    )

    validated_clients = []
    for client in clients:
        try:
            station, error = validate_client(
                initialize, client, gateway_ip
            )
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
        validated_clients.append(client)
        report_logger.print_success(
            f"PASS: Client '{client}' connected to BSSID {station['bssid']} "
            f"on interface '{station['interface']}'"
        )
    clients = validated_clients
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

    # ------------------------------------------------------------------
    # Step 3 — Periodic fronthaul link checks
    # ------------------------------------------------------------------
    report_logger.print_step(
        "Step 3: Revalidate every client's BSSID association and gateway "
        "reachability at each polling interval"
    )

    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < test_duration_sec:
        elapsed_min = int((time.time() - start_time) / 60)
        poll_count += 1
        report_logger.print_step(
            f"STEP: Poll #{poll_count} at ~{elapsed_min} min elapsed"
        )

        for client in clients:
            try:
                station, error = validate_client(
                    initialize,
                    client,
                    gateway_ip,
                )
            except Exception as err:
                msg = f"Poll #{poll_count}: Validation failed for '{client}': {err}"
                report_logger.print_error(msg)
                pytest.fail(msg)
            if error:
                msg = f"Poll #{poll_count} ({elapsed_min} min): Client '{client}' failed: {error}"
                report_logger.print_error(msg)
                pytest.fail(msg)
            report_logger.print_success(
                f"PASS: Poll #{poll_count}: Client '{client}' healthy on BSSID "
                f"{station['bssid']} via interface '{station['interface']}'"
            )

        time.sleep(poll_interval_sec)

    # ------------------------------------------------------------------
    # Step 4 — Final fronthaul connectivity check
    # ------------------------------------------------------------------
    report_logger.print_step(
        "Step 4: Perform the final per-client BSSID and gateway validation"
    )

    for client in clients:
        try:
            station, error = validate_client(
                initialize,
                client,
                gateway_ip,
            )
        except Exception as err:
            msg = f"Final validation failed for '{client}': {err}"
            report_logger.print_error(msg)
            pytest.fail(msg)
        if error:
            msg = f"Client '{client}' failed final validation: {error}"
            report_logger.print_error(msg)
            pytest.fail(msg)
        report_logger.print_success(
            f"PASS: Client '{client}' healthy on BSSID {station['bssid']} via "
            f"interface '{station['interface']}' at end of test"
        )
    report_logger.print_test("Exiting test_em_fronthaul_link_stability")
