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
from rdkbmeshzap.common_utils import report_logger
from rdkbmeshzap.common_utils.backhaul_utils import (
    get_backhaul_akm,
    verify_backhaul_association,
    verify_controller_connectivity,
    verify_link_metrics,
)

AGENT = "extender1"

# PUBLIC_INTERFACE
def test_em_backhaul_akm_security_configuration(initialize):
    """
    Verify configured backhaul AKM and successful wireless
    backhaul association.
    """
    report_logger.print_test("EM_Backhaul_AKM_Security_Configuration")

    report_logger.print_step("STEP 1: Verify AKM configuration")
    value = get_backhaul_akm(initialize)
    report_logger.print_success(f"PASS: Configured AKM: {value}")

    report_logger.print_step("STEP 2: Verify wireless backhaul association")
    output = verify_backhaul_association(initialize, AGENT)
    report_logger.print_success("PASS: Agent 1 is connected to the backhaul SSID")

    report_logger.print_step("STEP 3: Verify signal strength and link parameters")
    verify_link_metrics(output)
    report_logger.print_success("PASS: Valid link information displayed")

    report_logger.print_step("STEP 4: Verify Controller-Agent connectivity")
    verify_controller_connectivity(initialize, AGENT)
    report_logger.print_success("PASS: Controller-Agent connectivity established")

    report_logger.print_step("STEP 5: Verify Agent remains connected")
    time.sleep(30)
    verify_backhaul_association(initialize, AGENT)
    report_logger.print_success("PASS: Agent remained connected to the backhaul SSID")