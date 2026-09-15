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

    def get_file_presence_status(self,
                          device: str,
                          file_path: str,
                          method = 'cli') -> bool:
        """
        To check if a specific file exists on the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_file_presence_status(device, file_path)

    def get_file_list(self,
                   device: str,
                   directory_path: str,
                   method = 'cli') -> list:
        """
        To list all files in a specific directory on the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_file_list(device, directory_path)

    def get_backhaul_status(self,
                                 device: str,
                                 method = 'cli') -> bool:
        """
        To check the backhaul connection status of the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_backhaul_status(device)

    def copy_file_to_remote(self,
                            device: str,
                            remote_device_ip: str,
                            user: str,
                            local_file_path: str,
                            remote_file_path: str,
                            method = 'cli') -> bool:
        """
        To copy a file from the local system to the remote device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.copy_file_to_remote(device, remote_device_ip, user, local_file_path, remote_file_path)

    def start_monitoring_service(self,
                                 device: str,
                                 method = 'cli') -> bool:
        """
        To start the monitoring service on the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.start_monitoring_service(device)

    def stop_monitoring_service(self,
                                device: str,
                                method = 'cli') -> bool:
        """
        To stop the monitoring service on the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.stop_monitoring_service(device)

    def get_time_stamp(self,
                       device: str,
                       method = 'cli') -> float:
        """
        To get the current timestamp from the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_time_stamp(device)

    def get_file_modified_time(self,
                               device: str,
                               file_path: str,
                               method = 'cli') -> float:
        """
        To get the last modified time of a specific file on the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_file_modified_time(device, file_path)

    def set_channel_preference(self, device: str, uncheck_channel: int, check_channel: int, priority: int):
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object('gui')
        iface_obj.set_channel_preference(device, uncheck_channel, check_channel, priority)

    def get_mld_status(self,
                        device: str,
                        method = 'cli') -> bool:
        """
        To get the current SSID status on the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_mld_status(device)

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

    def get_operating_channel(self,
                              device: str,
                              method = 'cli') -> int:
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_operating_channel(device)

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

    def toggle_network_profile(self,
                               device: str,
                               profile_identifier,
                               enable: bool,
                               method: str = 'gui') -> bool:
        """
        Enable or disable a network profile on the device.

        - `profile_identifier` can be a profile name or index depending on the UI implementation.
        - `enable` True to enable, False to disable.
        Returns boolean success as returned by the underlying interface.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.toggle_network_profile(device, profile_identifier, enable)