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
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import POLL_INTERVAL_SEC, TEST_DURATION_SEC

def test_em_fronthaul_link_stability(initialize):
    """
    Verify stable fronthaul connectivity and reachability.
    """
    report_logger.print_test("Entering test_em_fronthaul_link_stability")
    try :
        report_logger.print_step("STEP 1: Identify configured WLAN clients, connect them to their assigned devices, and verify availability")
        present_clients = device_utils.get_enabled_clients(initialize)
        if not present_clients:
            report_logger.print_error("No fronthaul clients are marked present in the database")
        try:
            clients = connect_wlan_clients(
                initialize, present_clients, require_all=False)
        except Exception as err:
            report_logger.print_error(f"Unable to prepare fronthaul clients for monitoring: {err}")
        unavailable = [
            f"{client}: connection unavailable"
            for client in present_clients
            if client not in clients
        ]
        if unavailable:
            report_logger.print_error(f"Unable to establish association for all configured WLAN clients: {unavailable}")
            return
        else:    
            report_logger.print_success(f"PASS: Connected clients before stability test: {', '.join(clients)}")
        poll_interval_sec = POLL_INTERVAL_SEC
        test_duration_sec = TEST_DURATION_SEC
        gateway_ip = initialize.read_from_database("controller", "bridge_ip")
        report_logger.print_step("STEP 2: Capture and validate baseline controller-gateway reachability for each client")
        for client_index, client in enumerate(clients, start=1):
            try:
                report_logger.print_step(f"STEP 2.{client_index}: Ping the controller gateway from client #{client_index} '{client}' and validate reachability")
                ping_result = initialize.ping_ipv4(client, gateway_ip, "3")
            except Exception as err:
                report_logger.print_error(f"Baseline ping failed for '{client}' to gateway: {err}")
                continue
            if ping_result != 0:
                report_logger.print_error(f"Client '{client}' cannot ping controller gateway")
                continue
            report_logger.print_success(f"PASS: Client '{client}' can ping controller gateway")
        report_logger.print_info(f"INFO: Baseline ping checked for {len(clients)} configured present WLAN client(s)")
        report_logger.print_step("STEP 3: Validate controller-gateway reachability for every client at each poll")
        start_time = time.time()
        poll_count = 0
        while time.time() - start_time < test_duration_sec:
            elapsed_min = int((time.time() - start_time) / 60)
            poll_count += 1
            report_logger.print_info(f"INFO: Poll #{poll_count} at ~{elapsed_min} min elapsed")
            for client_index, client in enumerate(clients, start=1):
                try:
                    report_logger.print_step(f"STEP 3.{poll_count}.{client_index}: Ping the controller gateway from client #{client_index} '{client}' and validate reachability")
                    ping_result = initialize.ping_ipv4(client, gateway_ip, "3")
                except Exception as err:
                    report_logger.print_error(f"Poll #{poll_count}: Ping failed for '{client}' to {gateway_ip}: {err}")
                    continue
                if ping_result != 0:
                    report_logger.print_error(f"Poll #{poll_count} ({elapsed_min} min): Client '{client}' cannot ping controller gateway")
                    continue
                report_logger.print_success(f"PASS: Poll #{poll_count}: Client '{client}' can ping controller gateway {gateway_ip}")
            time.sleep(poll_interval_sec)
        report_logger.print_step("STEP 4: Perform the final controller-gateway reachability check for every client")
        for client_index, client in enumerate(clients, start=1):
            try:
                report_logger.print_info(f"INFO: Performing final ping check for client #{client_index} '{client}'")
                ping_result = initialize.ping_ipv4(client, gateway_ip, "3")
            except Exception as err:
                report_logger.print_error(f"Final ping failed for '{client}' to gateway: {err}")
                continue
            if ping_result != 0:
                report_logger.print_error(f"Client '{client}' cannot ping controller gateway at end of test")
                continue
            report_logger.print_success(f"PASS: Client '{client}' can ping controller gateway at end of test")
    finally:    
        report_logger.print_test("Exiting test_em_fronthaul_link_stability")
