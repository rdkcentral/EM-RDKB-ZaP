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
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils import recovery_utils

def test_controller_recovery_consecutive_reboots(initialize):
    """
    Verify the Controller recovers within the configured KPI across five consecutive reboot cycles.
    """
    report_logger.print_test("Entering test_controller_recovery_consecutive_reboots")
    capture_names = {}
    capture_started = set()
    extender_al_macs = {}
    all_extenders = []
    recovered_extenders = []
    try:
        report_logger.print_step("STEP 1: Discover all enabled extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled extenders found in infra.yaml")
            return
        all_extenders = list(extenders)
        report_logger.print_info(f"INFO: Enabled extenders for this recovery test: {extenders}")

        report_logger.print_step("STEP 2: Start IEEE 1905 packet capture on enabled extenders")
        for index, extender in enumerate(extenders, start=1):
            capture_names[extender] = device_utils.start_capture(initialize, extender, "test_controller_recovery_consecutive_reboots", step=f"2.{index}", include_device=True)
            extender_al_macs[extender] = initialize.get_al_mac_address(extender, "cli")
            capture_started.add(extender)
        report_logger.print_info("INFO: Packet captures have been started successfully on all extender devices")

        for cycle in range(1, recovery_utils.REBOOT_CYCLES + 1):
            report_logger.print_step(f"STEP {cycle + 2}: Reboot the controller (cycle {cycle}/{recovery_utils.REBOOT_CYCLES}) and measure its recovery time")
            report_logger.print_info(f"INFO: Starting controller recovery cycle {cycle}/{recovery_utils.REBOOT_CYCLES}")
            cycle_start = time.monotonic()
            initialize.reboot_device("controller", method="cli")
            report_logger.print_info("INFO: Controller reboot command executed")
            time.sleep(30)
            controller_results = {}
            recovery_utils.recover_device(initialize, "controller", cycle_start, controller_results)
            controller_result = controller_results.get("controller")
            if isinstance(controller_result, Exception):
                recovery_utils.print_recovery_summary(all_extenders, recovered_extenders, step=f"STEP {cycle + 3}", scope="after controller recovery")
                return
            if controller_result is False or controller_result is None:
                if controller_result is None:
                    report_logger.print_error("FAIL: Controller recovery result is unavailable")
                recovery_utils.print_recovery_summary(all_extenders, recovered_extenders, step=f"STEP {cycle + 3}", scope="after controller recovery")
                return
            report_logger.print_success(f"PASS: Controller recovered successfully in cycle {cycle}/{recovery_utils.REBOOT_CYCLES}")
        report_logger.print_info(f"INFO: All controller reboot cycles completed; checking extender reachability after cycle {recovery_utils.REBOOT_CYCLES}")
        extender_results = {}
        extender_threads = []
        final_cycle_start = cycle_start

        report_logger.print_step(f"STEP 8: Verify recovery of all extenders in parallel after controller cycle {recovery_utils.REBOOT_CYCLES} and record their recovery times")
        for index, extender in enumerate(extenders, start=1):
            thread = threading.Thread(
                target=recovery_utils.recover_device,
                args=(
                    initialize,
                    extender,
                    final_cycle_start,
                    extender_results,
                ),
                name=f"recover-{extender}-after-cycle-{recovery_utils.REBOOT_CYCLES}",
            )
            extender_threads.append(thread)
            thread.start()
        for thread in extender_threads:
            thread.join()
        report_logger.print_info("INFO: Recovery checks have finished for all extenders")
        recovered_results = {
            extender: result
            for extender, result in extender_results.items()
            if isinstance(result, (int, float)) and not isinstance(result, bool)
        }
        failed_cycles = {}
        if not recovered_results:
            failed_cycles = {extender: recovery_utils.REBOOT_CYCLES for extender in all_extenders}
            recovery_utils.print_recovery_summary(all_extenders, recovered_extenders, step="STEP 9", scope=f"after controller reboot cycle {recovery_utils.REBOOT_CYCLES}", failed_cycles=failed_cycles)
            return

        for extender in extenders:
            recovery_result = extender_results.get(extender)
            if isinstance(recovery_result, BaseException):
                failed_cycles[extender] = recovery_utils.REBOOT_CYCLES
                continue
            if recovery_result is False:
                failed_cycles[extender] = recovery_utils.REBOOT_CYCLES
                continue
            if recovery_result is None:
                failed_cycles[extender] = recovery_utils.REBOOT_CYCLES
                report_logger.print_error(f"FAIL: {extender}: no recovery result was recorded")
                continue
            if not initialize.is_device_alive(extender):
                failed_cycles[extender] = recovery_utils.REBOOT_CYCLES
                report_logger.print_error(f"FAIL: {extender}: extender is not reachable after controller reboot")
                continue
            recovered_extenders.append(extender)
        if recovered_extenders:
            report_logger.print_step(f"STEP 9: Reachable Extenders Report after controller cycle {recovery_utils.REBOOT_CYCLES}")
            for index, extender in enumerate(recovered_extenders, start=1):
                recovery_result = extender_results[extender]
                report_logger.print_step(f"STEP 9.{index}: Report {extender} recovery and reachability")
                report_logger.print_success(f"PASS: {extender} is reachable and recovered within the KPI threshold in {recovery_result:.1f}s")

        if not recovered_extenders:
            recovery_utils.print_recovery_summary(all_extenders, recovered_extenders, step="STEP 9", scope=f"after controller reboot cycle {recovery_utils.REBOOT_CYCLES}", failed_cycles=failed_cycles)
            return

        report_logger.print_step("STEP 10: Wait for topology packets to propagate before the captures are stopped")
        time.sleep(60)
        report_logger.print_info("INFO: Topology propagation wait is over; proceeding to capture validation")

        report_logger.print_step("STEP 11: Stop and collect captures from recovered extenders")
        packets_by_extender = {}
        for index, extender in enumerate(recovered_extenders, start=1):
            report_logger.print_step(f"STEP 11.{index}: Stop and collect capture for {extender}")
            try:
                local_path = device_utils.stop_and_collect_capture(initialize, extender, capture_names[extender])
                capture_started.remove(extender)
                packets_by_extender[extender] = local_path
            except Exception as error:
                error_message = f"FAIL: {extender}: capture collection failed: {error}"
                report_logger.print_error(error_message)

        report_logger.print_step("STEP 12: Validate topology exchange packets for recovered extenders")
        for index, (extender, local_path) in enumerate(
            packets_by_extender.items(), start=1
        ):
            report_logger.print_step(f"STEP 12.{index}: Check the topology traffic captured on {extender}")
            try:
                packets = reassemble_packets(local_path)
                recovery_utils.validate_topology_capture(packets, extender, extender_al_macs[extender])
            except Exception as error:
                error_message = f"FAIL: {extender}: topology traffic check failed: {error}"
                report_logger.print_error(error_message)

        report_logger.print_step("STEP 13: Identify the parent device of each recovered extender after the controller reboot")
        topology_devices = ["controller", *extenders]
        for extender in recovered_extenders:
            try:
                parent, bssid = device_utils.get_extender_parent_device(initialize, extender, topology_devices)
                if parent:
                    report_logger.print_success(f"PASS: {extender} is connected to {parent}")
                else:
                    report_logger.print_error(f"FAIL: {extender}: could not identify its upstream device")
            except Exception as error:
                report_logger.print_error(f"FAIL: {extender}: failed to look up its parent device: {error}")

        recovery_utils.print_recovery_summary(all_extenders, recovered_extenders, step="STEP 14", scope=f"across {recovery_utils.REBOOT_CYCLES} consecutive controller reboot cycles", failed_cycles=failed_cycles)

    finally:
        for extender in capture_started:
            capture_name = capture_names.get(extender)
            if not capture_name:
                continue
            try:
                # Always clean up captures that were started but not collected.
                device_utils.stop_and_collect_capture(initialize, extender, capture_name)
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not stop {extender} capture during cleanup: {error}")
        report_logger.print_test("Exiting test_controller_recovery_consecutive_reboots")
