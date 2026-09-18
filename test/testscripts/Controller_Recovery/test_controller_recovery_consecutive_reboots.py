import time

import pytest
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
import test_report_utils as zi_logger

import controller_recovery_utils as cr_utils
import device_utils
from rdkbmeshzap.cli.feature_interface_cli import FeatureInterfaceCLI


REBOOT_CYCLES = 5


def test_controller_recovery_consecutive_reboots(initialize):
    interface_cli = FeatureInterfaceCLI()
    extenders = device_utils.get_enabled_extenders(initialize)
    if not extenders:
        pytest.fail("No enabled extenders found in infra.yaml")

    capture_names = {}
    capture_started = set()
    recovery_times = {}
    controller_recovery = {}
    capture_validation_errors = []

    try:
        zi_logger.print_step(
            f"STEP 1: Start IEEE 1905 capture on enabled extenders: {extenders}"
        )
        for extender in extenders:
            capture_names[extender] = device_utils.start_capture(
                initialize, extender, "controller_recovery", step=1
            )
            capture_started.add(extender)
        zi_logger.print_success("PASS: Packet capture started on all enabled extenders")

        for cycle in range(1, REBOOT_CYCLES + 1):
            zi_logger.print_step(
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
                zi_logger,
            )
            if isinstance(controller_result, Exception):
                pytest.fail(f"controller: recovery failed: {controller_result}")
            if controller_result >= cr_utils.RECOVERY_KPI_SECONDS:
                pytest.fail(
                    f"controller: recovery took {controller_result:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )

            if cycle == REBOOT_CYCLES:
                for extender in extenders:
                    cr_utils.reconnect_device(
                        initialize,
                        extender,
                        zi_logger,
                        step=2,
                        started_at=cycle_start,
                    )
                    recovery_times[extender] = time.monotonic() - cycle_start
            else:
                zi_logger.print_success(f"PASS: Controller recovered after reboot cycle {cycle}")
        time.sleep(40)
        zi_logger.print_step(
            "STEP 7: Validate recovery KPI and reachability for each extender"
        )
        for extender in extenders:
            if extender not in recovery_times:
                pytest.fail(f"{extender}: recovery did not produce a result")
            if not initialize.is_device_alive(extender):
                pytest.fail(f"{extender}: extender is not reachable after recovery")
            if recovery_times[extender] >= cr_utils.RECOVERY_KPI_SECONDS:
                pytest.fail(
                    f"{extender}: recovery took {recovery_times[extender]:.1f}s; "
                    f"KPI is < {cr_utils.RECOVERY_KPI_SECONDS}s"
                )
            zi_logger.print_success(
                f"PASS: {extender} recovered in {recovery_times[extender]:.1f}s and is reachable after recovery"
            )

        zi_logger.print_step(
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
                zi_logger.print_success(f"PASS: {extender} recovery produced topology traffic")
            except Exception as error:
                capture_validation_errors.append(f"{extender}: {error}")

        if capture_validation_errors:
            pytest.fail("; ".join(capture_validation_errors))
    finally:
        if capture_started:
            for extender, capture_name in capture_names.items():
                if extender not in capture_started:
                    continue
                try:
                    device_utils.stop_and_collect_capture(initialize, extender, capture_name)
                except Exception as error:
                    zi_logger.log(f"Could not stop {extender} capture: {error}")
