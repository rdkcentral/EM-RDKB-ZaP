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

from rdkbmeshzap.feature_interface_gui import FeatureInterfaceGUI
from rdkbmeshzap.feature_interface_cli import FeatureInterfaceCLI
from rdkbmeshzap.feature_interface_de import FeatureInterfaceDE
import zaero.utils.zi_logger as zi_logger

class FeatureInterfaceModules:

    __instance = None
    __modules = {'gui': FeatureInterfaceGUI,
                 'cli': FeatureInterfaceCLI,
                 'de': FeatureInterfaceDE}
    __module_objects = {}

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            zi_logger.log("FeatureInterfaceModules Instance created")
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        zi_logger.print_context()

    def get_feature_interface_module_object(self, module):
        zi_logger.print_context()
        if module not in FeatureInterfaceModules.__module_objects:
            zi_logger.log(f"FeatureInterfaceModules.modules : {FeatureInterfaceModules.__modules}")
            FeatureInterfaceModules.__module_objects[module] = FeatureInterfaceModules.__modules[module]()
        return FeatureInterfaceModules.__module_objects[module]
