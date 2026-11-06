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

def test_agent_recovery_consecutive_reboots(initialize):
    report_logger.print_test("Entering test_agent_recovery_consecutive_reboots")
    # Read the configured recovery KPI before starting the cycles.
    AGENT_RECOVERY_KPI_SECONDS = cr_utils.get_recovery_kpi(initialize, "agent")
    capture_names = {}
    capture_started = set()
    capture_paths = {}
    extender_al_macs = {}
    validation_errors = []

    try:
        report_logger.print_step("STEP 1: Discover all enabled Extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders found in infra.yaml")
            return
        report_logger.print_info(f"INFO: Enabled extenders for this recovery test: {extenders}")
        for extender in extenders:
            # Store each extender AL MAC for topology validation.
            extender_al_macs[extender] = initialize.get_al_mac_address(extender, "cli")

        for cycle in range(1, cr_utils.REBOOT_CYCLES + 1):
            step = cycle + 1
            report_logger.print_step(f"STEP {step}: Extender recovery cycle {cycle}/{cr_utils.REBOOT_CYCLES}")
            step_offset = int(cycle == cr_utils.REBOOT_CYCLES)
            if step_offset:
                report_logger.print_info(f"INFO: Cycle {cycle} is about to start. Controller capture will run during this cycle to validate topology after {cr_utils.REBOOT_CYCLES} consecutive reboots.")
                capture_names["controller"] = device_utils.start_capture(
                    initialize,
                    "controller",
                    "test_agent_recovery_consecutive_reboots",
                    step=f"{step}.1",
                    include_device=True,
                )
                capture_started.add("controller")

            report_logger.print_step(f"STEP {step}.{1 + step_offset}: Reboot all Extenders")
            cycle_start = time.monotonic()
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
                    validation_errors.append(f"{extender}: cycle {cycle} reboot command failed: {reboot_errors[extender]}")
                    report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                else:
                    report_logger.print_info(f"INFO: Reboot command executed for {extender}")

            report_logger.print_step(f"STEP {step}.{2 + step_offset}: Recover Extenders concurrently")
            recovery_times = {}
            threads = []
            for extender in extenders:
                thread = threading.Thread(
                    # Recover each extender within the configured KPI window.
                    target=cr_utils.recover_device,
                    kwargs={
                        "initialize": initialize,
                        "device": extender,
                        "started_at": cycle_start,
                        "results": recovery_times,
                        "step": f"{step}.{2 + step_offset}",
                        "recovery_type": "agent",
                    },
                    name=f"recover-{extender}-cycle-{cycle}",
                )
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

            report_logger.print_step(f"STEP {step}.{3 + step_offset}: Validate Extender reachability after cycle {cycle}")
            cycle_failed = False
            reachable_extenders = []
            for extender in extenders:
                result = recovery_times.get(extender)
                if isinstance(result, BaseException):
                    validation_errors.append(
                        f"{extender}: cycle {cycle} recovery failed: {result}"
                    )
                    report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                    cycle_failed = True
                    continue
                if result is False:
                    validation_errors.append(
                        f"{extender}: cycle {cycle} recovery failed within the KPI"
                    )
                    report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                    cycle_failed = True
                    continue
                if result is None:
                    validation_errors.append(
                        f"{extender}: cycle {cycle} recovery result is unavailable"
                    )
                    report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                    cycle_failed = True
                    continue
                # Confirm the extender is reachable after recovery.
                if not initialize.is_device_alive(extender):
                    validation_errors.append(
                        f"{extender}: not reachable after cycle {cycle}"
                    )
                    report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                    cycle_failed = True
                else:
                    report_logger.print_success(f"PASS: {extender} is reachable after cycle {cycle}")
                    reachable_extenders.append(extender)

            report_logger.print_step(f"STEP {step}.{4 + step_offset}: Validate recovery KPI for reachable Extenders in cycle {cycle}")
            for extender in reachable_extenders:
                result = recovery_times.get(extender)
                if result >= AGENT_RECOVERY_KPI_SECONDS:
                    validation_errors.append(
                        f"{extender}: cycle {cycle} recovery exceeded {AGENT_RECOVERY_KPI_SECONDS}s"
                    )
                    report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                    cycle_failed = True
                    continue
                report_logger.print_success(f"PASS: {extender} recovered in {result:.1f}s during cycle {cycle}")
            if cycle_failed:
                report_logger.print_error(f"FAIL: Extender recovery cycle {cycle}/{cr_utils.REBOOT_CYCLES} failed")
                return

        report_logger.print_info(f"INFO: All Extender reboot cycles completed; checking parent links after cycle {cr_utils.REBOOT_CYCLES}")
        tail_step = cr_utils.REBOOT_CYCLES + 2
        report_logger.print_step(f"STEP {tail_step}: Validate Extender parent links")
        for extender in extenders:
            try:
                # Match the backhaul BSSID to an upstream device.
                parent, _ = device_utils.get_extender_parent_device(
                    initialize, extender, ["controller", *extenders]
                )
                if not parent:
                    validation_errors.append(
                        f"{extender}: upstream parent was not identified"
                    )
                    report_logger.print_error(f"FAIL: {validation_errors[-1]}")
                else:
                    report_logger.print_success(f"PASS: {extender} is connected to {parent}")
            except Exception as error:
                validation_errors.append(f"{extender}: parent lookup failed: {error}")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")

        report_logger.print_step(f"STEP {tail_step + 1}: Wait for topology packets to propagate")
        time.sleep(60)
        report_logger.print_info("INFO: Topology propagation wait is over; proceeding to capture validation")
        report_logger.print_step(f"STEP {tail_step + 2}: Stop and collect the controller packet capture")
        capture_paths["controller"] = device_utils.stop_and_collect_capture(
            initialize, "controller", capture_names["controller"]
        )
        capture_started.remove("controller")
        report_logger.print_success(f"PASS: Controller capture collected at {capture_paths['controller']}")

        report_logger.print_step(f"STEP {tail_step + 3}: Validate topology messages in the controller capture")
        # Reassemble the pcap for IEEE 1905 message validation.
        packets = reassemble_packets(capture_paths["controller"])
        for index, extender in enumerate(extenders, start=1):
            report_logger.print_step(f"STEP {tail_step + 3}.{index}: Validate topology traffic for {extender}")
            try:
                # Check for topology messages associated with this extender AL MAC.
                cr_utils.validate_topology_capture(packets, extender, extender_al_macs[extender])
            except Exception as error:
                validation_errors.append(f"{extender}: capture validation failed: {error}")
                report_logger.print_error(f"FAIL: {validation_errors[-1]}")

        if validation_errors:
            report_logger.print_error("Extender recovery validation failed: " + "; ".join(validation_errors))
            return
        report_logger.print_success("PASS: All consecutive Extender recovery cycles and topology validation passed")
    finally:
        # Collect captures left active after an early exit.
        for extender in capture_started:
            capture_name = capture_names.get(extender)
            if not capture_name:
                continue
            try:
                device_utils.stop_and_collect_capture(initialize, extender, capture_name)
            except Exception as error:
                report_logger.print_error(f"FAIL: Could not stop {extender} capture during cleanup: {error}")
        report_logger.print_test("Exiting test_agent_recovery_consecutive_reboots")
