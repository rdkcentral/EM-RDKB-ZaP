# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 RDK Management
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.client_utils import connect_wlan_clients
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_client_association(initialize):
    """
        1. Verify every extender is reachable; capture baseline client presence.
    """
    report_logger.print_test("Entering test_em_scale_client_association")
    try:
        report_logger.print_step("STEP 1: Discover extenders and configured WLAN clients for stability validation")
        agents = device_utils.get_enabled_extenders(initialize)
        clients = device_utils.get_enabled_clients(initialize)
        report_logger.print_info(f"INFO: Discovered {len(agents)} extenders and {len(clients)} configured WLAN clients: extenders={agents}, clients={clients}")
        if not clients:
            report_logger.print_error("No clients are marked present in the database")
            return
        report_logger.print_step("STEP 2: Connect configured WLAN clients and verify availability before baseline capture")
        clients = connect_wlan_clients(initialize, clients)
        report_logger.print_success(f"PASS: Connected clients before client-presence test: {', '.join(clients)}")
        expected_client_count = get_enabled_scale_setup(initialize)["expected_client_count"]
        poll_interval_sec = POLL_INTERVAL_SEC
        test_duration_sec = TEST_DURATION_SEC
        all_devices = ["controller"] + agents
        report_logger.print_step("STEP 3: Verify each active extender is reachable before capturing baseline client associations")
        for agent_index, agent in enumerate(agents, start=1):
            for attempt in range(1, 7):
                try:
                    output = initialize.get_iw_dev_info(agent)
                    if output:
                        report_logger.print_success(f"PASS: Extender #{agent_index} '{agent}' is reachable")
                        break
                    report_logger.print_info(f"INFO: Extender #{agent_index} '{agent}', attempt {attempt}: no interface data received yet")
                except Exception as err:
                    report_logger.print_info(f"INFO: Extender #{agent_index} '{agent}', attempt {attempt}: not ready — {err}")
                time.sleep(10)
            else:
                report_logger.print_error(f"Extender '{agent}' did not become reachable before baseline capture")
        report_logger.print_step("STEP 4: Capture fronthaul client MACs on each device and validate the baseline count")
        baseline = get_fronthaul_station_macs_by_device(initialize, all_devices)
        total_baseline = sum(len(macs) for macs in baseline.values())
        report_logger.print_info(f"INFO: Baseline client presence: observed {total_baseline}, expected {expected_client_count}")
        if total_baseline < expected_client_count:
            report_logger.print_error(f"Baseline client count mismatch: observed {total_baseline}, expected exactly {expected_client_count}")
        report_logger.print_success(f"PASS: Baseline captured: {total_baseline} clients across the discovered devices")
        report_logger.print_step("STEP 5: Periodically compare each active extender's client MAC associations with the baseline")
        start_time = time.time()
        poll_count = 0
        while time.time() - start_time < test_duration_sec:
            elapsed_min = int((time.time() - start_time) / 60)
            poll_count += 1
            report_logger.print_step(f"STEP 5.{poll_count}: Compare current client MAC associations with the baseline")
            report_logger.print_info(f"INFO: Poll #{poll_count} at ~{elapsed_min} min elapsed")
            current = get_fronthaul_station_macs_by_device(initialize, all_devices)
            mismatches = get_client_association_mismatches(baseline, current)
            current_client_count = sum(len(macs) for macs in current.values())
            report_logger.print_info(f"INFO: Poll #{poll_count}: {current_client_count} connected client(s) checked against baseline")
            if mismatches:
                report_logger.print_error(f"Poll #{poll_count} ({elapsed_min} min): Client-presence mismatch — {mismatches}")
            else:
                report_logger.print_success(f"PASS: Poll #{poll_count}: Client presence matches baseline ({current_client_count} clients)")
            time.sleep(poll_interval_sec)
        report_logger.print_step("STEP 6: Capture latest client MAC associations and validate count and baseline membership")
        final = get_fronthaul_station_macs_by_device(initialize, all_devices)
        final_mismatches = get_client_association_mismatches(baseline, final)
        final_client_count = sum(len(macs) for macs in final.values())
        report_logger.print_info(f"INFO: Latest client presence: observed {final_client_count}, expected {expected_client_count}")
        if final_client_count < expected_client_count or final_mismatches:
            if final_client_count < expected_client_count:
                report_logger.print_error(f"Latest client count mismatch: observed {final_client_count}, expected exactly {expected_client_count}")
            if final_mismatches:
                report_logger.print_error(f"Latest client presence does not match baseline: {final_mismatches}")
        else:
            report_logger.print_success(f"PASS: Latest client presence matches baseline: {final_client_count} clients")
    finally:
        report_logger.print_test("Exiting test_em_scale_client_association")
