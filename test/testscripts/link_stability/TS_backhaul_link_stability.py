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
        pytest.skip(message)
    interval = POLL_INTERVAL_SEC
    duration = TEST_DURATION_SEC
    interfaces = {}

    report_logger.print_step("STEP 1: Identify managed backhaul links and collect their baseline details")
    baseline = {}
    for agent in agents:
        try:
            interfaces[agent] = backhaul_interfaces(initialize, agent)
        except Exception as err:
            message = f"Unable to discover required backhaul interfaces on '{agent}': {err}"
            report_logger.print_error(message)
            continue
        if not interfaces[agent]:
            message = f"No managed backhaul interface found on required agent '{agent}'"
            report_logger.print_error(message)
            continue
        for interface in interfaces[agent]:
            try:
                state = backhaul_state(initialize, agent, interface)
            except Exception as err:
                message = f"Unable to capture required backhaul baseline for '{agent}/{interface}': {err}"
                report_logger.print_error(message)
                continue
            report_logger.print_info(
                f"INFO: Baseline {agent}/{interface}: {state}"
            )
            if not state["connected"] or state["bssid"] is None:
                message = f"Required backhaul link '{agent}/{interface}' is disconnected at baseline: {state}"
                report_logger.print_error(message)
                continue
            if state["connected_time"] is None:
                message = f"Connected time is unavailable for required backhaul link '{agent}/{interface}'"
                report_logger.print_error(message)
                continue
            baseline[(agent, interface)] = state
    report_logger.print_info(
        f"INFO: Baseline captured for {len(baseline)} managed backhaul link(s)"
    )
    previous_connected_times = {
        key: state["connected_time"] for key, state in baseline.items()
    }
    report_logger.print_step("STEP 2: Monitor backhaul connections and verify they remain stable")
    start = time.time()
    poll = 0
    while time.time() - start < duration:
        poll += 1
        poll_failure =0 
        for key, initial in baseline.items():
            agent, interface = key
            try:
                report_logger.print_step(
                    f"STEP 2.1: Monitor backhaul connectivity for {agent}/{interface}"
                )
                current = backhaul_state(initialize, agent, interface)
            except Exception as err:
                message = f"'{agent}/{interface}': state collection failed: {err}"
                report_logger.print_error(message)
                poll_failure +=1
                continue
            report_logger.print_info(
                f"INFO: Poll #{poll}, {agent}/{interface}: {current}"
            )
            if not current["connected"]:
                message = f"Poll #{poll}: '{agent}/{interface}' disconnected"
                report_logger.print_error(message)
                poll_failure +=1
                continue
            if current["bssid"] != initial["bssid"]:
                message = f"Poll #{poll}: '{agent}/{interface}' parent BSSID changed " f"from {initial['bssid']} to {current['bssid']}"
                report_logger.print_error(message)
                poll_failure +=1
            if current["connected_time"] is None:
                message = f"Poll #{poll}: '{agent}/{interface}' connected time unavailable"
                report_logger.print_error(message)
                poll_failure +=1
            elif current["connected_time"] < previous_connected_times[key]:
                message = f"Poll #{poll}: '{agent}/{interface}' connected time reset " f"from {previous_connected_times[key]} to {current['connected_time']} seconds"
                report_logger.print_error(message)
                poll_failure +=1
            else:
                previous_connected_times[key] = current["connected_time"]
            if poll_failure == 0:
                report_logger.print_success(
                    f"PASS: {agent}/{interface} remains connected "
                    f"to BSSID {current['bssid']}"
                )
        time.sleep(interval)
    report_logger.print_step(
        "STEP 3: Verify each backhaul link remains connected and "
        "compare its current parent BSSID and connection duration with the baseline"
    )
    for key, initial in baseline.items():
        agent, interface = key
        try:
            current = backhaul_state(initialize, agent, interface)
        except Exception as err:
            messag = f"{agent}/{interface}: final state collection failed: {err}"
            report_logger.print_error(messag)
            continue
        error = None
        if not current["connected"] or current["bssid"] != initial["bssid"]:
            error = f"{agent}/{interface}: baseline BSSID {initial['bssid']} -> " f"latest BSSID {current['bssid']}"
        elif current["connected_time"] is None or current["connected_time"] < previous_connected_times[key]:
            error = f"{agent}/{interface}: connected time previous sample " f"{previous_connected_times[key]} -> final {current['connected_time']}"
        if error:
            report_logger.print_error(error)
        else:
            report_logger.print_success(
            f"PASS: Final backhaul state validation passed for {agent}/{interface}"
        )
    report_logger.print_test("Exiting test_em_backhaul_link_stability")
