"""One-time client-association baseline validation."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import EXPECTED_CLIENT_COUNT, SCALE_AGENTS
from utility import (
    collect_fronthaul_associations,
    device_present,
    print_error,
    print_step,
    print_success,
    total_associations,
)


def test_em_scale_client_association_baseline(initialize):
    """Verify the expected client association count once at test start."""
    print_step("Step 1: Read the configured scale agents and expected client count")
    agents = [
        agent for agent in SCALE_AGENTS
        if device_present(initialize, agent)
    ]
    expected_client_count = EXPECTED_CLIENT_COUNT
    all_devices = ["controller", *agents]

    print_step("Step 2: Capture the initial fronthaul client-association baseline")
    print_step(
        f"Expected Result: At least {expected_client_count} clients should be "
        "associated across the controller and present agents"
    )
    baseline = collect_fronthaul_associations(initialize, all_devices)
    observed_client_count = total_associations(baseline)
    print_step(
        f"Observed Result: {observed_client_count} associated clients across "
        f"{len(all_devices)} devices: {baseline}"
    )

    if observed_client_count < expected_client_count:
        message = (
            f"Initial client-association baseline is below expected scale. "
            f"Expected at least {expected_client_count} clients, observed "
            f"{observed_client_count}: {baseline}"
        )
        print_error(message)
        pytest.fail(message)

    print_success(
        f"Initial client-association baseline meets expectation: "
        f"{observed_client_count} observed clients, "
        f"{expected_client_count} expected"
    )