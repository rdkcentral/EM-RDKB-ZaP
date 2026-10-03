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

import pytest
import time
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.client_utils import connect_wlan_clients
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_client_association(initialize):
    """
      1. Verify all Agents are reachable; capture baseline associations.
    """
    report_logger.print_test("Entering test_em_scale_client_association")
    report_logger.print_step(
        "STEP 1: Discover scale agents and configured WLAN clients"
    )
    agents = device_utils.get_enabled_extenders(initialize)
    clients = device_utils.get_enabled_clients(initialize)
    report_logger.print_info(
        f"INFO: Discovered {len(agents)} scale devices and "
        f"{len(clients)} configured WLAN clients: agents={agents}, clients={clients}"
    )
    if not clients:
        message = "No clients are marked present in the database"
        report_logger.print_info(f"INFO: Skipping association test: {message}")
        pytest.skip(message)
    report_logger.print_step(
        "STEP 2: Connect configured WLAN clients before baseline capture"
    )
    report_logger.print_info(
        f"INFO: WLAN clients selected for connection: {clients}"
    )
    clients = connect_wlan_clients(initialize, clients)
    report_logger.print_success(
        f"PASS: Connected clients before association test: {', '.join(clients)}"
    )
    expected_client_count = get_scale_setup(initialize)["expected_client_count"]
    poll_interval_sec = POLL_INTERVAL_SEC
    test_duration_sec = TEST_DURATION_SEC
    all_devices = ["controller"] + agents

    report_logger.print_step(
        "STEP 3: Verify each device is reachable before association capture"
    )
    failures = []
    for agent in agents:
        for attempt in range(1, 7):
            try:
                output = initialize.get_iw_dev_info(agent)
                if output:
                    report_logger.print_success(
                        f"PASS: Device '{agent}' is reachable"
                    )
                    break
                report_logger.print_info(
                    f"INFO: Attempt {attempt}: no interface data from '{agent}' yet"
                )
            except Exception as err:
                report_logger.print_info(
                    f"INFO: Attempt {attempt}: '{agent}' not ready — {err}"
                )
            time.sleep(10)
        else:
            message = (
                f"Device '{agent}' did not become reachable before baseline capture"
            )
            report_logger.print_error(message)
            failures.append(message)
    if failures:
        pytest.fail("Overall validation failed:\n- " + "\n- ".join(failures))

    report_logger.print_step(
        "STEP 4: Capture per-device fronthaul client MACs and validate the "
        "baseline client count"
    )
    baseline = collect_fronthaul_associations(initialize, all_devices)
    total_baseline = total_associations(baseline)
    if total_baseline < expected_client_count:
        message = (
            f"Baseline client count {total_baseline} is below the minimum "
            f"{expected_client_count}. Snapshot: {baseline}"
        )
        report_logger.print_error(message)
        pytest.fail(message)
    report_logger.print_success(
        f"PASS: Baseline captured: {total_baseline} clients "
        f"across {len(all_devices)} devices"
    )

    report_logger.print_step(
        "STEP 5: Periodically compare each device's client MAC associations "
        "with the baseline"
    )
    start_time = time.time()
    poll_count = 0
    while time.time() - start_time < test_duration_sec:
        elapsed_min = int((time.time() - start_time) / 60)
        poll_count += 1
        report_logger.print_step(
            "STEP 5: Compare current associations with the baseline"
        )
        report_logger.print_info(
            f"INFO: Poll #{poll_count} at ~{elapsed_min} min elapsed"
        )

        current = collect_fronthaul_associations(initialize, all_devices)
        mismatches = compare_associations(baseline, current)
        if mismatches:
            message = (
                f"Poll #{poll_count} ({elapsed_min} min): "
                f"Association mismatch — {mismatches}"
            )
            report_logger.print_error(message)
            pytest.fail(message)
        report_logger.print_success(
            f"PASS: Poll #{poll_count}: Associations match baseline "
            f"({total_associations(current)} clients)"
        )
        time.sleep(poll_interval_sec)

    report_logger.print_step(
        "STEP 6: Capture final per-device client associations and report any "
        "missing or unexpected client MACs"
    )
    final = collect_fronthaul_associations(initialize, all_devices)
    final_mismatches = compare_associations(baseline, final)
    if final_mismatches:
        message = f"Final associations do not match baseline: {final_mismatches}"
        report_logger.print_error(message)
        pytest.fail(message)
    report_logger.print_success(
        f"PASS: Final associations match baseline: "
        f"{total_associations(final)} clients — PASS"
    )
    report_logger.print_test("Exiting test_em_scale_client_association")
