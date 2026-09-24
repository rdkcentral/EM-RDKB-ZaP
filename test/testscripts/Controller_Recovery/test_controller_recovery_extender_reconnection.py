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
from rdkbmeshzap.common_utils import device_utils

def test_controller_recovery_extender_reconnection(initialize):
    report_logger.print_test("Entering test_controller_recovery_extender_reconnection")
    CONTROLLER_RECOVERY_KPI_SECONDS = cr_utils.get_controller_recovery_kpi(initialize)
    report_logger.print_step("STEP 1: Discover all enabled extenders")
    extenders = device_utils.get_enabled_extenders(initialize)
    if not extenders:
        pytest.fail("No enabled extenders found in infra.yaml")
    report_logger.print_info(
        f"INFO: Enabled extenders for this recovery test: {extenders}"
    )

    capture_names = {}
    capture_started = set()
    recovery_times = {}
    recovery_started = {}
    controller_recovery = {}
    extender_al_macs = {}
    capture_paths = {}
    validation_errors = []
    recovered_extenders = []

    try:
        # Collect captures before the controller reboot so recovery traffic is retained.
        report_logger.print_step("STEP 2: Start IEEE 1905 packet capture on enabled extenders")
        for index, extender in enumerate(extenders, start=1):
            capture_names[extender] = device_utils.start_capture(
                initialize,
                extender,
                "test_controller_recovery_extender_reconnection",
                step=f"2.{index}",
                include_device=True,
            )
            extender_al_macs[extender] = initialize.get_al_mac_address(
                extender, "cli"
            )
            capture_started.add(extender)
        report_logger.print_info(
            "INFO: Packet captures have been started successfully on all extender devices"
        )

        report_logger.print_step("STEP 3: Reboot the controller and start recovery timer")
        controller_started_at = time.monotonic()
        # Use one reboot timestamp so controller and extender recovery share the same KPI window.
        recovery_started = {extender: controller_started_at for extender in extenders}
        initialize.reboot_device("controller", method="cli")
        report_logger.print_info("INFO: Controller reboot command executed")
        # Allow some time for the controller to reboot before attempting reconnection.
        time.sleep(30)
        report_logger.print_step("STEP 4: Reconnect to the controller after reboot")
        controller_result = cr_utils.recover_device(
            initialize,
            "controller",
            controller_started_at,
            controller_recovery,
            "4.1",
        )
        if isinstance(controller_result, Exception):
            raise controller_result

        report_logger.print_step(
            "STEP 5: Verify all extenders in parallel for recovery and record recovery times"
        )
        threads = []
        for index, extender in enumerate(extenders, start=1):
            # Recover each extender concurrently to keep the timing comparable.
            thread = threading.Thread(
                target=cr_utils.recover_device,
                kwargs={
                    "initialize": initialize,
                    "device": extender,
                    "started_at": recovery_started[extender],
                    "results": recovery_times,
                    "step": f"5.{index}",
                },
                name=f"recover-{extender}",
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        # Each worker records its recovery duration.
        report_logger.print_info(
            "INFO: All extender recovery threads have completed"
        )

        report_logger.print_step(
            "STEP 6: Identify recovered extenders and validate their recovery KPI"
        )
        for index, extender in enumerate(extenders, start=1):
            report_logger.print_step(
                f"STEP 6.{index}: Validate {extender} recovery and reachability"
            )
            result = recovery_times.get(extender)
            if isinstance(result, BaseException):
                validation_errors.append(f"{extender}: recovery failed: {result}")
                report_logger.print_error(f"{extender}: recovery failed: {result}")
                continue
            if result is None:
                validation_errors.append(f"{extender}: recovery result is unavailable")
                report_logger.print_error(
                    f"{extender}: recovery result is unavailable; the recovery "
                    "process may have failed or did not complete"
                )
                continue

            if not initialize.is_device_alive(extender):
                validation_errors.append(f"{extender}: extender is not reachable after recovery")
                report_logger.print_error(validation_errors[-1])
                continue
            if result >= CONTROLLER_RECOVERY_KPI_SECONDS:
                validation_errors.append(
                    f"{extender}: recovery took {result:.1f}s; KPI is < "
                    f"{CONTROLLER_RECOVERY_KPI_SECONDS}s"
                )
                report_logger.print_error(validation_errors[-1])
                continue
            report_logger.print_success(
                f"PASS: {extender} is reachable and recovered within the KPI threshold "
                f"in {result:.1f}s"
            )
            recovered_extenders.append(extender)

        if not recovered_extenders:
            pytest.fail(
                "No extender recovered within the recovery KPI: "
                + "; ".join(validation_errors)
            )

        report_logger.print_step(
            "STEP 7: Wait for topology packets to propagate before stopping captures"
        )
        time.sleep(60)
        report_logger.print_info(
            "INFO: Topology propagation wait completed before capture validation"
        )

        report_logger.print_step(
            "STEP 8: Stop and collect packet captures from recovered extenders"
        )
        for extender in recovered_extenders:
            try:
                capture_paths[extender] = device_utils.stop_and_collect_capture(
                    initialize, extender, capture_names[extender]
                )
                capture_started.remove(extender)
            except Exception as error:
                validation_errors.append(f"{extender}: capture collection failed: {error}")

        report_logger.print_step(
            "STEP 9: Validate topology exchange packets for recovered extenders"
        )
        for index, extender in enumerate(recovered_extenders, start=1):
            report_logger.print_step(
                    f"STEP 9.{index}: Validate topology traffic for {extender}"
            )
            try:
                packets = reassemble_packets(capture_paths[extender])
                cr_utils.validate_topology_capture(
                    packets, extender, extender_al_macs[extender]
                )
            except Exception as error:
                validation_errors.append(f"{extender}: {error}")

        for error in validation_errors:
            report_logger.print_error(error)

        report_logger.print_step(
            "STEP 10: Verify each parent device of recovered extenders after Controller reboot"
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
                    f"{extender}: parent device lookup failed: {error}"
                )
                report_logger.print_error(validation_errors[-1])

        if validation_errors:
            pytest.fail("Recovery validation failed: " + "; ".join(validation_errors))

        report_logger.print_success("PASS: All extenders recovered and topology messages were validated")
    finally:
        report_logger.print_test(
            "Exiting test_controller_recovery_extender_reconnection"
        )
        if capture_started:
            for extender in recovered_extenders:
                capture_name = capture_names.get(extender)
                if extender not in capture_started:
                    continue
                if not capture_name:
                    continue
                try:
                    # Always clean up captures that were started but not validated successfully.
                    device_utils.stop_and_collect_capture(initialize, extender, capture_name)
                except Exception as error:
                    report_logger.print_error(
                        f"Could not stop {extender} capture: {error}"
                    )
