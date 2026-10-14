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

def test_em_fronthaul_phyrate_stability(initialize):
    """
    Verify client TX/RX PHY rates remain within the allowed drop limit.
    """
    report_logger.print_test("Entering test_em_fronthaul_phyrate_stability")
    try:
        report_logger.print_step("STEP 1: Identify configured WLAN clients, connect them to their assigned devices, and verify availability")
        present_clients = device_utils.get_enabled_clients(initialize)
        if not present_clients:
                report_logger.print_error("No fronthaul clients are marked present in the database")
        try:
            clients = connect_wlan_clients(
                initialize, present_clients, require_all=False)
        except Exception as err:
            report_logger.print_error(f"Unable to prepare fronthaul clients for PHY-rate monitoring: {err}")
        unavailable = [
            f"{client}: connection unavailable"
            for client in present_clients
            if client not in clients
        ]
        if unavailable:
            report_logger.print_error(f"Unable to establish association for all configured WLAN clients: {unavailable}")
            return
        report_logger.print_success(f"PASS: Connected clients before PHY-rate test: {', '.join(clients)}")
        poll_interval_sec = POLL_INTERVAL_SEC
        test_duration_sec = TEST_DURATION_SEC
        report_logger.print_step("STEP 2: Capture each client's baseline TX/RX PHY rates and validate that both rates are available")
        report_logger.print_info(f"INFO: Capturing baseline PHY rates for {len(clients)} client(s)")
        baseline_rates = {}
        for client_index, client in enumerate(clients, start=1):
            try:
                report_logger.print_info(f"INFO: Capturing baseline PHY rates for client #{client_index} '{client}'")
                bssid = initialize.get_association_status(client, "cli")
                host = get_device_advertising_bssid(initialize, bssid)
                state = get_client_phy_rates(initialize, client, host)
                error = validate_client_phy_rates(state)
            except Exception as err:
                report_logger.print_error(f"Unable to capture baseline PHY rate for '{client}': {err}")
                continue
            if error:
                report_logger.print_error(f"Client '{client}' failed baseline PHY-rate validation: {error}")
                continue
            baseline_rates[client] = state
            report_logger.print_success(
                f"PASS: Client '{client}' baseline PHY rate: "
                f"TX {state['tx_mbps']:.1f} Mbps, RX {state['rx_mbps']:.1f} Mbps "
                f"on {state['host']}/{state['interface']}")
        report_logger.print_info(f"INFO: Baseline captured for all {len(baseline_rates)} configured present WLAN client(s)")
        report_logger.print_step("STEP 3: Monitor each client's TX/RX PHY rates and validate the allowed baseline drop throughout the test")
        start_time = time.time()
        poll_count = 0
        while time.time() - start_time < test_duration_sec:
            poll_count += 1
            elapsed_sec = int(time.time() - start_time)
            report_logger.print_step(f"STEP 3.{poll_count}: Validate each client's TX/RX PHY rates against its baseline")
            report_logger.print_info(f"INFO: Poll #{poll_count} at {elapsed_sec}s elapsed")
            for client_index, client in enumerate(clients, start=1):
                try:
                    report_logger.print_step(f"STEP 3.{poll_count}.{client_index}: Validate PHY rates for client #{client_index} '{client}'")
                    bssid = initialize.get_association_status(client, "cli")
                    host = get_device_advertising_bssid(initialize, bssid)
                    state = get_client_phy_rates(initialize, client, host)
                    error = validate_client_phy_rates(state, baseline_rates[client], PHY_RATE_DROP_PERCENT)
                except Exception as err:
                    report_logger.print_error(f"PHY-rate poll #{poll_count} failed for '{client}': {err}")
                    continue
                if error:
                    report_logger.print_error(f"Client '{client}' PHY-rate check failed: {error}")
                    continue
                report_logger.print_success(
                    f"PASS: Client '{client}' PHY rate: TX {state['tx_mbps']:.1f} Mbps, "
                    f"RX {state['rx_mbps']:.1f} Mbps on "
                    f"{state['host']}/{state['interface']}")
            time.sleep(poll_interval_sec)
        report_logger.print_step("STEP 4: Capture final PHY rates for all clients and validate the allowed baseline drop limit")
        for client_index, client in enumerate(clients, start=1):
            try:
<<<<<<< HEAD
                report_logger.print_info(f"INFO: Capturing final PHY rates for client #{client_index} '{client}'")
=======
            report_logger.print_info(f"INFO: Capturing final PHY rates for client #{client_index} '{client}'")
>>>>>>> b0e5ef072ff1d5a0bbdaa537170ffab5b1eea238
                bssid = initialize.get_association_status(client, "cli")
                host = get_device_advertising_bssid(initialize, bssid)
                state = get_client_phy_rates(initialize, client, host)
            except Exception as err:
                report_logger.print_error(f"Final PHY-rate Monitoring failed for '{client}': {err}")
                continue
            error = validate_client_phy_rates(state, baseline_rates[client], PHY_RATE_DROP_PERCENT)
            if error:
                report_logger.print_error(f"Client '{client}' final PHY validation failed: {error}")
                continue
            report_logger.print_success(
                f"PASS: Client '{client}' final PHY rate: "
                f"TX {state['tx_mbps']:.1f} Mbps, "
                f"RX {state['rx_mbps']:.1f} Mbps on "
                f"{state['host']}/{state['interface']}")
    finally:        
        report_logger.print_test("Exiting test_em_fronthaul_phyrate_stability")
