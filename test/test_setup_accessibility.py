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

import pytest
from rdkbmeshzap.common_utils import report_logger

@pytest.mark.connectivity_check
def test_setup_accessibility(initialize):
    """
    Validate SSH accessibility for every configured testbed device.
    """
    report_logger.print_test("Entering Setup Accessibility Validation")
    devices = initialize.get_testbed_devices()
    failures = []

    report_logger.print_info(
        f"INFO: Validating accessibility of {len(devices)} configured devices"
    )
    for device in devices:
        report_logger.print_info(f"INFO: Connecting to {device}")
        try:
            connected = initialize.connect_with_device(device)
            if connected is False:
                raise RuntimeError("connection API returned False")
        except Exception as error:
            failures.append(device)
            report_logger.print_error(
                f"ERROR: {device} accessibility validation failed: {error}"
            )
        else:
            report_logger.print_info(
                f"INFO: {device} is accessible over SSH"
            )

    if failures:
        pytest.fail(
            "Accessibility validation failed for: " + ", ".join(failures)
        )

    initialize.accessibility_validated = True
    report_logger.print_success(
        "PASS: All configured devices passed accessibility validation"
    )
    report_logger.print_test("Exiting Setup Accessibility Validation")
