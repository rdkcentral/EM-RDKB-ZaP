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

from rdkbmeshzap.bridge.feature_interface_modules import FeatureInterfaceModules
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

    def get_iw_dev_info(self, device: str, method: str = 'cli') -> str:
        """
        Get `iw dev` output for a device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_iw_dev_info(device)

    def get_iw_dev_interface_info(
        self, device: str, iface: str, method: str = 'cli') -> str:
        """
        Get `iw dev <interface> info` output for a device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_iw_dev_interface_info(device, iface)

    def get_iw_dev_sta_dump(self, device: str, iface: str, method: str = 'cli') -> str:
        """
        Get `iw dev <interface> station dump` output for a device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_iw_dev_sta_dump(device, iface)

    def get_iw_dev_link_info(self, device: str, iface: str, method: str = 'cli') -> str:
        """
        Get `iw dev <interface> link` output for a device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_iw_dev_link_info(device, iface)

    def get_cpu_utilization(self, device: str, method: str = 'cli') -> str:
        """
        Get one non-interactive CPU snapshot from the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_cpu_utilization(device)

    def get_memory_utilization(self, device: str, method: str = 'cli') -> str:
        """
        Get one memory snapshot from the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_memory_utilization(device)

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

    def set_ap_metrics_reporting_interval(self,
                                          device: str,
                                          interval: int,
                                          apply_scope: str = 'all',
                                          method: str = 'gui'):
        """
        Set the AP Metrics reporting interval through the selected interface.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.set_ap_metrics_reporting_interval(
            device, interval, apply_scope
        )

    def get_ap_metrics_reporting_interval(self,
                                          device: str,
                                          method: str = 'gui') -> str:
        """
        Get the AP Metrics reporting interval through the selected interface.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_ap_metrics_reporting_interval(device)

    def verify_service_status(self, device: str, service_name: str,
                              method: str = 'cli'):
        """
        Verify the status of a device service.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.verify_service_status(device, service_name)

    def get_fronthaul_credentials(self, device: str,
                                  method: str = 'cli') -> tuple:
        """
        Return the fronthaul SSID and passphrase.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_fronthaul_credentials(device)

    def get_fronthaul_bssids(self, device: str,
                             method: str = 'cli') -> list:
        """
        Return the fronthaul BSSIDs of a device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_fronthaul_bssids(device)

    def get_file_presence_status(self,device: str,file_path: str,
                        method = 'cli') -> bool:
        """
        To check if a specific file exists on the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_file_presence_status(device, file_path)

    def get_time_stamp(self,device: str,
                    method = 'cli') -> float:
        """
        To get the current timestamp from the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_time_stamp(device)

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