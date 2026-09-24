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
import threading
import pytest
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import report_logger
import controller_recovery_utils as cr_utils
from rdkbmeshzap.common_utils import client_utils, device_utils

def test_controller_recovery_client_continuity(initialize):
    report_logger.print_test(
        "Entering test_controller_recovery_client_continuity"
    )
    CONTROLLER_RECOVERY_KPI_SECONDS = cr_utils.get_controller_recovery_kpi(initialize)
    report_logger.print_step(
        "STEP 1: Identify enabled extenders and their configured WLAN clients"
    )
    extenders = device_utils.get_enabled_extenders(initialize)
    if not extenders:
        pytest.fail("No enabled extenders found in infra.yaml")
    client_devices = [
        device
        for device in initialize.get_testbed_devices()
        if (
            "client" in device
            and "wlan" in device
            and initialize.read_from_database(device, "device_present")
        )
    ]
    if not client_devices:
        pytest.fail("No enabled WLAN clients found in infra.yaml")
    client_groups = {
        extender: [
            client
            for client in client_devices
            if client.startswith(f"{extender}_")
        ]
        for extender in extenders
    }
    extenders_without_clients = [
        extender for extender, clients in client_groups.items() if not clients
    ]
    if extenders_without_clients:
        pytest.fail(
            "Enabled extenders without enabled WLAN clients: "
            f"{extenders_without_clients}"
        )
    else:
        report_logger.print_success(
            "PASS: All enabled extenders have configured WLAN clients"
        )

    capture_names = {}
    extender_al_macs = {}
    capture_started = set()
    recovery_started = {}
    recovery_results = {}
    ssh = initialize.get_connection_module_object("ssh")
    allowed_bssids = set()
    capture_validation_errors = []

    try:
        # Keep the controller session established before the recovery window starts.
        ssh.switch_connection("controller")

        report_logger.print_step(
            "STEP 2: Associate configured WLAN client with each extender and record its initial BSSID"
        )
        report_logger.print_info(
            "INFO: Recording initial client association status before controller reboot"
        )
        for index, extender in enumerate(extenders, start=1):
            # Record the original BSSID before recovery changes the topology.
            clients = client_groups[extender]
            client = clients[0]
            client_utils.connect_clients_to_extender(initialize, [client], extender)
            client_bssid = client_utils.get_connected_client_bssid(initialize, client, ssh)
            if not client_bssid:
                pytest.fail(f"{client}: could not determine initial client connected BSSID")
            report_logger.print_success(f"PASS: {extender} client connected to BSSID: {client_bssid}")

        allowed_bssids.update(initialize.get_fronthaul_bssids("controller"))
        for extender in extenders:
            allowed_bssids.update(initialize.get_fronthaul_bssids(extender))

        report_logger.print_step(
            "STEP 3: Start IEEE 1905 captures on all extenders before the controller reboot"
        )
        for index, extender in enumerate(extenders, start=1):
            # Start capture and ping traffic before rebooting the controller.
            capture_names[extender] = device_utils.start_capture(
                initialize,
                extender,
                "test_controller_recovery_client_continuity",
                step=f"3.{index}",
                include_device=True,
            )
            capture_started.add(extender)
            extender_al_macs[extender] = initialize.get_al_mac_address(
                extender, "cli"
            )

        report_logger.print_step(
            "STEP 4: Start continuous client ping before the controller reboot"
        )
        for extender in extenders:
            clients = client_groups[extender]
            if clients:
                client_utils.start_client_ping(
                    initialize,
                    clients,
                    f"/tmp/controller_recovery_{extender}_client_ping.txt",
                )
                report_logger.print_success(
                    f"PASS: Continuous client ping started for {clients} "
                    f"associated with {extender} for recovery measurement"
                )

        report_logger.print_step(
            "STEP 5: Reboot the controller and start per-extender recovery timers"
        )
        report_logger.print_info(
            "INFO: Starting the controller recovery observation window"
        )
        initialize.reboot_device("controller", method="cli")
        # Start timing only after the reboot command has been issued.
        controller_started_at = time.monotonic()
        recovery_started = {
            extender: time.monotonic() for extender in extenders
        }
        report_logger.print_success(
            "PASS: Controller rebooted and per-extender recovery timers started successfully"
        )
        time.sleep(30)
        report_logger.print_step(
            "STEP 6: Reconnect to the controller and verify controller recovery"
        )
        controller_recovery = {}
        controller_result = cr_utils.recover_device(
            initialize,
            "controller",
            controller_started_at,
            controller_recovery,
            "6.1",
        )
        if isinstance(controller_result, Exception):
            report_logger.print_error(
                f"ERROR: Controller recovery failed: {controller_result}"
            )
            raise controller_result

        report_logger.print_step(
            "STEP 7: Recover extenders in parallel and collect recovery and capture results"
        )
        report_logger.print_info(
            "INFO: Recovering extenders concurrently after controller recovery"
        )
        threads = []
        for index, extender in enumerate(extenders, start=1):
            # Recover each extender in parallel once the controller returns.
            thread = threading.Thread(
                target=cr_utils.recover_extender_and_client,
                args=(
                    initialize,
                    extender,
                    client_groups[extender],
                    capture_names[extender],
                    recovery_started[extender],
                    allowed_bssids,
                    recovery_results,
                    f"7.{index}",
                ),
                name=f"recover-{extender}",
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        report_logger.print_info(
            "INFO: All extender recovery threads have completed"
        )

        report_logger.print_step(
            "STEP 8: Identify recovered extenders and validate their recovery KPI"
        )
        recovered_extenders = []
        for index, extender in enumerate(extenders, start=1):
            report_logger.print_step(
                f"STEP 8.{index}: Validate {extender} recovery and reachability"
            )
            result = recovery_results.get(extender, {})
            if "capture_path" in result:
                capture_started.discard(extender)
            if "error" in result:
                report_logger.print_error(
                    f"FAIL: {extender} recovery failed: {result['error']}"
                )
                continue
            if not result:
                report_logger.print_error(
                    f"FAIL: {extender} recovery result is unavailable; the recovery "
                    "worker may have failed or did not complete"
                )
                continue
            recovery_time = result["recovery_time"]
            if recovery_time >= CONTROLLER_RECOVERY_KPI_SECONDS:
                report_logger.print_error(
                    f"FAIL: {extender} recovery took {recovery_time:.1f}s; "
                    f"KPI is < {CONTROLLER_RECOVERY_KPI_SECONDS}s"
                )
                continue
            if not initialize.is_device_alive(extender):
                report_logger.print_error(
                    f"FAIL: {extender} is not reachable after recovery"
                )
                continue
            report_logger.print_success(
                f"PASS: {extender} is reachable and recovered within the KPI threshold "
                f"in {recovery_time:.1f}s"
            )
            recovered_extenders.append(extender)

        if not recovered_extenders:
            pytest.fail("No extender recovered within the recovery KPI")

        report_logger.print_step(
            "STEP 9: Stop client ping and validate ping recovery logs"
        )
        for extender in recovered_extenders:
            result = recovery_results.get(extender, {})
            if "error" in result:
                pytest.fail(f"{extender}: recovery failed: {result['error']}")
            if not result:
                pytest.fail(f"{extender}: recovery result is unavailable")
            if not result["client_accessible"]:
                pytest.fail(f"{extender}: one or more WLAN clients were inaccessible")
            report_logger.print_step(
                f"{extender}: Check stopped client ping output and recovery"
            )
            report_logger.print_success(f"PASS: {extender} assigned clients are SSH accessible")
            for client, output in result["ping_outputs"].items():
                if client_utils.validate_ping_recovery(output, client):
                    report_logger.print_success(
                        f"PASS: {client} ping shows recovery outage and successful replies"
                    )

        report_logger.print_step(
            "STEP 10: Verify client connection device and BSSID after recovery"
        )
        bssid_devices = {
            bssid: "controller"
            for bssid in initialize.get_fronthaul_bssids("controller")
        }
        for extender in recovered_extenders:
            bssid_devices.update({
                bssid: extender
                for bssid in initialize.get_fronthaul_bssids(extender)
            })
            result = recovery_results[extender]
            mismatched_bssids = [
                client
                for client, matches in result["bssid_matches"].items()
                if not matches
            ]
            if mismatched_bssids:
                report_logger.print_error(
                    f"{extender}: clients connected to a non-fronthaul BSSID: "
                    f"{mismatched_bssids}"
                )
                continue
            for client, bssid in result["client_bssids"].items():
                connected_device = bssid_devices.get(bssid) or cr_utils.get_parent_device_by_bssid(
                    initialize, ["controller", *extenders], bssid
                ) or "unknown device"
                report_logger.print_info(
                    f"INFO: {client} connected to {connected_device} after recovery "
                    f"(BSSID: {bssid})"
                )
            report_logger.print_success(
                f"PASS: {extender} clients stayed on a valid fronthaul BSSID"
            )

        report_logger.print_step(
            "STEP 11: Validate topology exchange packets for recovered extenders"
        )
        for index, extender in enumerate(recovered_extenders, start=1):
            report_logger.print_step(
                f"STEP 11.{index}: Validate topology traffic for {extender}"
            )
            result = recovery_results[extender]
            local_path = result["capture_path"]
            try:
                packets = reassemble_packets(local_path)
                cr_utils.validate_topology_capture(
                    packets, extender, extender_al_macs[extender]
                )
            except Exception as error:
                capture_validation_errors.append(f"{extender}: {error}")
            else:
                capture_started.discard(extender)

        if capture_validation_errors:
            pytest.fail(
                "Topology capture validation failed: "
                + "; ".join(capture_validation_errors)
            )
    finally:
        report_logger.print_test(
            "Exiting test_controller_recovery_client_continuity"
        )
        if capture_started:
            for extender in recovered_extenders:
                capture_name = capture_names.get(extender)
                if extender not in capture_started:
                    continue
                if not capture_name:
                    continue
                try:
                    device_utils.stop_and_collect_capture(
                        initialize, extender, capture_name
                    )
                except Exception as error:
                    report_logger.print_error(
                        f"Could not stop {extender} capture: {error}"
                    )
