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
from zaero.bridge.ui_modules import UiModules
import zaero.utils.zi_logger as zi_logger
import time

class FeatureInterfaceGUI(DatabaseModule,
                          ConnectionModules,
                          UiModules):
    
    def __init__(self):
        zi_logger.print_context()
        ConnectionModules.__init__(self)
        DatabaseModule.__init__(self)
        UiModules.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")

    def _create_ui_obj(self, device):
        zi_logger.print_context()
        platform = self.db_obj.read_from_database(device, 'platform')
        self.ui_obj = self.get_ui_module_object(platform)

    def set_ssid(self,
                device: str,
                index: str,
                ssid: str):
        """
        To set SSID in the GUI Application
        """
        zi_logger.print_context()
        self._create_ui_obj(device)
        self.ui_obj.ui_navigate_to_home_page(device)
        time.sleep(3)
        self.ui_obj.ui_navigate_to_required_page( "Wireless Settings")
        time.sleep(3)
        self.ui_obj.ui_update_input_and_save("Fronthaul", "#profile-ssid", ssid)        
        time.sleep(3)

    def get_ssid(self,
                 device: str,
                 index: str) -> str:
        """
        To get SSID in the GUI Application
        """
        zi_logger.print_context()
        raise NotImplementedError("FeatureInterfaceGUI.get_ssid() is not implemented")

    def check_ssid(self,
                   device: str,
                   index: str,
                   ssid: str) -> None:        
        """
        To read ssid from mariadb in controller
        """
        zi_logger.print_context()
        raise NotImplementedError("FeatureInterfaceGUI.check_ssid() is not implemented")

    def wifi_reset(self,
                 device: str):
        """
        To reset WiFi in the GUI Application
        """
        zi_logger.print_context()
        self._create_ui_obj(device)
        self.ui_obj.ui_navigate_to_home_page(device)
        time.sleep(3)
        self.ui_obj.ui_navigate_to_required_page( "System Settings")
        time.sleep(3)
        self.ui_obj.ui_set_dialog_handler()
        time.sleep(3)
        self.ui_obj.ui_click_button("#reset-btn")        
        time.sleep(3)
