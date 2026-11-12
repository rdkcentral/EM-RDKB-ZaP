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

from rdkbmeshzap.common_utils import report_logger, traffic_utils

def test_client_association_traffic_flow_TCP_downstream(initialize):
    """
    Verify that Wi-Fi client devices can successfully associate with the
    EasyMesh SSID and establish downstream TCP traffic flow from the Controller.
    """
    report_logger.print_test("Entering test_client_association_traffic_flow_TCP_downstream")
    try:
        report_logger.print_step("STEP 1: Get enabled clients and randomly select one controller client and one extender client")
        selected_clients = traffic_utils.select_wifi_clients(initialize)
        if not selected_clients:
            report_logger.print_error("FAIL: No WLAN clients available for testing")
            return
        report_logger.print_step("STEP 2: Connect selected clients to EasyMesh SSID and verify association")
        connected_clients, association_passed = (traffic_utils.connect_and_verify_clients(initialize, selected_clients))
        if not connected_clients:
            report_logger.print_error("FAIL: Failed to connect selected clients")
            return
        report_logger.print_info(f"INFO: Successfully connected clients: {connected_clients}")
        report_logger.print_step("STEP 3: Start TCP downstream traffic flow from selected Wi-Fi clients to Controller")
        for client in connected_clients:
            report_logger.print_info(f"INFO: Starting TCP downstream traffic flow from Controller to {client}.")
            traffic_passed = traffic_utils.run_tcp_traffic(
                initialize,
                client,
                direction = "downstream",
                mode = "reverse")
            if association_passed and traffic_passed:
                report_logger.print_success(f"PASS: TCP downstream traffic flow verified successfully for all selected clients")
            else:
                report_logger.print_error(f"FAIL: TCP downstream traffic test failed")
        report_logger.print_step("STEP 4: Validate TCP traffic flow.")
        traffic_step_passed = True
        for client in connected_clients:
            report_logger.print_info(f"INFO: Reading TCP downstream iperf log for {client}.")
            log_output = initialize.execute_command(client,"cat controller_downstream_tcp_iperf_client.log")
            if not traffic_utils.validate_tcp_iperf_output(log_output, client):
                traffic_step_passed = False
            else:
                report_logger.print_success(f"PASS: TCP downstream traffic validation successful for {client}")
        if traffic_step_passed:
            report_logger.print_success("PASS: All TCP downstream traffic validations successful.")
        else:
            report_logger.print_error("FAIL: TCP downstream traffic validation failed for one or more clients.")
    finally:
        report_logger.print_test("Exiting test_client_association_traffic_flow_TCP_downstream")