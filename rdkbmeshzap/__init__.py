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

from rdkbmeshzap.feature_interface import FeatureInterface
from rdkbmeshzap.feature_onboarding_de import FeatureOnboarding
from rdkbmeshzap.feature_client_association_de import FeatureClientAssociation
from rdkbmeshzap.feature_radio_de import FeatureRadio
from  rdkbmeshzap.feature_backhaul_de import FeatureBackhaul

import zaero.utils.zi_logger as zi_logger

class rdkbmeshzap(FeatureInterface,FeatureOnboarding,FeatureClientAssociation,FeatureBackhaul,FeatureRadio):
    
    def __init__(self):
        zi_logger.print_context()
        FeatureInterface.__init__(self)
        FeatureOnboarding.__init__(self)
        FeatureClientAssociation.__init__(self)
        FeatureBackhaul.__init__(self)
        FeatureRadio.__init__(self)
        zi_logger.log("Rdkb __init__ : END")
