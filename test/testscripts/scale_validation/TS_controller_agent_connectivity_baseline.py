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

# Test Case: EM_Scale_ControllerAgent_Connectivity
# Topology: 1 Controller + N Agents (agent list driven by platform DB scale_agents)
# Validates that the expected EasyMesh agent scale forms using iw station dump
# (no Data Elements / rbuscli involved), with a single check (no repeated
# polling). Client connectivity and stability over time are covered separately;
# see
# test_controller_agent_stability.py.

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import SCALE_AGENTS
from utility import (
    all_stations, device_present,
    print_step, print_success, print_error,
    print_test,
)


def test_em_scale_controller_agent_connectivity(initialize):
    """
    EM_Scale_ControllerAgent_Connectivity — 1 Controller + N Agents.

    Verify that the configured number of Agents is connected to the Controller
    at the time of the check. Client connectivity and connection duration are
    outside this test's scope.
    """
    print_test("Entering test_em_scale_controller_agent_connectivity")
    print_step("Step 1: Read the controller's configured scale agent list from the platform database")
    configured_agents = SCALE_AGENTS

    print_step("Step 2: Keep only the agents that are marked present and available for validation")
    agents = [
        agent for agent in configured_agents
        if device_present(initialize, agent)
    ]

    expected_agent_count = len(agents)
    print_step(
        "Step 3: Validate the controller sees the expected scale of agents"
    )
    print_step(
        f"Expected Result: Controller should report {expected_agent_count} "
        "connected scale agents"
    )

    connected_agent_macs = all_stations(initialize, "controller")
    actual_agent_count = len(connected_agent_macs)

    print_step(
        f"Observed Result: Controller station dump reported {actual_agent_count} "
        f"connected agent MACs: {sorted(connected_agent_macs)}"
    )

    if actual_agent_count < expected_agent_count:
        msg = (
            f"Expected scale agents are not present. Expected {expected_agent_count} "
            f"agents, but only {actual_agent_count} were connected. "
            f"Found connected MACs: {sorted(connected_agent_macs)}"
        )
        print_error(msg)
        pytest.fail(msg)

    print_success(
        f"Expected scale agents are present. "
        f"Expected {expected_agent_count} agents and controller sees {actual_agent_count} connected agent MACs: "
        f"{sorted(connected_agent_macs)}"
    )
    print_test("Exiting test_em_scale_controller_agent_connectivity")
