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
from rdkbmeshzap.common_utils.client_utils import connect_wlan_clients
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_client_association(initialize):
    """
      1. Verify all Agents are reachable; capture baseline client presence.
    """
    report_logger.print_test("Entering test_em_scale_client_association")
    try:
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
            report_logger.print_error(
                "No clients are marked present in the database"
            )
            return
        report_logger.print_step(
            "STEP 2: Connect configured WLAN clients before baseline capture"
        )
        clients = connect_wlan_clients(initialize, clients)
        report_logger.print_success(
            f"PASS: Connected clients before client-presence test: {', '.join(clients)}"
        )
        expected_client_count = get_scale_setup(initialize)["expected_client_count"]
        poll_interval_sec = POLL_INTERVAL_SEC
        test_duration_sec = TEST_DURATION_SEC
        all_devices = ["controller"] + agents
        report_logger.print_step(
            "STEP 3: Verify each device is reachable before client connection capture"
        )
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
                report_logger.print_error(
                    f"Device '{agent}' did not become reachable before baseline capture"
                )
        report_logger.print_step(
            "STEP 4: Capture devices fronthaul client MACs and validate the baseline client count"
        )
        baseline = get_fronthaul_client_macs(initialize, all_devices)
        total_baseline = get_total_connected_clients(baseline)
        report_logger.print_info(
            f"INFO: Baseline client presence: observed {total_baseline}, "
            f"expected {expected_client_count}"
        )
        if total_baseline != expected_client_count:
            report_logger.print_error(
                f"Baseline client count mismatch: observed {total_baseline}, "
                f"expected exactly {expected_client_count}"
            )
        report_logger.print_success(
            f"PASS: Baseline captured: {total_baseline} clients "
            f"across {len(all_devices)} devices"
        )
        report_logger.print_step(
            "STEP 5: Periodically compare each device's client presence "
            "with the baseline"
        )
        start_time = time.time()
        poll_count = 0
        while time.time() - start_time < test_duration_sec:
            elapsed_min = int((time.time() - start_time) / 60)
            poll_count += 1
            report_logger.print_step(
                f"STEP 5.{poll_count}: Compare current client presence with the baseline"
            )
            report_logger.print_info(
                f"INFO: Poll #{poll_count} at ~{elapsed_min} min elapsed"
            )
            current = get_fronthaul_client_macs(initialize, all_devices)
            mismatches = get_connected_client_mismatch(baseline, current)
            current_client_count = get_total_connected_clients(current)
            report_logger.print_info(
                f"INFO: Poll #{poll_count}: {current_client_count} "
                "connected client(s) checked against baseline"
            )
            if mismatches:
                report_logger.print_error(
                    f"Poll #{poll_count} ({elapsed_min} min): "
                    f"Client-presence mismatch — {mismatches}"
                )
            else:
                report_logger.print_success(
                    f"PASS: Poll #{poll_count}: Client presence matches baseline "
                    f"({current_client_count} clients)"
                )
            report_logger.print_info(
                f"INFO: Poll #{poll_count} completed"
            )
            time.sleep(poll_interval_sec)
        report_logger.print_step(
            "STEP 6: Capture final client presence and report any missing client(s)"
        )
        final = get_fronthaul_client_macs(initialize, all_devices)
        final_mismatches = get_connected_client_mismatch(baseline, final)
        final_client_count = get_total_connected_clients(final)
        report_logger.print_info(
            f"INFO: Final client presence: observed {final_client_count}, "
            f"expected {expected_client_count}"
        )
        if final_client_count != expected_client_count:
            report_logger.print_error(
                f"Final client count mismatch: observed {final_client_count}, "
                f"expected exactly {expected_client_count}"
            )
        if final_mismatches:
            report_logger.print_error(
                f"Final client presence does not match baseline: {final_mismatches}"
            )
        if final_client_count == expected_client_count and not final_mismatches:
            report_logger.print_success(
                f"PASS: Final client presence matches baseline: "
                f"{final_client_count} clients — PASS"
            )
    finally:
        report_logger.print_test("Exiting test_em_scale_client_association")
