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

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from packet_analyzer.packet_dissector import reassemble_packets
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils import recovery_utils as cr_utils

def test_agent_recovery_controller_rediscovery(initialize):
    report_logger.print_test("Entering test_agent_recovery_controller_rediscovery")
    AGENT_RECOVERY_KPI_SECONDS = cr_utils.get_recovery_kpi(initialize, "agent")
    capture_names = {}
    capture_started = set()
    capture_paths = {}
    recovery_times = {}
    recovery_started = {}
    extender_al_macs = {}
    validation_errors = []

    try:
        report_logger.print_step("STEP 1: Discover enabled Extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in infra.yaml")
            return
        report_logger.print_info(f"INFO: Enabled extenders for this recovery test: {extenders}")

        for extender in extenders:
            extender_al_macs[extender] = initialize.get_al_mac_address(extender, "cli")

        report_logger.print_step("STEP 2: Extender recovery")
        report_logger.print_step("STEP 2.1: Reboot all Extenders")
        extenders_started_at = time.monotonic()
        recovery_started = {extender: extenders_started_at for extender in extenders}
        reboot_errors = {}
        with ThreadPoolExecutor(max_workers=len(extenders)) as executor:
            reboot_futures = {
                executor.submit(initialize.reboot_device, extender, method="cli"): extender
                for extender in extenders
            }
            for future in as_completed(reboot_futures):
                extender = reboot_futures[future]
                try:
                    future.result()
                except Exception as error:
                    reboot_errors[extender] = error
        for extender in extenders:
            if extender in reboot_errors:
                validation_errors.append(f"{extender}: reboot command failed: {reboot_errors[extender]}")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")
            else:
                report_logger.print_info(f"INFO: Reboot command executed for {extender}")

        capture_names["controller"] = device_utils.start_capture(
            initialize,
            "controller",
            "test_agent_recovery_controller_rediscovery",
            step="2.2",
            include_device=True,
        )
        capture_started.add("controller")
        report_logger.print_success("PASS: IEEE 1905 capture started on the controller")

        report_logger.print_step("STEP 2.3: Recover all Extenders concurrently")
        report_logger.print_info(f"INFO: Recovering {len(extenders)} Extenders in parallel")
        threads = []
        for extender in extenders:
            thread = threading.Thread(
                target=cr_utils.recover_device,
                kwargs={
                    "initialize": initialize,
                    "device": extender,
                    "started_at": recovery_started[extender],
                    "results": recovery_times,
                    "step": "2.3",
                    "recovery_type": "agent",
                },
                name=f"recover-{extender}",
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        report_logger.print_info("INFO: Recovery checks have finished for all Extenders")

        report_logger.print_step("STEP 2.4: Validate Extender reachability")
        reachable_extenders = []
        for extender in extenders:
            result = recovery_times.get(extender)
            if isinstance(result, BaseException):
                validation_errors.append(f"{extender}: recovery failed: {result}")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                continue
            if result is None or result is False:
                validation_errors.append(f"{extender}: recovery did not complete within {AGENT_RECOVERY_KPI_SECONDS}s")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                continue
            if not initialize.is_device_alive(extender):
                validation_errors.append(f"{extender}: Extender is not reachable after reboot")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")
            else:
                report_logger.print_success(f"PASS: {extender} is reachable after reboot")
                reachable_extenders.append(extender)

        report_logger.print_step("STEP 2.5: Validate recovery KPI for reachable Extenders")
        for extender in reachable_extenders:
            result = recovery_times[extender]
            if result >= AGENT_RECOVERY_KPI_SECONDS:
                validation_errors.append(f"{extender}: recovery did not complete within {AGENT_RECOVERY_KPI_SECONDS}s")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")
            else:
                report_logger.print_success(f"PASS: {extender} recovered in {result:.1f}s")

        report_logger.print_step("STEP 2.6: Validate Extender parent links")
        for extender in reachable_extenders:
            try:
                parent, _ = device_utils.get_extender_parent_device(
                    initialize, extender, ["controller", *extenders]
                )
                if not parent:
                    validation_errors.append(f"{extender}: upstream parent was not identified")
                    report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                else:
                    report_logger.print_success(f"PASS: {extender} is connected to {parent}")
            except Exception as error:
                validation_errors.append(f"{extender}: parent lookup failed: {error}")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")

        report_logger.print_step("STEP 2.7: Wait for topology packets to propagate")
        time.sleep(60)
        report_logger.print_info("INFO: Topology propagation wait is over; proceeding to capture validation")
        report_logger.print_step("STEP 2.8: Stop and collect the Controller packet capture")
        capture_paths["controller"] = device_utils.stop_and_collect_capture(
            initialize, "controller", capture_names["controller"]
        )
        capture_started.remove("controller")
        report_logger.print_success(f"PASS: Controller capture collected at {capture_paths['controller']}")

        report_logger.print_step("STEP 2.9: Validate topology messages in the Controller capture")
        packets = reassemble_packets(capture_paths["controller"])
        for index, extender in enumerate(reachable_extenders, start=1):
            report_logger.print_step(f"STEP 2.9.{index}: Validate topology traffic for {extender}")
            try:
                cr_utils.validate_topology_capture(packets, extender, extender_al_macs[extender])
            except Exception as error:
                validation_errors.append(f"{extender}: capture validation failed: {error}")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")

        if validation_errors:
            report_logger.print_error("Extender recovery validation failed: " + "; ".join(validation_errors))
            return
        report_logger.print_success("PASS: All Extenders recovered, reconnected, and exchanged topology messages")
    finally:
        for extender in capture_started:
            capture_name = capture_names.get(extender)
            if not capture_name:
                continue
            try:
                device_utils.stop_and_collect_capture(initialize, extender, capture_name)
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not stop {extender} capture during cleanup: {error}")
        report_logger.print_test("Exiting test_agent_recovery_controller_rediscovery")
