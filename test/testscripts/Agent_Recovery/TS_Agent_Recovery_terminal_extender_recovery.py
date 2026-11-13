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
from concurrent.futures import ThreadPoolExecutor, as_completed
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils import recovery_utils

def test_agent_recovery_terminal_extender_recovery(initialize):
    """
    Reboot terminal Extenders, recover them, and verify their active parents.
    """
    report_logger.print_test("Entering test_agent_recovery_terminal_extender_recovery")

    try:
        report_logger.print_step("STEP 1: Discover enabled Extenders")
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("FAIL: No enabled Extenders were found")
            return
        report_logger.print_info(f"INFO: Enabled Extenders discovered: {extenders}")

        report_logger.print_step("STEP 2: Identify terminal Extenders with no downstream Extenders")
        extender_parents = {}
        for extender in extenders:
            try:
                parent, _ = device_utils.get_extender_parent_device(initialize, extender, ["controller", *extenders])
            except Exception as error:
                report_logger.print_error(f"FAIL: Upstream parent lookup failed for {extender}: {error}")
                return
            if parent not in ["controller", *extenders]:
                report_logger.print_error(f"FAIL: Active parent was not identified for {extender}")
                return
            extender_parents[extender] = parent
            report_logger.print_info(f"INFO: {extender} active upstream parent: {parent}")

        # Select Extenders with a recognized parent and no downstream Extenders.
        terminal_extenders = [
            extender
            for extender, parent in extender_parents.items()
            if parent in ["controller", *extenders] and extender not in extender_parents.values()
        ]
        if not terminal_extenders:
            report_logger.print_error("FAIL: No Extender without downstream Extenders was found")
            return
        report_logger.print_success(f"PASS: Terminal Extenders planned for reboot: {terminal_extenders}")

        report_logger.print_step("STEP 3: Reboot selected terminal Extenders concurrently")
        # Share one recovery KPI start time across all selected terminal Extenders.
        recovery_started = time.monotonic()
        reboot_errors = {}
        with ThreadPoolExecutor(max_workers=len(terminal_extenders)) as executor:
            reboot_futures = {
                executor.submit(initialize.reboot_device, extender, method="cli"): extender
                for extender in terminal_extenders
            }
            for future in as_completed(reboot_futures):
                extender = reboot_futures[future]
                try:
                    future.result()
                except Exception as error:
                    reboot_errors[extender] = error
                    report_logger.print_error(f"FAIL: Reboot command failed for {extender}: {error}")
                else:
                    report_logger.print_info(f"INFO: Reboot command issued for {extender}")
        
        report_logger.print_step("STEP 4: Wait 30 seconds after rebooting the Extenders")
        time.sleep(30)
        report_logger.print_info("INFO: 30-second wait after reboot completed")
        
        report_logger.print_step("STEP 5: Recover rebooted terminal Extenders concurrently")
        recovery_results = {}
        recovery_threads = []
        # Recover rebooted Extenders concurrently within the shared KPI window.
        for extender in terminal_extenders:
            if extender in reboot_errors:
                report_logger.print_info(f"INFO: Skipping recovery for {extender} because its reboot command failed")
                continue
            thread = threading.Thread(
                target=recovery_utils.recover_device,
                kwargs={
                    "initialize": initialize,
                    "device": extender,
                    "started_at": recovery_started,
                    "results": recovery_results,
                    "recovery_type": "agent",
                },
                name=f"recover-{extender}",
            )
            recovery_threads.append(thread)
            thread.start()
        for thread in recovery_threads:
            thread.join()
        report_logger.print_info("INFO: Recovery checks completed for all rebooted terminal Extenders")

        reachable_extenders = []
        # Only Extenders with successful recovery results and active connections proceed.
        for extender in terminal_extenders:
            if extender in reboot_errors:
                continue
            recovery_result = recovery_results.get(extender)
            if isinstance(recovery_result, BaseException):
                continue
            if recovery_result is False:
                continue
            if recovery_result is None:
                report_logger.print_error(f"FAIL: {extender}: recovery result is unavailable")
                continue
            try:
                extender_reachable = initialize.is_device_alive(extender)
            except Exception as error:
                report_logger.print_error(f"FAIL: Post-recovery reachability check failed for {extender}: {error}")
                continue
            if not extender_reachable:
                report_logger.print_error(f"FAIL: Recovered terminal Extender {extender} is not reachable")
                continue
            reachable_extenders.append(extender)

        report_logger.print_step("STEP 6: Report recovery status for each terminal Extender after reboot")
        for extender in terminal_extenders:
            if extender in reachable_extenders:
                report_logger.print_success(f"PASS: {extender} is reachable and recovered in {recovery_results[extender]:.1f}s")
            else:
                report_logger.print_error(f"FAIL: {extender} did not recover after reboot")
        if not reachable_extenders:
            return

        report_logger.print_step("STEP 7: Report each recovered terminal Extender's parent after reboot")
        for extender in reachable_extenders:
            try:
                recovered_parent, _ = device_utils.get_extender_parent_device(initialize, extender, ["controller", *extenders])
            except Exception as error:
                report_logger.print_error(f"FAIL: Post-recovery parent lookup failed for {extender}: {error}")
                continue
            if not recovered_parent:
                report_logger.print_error(f"FAIL: Active parent was not identified for recovered Extender {extender}")
                continue
            report_logger.print_success(f"PASS: {extender}'s parent after reboot is {recovered_parent}")
    finally:
        report_logger.print_test("Exiting test_agent_recovery_terminal_extender_recovery")