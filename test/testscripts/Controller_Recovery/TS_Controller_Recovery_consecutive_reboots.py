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
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import report_logger
import controller_recovery_utils as cr_utils
from rdkbmeshzap.common_utils import device_utils

def test_controller_recovery_consecutive_reboots(initialize):
    report_logger.print_test("Entering test_controller_recovery_consecutive_reboots")
    CONTROLLER_RECOVERY_KPI_SECONDS = cr_utils.get_controller_recovery_kpi(initialize)
    extenders = device_utils.get_enabled_extenders(initialize)
    if not extenders:
        pytest.fail("No enabled extenders found in infra.yaml")

    capture_names = {}
    capture_started = set()
    recovery_times = {}
    recovery_errors = {}
    controller_recovery = {}
    capture_validation_errors = []

    try:
        report_logger.print_step(
            f"STEP 1: Start IEEE 1905 capture on enabled extenders: {extenders}"
        )
        for index, extender in enumerate(extenders, start=1):
            capture_names[extender] = device_utils.start_capture(
                initialize,
                extender,
                "test_controller_recovery_consecutive_reboots",
                step=f"1.{index}",
                include_device=True,
            )
            capture_started.add(extender)
        report_logger.print_success("PASS: Packet capture started on all enabled extenders")

        for cycle in range(1, cr_utils.REBOOT_CYCLES + 1):
            report_logger.print_step(
                f"STEP {cycle + 1}: Reboot the controller for recovery cycle "
                f"{cycle}/{cr_utils.REBOOT_CYCLES} and measure recovery time"
            )
            report_logger.print_info(
                f"INFO: Executing controller recovery cycle {cycle}/{cr_utils.REBOOT_CYCLES}"
            )
            cycle_success = True
            cycle_start = time.monotonic()
            initialize.reboot_device("controller", method="cli")
            report_logger.print_info("INFO: Controller reboot initiated")
            time.sleep(10)
            controller_result = cr_utils.recover_device(
                initialize,
                "controller",
                cycle_start,
                controller_recovery,
                f"{cycle + 1}.1",
            )
            if isinstance(controller_result, Exception):
                cycle_success = False
                report_logger.print_error(
                    f"controller: recovery failed: {controller_result}"
                )
                continue
            if controller_result >= CONTROLLER_RECOVERY_KPI_SECONDS:
                cycle_success = False
                report_logger.print_error(
                    f"controller: recovery took {controller_result:.1f}s; "
                    f"KPI is < {CONTROLLER_RECOVERY_KPI_SECONDS}s"
                )

            if cycle_success:
                report_logger.print_success(
                    f"PASS: Controller completed recovery cycle "
                    f"{cycle}/{cr_utils.REBOOT_CYCLES}"
                )
            else:
                report_logger.print_error(
                    f"Recovery cycle {cycle}/{cr_utils.REBOOT_CYCLES} completed with errors"
                )
        report_logger.print_info(
            f"INFO: All controller reboot cycles completed; checking extender reachability after cycle {cr_utils.REBOOT_CYCLES}"
        )
        extender_results = {}
        extender_threads = []
        final_cycle_start = cycle_start

        report_logger.print_step(
            f"STEP 7: Check extender reachability after controller cycle {cr_utils.REBOOT_CYCLES}"
        )
        for index, extender in enumerate(extenders, start=1):
            thread = threading.Thread(
                target=cr_utils.recover_device,
                args=(
                    initialize,
                    extender,
                    final_cycle_start,
                    extender_results,
                    f"7.{index}",
                ),
                name=f"recover-{extender}-after-cycle-{cr_utils.REBOOT_CYCLES}",
            )
            extender_threads.append(thread)
            thread.start()
        for thread in extender_threads:
            thread.join()
        report_logger.print_info(
            "INFO: All extender recovery threads have completed"
        )

        report_logger.print_step(
            "STEP 8: Identify recovered extenders and validate their recovery KPI"
        )
        recovered_extenders = []
        validation_errors = []
        for index, extender in enumerate(extenders, start=1):
            report_logger.print_step(
                f"STEP 8.{index}: Validate {extender} recovery and reachability"
            )
            recovery_result = extender_results.get(extender)
            if isinstance(recovery_result, BaseException):
                recovery_errors[extender] = recovery_result
                validation_errors.append(
                    f"{extender}: recovery failed after controller cycle "
                    f"{cr_utils.REBOOT_CYCLES}: {recovery_result}"
                )
                report_logger.print_error(
                    f"{extender}: recovery failed after controller cycle "
                    f"{cr_utils.REBOOT_CYCLES}: {recovery_result}"
                )
                continue
            if recovery_result is None:
                validation_errors.append(f"{extender}: recovery result is unavailable")
                report_logger.print_error(validation_errors[-1])
                continue
            recovery_times[extender] = recovery_result
            if not initialize.is_device_alive(extender):
                validation_errors.append(
                    f"{extender}: extender is not reachable after recovery"
                )
                report_logger.print_error(validation_errors[-1])
                continue
            if recovery_result >= CONTROLLER_RECOVERY_KPI_SECONDS:
                validation_errors.append(
                    f"{extender}: recovery took {recovery_result:.1f}s; KPI is < "
                    f"{CONTROLLER_RECOVERY_KPI_SECONDS}s"
                )
                report_logger.print_error(validation_errors[-1])
                continue
            recovered_extenders.append(extender)
            report_logger.print_success(
                f"PASS: {extender} is reachable and recovered within the KPI threshold "
                f"in {recovery_result:.1f}s"
            )

        if not recovered_extenders:
            pytest.fail(
                f"No extender recovered within the {CONTROLLER_RECOVERY_KPI_SECONDS}s KPI: "
                + "; ".join(validation_errors)
            )

        report_logger.print_step(
            "STEP 9: Wait for topology packets to propagate before stopping captures"
        )
        time.sleep(60)
        report_logger.print_info(
            "INFO: Topology propagation wait completed before capture validation"
        )

        report_logger.print_step(
            "STEP 10: Stop and collect captures from recovered extenders"
        )
        packets_by_extender = {}
        for index, extender in enumerate(recovered_extenders, start=1):
            report_logger.print_step(
                f"STEP 10.{index}: Stop and collect capture for {extender}"
            )
            try:
                local_path = device_utils.stop_and_collect_capture(
                    initialize, extender, capture_names[extender]
                )
                capture_started.remove(extender)
                packets_by_extender[extender] = local_path
                report_logger.print_success(
                    f"PASS: Capture stopped and collected successfully for {extender}"
                )
            except Exception as error:
                error_message = f"{extender}: capture collection failed: {error}"
                capture_validation_errors.append(error_message)
                report_logger.print_error(error_message)

        for index, (extender, local_path) in enumerate(
            packets_by_extender.items(), start=1
        ):
            report_logger.print_step(
                f"STEP 11.{index}: Validate topology traffic for {extender}"
            )
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
                report_logger.print_success(
                    f"PASS: Topology query and response validated successfully for {extender}"
                )
            except Exception as error:
                error_message = f"{extender}: topology validation failed: {error}"
                capture_validation_errors.append(error_message)
                report_logger.print_error(error_message)

        report_logger.print_step(
            "STEP 12: Verify each recovered extender parent using iw dev wifi1.3 link output"
        )
        topology_devices = ["controller", *extenders]
        for extender in recovered_extenders:
            try:
                parent, bssid = cr_utils.get_extender_parent(
                    initialize, extender, topology_devices
                )
                if parent:
                    report_logger.print_success(
                        f"PASS: {extender} is connected to {parent}"
                    )
                else:
                    validation_errors.append(
                        f"{extender}: could not identify its upstream device"
                    )
                    report_logger.print_error(validation_errors[-1])
            except Exception as error:
                validation_errors.append(
                    f"{extender}: parent lookup failed: {error}"
                )
                report_logger.print_error(validation_errors[-1])

        if validation_errors or capture_validation_errors:
            for error in validation_errors + capture_validation_errors:
                report_logger.print_error(error)
            pytest.fail(
                "Recovery validation failed: "
                + "; ".join(validation_errors + capture_validation_errors)
            )
        report_logger.print_success(
            "PASS: All extenders recovered and topology messages were validated"
        )
    finally:
        report_logger.print_test(
            "Exiting test_controller_recovery_consecutive_reboots"
        )
        if capture_started:
            for extender in recovery_times:
                capture_name = capture_names.get(extender)
                if extender not in capture_started:
                    continue
                if not capture_name:
                    continue
                try:
                    device_utils.stop_and_collect_capture(initialize, extender, capture_name)
                except Exception as error:
                    report_logger.print_error(
                        f"Could not stop {extender} capture: {error}"
                    )
