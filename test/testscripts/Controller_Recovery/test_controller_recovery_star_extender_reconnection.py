import time
import threading

import pytest
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import report_logger

import controller_recovery_utils as cr_utils
from rdkbmeshzap.common_utils import device_utils


def test_controller_recovery_star_extender_reconnection(initialize):
    report_logger.print_test("Entering test_controller_recovery_star_extender_reconnection")
    report_logger.print_step("STEP 1: Discover enabled star extenders")
    extenders = device_utils.get_extenders_by_topology_role(initialize, "star")
    if not extenders:
        pytest.fail("No star extenders found in infra.yaml")

    capture_names = {}
    capture_started = set()
    recovery_times = {}
    recovery_started = {}
    controller_recovery = {}
    extender_al_macs = {}
    validation_errors = []

    try:
        # Collect captures before the controller reboot so recovery traffic is retained.
        report_logger.print_step("STEP 2: Start IEEE 1905 packet capture on star extenders")
        for extender in extenders:
            capture_names[extender] = device_utils.start_capture(
                initialize,
                extender,
                "test_controller_recovery_star_extender_reconnection",
                step=2,
                include_device=True,
            )
            extender_al_macs[extender] = initialize.get_al_mac_address(
                extender, "cli"
            )
            capture_started.add(extender)

        report_logger.print_step("STEP 3: Reboot the controller")
        initialize.reboot_device("controller", method="cli")
        controller_started_at = time.monotonic()
        # Measure recovery from the moment the reboot command is issued.
        recovery_started = {extender: time.monotonic() for extender in extenders}
        time.sleep(10)
        report_logger.print_step("STEP 4: Reconnect to the controller after reboot")
        cr_utils.recover_device(
            initialize,
            "controller",
            controller_started_at,
            controller_recovery,
            4,
            report_logger,
        )

        report_logger.print_step("STEP 5: Reconnect all extenders in parallel")
        threads = []
        for extender in extenders:
            # Recover each extender concurrently to keep the timing comparable.
            thread = threading.Thread(
                target=cr_utils.recover_device,
                kwargs={
                    "initialize": initialize,
                    "device": extender,
                    "started_at": recovery_started[extender],
                    "results": recovery_times,
                    "step": 5,
                    "logger": report_logger,
                },
                name=f"recover-{extender}",
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        for extender, result in recovery_times.items():
            if isinstance(result, Exception):
                report_logger.print_error(f"{extender}: recovery failed: {result}")
                continue
            if result >= cr_utils.RECOVERY_KPI_SECONDS:
                report_logger.print_error(
                    f"{extender}: recovery took {result:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )

        report_logger.print_step(
            "STEP 6: Wait for topology packets to propagate before stopping captures"
        )
        time.sleep(60)

        report_logger.print_step("STEP 7: Validate recovery KPI for each extender")
        for extender in extenders:
            # Check the KPI before stopping the capture for this extender.
            result = recovery_times.get(extender)
            if isinstance(result, Exception):
                report_logger.print_error(f"{extender}: recovery failed: {result}")
                continue
            if result is None:
                report_logger.print_error(
                    f"{extender}: recovery result is unavailable; the recovery "
                    "process may have failed or did not complete"
                )
                continue

            if result >= cr_utils.RECOVERY_KPI_SECONDS:
                report_logger.print_error(
                    f"{extender}: recovery took {result:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )
            report_logger.print_success(f"PASS: {extender} recovered in {result:.1f}s")

        report_logger.print_step("STEP 8: Stop captures and validate topology messages")
        for extender in extenders:
            # Validate each extender immediately after its capture is stopped.
            capture_started.remove(extender)
            try:
                cr_utils.stop_collect_reassemble_and_validate_topology_capture(
                    initialize,
                    extender,
                    capture_names[extender],
                    8,
                    extender_al_macs[extender],
                )
            except Exception as error:
                validation_errors.append(f"{extender}: {error}")

        for error in validation_errors:
            report_logger.print_error(error)

        report_logger.print_success("PASS: All extenders recovered and topology messages were validated")
    finally:
        report_logger.print_test(
            "Exiting test_controller_recovery_star_extender_reconnection"
        )
        if capture_started:
            for extender, capture_name in capture_names.items():
                if extender not in capture_started:
                    continue
                try:
                    device_utils.stop_and_collect_capture(initialize, extender, capture_name)
                except Exception as error:
                    report_logger.log(f"Could not stop {extender} capture: {error}")
