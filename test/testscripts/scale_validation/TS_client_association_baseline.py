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

from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.client_utils import connect_wlan_clients

from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_client_association_baseline(initialize):
    """
    Verify the present client associations once at test start.
    """
    report_logger.print_test("Entering test_em_scale_client_association_baseline")
    report_logger.print_step(
        "Step 1: Discover the configured scale agents and WLAN clients"
    )
    agents = device_utils.get_enabled_extenders(initialize)
    clients = device_utils.get_enabled_clients(initialize)
    if not clients:
        pytest.skip("No WLAN clients are marked present in the database")
    report_logger.print_step(
        f"Step 2: Connect configured WLAN clients and verify all are available: "
        f"{clients}"
    )
    clients = connect_wlan_clients(initialize, clients)
    report_logger.print_success(
        f"PASS: Connected clients before baseline validation: {', '.join(clients)}"
    )
    expected_client_count = get_scale_setup(initialize)["expected_client_count"]
    all_devices = ["controller", *agents]

    report_logger.print_step(
        "Step 3: Capture client MAC associations from each controller and "
        "agent fronthaul interface"
    )
    baseline = collect_fronthaul_associations(initialize, all_devices)
    observed_client_count = total_associations(baseline)
    report_logger.print_step(
        f"Step 4: Compare the {observed_client_count} observed associations with "
        f"the expected client count across "
        f"{len(all_devices)} devices: {baseline}"
    )
    if observed_client_count != expected_client_count:
        message = (
            f"Observed {observed_client_count} clients, expected "
            f"{expected_client_count}: {baseline}"
        )
        report_logger.print_error(message)
        pytest.fail(message)

    report_logger.print_success(
        f"PASS: Initial client-association baseline captured: "
        f"{observed_client_count} present clients observed"
    )
    report_logger.print_test("Exiting test_em_scale_client_association_baseline")