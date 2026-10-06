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

# CPU usage baseline values for stability analysis.
AVG_CPU_BASELINE = 5
# Maximum CPU usage baseline for stability analysis.
MAX_CPU_BASELINE = 20
# Time to wait after SSID update, in seconds.
SSID_UPDATE_WAITING_TIME = 100
# Time to wait after channel update, in seconds.
CHANNEL_UPDATE_WAITING_TIME = 100  
# Time to wait after fronthaul toggle, in seconds.
FRONTHAUL_TOGGLE_WAITING_TIME = 100
# Maximum number of attempts to enable fronthaul.
MAX_FRONTHAUL_ENABLE_RETRIES = 10
LOG_PATHS = ["/tmp/onewifi_em_ctrl_monitor.csv", "/tmp/onewifi_em_agent_monitor.csv", "/tmp/OneWifi_monitor.csv"]