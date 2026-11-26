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

from rdkbmeshzap.common_utils import device_utils, report_logger, client_utils, traffic_utils

def test_client_association_association_time_threshold(initialize):
    """
    Verify that a Wi-Fi client device associates to the EasyMesh SSID within an acceptable time threshold after 
    initiating connection request, regardless of whether it associates to the Controller or one of the 3 Agents.
    """
    report_logger.print_test("Entering test_client_association_association_time_threshold")
    ITERATIONS = 10
    THRESHOLD = 20
    results = []
    step_index = 1
    try:
        report_logger.print_step(f"STEP {step_index}: Get enabled clients and randomly select one controller client and one extender client")
        selected_clients = traffic_utils.select_wifi_clients(initialize)
        if not selected_clients:
            report_logger.print_error("FAIL: No WLAN clients available for testing")
            return
        # STEP 2: Retrieve SSID and password
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Retrieve EasyMesh SSID and password")
        ssid = initialize.get_ssid("controller","controller_device_index","de")
        password = initialize.get_fronthaul_password("controller","gui")
        if not ssid or not password:
            raise RuntimeError("Failed to retrieve SSID or password")
        report_logger.print_info(f"INFO: SSID: {ssid}")
        # STEP 3: Retrieve AP radio MACs for identifying selected AP
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Retrieve Controller and Extender radio MACs")
        enabled_extenders = device_utils.get_enabled_extenders(initialize)
        mesh_devices = ["controller"] + enabled_extenders
        ap_radio_macs = {}
        for device in mesh_devices:
            radio_macs = {"2G": initialize.read_from_database(device, "2g_radio_mac"),
                          "5G": initialize.read_from_database(device, "5g_radio_mac"),
                          "6G": initialize.read_from_database(device, "6g_radio_mac")}
            ap_radio_macs[device] = radio_macs
            report_logger.print_info(f"INFO: {device} radio MACs: {radio_macs}")
        # STEP 4: Run 10 connection attempts 
        step_index += 1
        report_logger.print_step(f"STEP {step_index}: Connect client to the AP and verify association/IP within {THRESHOLD} seconds")
        for client in selected_clients:
            report_logger.print_info(f"INFO: Testing client: {client}")
            for iteration in range(1, ITERATIONS + 1):
                report_logger.print_info(f"INFO: Starting iteration {iteration}/{ITERATIONS}")
                result = client_utils.connect_client_without_bssid(initialize,client,ssid,password, threshold=THRESHOLD,timeout=15)
                result["iteration"] = iteration
                # Identify actual connected AP/radio using its BSSID
                associated_bssid = result.get("associated_bssid")
                associated_device = None
                associated_radio = None
                if associated_bssid:
                    for device, radios in ap_radio_macs.items():
                        for radio, radio_mac in radios.items():
                            if (radio_mac and associated_bssid.lower() == radio_mac.lower()):
                                associated_device = device
                                associated_radio = radio
                                break
                        if associated_device:
                            break
                result["associated_device"] = associated_device
                result["associated_radio"] = associated_radio
                results.append(result)
                if result["status"] == "PASS":
                    report_logger.print_info(f"INFO: Iteration {iteration}: Association={result['association_time']}s, Total={result['total_time']}s, BSSID={associated_bssid}, AP={associated_device}, Radio={associated_radio}, IP={result['ip_address']}")
                else:
                    report_logger.print_error(f"FAIL: Iteration {iteration}: Reason={result['reason']}, Association={result['association_time']}, Total={result['total_time']}, BSSID={associated_bssid}")
            # STEP 5: Print summary
            step_index += 1
            report_logger.print_step(f"STEP {step_index}: Association performance summary")
            successful_results = [r for r in results if r["status"] == "PASS" ]
            association_times = [
                r["association_time"]
                for r in results
                if r["association_time"] is not None]
            total_times = [
                r["total_time"]
                for r in results
                if r["total_time"] is not None]
            failed_count = ITERATIONS - len(successful_results)
            report_logger.print_info(
                f"INFO: Total attempts: {ITERATIONS}")
            report_logger.print_info(f"INFO: Successful attempts: {len(successful_results)}")
            report_logger.print_info(f"INFO: Failed attempts: {failed_count}")
            if association_times:
                average_association = round(sum(association_times) / len(association_times), 3)
                maximum_association = max(association_times)
                report_logger.print_info(f"INFO: Average association time: {average_association}s")
                report_logger.print_info(f"INFO: Maximum association time: {maximum_association}s")
            if total_times:
                average_total = round(sum(total_times) / len(total_times), 3)
                maximum_total = max(total_times)
                report_logger.print_info(f"INFO: Average total connection time: {average_total}s")
                report_logger.print_info(f"INFO: Maximum total connection time: {maximum_total}s")
    finally:
        report_logger.print_test("Exiting test_client_association_association_time_threshold")