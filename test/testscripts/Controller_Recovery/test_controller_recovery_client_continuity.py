import time
import threading

import pytest
from packet_analyzer.ieee1905_utils import *  # noqa: F401,F403
from packet_analyzer.packet_dissector import *  # noqa: F401,F403
from zaero.utils import zi_logger

import controller_recovery_utils as cr_utils
import device_utils


def _recover_extender(
    initialize,
    extender,
    clients,
    capture_name,
    started_at,
    allowed_bssids,
    results,
    step=None,
):
    try:
        recovery_result = cr_utils.recover_device(
            initialize,
            extender,
            started_at,
            results,
            step,
            zi_logger,
        )
        if isinstance(recovery_result, Exception):
            raise recovery_result
        recovery_time = recovery_result
        zi_logger.print_success(f"{extender}: SSH reachable after {recovery_time:.1f}s")
        results[extender] = {
            "recovery_time": recovery_time,
            "clients": clients,
        }
        zi_logger.print_success(f"PASS: {extender} services active; timer stopped at {recovery_time:.1f}s")
        zi_logger.print_step(f"{extender}: waiting 20 seconds before stopping capture")
        time.sleep(20)
        local_path = cr_utils.stop_and_collect_capture(
            initialize, extender, capture_name
        )
        zi_logger.print_step(f"{extender}: capture stopped")
        for client in clients:
            cr_utils.reconnect_device(initialize, client, zi_logger, step=9)
        results[extender]["client_accessible"] = all(
            initialize.is_device_alive(client) for client in clients
        )
        ssh = initialize.get_connection_module_object("ssh")
        results[extender]["bssid_matches"] = {
            client: cr_utils.get_connected_bssid(initialize, client, ssh)
            in allowed_bssids
            for client in clients
        }
        zi_logger.print_success(f"{extender}: assigned client SSH access = {results[extender]['client_accessible']} ({clients})")
        results[extender]["ping_outputs"] = cr_utils.download_client_pings(
            initialize, clients, extender
        )
        results[extender]["capture_path"] = local_path
        zi_logger.print_step(f"{extender}: downloaded ping output and capture {local_path}")
    except Exception as error:
        results[extender] = {"error": error}


def test_controller_recovery_client_continuity(initialize):
    zi_logger.print_test(
        "Entering test_controller_recovery_client_continuity"
    )
    zi_logger.print_step("STEP 1: Discover enabled extenders and WLAN clients")
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

    zi_logger.print_step("STEP 2: Map the first WLAN client to each extender")
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

        zi_logger.print_step(
            f"STEP 3: Connect one WLAN client to each extender: {client_groups}"
        )
        for extender in extenders:
            # Record the original BSSID before recovery changes the topology.
            clients = client_groups[extender]
            client = clients[0]
            cr_utils.connect_clients_to_extender(initialize, [client], extender)
            client_bssid = cr_utils.get_connected_bssid(initialize, client, ssh)
            if not client_bssid:
                pytest.fail(f"{client}: could not determine initial connected BSSID")
            allowed_bssids.add(client_bssid)
            zi_logger.print_success(f"PASS: {extender} client connected by BSSID: {[client]}")

        allowed_bssids.update(cr_utils.get_fronthaul_bssids(initialize, "controller", ssh))
        for extender in extenders:
            allowed_bssids.update(cr_utils.get_fronthaul_bssids(initialize, extender, ssh))

        zi_logger.print_step("STEP 4: Start packet captures on all extenders")
        for extender in extenders:
            # Start capture and ping traffic before rebooting the controller.
            capture_names[extender] = cr_utils.start_extender_capture(
                initialize, extender, "controller_recovery_client", step=4
            )
            extender_al_macs[extender] = initialize.get_al_mac_address(
                extender, "cli"
            )
            capture_started.add(extender)
            clients = client_groups[extender]
            if clients:
                cr_utils.start_client_ping(
                    initialize,
                    clients,
                    f"/tmp/controller_recovery_{extender}_client_ping.txt",
                )
                zi_logger.print_step(
                    f"STEP 5: {extender}: Start continuous Wi-Fi client ping to 8.8.8.8"
                )

        zi_logger.print_step("STEP 6: Reboot the controller and start recovery timers")
        initialize.reboot_device("controller", method="cli")
        # Start timing only after the reboot command has been issued.
        controller_started_at = time.monotonic()
        recovery_started = {
            extender: time.monotonic() for extender in extenders
        }
        time.sleep(30)
        zi_logger.print_step("STEP 7: Reconnect to the controller after reboot")
        controller_recovery = {}
        controller_result = cr_utils.recover_device(
            initialize,
            "controller",
            controller_started_at,
            controller_recovery,
            7,
            zi_logger,
        )
        if isinstance(controller_result, Exception):
            raise controller_result

        zi_logger.print_step("STEP 9: Recover extenders and collect recovery results")
        threads = []
        for extender in extenders:
            # Recover each extender in parallel once the controller returns.
            thread = threading.Thread(
                target=_recover_extender,
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

        zi_logger.print_step("STEP 10: Validate recovery KPI and extender reachability")
        for extender in extenders:
            result = recovery_results.get(extender, {})
            if "error" in result:
                pytest.fail(f"{extender}: recovery failed: {result['error']}")
            recovery_time = result["recovery_time"]
            if recovery_time >= cr_utils.RECOVERY_KPI_SECONDS:
                pytest.fail(
                    f"{extender}: recovery took {recovery_time:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )
            if not initialize.is_device_alive(extender):
                pytest.fail(f"{extender}: extender is not reachable after recovery")
            zi_logger.print_success(
                f"PASS: {extender} recovered in {recovery_time:.1f}s and is reachable after recovery"
            )

        zi_logger.print_step("STEP 11: Validate client connectivity and ping recovery")
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
                pytest.fail(
                    f"{extender}: clients connected to a non-fronthaul BSSID after recovery: "
                    f"{mismatched_bssids}"
                )
            zi_logger.print_success(f"PASS: {extender} clients stayed on a valid fronthaul BSSID")
            zi_logger.print_step(f"{extender}: Validate client ping outage and recovery")
            zi_logger.print_success(f"PASS: {extender} assigned clients are SSH accessible")
            for client, output in result["ping_outputs"].items():
                cr_utils.validate_ping_recovery(output, client)
                zi_logger.print_success(f"PASS: {client} ping shows recovery outage and successful replies")

        zi_logger.print_step("STEP 12: Validate topology packet captures")
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

        if capture_validation_errors:
            pytest.fail("; ".join(capture_validation_errors))
    finally:
        for extender, capture_name in capture_names.items():
            try:
                if extender not in capture_started:
                    continue
                ssh.switch_connection(extender)
                initialize.stop_frame_capture(extender)
                initialize.delete_captured_pcap(extender, capture_name)
            except Exception as error:
                zi_logger.log(f"Could not clean up {extender} capture: {error}")
