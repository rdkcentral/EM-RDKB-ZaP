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

from concurrent.futures import ThreadPoolExecutor, as_completed
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils import recovery_utils
import threading
import time

def test_agent_recovery_extender_isolation_resilience(initialize):
    """
    Verify peer extender recovery does not disconnect active extender.
    """
    report_logger.print_test("Entering test_agent_recovery_extender_isolation_resilience")
    all_extenders = []
    survivor_failures = []
    monitor_stop = threading.Event()
    monitor_failure = threading.Event()
    monitor_thread = None

    try:
        report_logger.print_step("STEP 1: Discover all enabled Extenders")
        all_extenders = device_utils.get_enabled_extenders(initialize)
        if len(all_extenders) < 2:
            report_logger.print_error("FAIL: At least two enabled Extenders are required in infra.yaml")
            return
        report_logger.print_info(f"INFO: Enabled extenders for this recovery test: {all_extenders}")

        # A controller-connected survivor remains independent of peer backhaul links.
        report_logger.print_step("STEP 2: Select a controller-connected survivor and reboot targets")
        controller_connected_extenders = []
        for extender in all_extenders:
            try:
                parent, _ = device_utils.get_extender_parent_device(initialize, extender, ["controller", *all_extenders])
            except Exception as error:
                report_logger.print_info(f"INFO: Could not identify the upstream parent for {extender}: {error}")
                continue
            if parent == "controller":
                controller_connected_extenders.append(extender)
        if not controller_connected_extenders:
            report_logger.print_error("FAIL: No controller-connected Extender found for safe isolation testing")
            return
        survivor = controller_connected_extenders[0]
        reboot_extenders = [extender for extender in all_extenders if extender != survivor]
        report_logger.print_success(f"PASS: Selected controller-connected survivor: {survivor}")
        report_logger.print_success(f"PASS: Extenders to reboot: {reboot_extenders}")

        # Ensure the survivor is reachable before disturbing its peers.
        report_logger.print_step("STEP 3: Confirm the survivor extender is reachable before peer reboot")
        try:
            initial_failure = not initialize.is_device_alive(survivor)
        except Exception as error:
            initial_failure = f"reachability check failed: {error}"
        if initial_failure:
            report_logger.print_error(f"FAIL: {survivor}: {initial_failure} before peer reboot")
            return
        report_logger.print_success(f"PASS: {survivor} is reachable before peer reboot")

        # Start the shared recovery KPI window before issuing peer reboot commands.
        cycle_start = time.monotonic()

        # Reboot peers concurrently and check survivor reachability.
        report_logger.print_step("STEP 4: Reboot peer Extenders")
        reboot_errors = {}
        with ThreadPoolExecutor(max_workers=len(reboot_extenders)) as executor:
            reboot_futures = {
                executor.submit(initialize.reboot_device, extender, method="cli"): extender
                for extender in reboot_extenders
            }
            for future in as_completed(reboot_futures):
                extender = reboot_futures[future]
                try:
                    future.result()
                except Exception as error:
                    reboot_errors[extender] = error
                    report_logger.print_error(f"FAIL: {extender}: reboot command failed: {error}")
                else:
                    report_logger.print_info(f"INFO: Reboot command executed for {extender}")
                # Check that rebooting this peer did not disconnect the survivor.
                try:
                    survivor_reachable = initialize.is_device_alive(survivor)
                except Exception as error:
                    survivor_reachability_failure = f"reachability check failed: {error}"
                else:
                    survivor_reachability_failure = None if survivor_reachable else "not reachable"
                if survivor_reachability_failure:
                    survivor_failures.append(f"{survivor_reachability_failure} after rebooting {extender}")
                    report_logger.print_error(f"FAIL: {survivor} {survivor_reachability_failure} after issuing the reboot command for {extender}")
                else:
                    report_logger.print_success(f"PASS: {survivor} is reachable after the reboot command was issued for {extender}")

        report_logger.print_step("STEP 5: Start survivor reachability polling")
        # Monitor the survivor until all peer recovery workers finish.
        monitor_thread = threading.Thread(
            target=recovery_utils.monitor_device_reachability,
            kwargs={
                "initialize": initialize,
                "device": survivor,
                "stop_event": monitor_stop,
                "status_context": f"while peer reboot/recovery is in progress ({', '.join(reboot_extenders)})",
                "poll_failure_event": monitor_failure,
            },
            name=f"monitor-{survivor}",
            daemon=True,
        )
        monitor_thread.start()
        report_logger.print_info(f"INFO: Survivor reachability polling started for {survivor}")

        # Allow time for peer boot-up before starting their recovery checks.
        report_logger.print_step("STEP 6: Wait 30 seconds after rebooting peer Extenders")
        time.sleep(30)
        report_logger.print_info("INFO: 30-second wait after peer reboot completed")

        # Recover each rebooted peer concurrently within the shared KPI window.
        report_logger.print_step("STEP 7: Recover peer Extenders concurrently")
        recovery_times = {}
        recovery_threads = []
        for extender in reboot_extenders:
            thread = threading.Thread(
                target=recovery_utils.recover_device,
                kwargs={
                    "initialize": initialize,
                    "device": extender,
                    "started_at": cycle_start,
                    "results": recovery_times,
                    "recovery_type": "agent",
                },
                name=f"recover-{extender}",
            )
            recovery_threads.append(thread)
            thread.start()
        # Wait until every peer recovery check has finished before stopping the monitor.
        for thread in recovery_threads:
            thread.join()

        # Stop polling after every peer's recovery check has completed.
        monitor_stop.set()
        monitor_thread.join()
        monitor_thread = None

        # Confirm peer recovery, reachability, and an identifiable upstream parent.
        report_logger.print_step("STEP 8: Validate rebooted Extender reachability and reconnection")
        for extender in reboot_extenders:
            result = recovery_times.get(extender)
            if extender in reboot_errors:
                report_logger.print_error(f"FAIL: {extender} did not recover after reboot: reboot command failed")
                continue
            if isinstance(result, BaseException) or result is False:
                report_logger.print_error(f"FAIL: {extender} did not recover after reboot")
                continue
            if result is None:
                report_logger.print_error(f"FAIL: {extender} did not recover after reboot: recovery result is unavailable")
                continue
            try:
                extender_reachable = initialize.is_device_alive(extender)
            except Exception as error:
                report_logger.print_error(f"FAIL: {extender} did not recover after reboot: reachability check failed: {error}")
                continue
            if not extender_reachable:
                report_logger.print_error(f"FAIL: {extender} did not recover after reboot: not reachable")
                continue
            # Verify that the recovered peer has an active upstream connection.
            try:
                parent, _ = device_utils.get_extender_parent_device(initialize, extender, ["controller", *all_extenders])
            except Exception as error:
                parent = None
                report_logger.print_error(f"FAIL: {extender}: parent lookup failed: {error}")
            if not parent:
                report_logger.print_error(f"FAIL: {extender}: active upstream parent was not identified")
                continue
            report_logger.print_success(f"PASS: {extender} is reachable after recovery and connected to {parent}")

        # Perform a final survivor check and summarize any observed outages.
        report_logger.print_step("STEP 9: Confirm the surviving Extender remained reachable")
        if survivor_failures or monitor_failure.is_set():
            report_logger.print_error(f"FAIL: {survivor}: reachability was affected during peer reboot and recovery")
        else:
            report_logger.print_success(f"PASS: {survivor} remained reachable during peer reboot and recovery")
    finally:
        # Ensure the monitor thread is stopped even when the test exits early.
        monitor_stop.set()
        if monitor_thread is not None:
            monitor_thread.join()
        report_logger.print_test("Exiting test_agent_recovery_extender_isolation_resilience")