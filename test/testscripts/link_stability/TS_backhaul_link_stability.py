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

def test_em_backhaul_link_stability(initialize):
    """
    Verify every agent stays connected to the same parent BSSID.
    """
    report_logger.print_test("Entering test_em_backhaul_link_stability")
    try:
        agents = device_utils.get_enabled_extenders(initialize)
        if not agents:
            report_logger.print_error("No backhaul agents are marked present in the database")
            return
        interval = POLL_INTERVAL_SEC
        duration = TEST_DURATION_SEC
        interfaces = {}
        report_logger.print_step("STEP 1: Identify configured backhaul interfaces and validate baseline connectivity, parent BSSID, and connection time")
        baseline = {}
        for agent in agents:
            try:
                stored_interface = initialize.read_from_database(
                    agent, "backhaul_interface")
                if not stored_interface:
                    report_logger.print_error(f"FAIL: {agent}: backhaul_interface is missing from platform.yaml")
                    continue
                interfaces[agent] = [stored_interface]
            except Exception as err:
                report_logger.print_error(f"Unable to discover required backhaul interfaces on '{agent}': {err}")
                continue
            if not interfaces[agent]:
                report_logger.print_error(f"No managed backhaul interface found on required agent '{agent}'")
                continue
            for interface in interfaces[agent]:
                try:
                    state = initialize.get_backhaul_interface_details(agent, interface)
                except Exception as err:
                    report_logger.print_error(f"Unable to capture required backhaul baseline for '{agent}/{interface}': {err}")
                    continue
                report_logger.print_info(f"INFO: Baseline {agent}/{interface}: {state}")
                if not state["connected"] or state["bssid"] is None:
                    report_logger.print_error(f"Required backhaul link '{agent}/{interface}' is disconnected at baseline: {state}")
                    continue
                if state["connected_time"] is None:
                    report_logger.print_error(f"Connected time is unavailable for required backhaul link '{agent}/{interface}'")
                    continue
                baseline[(agent, interface)] = state
        report_logger.print_info(f"INFO: Baseline captured for {len(baseline)} managed backhaul link(s)")
        previous_connected_times = {
            key: state["connected_time"] for key, state in baseline.items()
        }
        report_logger.print_step("STEP 2: Monitor backhaul connectivity and validate stable connections, parent BSSIDs, and connection times")
        start = time.time()
        poll = 0
        while time.time() - start < duration:
            poll += 1
            poll_failure = 0
            for link_index, (key, initial) in enumerate(baseline.items(), start=1):
                agent, interface = key
                try:
                    report_logger.print_step(f"STEP 2.{poll}.{link_index}: Validate connectivity, parent BSSID, and connection time for {agent}/{interface}")
                    current = initialize.get_backhaul_interface_details(agent, interface)
                except Exception as err:
                    report_logger.print_error(f"'{agent}/{interface}': state collection failed: {err}")
                    poll_failure += 1
                    continue
                report_logger.print_info(f"INFO: Poll #{poll}, link #{link_index} {agent}/{interface}: {current}")
                if not current["connected"]:
                    report_logger.print_error(f"Poll #{poll}: '{agent}/{interface}' disconnected")
                    poll_failure += 1
                    continue
                if current["bssid"] != initial["bssid"]:
                    report_logger.print_error(f"Poll #{poll}: '{agent}/{interface}' parent BSSID changed from {initial['bssid']} to {current['bssid']}")
                    poll_failure += 1
                if current["connected_time"] is None:
                    report_logger.print_error(f"Poll #{poll}: '{agent}/{interface}' connected time unavailable")
                    poll_failure += 1
                elif current["connected_time"] < previous_connected_times[key]:
                    report_logger.print_error(
                        f"Poll #{poll}: '{agent}/{interface}' connected time reset "
                        f"from {previous_connected_times[key]} to "
                        f"{current['connected_time']} seconds")
                    poll_failure += 1
                else:
                    previous_connected_times[key] = current["connected_time"]
                if poll_failure == 0:
                    report_logger.print_success(f"PASS: {agent}/{interface} remains connected to BSSID {current['bssid']}")
            time.sleep(interval)
        report_logger.print_step("STEP 3: Validate each backhaul link against its baseline connectivity, parent BSSID, and connection time")
        for link_index, (key, initial) in enumerate(baseline.items(), start=1):
            agent, interface = key
            try:
            report_logger.print_info(f"INFO: Final state collection for link #{link_index} {agent}/{interface}")
                current = initialize.get_backhaul_interface_details(agent, interface)
            except Exception as err:
                report_logger.print_error(f"{agent}/{interface}: final state collection failed: {err}")
                continue
            error = None
            if not current["connected"] or current["bssid"] != initial["bssid"]:
                error = f"{agent}/{interface}: baseline BSSID {initial['bssid']} -> " f"latest BSSID {current['bssid']}"
            elif current["connected_time"] is None or current["connected_time"] < previous_connected_times[key]:
                error = f"{agent}/{interface}: connected time previous sample " f"{previous_connected_times[key]} -> final {current['connected_time']}"
            if error:
                report_logger.print_error(error)
            else:
                report_logger.print_success(f"PASS: Final backhaul state validation passed for {agent}/{interface}")
    finally:
        report_logger.print_test("Exiting test_em_backhaul_link_stability")
