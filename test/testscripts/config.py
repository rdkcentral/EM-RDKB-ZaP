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
"""Shared configuration for test-script scenarios."""
"""Shared configuration for test-script scenarios."""

SCALE_AGENTS = ["extender1", "extender2", "extender3"]
EXPECTED_AGENT_COUNT = 2
EXPECTED_CLIENT_COUNT = 1
POLL_INTERVAL_SEC = 60
TEST_DURATION_SEC = 120
FRONTHAUL_CLIENTS = [
    "controller_wlan_client_1",
    "extender1_wlan_client_1",
    "extender2_wlan_client_1",
]
