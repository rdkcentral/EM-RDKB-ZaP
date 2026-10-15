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
from rdkbmeshzap.common_utils.device_utils import *
from rdkbmeshzap.common_utils.client_utils import *
from rdkbmeshzap.common_utils.test_report_utils import *
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_fronthaul_rssi_stability(initialize):
    """
    Verify client RSSI remains within the allowed degradation limit.
    """
    report_logger.print_test("Entering test_em_fronthaul_rssi_stability")
    try:
        report_logger.print_step("STEP 1: Identify configured WLAN clients, connect them to their assigned devices, and verify availability")
        present_clients = device_utils.get_enabled_clients(initialize)
        if not present_clients:
            report_logger.print_error("No fronthaul clients are marked present in the database")
        try:
            clients = connect_wlan_clients(
                initialize, present_clients, require_all=False)
        except Exception as err:
            report_logger.print_error(f"Unable to prepare fronthaul clients for RSSI monitoring: {err}")
        unavailable = [
            f"{client}: connection unavailable"
            for client in present_clients
            if client not in clients
        ]
        if unavailable:
            report_logger.print_error(f"Unable to establish association for all configured WLAN clients: {unavailable}")
            return
        report_logger.print_success(f"PASS: Connected clients before RSSI test: {', '.join(clients)}")
        poll_interval_sec = POLL_INTERVAL_SEC
        test_duration_sec = TEST_DURATION_SEC
        report_logger.print_step("STEP 2: Capture each client's baseline RSSI and validate that the signal sample is available")
        report_logger.print_info(f"INFO: Capturing baseline RSSI for {len(clients)} client(s)")
        baseline_rssi = {}
        for client_index, client in enumerate(clients, start=1):
            try:
                report_logger.print_info(f"INFO: Capturing baseline RSSI for client #{client_index} '{client}'")
                bssid = initialize.get_association_status(client, "cli")
                host = get_device_advertising_bssid(initialize, bssid)
                state = get_client_rssi(initialize, client, host)
                error = validate_client_rssi(state)
            except Exception as err:
                report_logger.print_error(f"Unable to capture baseline RSSI for '{client}': {err}")
                continue
            if error:
                report_logger.print_error(f"Client '{client}' failed baseline RSSI validation: {error}")
                continue
            baseline_rssi[client] = state["rssi_dbm"]
            report_logger.print_success(f"PASS: Client '{client}' baseline RSSI: {state['rssi_dbm']} dBm on {state['host']}/{state['interface']}")
        report_logger.print_info(f"INFO: Baseline captured for all {len(baseline_rssi)} configured present WLAN client(s)")
        report_logger.print_step("STEP 3: Monitor each client's RSSI and validate the allowed baseline degradation throughout the test")
        start_time = time.time()
        poll_count = 0
        while time.time() - start_time < test_duration_sec:
            poll_count += 1
            elapsed_sec = int(time.time() - start_time)
            report_logger.print_step(f"STEP 3.{poll_count}: Validate each client's RSSI against its baseline")
            report_logger.print_info(f"INFO: Poll #{poll_count} at {elapsed_sec}s elapsed")
            for client_index, client in enumerate(clients, start=1):
                try:
                    report_logger.print_step(f"STEP 3.{poll_count}.{client_index}: Validate RSSI for client #{client_index} '{client}'")
                    bssid = initialize.get_association_status(client, "cli")
                    host = get_device_advertising_bssid(initialize, bssid)
                    state = get_client_rssi(initialize, client, host)
                    error = validate_client_rssi(state, baseline_rssi[client], MAX_RSSI_DEGRADATION_DB)
                except Exception as err:
                    report_logger.print_error(f"RSSI poll #{poll_count} failed for '{client}': {err}")
                    continue
                if error:
                    report_logger.print_error(f"Client '{client}' RSSI check failed: {error}")
                    continue
                report_logger.print_success(
                    f"PASS: Client '{client}' RSSI is {state['rssi_dbm']} dBm "
                    f"(baseline {baseline_rssi[client]} dBm) on "
                    f"{state['host']}/{state['interface']}")
            time.sleep(poll_interval_sec)
        report_logger.print_step("STEP 4: Capture final RSSI for all clients and validate the allowed baseline degradation")
        for client_index, client in enumerate(clients, start=1):
            try:
                report_logger.print_info(f"INFO: Performing final RSSI check for client #{client_index} '{client}'")
                bssid = initialize.get_association_status(client, "cli")
                host = get_device_advertising_bssid(initialize, bssid)
                state = get_client_rssi(initialize, client, host)
            except Exception as err:
                report_logger.print_error(f"Final RSSI Monitoring check failed for '{client}': {err}")
                continue
            error = validate_client_rssi(state, baseline_rssi[client], MAX_RSSI_DEGRADATION_DB)
            if error:
                report_logger.print_error(f"Client '{client}' final RSSI validation failed: {error}")
                continue
            report_logger.print_success(
                f"PASS: Client '{client}' final RSSI is {state['rssi_dbm']} dBm; "
                f"no degradation beyond {MAX_RSSI_DEGRADATION_DB} dB on "
                f"{state['host']}/{state['interface']}")
    finally:        
        report_logger.print_test("Exiting test_em_fronthaul_rssi_stability")
