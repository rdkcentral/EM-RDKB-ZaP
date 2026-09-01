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
from rdkbmeshzap.feature_interface_modules import FeatureInterfaceModules
import zaero.utils.zi_logger as zi_logger
class FeatureInterface(FeatureInterfaceModules):
    def __init__(self):
        zi_logger.print_context()
        FeatureInterfaceModules.__init__(self)
        zi_logger.log("RDKB.FeatureInterface __init__ : END")
    def _create_ui_obj(self, device):
        zi_logger.print_context()
        platform = self.db_obj.read_from_database(device, 'platform')
        self.ui_obj = self.get_ui_module_object(platform)
    def get_al_mac_address(self, device: str, method: str = 'cli') -> str:
        """
        To get AL MAC address of the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        al_mac = iface_obj.get_al_mac_address(device)
        return al_mac
    def set_ssid(self,
                 device: str,
                 index: str,
                 ssid: str,
                 method = 'gui'):
        """
        To set SSID for the specific interface.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.set_ssid(device, index, ssid)
    def get_ssid(self,
                 device: str,
                 index: str,
                 method = 'gui') -> str:
        """
        To get SSID assigned to a specific interface.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        ssid = iface_obj.get_ssid(device, index)
        return ssid
    def check_ssid(self,
                   device: str,
                   index: str,
                   ssid: str,
                   method = 'gui'):
        """
        To check SSID assigned to a specific interface,
        Which will be derived from the radio index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.check_ssid(device, index, ssid)
    def reboot_device(self,
                      device,
                      method = 'gui'):
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.reboot_device(device)
    def wifi_reset(self,
                   device: str,
                   method = 'gui'):
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.wifi_reset(device)
