import time
import threading

import pytest
from packet_analyzer.ieee1905_utils import *  # noqa: F401,F403
from packet_analyzer.packet_dissector import *  # noqa: F401,F403
from zaero.utils import zi_logger

import controller_recovery_utils as cr_utils
import device_utils


def test_controller_recovery_star_extender_reconnection(initialize):
    zi_logger.print_test("Entering test_controller_recovery_star_extender_reconnection")
    zi_logger.print_step("STEP 1: Discover enabled star extenders")
    extenders = cr_utils.get_extenders_by_topology_role(initialize, "star")
    if not extenders:
        pytest.fail("No star extenders found in infra.yaml")

    capture_names = {}
    capture_started = set()
    recovery_times = {}
    recovery_started = {}
    controller_recovery = {}
    validation_errors = []

    try:
        # Collect captures before the controller reboot so recovery traffic is retained.
        zi_logger.print_step("STEP 2: Start IEEE 1905 packet capture on star extenders")
        for extender in extenders:
            capture_names[extender] = cr_utils.start_extender_capture(
                initialize, extender, "controller_recovery_star", step=2
            )
            capture_started.add(extender)

        zi_logger.print_step("STEP 3: Reboot the controller")
        initialize.reboot_device("controller", method="cli")
        controller_started_at = time.monotonic()
        # Measure recovery from the moment the reboot command is issued.
        recovery_started = {extender: time.monotonic() for extender in extenders}
        time.sleep(10)
        zi_logger.print_step("STEP 4: Reconnect to the controller after reboot")
        cr_utils.recover_device(
            initialize,
            "controller",
            controller_started_at,
            controller_recovery,
            4,
            zi_logger,
        )

        zi_logger.print_step("STEP 5: Reconnect all extenders in parallel")
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
                    "logger": zi_logger,
                },
                name=f"recover-{extender}",
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        zi_logger.print_step(
            "STEP 6: Wait for topology packets to propagate before stopping captures"
        )
        time.sleep(60)

        zi_logger.print_step("STEP 7: Validate recovery KPI for each extender")
        for extender in extenders:
            # Check the KPI before stopping the capture for this extender.
            result = recovery_times.get(extender)
            if isinstance(result, Exception):
                pytest.fail(f"{extender}: recovery failed: {result}")
            if result is None:
                pytest.fail(f"{extender}: recovery did not produce a result")

            if result >= cr_utils.RECOVERY_KPI_SECONDS:
                pytest.fail(
                    f"{extender}: recovery took {result:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )
            zi_logger.print_success(f"PASS: {extender} recovered in {result:.1f}s")

        zi_logger.print_step("STEP 8: Stop captures and validate topology messages")
        for extender in extenders:
            # Validate each extender immediately after its capture is stopped.
            capture_started.remove(extender)
            try:
                cr_utils.stop_collect_reassemble_and_validate_topology_capture(
                    initialize, extender, capture_names[extender], 8
                )
            except Exception as error:
                validation_errors.append(f"{extender}: {error}")

        if validation_errors:
            pytest.fail("; ".join(validation_errors))

        zi_logger.print_success("PASS: All extenders recovered and topology messages were validated")
    finally:
        if capture_started:
            for extender, capture_name in capture_names.items():
                if extender not in capture_started:
                    continue
                try:
                    cr_utils.stop_and_collect_capture(initialize, extender, capture_name)
                except Exception as error:
                    zi_logger.log(f"Could not stop {extender} capture: {error}")
