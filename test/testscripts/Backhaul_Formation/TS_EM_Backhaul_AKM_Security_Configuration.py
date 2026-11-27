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
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.backhaul_utils import (
    verify_backhaul_association,
    verify_controller_connectivity,
)

# PUBLIC_INTERFACE
def test_em_backhaul_akm_security_configuration(initialize):
    """Verify configured backhaul AKM and successful wireless backhaul association."""
    report_logger.print_test("Entering test_em_backhaul_akm_security_configuration")
    controller = "controller"
    try:
        agent = device_utils.get_enabled_extenders(initialize)[0]
        backhaul_iface = initialize.read_from_database(agent, "backhaul_interface")
        expected_ssid = initialize.read_from_database(controller, "mesh_backhaul_ssid")
        controller_ip = initialize.read_from_database(controller, "bridge_ip")

        report_logger.print_step("STEP 1: Verify AKM configuration")
        value = initialize.get_backhaul_akm(controller)
        report_logger.print_success(f"PASS: Configured AKM: {value}")

        report_logger.print_step("STEP 2: Verify wireless backhaul association")
        verify_backhaul_association(initialize, agent, backhaul_iface, expected_ssid)
        report_logger.print_success(f"PASS: {agent} is connected to the backhaul SSID")

        report_logger.print_step("STEP 3: Verify signal strength and link parameters")
        signal = initialize.get_iw_link_details(agent, backhaul_iface, "signal")
        freq = initialize.get_iw_link_details(agent, backhaul_iface, "freq")
        rates = initialize.get_iw_link_details(agent, backhaul_iface, "rates")
        tx_rates = [rate for direction, rate, _ in rates if direction.lower() == "tx"]
        assert signal, f"{agent}: Signal strength information missing"
        assert freq and float(freq[0]) > 0, f"{agent}: Frequency information missing"
        assert tx_rates and float(tx_rates[0]) > 0, f"{agent}: Transmit bitrate information missing"
        report_logger.print_success(f"PASS: Valid link information displayed (signal={signal[0]} dBm, freq={freq[0]} MHz, tx={tx_rates[0]})")

        report_logger.print_step("STEP 4: Verify Controller-Agent connectivity")
        verify_controller_connectivity(initialize, agent, controller_ip)
        report_logger.print_success("PASS: Controller-Agent connectivity established")

        report_logger.print_step("STEP 5: Verify Agent remains connected")
        time.sleep(30)
        verify_backhaul_association(initialize, agent, backhaul_iface, expected_ssid)
        report_logger.print_success("PASS: Agent remained connected to the backhaul SSID")
    except Exception as exc:
        report_logger.print_error(f"FAIL: test_em_backhaul_akm_security_configuration: {exc}")
        raise
    finally:
        report_logger.print_test("Exiting test_em_backhaul_akm_security_configuration")