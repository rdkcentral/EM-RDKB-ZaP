# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
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

from rdkbmeshzap.common_utils import report_logger, client_utils, traffic_utils


def test_client_association_success_rate_repeated_cycles(initialize):
    """
    Verify Wi-Fi client association success rate during 100 repeated
    connect/disconnect cycles across an EasyMesh network consisting
    of 1 Controller and 3 Agents.
    """
    report_logger.print_test("Entering test_client_association_success_rate_repeated_cycles")
    try:
        step_index = 1
        report_logger.print_step(f"STEP {step_index}: Select Wi-Fi client for repeated association testing")
        selected_clients = traffic_utils.select_wifi_clients(initialize)
        if not selected_clients:
            report_logger.print_error("FAIL: No WLAN clients available for testing")
            return
        step_index += 1
        report_logger.print_step( f"STEP {step_index}: Verify EasyMesh SSID is enabled on Controller")
        ssid = initialize.get_ssid("controller", "controller_device_index", "de")
        if not ssid:
            report_logger.print_error("FAIL: Unable to retrieve EasyMesh SSID")
            return
        report_logger.print_success(f"PASS: EasyMesh SSID retrieved successfully: {ssid}")
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Retrieve Fronthaul password")
        password = initialize.get_fronthaul_password("controller", "gui")
        if not password:
            report_logger.print_error("FAIL: Unable to retrieve Fronthaul password")
            return
        report_logger.print_success("PASS: Fronthaul password retrieved successfully")
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Execute 100 association/disassociation cycles")
        for client in selected_clients:
            total_cycles = initialize.read_from_database("test_parameters","client_association", "association_cycles")
            cycle_results = client_utils.verify_repeated_association_cycles(
                initialize=initialize,
                client=client,
                ssid=ssid,
                password=password,
                total_cycles=total_cycles,
                connection_wait=10,
                disconnection_wait=5)
            total_cycles = cycle_results["total"]
            successful_cycles = cycle_results["success"]
            failed_cycles = cycle_results["failures"]
            report_logger.print_info(f"Total cycles: {total_cycles}")
            report_logger.print_info(f"Successful cycles: {successful_cycles}")
            report_logger.print_info(f"Failed cycles: {failed_cycles}")
            step_index += 1
            report_logger.print_step(f"STEP {step_index}: Calculate association success rate")
            success_rate = (successful_cycles / total_cycles) * 100
            report_logger.print_info(f"Association Success Rate for {client}: {success_rate:.2f}%")
            if success_rate >= 99.0:
                report_logger.print_success(f"PASS: Association success rate is within acceptable range for {client}")
            else:
                report_logger.print_error(f"FAIL: Association success rate is {success_rate:.2f}% for {client}. Expected >= 99%")
            step_index += 1
            report_logger.print_step(f"STEP {step_index}: Final test result")
            if success_rate >= 99.0:
                report_logger.print_success(f"PASS: Repeated Wi-Fi association stability verified for {client}")
            else:
                report_logger.print_error(f"FAIL: Repeated Wi-Fi association stability validation failed for {client}")
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Verify kernel logs for any errors")
        kernel_errors = client_utils.verify_kernel_errors(initialize)
        if kernel_errors == True:
            report_logger.print_success("PASS: No kernel errors found during the test")
        else:
            report_logger.print_error("FAIL: Kernel errors found during the test")
    finally:
        report_logger.print_test("Exiting test_client_association_success_rate_repeated_cycles")