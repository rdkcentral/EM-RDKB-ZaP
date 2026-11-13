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
from rdkbmeshzap.common_utils import client_utils, device_utils, report_logger
from rdkbmeshzap.common_utils.scale_validation_utils import *
def test_em_scale_client_traffic_throughput(initialize):
    """Verify client-to-extender throughput and scale stability."""
    report_logger.print_test("Entering test_em_scale_client_traffic_throughput")
    extenders = []
    devices = []
    clients = []
    server_started = False
    try:
        report_logger.print_step("STEP 1: Discover scale topology and connect WLAN clients")
        extenders = device_utils.get_enabled_extenders(initialize)
        devices = [CONTROLLER_DEVICE, *extenders]
        all_clients = device_utils.get_enabled_clients(initialize)
        clients = [
            client
            for client in all_clients
            if client.rsplit("_wlan_client_", 1)[0] in devices
        ]
        excluded_clients = [
            client for client in all_clients if client not in clients
        ]
        if excluded_clients:
            report_logger.print_info("Excluding clients without an enabled extender owner: " f"{', '.join(excluded_clients)}")
        if not extenders or not clients:
            report_logger.print_error("No enabled extenders or WLAN clients are available")
            return
        try:
            ssid = initialize.get_ssid(CONTROLLER_DEVICE, "controller_device_index", "de")
            password = initialize.get_fronthaul_password(CONTROLLER_DEVICE, "gui")
        except Exception as error:
            report_logger.print_error(f"Unable to retrieve WLAN credentials: {error}")
            return
        connected_clients = []
        for client in clients:
            if client_utils.remove_and_connect_client(initialize, client, ssid, password):
                connected_clients.append(client)
            else:
                report_logger.print_error(f"{client} (owner={client.rsplit('_wlan_client_', 1)[0]}): unable to connect to the EasyMesh SSID")
        clients = connected_clients
        if not clients:
            report_logger.print_error("No mesh-owned WLAN clients connected successfully")
            return
        scale_setup = get_enabled_scale_setup(initialize)
        expected_extenders = scale_setup["expected_agent_count"]
        expected_clients = scale_setup["expected_client_count"]
        if len(extenders) < expected_extenders:
            report_logger.print_error(f"Configured extender count {len(extenders)} is below expected scale count {expected_extenders}")
            return
        if len(clients) < expected_clients:
            report_logger.print_error(f"Configured extender-client count {len(clients)} is below expected scale count {expected_clients}")
            return
        report_logger.print_info("INFO: Using connected WLAN clients: " + ", ".join(f"{client} (owner={client.rsplit('_wlan_client_', 1)[0]})" for client in clients))
        report_logger.print_step("STEP 2: Capture topology, client association, and throughput baseline")
        baseline_associations = get_fronthaul_station_macs_by_device(initialize, devices)
        association_mismatches = validate_client_associations(initialize, devices, clients, baseline_associations)
        if association_mismatches:
            for mismatch in association_mismatches:
                report_logger.print_error(f"Baseline association: {mismatch}")
            return
        baseline_presence = get_extender_presence_snapshot(initialize, extenders)
        presence_mismatches = get_extender_presence_mismatches(expected_extenders, baseline_presence, baseline_presence)
        if presence_mismatches:
            for mismatch in presence_mismatches:
                report_logger.print_error(f"Baseline topology: {mismatch}")
            return
        controller_ip = initialize.read_from_database(CONTROLLER_DEVICE, "bridge_ip")
        try:
            initialize.execute_command(CONTROLLER_DEVICE, f"rm -f {IPERF_SERVER_LOG}")
            initialize.start_iperf_server(CONTROLLER_DEVICE, controller_ip, IPERF_SERVER_LOG)
            server_started = True
            report_logger.print_success("PASS: Started iperf3 server on controller")
        except Exception as error:
            report_logger.print_error(f"Unable to start iperf3 server on controller: {error}")
            return
        client_targets = {
            client: controller_ip
            for client in clients
        }
        baseline_throughput = collect_client_iperf_samples(initialize, client_targets, IPERF_SAMPLE_DURATION_SEC)
        missing_baseline = sorted(set(clients) - set(baseline_throughput))
        if missing_baseline:
            report_logger.print_error("Baseline throughput is missing for clients: " f"{', '.join(missing_baseline)}")
            return
        for client, throughput in baseline_throughput.items():
            report_logger.print_success(f"PASS: Baseline throughput {client} (owner={client.rsplit('_wlan_client_', 1)[0]})={throughput:.2f} Mbps")
        report_logger.print_step("STEP 3: Monitor topology, client associations, and throughput")
        end_time = time.time() + TEST_DURATION_SEC
        poll_count = 0
        while time.time() < end_time:
            poll_count += 1
            presence = get_extender_presence_snapshot(initialize, extenders)
            presence_mismatches = get_extender_presence_mismatches(expected_extenders, baseline_presence, presence)
            for mismatch in presence_mismatches:
                report_logger.print_error(f"Poll #{poll_count}: topology mismatch: {mismatch}")
            if presence_mismatches:
                return
            association_mismatches = validate_client_associations(initialize, devices, clients, baseline_associations)
            for mismatch in association_mismatches:
                report_logger.print_error(f"Poll #{poll_count}: client association mismatch: {mismatch}")
            if association_mismatches:
                return
            throughput = collect_client_iperf_samples(initialize, client_targets, IPERF_SAMPLE_DURATION_SEC)
            missing_clients = sorted(set(clients) - set(throughput))
            if missing_clients:
                report_logger.print_error(f"Poll #{poll_count}: throughput missing for clients: {', '.join(missing_clients)}")
                return
            for client, value in throughput.items():
                baseline = baseline_throughput.get(client)
                minimum = baseline * MIN_THROUGHPUT_RATIO if baseline else 0
                if baseline is None or value < minimum:
                    report_logger.print_error(f"Poll #{poll_count}: {client} (owner={client.rsplit('_wlan_client_', 1)[0]}) throughput degraded: observed={value:.2f} Mbps, floor={minimum:.2f} Mbps")
                else:
                    report_logger.print_success(f"PASS: Poll #{poll_count}: {client} (owner={client.rsplit('_wlan_client_', 1)[0]}) throughput={value:.2f} Mbps")
            remaining = end_time - time.time()
            if remaining > 0:
                time.sleep(min(POLL_INTERVAL_SEC, remaining))
        report_logger.print_step("STEP 4: Capture final topology, associations, and throughput")
        final_presence = get_extender_presence_snapshot(initialize, extenders)
        final_presence_mismatches = get_extender_presence_mismatches(expected_extenders, baseline_presence, final_presence)
        for mismatch in final_presence_mismatches:
            report_logger.print_error(f"Final topology mismatch: {mismatch}")
        final_association_mismatches = validate_client_associations(initialize, devices, clients, baseline_associations)
        for mismatch in final_association_mismatches:
            report_logger.print_error(f"Final association mismatch: {mismatch}")
        if final_presence_mismatches or final_association_mismatches:
            return
    finally:
        if server_started:
            try:
                initialize.stop_iperf_server(CONTROLLER_DEVICE)
            except Exception as error:
                report_logger.print_error(f"Unable to stop iperf3 server on controller: {error}")
        report_logger.print_test("Exiting test_em_scale_client_traffic_throughput")