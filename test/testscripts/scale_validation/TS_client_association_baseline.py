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
"""One-time client-association baseline validation."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import EXPECTED_CLIENT_COUNT, SCALE_AGENTS
from rdkbmeshzap.common_utils import report_logger

from utility import (
    collect_fronthaul_associations,
    device_present,
    total_associations,
)


def test_em_scale_client_association_baseline(initialize):
    """Verify the expected client association count once at test start."""
    report_logger.print_test("Entering test_em_scale_client_association_baseline")
    report_logger.print_step("Step 1: Read the configured scale agents and expected client count")
    agents = [
        agent for agent in SCALE_AGENTS
        if device_present(initialize, agent)
    ]
    expected_client_count = EXPECTED_CLIENT_COUNT
    all_devices = ["controller", *agents]

    report_logger.print_step("Step 2: Capture the initial fronthaul client-association baseline")
    report_logger.print_step(
        f"Expected Result: At least {expected_client_count} clients should be "
        "associated across the controller and present agents"
    )
    baseline = collect_fronthaul_associations(initialize, all_devices)
    observed_client_count = total_associations(baseline)
    report_logger.print_step(
        f"Observed Result: {observed_client_count} associated clients across "
        f"{len(all_devices)} devices: {baseline}"
    )

    if observed_client_count < expected_client_count:
        message = (
            f"Initial client-association baseline is below expected scale. "
            f"Expected at least {expected_client_count} clients, observed "
            f"{observed_client_count}: {baseline}"
        )
        report_logger.print_error(message)
        pytest.fail(message)

    report_logger.print_success(
        f"Initial client-association baseline meets expectation: "
        f"{observed_client_count} observed clients, "
        f"{expected_client_count} expected"
    )
    report_logger.print_test("Exiting test_em_scale_client_association_baseline")