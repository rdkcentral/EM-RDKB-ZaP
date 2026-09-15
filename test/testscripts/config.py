"""Shared configuration for test-script scenarios."""

SCALE_AGENTS = ["extender1", "extender2", "extender3"]
EXPECTED_AGENT_COUNT = 3
EXPECTED_CLIENT_COUNT = 3
POLL_INTERVAL_SEC = 60
TEST_DURATION_SEC = 120
FRONTHAUL_CLIENTS = [
    "controller_wlan_client_1",
    "extender1_wlan_client_1",
    "extender2_wlan_client_1",
]
