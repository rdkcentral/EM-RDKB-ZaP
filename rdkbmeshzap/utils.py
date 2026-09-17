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


from zaero.bridge.database_module import DatabaseModule
from zaero.bridge.connection_modules import ConnectionModules

import zaero.utils.zi_logger as zi_logger

class Utils(DatabaseModule, ConnectionModules):
    
    def __init__(self):
        DatabaseModule.__init__(self)
        ConnectionModules.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")

    def get_enabled_extenders(initialize):
        """Return extender devices enabled in the testbed configuration."""
        return [
            device

          for device in initialize.get_testbed_devices()
            if device.startswith("extender") and "_client_" not in device
        ]

    def get_enabled_clients(initialize):
        """Return client devices enabled in the testbed configuration."""
        return [
            device
            for device in initialize.get_testbed_devices()
            if "_wlan_client_" in device
        ]

    def normalize_security(self, value: str) -> str:
        """
        Maps AKM/key_mgmt values from either DataElements or wpa_cli
        to a common security family for comparison.
        """
        value = value.lower()
        wpa3_values = ["sae", "dpp", "dpp+sae", "eap-sha256", "eap-sha384"]
        wpa2_values = ["psk", "wpa2-psk", "eap", "dot1x", "wpa-eap"]
        transition_values = ["psk+sae"]
        if value in wpa3_values:
            return "WPA3"
        elif value in wpa2_values:
            return "WPA2"
        elif value in transition_values:
            return "WPA2/WPA3-Transition"
        else:
            return f"UNKNOWN({value})"
