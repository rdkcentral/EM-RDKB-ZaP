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
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_backhaul_link_stability(initialize):
    """
    Verify every agent stays connected to the same parent BSSID.
    """
    report_logger.print_test("Entering test_em_backhaul_link_stability")
    agents = device_utils.get_enabled_extenders(initialize)
    if not agents:
        message = "No backhaul agents are marked present in the database"
        report_logger.print_error(message)
        pytest.fail(message)
    interval = POLL_INTERVAL_SEC
    duration = TEST_DURATION_SEC
    interfaces = {}

    report_logger.print_step("STEP 1: Discover and capture managed backhaul links")
    baseline = {}
    skipped = []
    for agent in agents:
        try:
            interfaces[agent] = backhaul_interfaces(initialize, agent)
        except Exception as err:
            skipped.append(f"{agent}: interface discovery failed: {err}")
            report_logger.print_info(
                f"INFO: Skipping unreachable device '{agent}': "
                f"interface discovery failed: {err}"
            )
            continue
        if not interfaces[agent]:
            skipped.append(f"{agent}: no managed backhaul interface found")
            report_logger.print_info(
                f"INFO: Skipping device '{agent}': no managed backhaul interface found"
            )
            continue
        for interface in interfaces[agent]:
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                skipped.append(f"{agent}/{interface}: state collection failed: {err}")
                report_logger.print_info(
                    f"INFO: Skipping unreachable link '{agent}/{interface}': {err}"
                )
                continue
            report_logger.print_info(
                f"INFO: Baseline {agent}/{interface}: {state}"
            )
            if not state["connected"] or state["bssid"] is None:
                skipped.append(f"{agent}/{interface}: unavailable baseline: {state}")
                report_logger.print_info(
                    f"INFO: Skipping unavailable link '{agent}/{interface}': {state}"
                )
                continue
            if state["connected_time"] is None:
                skipped.append(f"{agent}/{interface}: connected time unavailable")
                report_logger.print_info(
                    f"INFO: Skipping link '{agent}/{interface}': "
                    "connected time unavailable"
                )
                continue
            baseline[(agent, interface)] = state
    if not baseline:
        message = "No reachable backhaul links were available for baseline validation"
        report_logger.print_error(message)
        pytest.fail(message)
    report_logger.print_info(
        f"INFO: Baseline captured for {len(baseline)} link(s); "
        f"skipped {len(skipped)} present link/agent item(s)"
    )
    for item in skipped:
        report_logger.print_info(f"INFO: Backhaul item not monitored: {item}")

    report_logger.print_step("STEP 2: Monitor backhaul connection continuity")
    start = time.time()
    poll = 0
    while time.time() - start < duration:
        poll += 1
        failures = []
        for key, initial in baseline.items():
            agent, interface = key
            failure_count = len(failures)
            try:
                current = backhaul_state(initialize, agent, interface)
            except Exception as err:
                failures.append(f"{agent}/{interface}: state collection failed: {err}")
                continue
            report_logger.print_step(
                "STEP 2: Check backhaul connection continuity"
            )
            report_logger.print_info(
                f"INFO: Poll #{poll}, {agent}/{interface}: {current}"
            )
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
            if len(failures) == failure_count:
                report_logger.print_success(
                    f"PASS: Step 2.{poll}: {agent}/{interface} remains connected "
                    f"to BSSID {current['bssid']}"
                )
        if failures:
            message = "Backhaul link failures:\n- " + "\n- ".join(failures)
            report_logger.print_error(message)
            pytest.fail(message)
        time.sleep(interval)
    report_logger.print_step(
        "STEP 3: Recheck each backhaul link and compare its final parent BSSID "
        "and connected time with the baseline"
    )
    final_failures = []
    for key, initial in baseline.items():
        agent, interface = key
        try:
            current = backhaul_state(initialize, agent, interface)
        except Exception as err:
            final_failures.append(f"{agent}/{interface}: final state collection failed: {err}")
            continue
        if not current["connected"] or current["bssid"] != initial["bssid"]:
            final_failures.append(
                f"{agent}/{interface}: baseline BSSID {initial['bssid']} -> "
                f"latest BSSID {current['bssid']}"
            )
        if current["connected_time"] is None or current["connected_time"] < initial["connected_time"]:
            final_failures.append(
                f"{agent}/{interface}: connected time baseline "
                f"{initial['connected_time']} -> latest {current['connected_time']}"
            )
    if final_failures:
        message = "Final backhaul baseline comparison failed:\n- " + "\n- ".join(final_failures)
        report_logger.print_error(message)
        pytest.fail(message)
    report_logger.print_success(
        f"PASS: Final backhaul state matches baseline for {len(baseline)} links"
    )
    report_logger.print_test("Exiting test_em_backhaul_link_stability")
