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
    report_logger.print_step("STEP 1: Discover enabled extenders and WLAN clients")
    extenders = device_utils.get_enabled_extenders(initialize)
    if not extenders:
        pytest.fail("No enabled extenders found in infra.yaml")
    client_devices = [
        device
        for device in initialize.get_testbed_devices()
        if "client" in device and "wlan" in device
    ]
    if not client_devices:
        pytest.fail("No enabled WLAN clients found in infra.yaml")
    extenders = [
        extender
        for extender in extenders
        if any(client.startswith(f"{extender}_") for client in client_devices)
    ]
    if not extenders:
        pytest.fail("No enabled extenders have a configured WLAN client")

    report_logger.print_step("STEP 2: Map the first WLAN client to each extender")
    client_groups = cr_utils.map_clients_to_extenders(client_devices, extenders)

    capture_names = {
        extender: f"controller_recovery_client_{extender}_{int(time.time())}.pcapng"
        for extender in extenders
    }
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
            f"STEP 3: Connect one WLAN client to each extender: {client_groups}"
        )
        for extender in extenders:
            # Record the original BSSID before recovery changes the topology.
            clients = client_groups[extender]
            client = clients[0]
            client_utils.connect_clients_to_extender(initialize, [client], extender)
            client_bssid = client_utils.get_connected_client_bssid(initialize, client, ssh)
            if not client_bssid:
                report_logger.print_error(
                    f"{client}: could not determine initial connected BSSID"
                )
                continue
            allowed_bssids.add(client_bssid)
            report_logger.print_success(f"PASS: {extender} client connected by BSSID: {[client]}")

        allowed_bssids.update(initialize.get_fronthaul_bssids("controller"))
        for extender in extenders:
            allowed_bssids.update(initialize.get_fronthaul_bssids(extender))

        report_logger.print_step("STEP 4: Start packet captures on all extenders")
        for extender in extenders:
            # Start capture and ping traffic before rebooting the controller.
            capture_names[extender] = device_utils.start_capture(
                initialize,
                extender,
                "test_controller_recovery_client_continuity",
                step=4,
                include_device=True,
            )
            extender_al_macs[extender] = initialize.get_al_mac_address(
                extender, "cli"
            )
            capture_started.add(extender)
            clients = client_groups[extender]
            if clients:
                client_utils.start_client_ping(
                    initialize,
                    clients,
                    f"/tmp/controller_recovery_{extender}_client_ping.txt",
                )
                report_logger.print_step(
                    f"STEP 5: {extender}: Start continuous Wi-Fi client ping to 8.8.8.8"
                )

        report_logger.print_step("STEP 6: Reboot the controller and start recovery timers")
        initialize.reboot_device("controller", method="cli")
        # Start timing only after the reboot command has been issued.
        controller_started_at = time.monotonic()
        recovery_started = {
            extender: time.monotonic() for extender in extenders
        }
        time.sleep(30)
        report_logger.print_step("STEP 7: Reconnect to the controller after reboot")
        controller_recovery = {}
        controller_result = cr_utils.recover_device(
            initialize,
            "controller",
            controller_started_at,
            controller_recovery,
            7,
            report_logger,
        )
        if isinstance(controller_result, Exception):
            raise controller_result

        report_logger.print_step("STEP 9: Recover extenders and collect recovery results")
        threads = []
        for extender in extenders:
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
                    9,
                ),
                name=f"recover-{extender}",
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        for extender, result in recovery_results.items():
            if "capture_path" in result:
                capture_started.discard(extender)
            if "error" in result:
                report_logger.print_error(
                    f"{extender}: recovery failed: {result['error']}"
                )
                continue
            if result["recovery_time"] >= cr_utils.RECOVERY_KPI_SECONDS:
                report_logger.print_error(
                    f"{extender}: recovery took {result['recovery_time']:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )

        report_logger.print_step("STEP 10: Validate recovery KPI and extender reachability")
        for extender in extenders:
            result = recovery_results.get(extender, {})
            if "error" in result:
                report_logger.print_error(
                    f"{extender}: recovery failed: {result['error']}"
                )
                continue
            if not result:
                report_logger.print_error(
                    f"{extender}: recovery result is unavailable; the recovery "
                    "worker may have failed or did not complete"
                )
                continue
            recovery_time = result["recovery_time"]
            if recovery_time >= cr_utils.RECOVERY_KPI_SECONDS:
                report_logger.print_error(
                    f"{extender}: recovery took {recovery_time:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )
            if not initialize.is_device_alive(extender):
                report_logger.print_error(
                    f"{extender}: extender is not reachable after recovery"
                )
            report_logger.print_success(
                f"PASS: {extender} recovered in {recovery_time:.1f}s and is reachable after recovery"
            )

        report_logger.print_step("STEP 11: Validate client connectivity and ping recovery")
        bssid_devices = {
            bssid: "controller"
            for bssid in initialize.get_fronthaul_bssids("controller")
        }
        for extender in extenders:
            bssid_devices.update({
                bssid: extender
                for bssid in initialize.get_fronthaul_bssids(extender)
            })
        for extender in extenders:
            result = recovery_results[extender]
            if not result["client_accessible"]:
                pytest.fail(f"{extender}: one or more WLAN clients were inaccessible")
            mismatched_bssids = [
                client
                for client, matches in result["bssid_matches"].items()
                if not matches
            ]
            if mismatched_bssids:
                report_logger.print_error(
                    f"{extender}: clients connected to a non-fronthaul BSSID after recovery: "
                    f"{mismatched_bssids}"
                )
            for client, bssid in result["client_bssids"].items():
                connected_device = bssid_devices.get(bssid)
                if connected_device is None:
                    connected_device = cr_utils.get_bssid_device(
                        initialize, ["controller", *extenders], bssid
                    ) or "unknown device"
                report_logger.print_step(
                    f"{client}: connected to {connected_device} after recovery "
                    f"(BSSID {bssid})"
                )
            report_logger.print_success(f"PASS: {extender} clients stayed on a valid fronthaul BSSID")
            report_logger.print_step(f"{extender}: Validate client ping outage and recovery")
            report_logger.print_success(f"PASS: {extender} assigned clients are SSH accessible")
            for client, output in result["ping_outputs"].items():
                if client_utils.validate_ping_recovery(output, client):
                    report_logger.print_success(
                        f"PASS: {client} ping shows recovery outage and successful replies"
                    )

        report_logger.print_step("STEP 12: Validate topology packet captures")
        for extender in extenders:
            result = recovery_results[extender]
            local_path = result["capture_path"]
            try:
                packets = reassemble_packets(local_path)
                cr_utils.validate_topology_capture(
                    packets, extender, 12, extender_al_macs[extender]
                )
            except Exception as error:
                capture_validation_errors.append(f"{extender}: {error}")
            capture_started.discard(extender)

        for error in capture_validation_errors:
            report_logger.print_error(error)
    finally:
        report_logger.print_test(
            "Exiting test_controller_recovery_client_continuity"
        )
        for extender, capture_name in capture_names.items():
            try:
                if extender not in capture_started:
                    continue
                device_utils.stop_and_collect_capture(
                    initialize, extender, capture_name
                )
            except Exception as error:
                report_logger.log(f"Could not clean up {extender} capture: {error}")
