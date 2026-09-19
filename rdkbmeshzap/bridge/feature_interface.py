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
        
    def get_al_mac_address(self, device: str, method: str = 'cli') -> str:
        """
        To get AL MAC address of the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        al_mac = iface_obj.get_al_mac_address(device)
        return al_mac

    def verify_service_status(self, device: str, service_name: str,
                              method: str = 'cli'):
        """
        To verify the status of a device service.
        """
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.verify_service_status(device, service_name)

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

    def get_fronthaul_credentials(self, device: str, method: str = 'cli') -> tuple:
        """
        To get the fronthaul SSID and passphrase.
        """
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_fronthaul_credentials(device)

    def get_fronthaul_bssids(self, device: str, method: str = 'cli') -> list:
        """
        To get the fronthaul BSSIDs of a device.
        """
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_fronthaul_bssids(device)

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
        """
        To reboot a device using the selected interface method.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.reboot_device(device)

    def wifi_reset(self,
                   device: str,
                   method = 'gui'):
        """
        To reset Wi-Fi settings on a device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        iface_obj.wifi_reset(device)

    def get_ap_metrics_reporting_interval(self,
                                          device: str,
                                          method: str = 'gui') -> str:
        """
        To get the AP Metrics reporting interval.
        """
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_ap_metrics_reporting_interval(device)

    def set_ap_metrics_reporting_interval(
        self,
        device: str,
        interval: int,
        apply_scope: str = "all",
        method: str = 'gui',
    ):
        """
        To set the AP Metrics reporting interval.
        """
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.set_ap_metrics_reporting_interval(
            device, interval, apply_scope
        )

    def get_wifi_interfaces_from_bridge(self, bridge_output, method: str = 'cli'):
        """
        To get Wi-Fi interfaces from bridge output.
        """
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_wifi_interfaces_from_bridge(bridge_output)

    def get_associated_station_interface(
        self, initialize, device, bridge_iface, method: str = 'cli'
    ):
        """
        To get the Wi-Fi interface with an associated station.
        """
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_associated_station_interface(
            initialize, device, bridge_iface
        )

    def get_connected_wifi_interface(
        self, initialize, device, bridge_iface, method: str = 'cli'
    ):
        """
        To get the Wi-Fi interface with an active connection.
        """
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_connected_wifi_interface(
            initialize, device, bridge_iface
        )

