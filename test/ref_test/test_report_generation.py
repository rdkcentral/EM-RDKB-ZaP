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
import pytest
from rdkbmeshzap.common_utils import report_logger

def test_report_generation(initialize):
    report_logger.print_test("Entering test_report_generation")
    report_logger.print_step("STEP 1: Generate the expected SSID value")
    expected_value = initialize.get_random_ssid()
    report_logger.print_info("INFO: Generated the expected SSID value")
    report_logger.print_step("STEP 2: Configure the SSID through the GUI")
    initialize.set_ssid("controller", "mld_iface_index", expected_value, "gui")
    report_logger.print_success("PASS: SSID configuration request completed")
    for attempt in range(1, 31):
        try:
            report_logger.print_step(
                f"STEP 3.{attempt}: Verify the configured SSID"
            )
            current_value = initialize.get_ssid(
                "controller", "2g_ssid_index", "de"
            )
            if current_value != expected_value:
                raise RuntimeError(
                    f"Expected SSID {expected_value!r}; found {current_value!r}"
                )
            initialize.check_ssid(
                "controller", "mld_iface_index", expected_value, "cli"
            )
        except Exception as error:
            report_logger.print_info(
                f"INFO: SSID validation attempt {attempt} did not match yet: {error}"
            )
        else:
            report_logger.print_success(
                f"PASS: SSID matched successfully on attempt {attempt}"
            )
            break
        time.sleep(5)
    else:
        report_logger.print_error(
            "ERROR: SSID was not updated on the device after 30 attempts"
        )
        pytest.fail("SSID was not updated on the device")

    report_logger.print_test("Exiting test_report_generation")
