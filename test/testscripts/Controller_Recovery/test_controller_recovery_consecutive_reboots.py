import time

import pytest
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import report_logger

import controller_recovery_utils as cr_utils
from rdkbmeshzap.common_utils import device_utils


REBOOT_CYCLES = 5


def test_controller_recovery_consecutive_reboots(initialize):
    report_logger.print_test("Entering test_controller_recovery_consecutive_reboots")
    extenders = device_utils.get_enabled_extenders(initialize)
    if not extenders:
        pytest.fail("No enabled extenders found in infra.yaml")

    capture_names = {}
    capture_started = set()
    recovery_times = {}
    controller_recovery = {}
    capture_validation_errors = []

    try:
        report_logger.print_step(
            f"STEP 1: Start IEEE 1905 capture on enabled extenders: {extenders}"
        )
        for extender in extenders:
            capture_names[extender] = device_utils.start_capture(
                initialize,
                extender,
                "test_controller_recovery_consecutive_reboots",
                step=1,
                include_device=True,
            )
            capture_started.add(extender)
        report_logger.print_success("PASS: Packet capture started on all enabled extenders")

        for cycle in range(1, REBOOT_CYCLES + 1):
            report_logger.print_step(
                f"STEP {cycle + 1}: Reboot controller, consecutive cycle {cycle}/{REBOOT_CYCLES}"
            )
            cycle_start = time.monotonic()
            initialize.reboot_device("controller", method="cli")
            time.sleep(10)
            controller_result = cr_utils.recover_device(
                initialize,
                "controller",
                cycle_start,
                controller_recovery,
                2,
                report_logger,
            )
            if isinstance(controller_result, Exception):
                report_logger.print_error(
                    f"controller: recovery failed: {controller_result}"
                )
                continue
            if controller_result >= cr_utils.RECOVERY_KPI_SECONDS:
                report_logger.print_error(
                    f"controller: recovery took {controller_result:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )

            if cycle == REBOOT_CYCLES:
                for extender in extenders:
                    cr_utils.reconnect_device(
                        initialize,
                        extender,
                        report_logger,
                        step=2,
                        started_at=cycle_start,
                    )
                    recovery_times[extender] = time.monotonic() - cycle_start
            else:
                report_logger.print_success(f"PASS: Controller recovered after reboot cycle {cycle}")
        time.sleep(40)
        report_logger.print_step(
            "STEP 7: Validate recovery KPI and reachability for each extender"
        )
        for extender in extenders:
            if extender not in recovery_times:
                report_logger.print_error(
                    f"{extender}: recovery result is unavailable; the recovery "
                    "process may have failed or did not complete"
                )
                continue
            if not initialize.is_device_alive(extender):
                report_logger.print_error(
                    f"{extender}: extender is not reachable after recovery"
                )
            if recovery_times[extender] >= cr_utils.RECOVERY_KPI_SECONDS:
                report_logger.print_error(
                    f"{extender}: recovery took {recovery_times[extender]:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )
            report_logger.print_success(
                f"PASS: {extender} recovered in {recovery_times[extender]:.1f}s and is reachable after recovery"
            )

        report_logger.print_step(
            "STEP 8: Stop captures and validate final-cycle topology synchronization"
        )
        packets_by_extender = {}
        for extender in extenders:
            capture_started.remove(extender)
            local_path = device_utils.stop_and_collect_capture(initialize, extender, capture_names[extender])
            packets_by_extender[extender] = local_path

        for extender, local_path in packets_by_extender.items():
            try:
                packets = reassemble_packets(local_path)
                queries = check_message_presence(packets, MSG_TYPE_AP_TOPOLOGY_QUERY) or []
                responses = check_message_presence(
                    packets, MSG_TYPE_AP_TOPOLOGY_RESPONSE
                ) or []
                if not queries or not responses:
                    raise RuntimeError(
                        "expected Topology Query and Response after final reboot"
                    )
                report_logger.print_success(f"PASS: {extender} recovery produced topology traffic")
            except Exception as error:
                capture_validation_errors.append(f"{extender}: {error}")

        for error in capture_validation_errors:
            report_logger.print_error(error)
    finally:
        report_logger.print_test(
            "Exiting test_controller_recovery_consecutive_reboots"
        )
        if capture_started:
            for extender, capture_name in capture_names.items():
                if extender not in capture_started:
                    continue
                try:
                    device_utils.stop_and_collect_capture(initialize, extender, capture_name)
                except Exception as error:
                    report_logger.log(f"Could not stop {extender} capture: {error}")
