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

def test_em_backhaul_rssi_stability(initialize):
    """
    Verify backhaul RSSI stays above threshold and near its baseline.
    """
    report_logger.print_test("Entering test_em_backhaul_rssi_stability")
    agents = device_utils.get_enabled_extenders(initialize)
    if not agents:
        message = "No backhaul agents are marked present in the database"
        report_logger.print_error(message)
        pytest.fail(message)
    interval = POLL_INTERVAL_SEC
    duration = TEST_DURATION_SEC
    baseline = {}
    report_logger.print_step("STEP 1: Capture baseline backhaul RSSI")
    for agent in agents:
        try:
            interfaces = backhaul_interfaces(initialize, agent)
        except Exception as err:
            message = f"Unable to discover required backhaul interfaces on '{agent}': {err}"
            report_logger.print_error(message)
            continue
        if not interfaces:
            message = f"No managed backhaul interface found on required agent '{agent}'"
            report_logger.print_error(message)
            continue
        for interface in interfaces:
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                message = f"Unable to capture required backhaul RSSI baseline for '{agent}/{interface}': {err}"
                report_logger.print_error(message)
                continue
            report_logger.print_info(
                f"INFO: Baseline {agent}/{interface}: {state}"
            )
            if not state["connected"] or state["rssi_dbm"] is None:
                message = f"RSSI baseline unavailable on required backhaul link '{agent}/{interface}': {state}"
                report_logger.print_error(message)
                continue
            if state["rssi_dbm"] < MIN_RSSI_DBM:
                message = (
                    f"Baseline RSSI on required backhaul link '{agent}/{interface}' "
                    f"is {state['rssi_dbm']} dBm, below {MIN_RSSI_DBM} dBm"
                )
                report_logger.print_error(message)
                continue
            baseline[(agent, interface)] = state["rssi_dbm"]
    report_logger.print_info(
        f"INFO: Baseline captured for {len(baseline)} link(s); "
        "all configured agents and managed backhaul links are covered"
    )

    report_logger.print_step("STEP 2: Monitor backhaul RSSI")
    start = time.time()
    poll = 0
    while time.time() - start < duration:
        poll += 1
        poll_failure = 0
        for (agent, interface), initial_rssi in baseline.items():
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                message = f"{agent}/{interface}: state collection failed: {err}"
                poll_failure += 1
                report_logger.print_error(message)
                continue
            report_logger.print_step(
                "STEP 2: Check backhaul RSSI"
            )
            report_logger.print_info(
                f"INFO: Poll #{poll}, {agent}/{interface}: {state}"
            )
            if not state["connected"] or state["rssi_dbm"] is None:
                message = f"{agent}/{interface}: RSSI unavailable: {state}"
                report_logger.print_error(message)
                poll_failure += 1
                continue
            if state["rssi_dbm"] < MIN_RSSI_DBM:
                message = f"{agent}/{interface}: RSSI {state['rssi_dbm']} dBm " f"below {MIN_RSSI_DBM} dBm"
                report_logger.print_error(message)
                poll_failure += 1
                continue
            if initial_rssi - state["rssi_dbm"] > MAX_RSSI_DEGRADATION_DB:
                message = f"RSSI degraded by more than {MAX_RSSI_DEGRADATION_DB} dB " f"for '{agent}/{interface}': {initial_rssi} -> {state['rssi_dbm']} dBm"
                report_logger.print_error(message)
                poll_failure +=1
            if poll_failure  == 0 :
                report_logger.print_success(
                    f"PASS: Step 2.{poll}: {agent}/{interface} RSSI is "
                    f"{state['rssi_dbm']} dBm"
                )
        time.sleep(interval)
    report_logger.print_step(
        "STEP 3: Recheck each backhaul link and compare final RSSI with its "
        "baseline and configured threshold"
    )
    for (agent, interface), initial_rssi in baseline.items():
        try:
            state = backhaul_state(initialize, agent, interface)
        except Exception as err:
            message = f"{agent}/{interface}: final state collection failed: {err}"
            report_logger.print_error(message) 
            continue
        current_rssi = state["rssi_dbm"]
        if not state["connected"] or current_rssi is None:
            message = f"{agent}/{interface}: latest RSSI unavailable: {state}"
            report_logger.print_error(message)
        elif current_rssi < MIN_RSSI_DBM:
            message = f"{agent}/{interface}: latest RSSI {current_rssi} dBm below {MIN_RSSI_DBM} dBm"
            report_logger.print_error(message)
        elif initial_rssi - current_rssi > MAX_RSSI_DEGRADATION_DB:
            message = f"{agent}/{interface}: baseline RSSI {initial_rssi} -> " f"latest RSSI {current_rssi} dBm"
            report_logger.print_error(message)
        else:    
            report_logger.print_success(
            f"PASS: Final RSSI meets baseline and threshold for {len(baseline)} links"
            )
    report_logger.print_test("Exiting test_em_backhaul_rssi_stability")
