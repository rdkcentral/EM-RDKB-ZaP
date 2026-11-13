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

from rdkbmeshzap.common_utils import client_utils, device_utils, report_logger
from rdkbmeshzap.common_utils.scale_validation_utils import *

def test_em_scale_client_traffic_throughput(initialize):
    """Verify client-to-extender throughput with one iperf3 sample."""
    report_logger.print_test(
        "Entering test_em_scale_client_traffic_throughput")
    extenders = []
    devices = []
    clients = []
    server_started = False
    try:
        report_logger.print_step("STEP 1: Discover scale topology and connect WLAN clients")
        extenders = device_utils.get_enabled_extenders(initialize)
        devices = [CONTROLLER_DEVICE, *extenders]
        all_clients = device_utils.get_enabled_clients(initialize)
        clients = [client
            for client in all_clients
            if client.rsplit("_wlan_client_", 1)[0] in devices]
        if not extenders or not clients:
            report_logger.print_error("No enabled extenders or WLAN clients are available")
            return
        try:
            ssid = initialize.get_ssid(
                CONTROLLER_DEVICE, "controller_device_index", "de")
            password = initialize.get_fronthaul_password(
                CONTROLLER_DEVICE, "gui"
            )
        except Exception as error:
            report_logger.print_error(
                f"Unable to retrieve WLAN credentials: {error}"
            )
            return

        connected_clients = []
        for client in clients:
            if client_utils.remove_and_connect_client(
                initialize, client, ssid, password
            ):
                connected_clients.append(client)
            else:
                report_logger.print_error(
                    f"{client} (owner={client.rsplit('_wlan_client_', 1)[0]}): unable to "
                    "connect to the EasyMesh SSID"
                )
        clients = connected_clients
        if not clients:
            report_logger.print_error(
                "No mesh-owned WLAN clients connected successfully"
            )
            return
        report_logger.print_success(
            "Connected WLAN clients: "
            + ", ".join(
                f"{client} (owner={client.rsplit('_wlan_client_', 1)[0]})"
                for client in clients
            )
        )

        scale_setup = get_enabled_scale_setup(initialize)
        expected_extenders = scale_setup["expected_agent_count"]
        expected_clients = scale_setup["expected_client_count"]
        if len(extenders) < expected_extenders:
            report_logger.print_error(
                f"Configured extender count {len(extenders)} is below "
                f"expected scale count {expected_extenders}"
            )
            return
        if len(clients) < expected_clients:
            report_logger.print_error(
                f"Configured extender-client count {len(clients)} is below "
                f"expected scale count {expected_clients}"
            )
            return
        report_logger.print_success(
            "PASS: Using connected WLAN clients: "
            + ", ".join(
                f"{client} (owner={client.rsplit('_wlan_client_', 1)[0]})"
                for client in clients
            )
        )

        report_logger.print_step(
            "STEP 2: Validate topology and client association before throughput test"
        )
        baseline_associations = get_fronthaul_station_macs_by_device(
            initialize, devices)
        association_mismatches = validate_client_associations(
            initialize, devices, clients, baseline_associations)
        if association_mismatches:
            for mismatch in association_mismatches:
                report_logger.print_error(f"Client association: {mismatch}")
            return

        baseline_presence = get_extender_presence_snapshot(initialize, extenders)
        presence_mismatches = get_extender_presence_mismatches(
            expected_extenders, baseline_presence, baseline_presence)
        if presence_mismatches:
            for mismatch in presence_mismatches:
                report_logger.print_error(f"Topology: {mismatch}")
            return

        controller_ip = initialize.read_from_database(
            CONTROLLER_DEVICE, "bridge_ip")
        try:
            initialize.execute_command(
                CONTROLLER_DEVICE, f"rm -f {IPERF_SERVER_LOG}"
            )
            initialize.start_iperf_server(
                CONTROLLER_DEVICE,
                controller_ip,
                IPERF_SERVER_LOG,
            )
            server_started = True
            report_logger.print_success(
                "PASS: Started iperf3 server on controller"
            )
        except Exception as error:
            report_logger.print_error(
                f"Unable to start iperf3 server on controller: {error}"
            )
            return
        client_targets = {
            client: controller_ip
            for client in clients
        }
        throughput = collect_client_iperf_samples(
            initialize, client_targets, IPERF_SAMPLE_DURATION_SEC)
        missing_clients = sorted(set(clients) - set(throughput))
        if missing_clients:
            report_logger.print_error(
                "Throughput is missing for clients: "
                f"{', '.join(missing_clients)}"
            )
            return
        for client, value in throughput.items():
            report_logger.print_success(
                f"PASS: Throughput {client} "
                f"(owner={client.rsplit('_wlan_client_', 1)[0]})={value:.2f} Mbps"
            )
    finally:
        if server_started:
            try:
                initialize.stop_iperf_server(CONTROLLER_DEVICE)
            except Exception as error:
                report_logger.print_error(
                    f"Unable to stop iperf3 server on controller: {error}"
                )
        report_logger.print_test(
            "Exiting test_em_scale_client_traffic_throughput"
        )
