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

from rdkbmeshzap.cli.feature_recovery_cli import FeatureRecoveryCLI
from rdkbmeshzap.gui.feature_recovery_gui import FeatureRecoveryGUI
from rdkbmeshzap.de.feature_recovery_de import FeatureRecoveryDE
import zaero.utils.zi_logger as zi_logger


class FeatureRecoveryModules:

    __instance = None
    __modules = {'gui': FeatureRecoveryGUI,
                 'cli': FeatureRecoveryCLI,
                 'de': FeatureRecoveryDE}
    __module_objects = {}

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            zi_logger.log("FeatureRecoveryModules Instance created")
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        zi_logger.print_context()

    def get_feature_recovery_module_object(self, module):
        zi_logger.print_context()
        if module not in FeatureRecoveryModules.__module_objects:
            zi_logger.log(f"FeatureRecoveryModules.modules : {FeatureRecoveryModules.__modules}")
            FeatureRecoveryModules.__module_objects[module] = FeatureRecoveryModules.__modules[module]()
        return FeatureRecoveryModules.__module_objects[module]
