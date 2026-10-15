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
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_backhaul_rssi_stability(initialize):
    """
    Verify backhaul RSSI stays above threshold and near its baseline.
    """
    report_logger.print_test("Entering test_em_backhaul_rssi_stability")
    try:
        agents = device_utils.get_enabled_extenders(initialize)
        if not agents:
            report_logger.print_error("No backhaul agents are marked present in the database")
        interval = POLL_INTERVAL_SEC
        duration = TEST_DURATION_SEC
        baseline = {}
        report_logger.print_step("STEP 1: Capture baseline RSSI and validate connectivity and the minimum signal threshold for each backhaul link")
        for agent_index, agent in enumerate(agents, start=1):
            try:
                stored_interface = initialize.read_from_database(
                    agent, "backhaul_interface")
                if not stored_interface:
                    report_logger.print_error(f"FAIL: {agent}: backhaul_interface is missing from platform.yaml")
                    continue
                interfaces = [stored_interface]
            except Exception as err:
                report_logger.print_error(f"Unable to discover required backhaul interfaces on '{agent}': {err}")
                continue
            if not interfaces:
                report_logger.print_error(f"No managed backhaul interface found on required agent '{agent}'")
                continue
            for interface in interfaces:
                try:
                    state = initialize.get_backhaul_interface_details(agent, interface)
                except Exception as err:
                    report_logger.print_error(f"Unable to capture required backhaul RSSI baseline for '{agent}/{interface}': {err}")
                    continue
                report_logger.print_info(f"INFO: Baseline agent #{agent_index} {agent}/{interface}: {state}")
                if not state["connected"] or state["rssi_dbm"] is None:
                    report_logger.print_error(f"RSSI baseline unavailable on required backhaul link '{agent}/{interface}': {state}")
                    continue
                if state["rssi_dbm"] < MIN_RSSI_DBM:
                    report_logger.print_error(
                        f"Baseline RSSI on required backhaul link "
                        f"'{agent}/{interface}' is {state['rssi_dbm']} dBm, "
                        f"below {MIN_RSSI_DBM} dBm")
                    continue
                baseline[(agent, interface)] = state["rssi_dbm"]
            report_logger.print_info(f"INFO: Baseline RSSI captured for {len(baseline)} backhaul link(s)")
        report_logger.print_step("STEP 2: Monitor backhaul RSSI")
        start = time.time()
        poll = 0
        while time.time() - start < duration:
            poll += 1
            poll_failure = 0
            for link_index, ((agent, interface), initial_rssi) in enumerate(baseline.items(), start=1):
                try:
                    report_logger.print_step(f"STEP 2.{poll}.{link_index}: Validate RSSI against the threshold and baseline for {agent}/{interface}")
                    state = initialize.get_backhaul_interface_details(agent, interface)
                except Exception as err:
                    poll_failure += 1
                    report_logger.print_error(f"{agent}/{interface}: state collection failed: {err}")
                    continue
                report_logger.print_info(f"INFO: Poll #{poll}, link #{link_index} {agent}/{interface}: {state}")
                if not state["connected"] or state["rssi_dbm"] is None:
                    report_logger.print_error(f"{agent}/{interface}: RSSI unavailable: {state}")
                    poll_failure += 1
                    continue
                if state["rssi_dbm"] < MIN_RSSI_DBM:
                    report_logger.print_error(f"{agent}/{interface}: RSSI {state['rssi_dbm']} dBm below {MIN_RSSI_DBM} dBm")
                    poll_failure += 1
                    continue
                if initial_rssi - state["rssi_dbm"] > MAX_RSSI_DEGRADATION_DB:
                    report_logger.print_error(
                        f"RSSI degraded by more than {MAX_RSSI_DEGRADATION_DB} dB "
                        f"for '{agent}/{interface}': {initial_rssi} -> "
                        f"{state['rssi_dbm']} dBm")
                    poll_failure += 1
                if poll_failure == 0:
                    report_logger.print_success(f"PASS: {agent}/{interface} RSSI is {state['rssi_dbm']} dBm")
            time.sleep(interval)
        report_logger.print_step("STEP 3: Validate each backhaul link's final RSSI against its baseline and configured threshold")
        for link_index, ((agent, interface), initial_rssi) in enumerate(baseline.items(), start=1):
            try:
                report_logger.print_info(f"INFO: Final state collection for link #{link_index} {agent}/{interface}")
                state = initialize.get_backhaul_interface_details(agent, interface)
            except Exception as err:
                report_logger.print_error(f"{agent}/{interface}: final state collection failed: {err}")
                continue
            current_rssi = state["rssi_dbm"]
            error = None
            if not state["connected"] or current_rssi is None:
                error = f"{agent}/{interface}: latest RSSI unavailable: {state}"
            elif current_rssi < MIN_RSSI_DBM:
                error = f"{agent}/{interface}: latest RSSI {current_rssi} dBm below {MIN_RSSI_DBM} dBm"
            elif initial_rssi - current_rssi > MAX_RSSI_DEGRADATION_DB:
                error = (
                    f"{agent}/{interface}: baseline RSSI {initial_rssi} -> "
                    f"latest RSSI {current_rssi} dBm")
            if error:
                report_logger.print_error(error)
            else:
                report_logger.print_success(f"PASS: {agent}/{interface} final RSSI validation passed")
    finally:
        report_logger.print_test("Exiting test_em_backhaul_rssi_stability")
