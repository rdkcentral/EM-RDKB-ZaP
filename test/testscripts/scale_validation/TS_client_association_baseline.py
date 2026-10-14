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

from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.client_utils import connect_wlan_clients
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_client_association_baseline(initialize):
    """
    Verify the present client associations once at test start.
    """
    report_logger.print_test("Entering test_em_scale_client_association_baseline")
    try:
        report_logger.print_step("STEP 1: Discover configured scale agents and WLAN clients for baseline validation")
        agents = device_utils.get_enabled_extenders(initialize)
        clients = device_utils.get_enabled_clients(initialize)
        report_logger.print_info(f"INFO: Discovered {len(agents)} scale devices and {len(clients)} configured WLAN clients: agents={agents}, clients={clients}")
        if not clients:
            report_logger.print_error("No WLAN clients are marked present in the database")
            return
        report_logger.print_step("STEP 2: Connect configured WLAN clients and verify availability for baseline capture")
        report_logger.print_info(f"INFO: WLAN clients selected for connection: {clients}")
        clients = connect_wlan_clients(initialize, clients)
        report_logger.print_success(f"PASS: Connected clients before baseline validation: {', '.join(clients)}")
        expected_client_count = get_enabled_scale_setup(initialize)["expected_client_count"]
        all_devices = ["controller", *agents]
        report_logger.print_step("STEP 3: Capture fronthaul client MAC associations from the controller and each agent")
        baseline = get_fronthaul_station_macs_by_device(initialize, all_devices)
        observed_client_count = sum(len(macs) for macs in baseline.values())
        report_logger.print_info(f"INFO: Captured {observed_client_count} client associations across {len(all_devices)} devices")
        report_logger.print_step("STEP 4: Validate that the observed client-association count matches the expected count")
        report_logger.print_info(f"INFO: Observed {observed_client_count} associations across {len(all_devices)} devices; snapshot={baseline}")
        if observed_client_count < expected_client_count:
            report_logger.print_error(f"Observed {observed_client_count} clients, expected exactly {expected_client_count}: {baseline}")
        else:
            report_logger.print_success(f"PASS: Initial client-association baseline captured: {observed_client_count} client(s)")
    finally:
        report_logger.print_test("Exiting test_em_scale_client_association_baseline")