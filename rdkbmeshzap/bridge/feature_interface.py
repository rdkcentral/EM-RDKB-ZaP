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

    def get_fronthaul_password(self,
        device: str,
        index: str) -> str:
        """
        Get the fronthaul password for a given device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object('gui')
        return iface_obj.get_fronthaul_password(device, index)

    def get_device_number_of_entries(self, device: str,method='gui') -> int:
        """
        Get the number of entries for a given device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_device_number_of_entries(device)

    def get_device_id(self, 
                           device: str, index: str, method='gui') -> str:
        """
        Get the device ID for a given device and index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_device_id(device, index)

    def get_ap_ssid_visibility(self, device:str, ssid:str, method='gui') -> str:
        """
        Get the visibility of the given SSID for a specific device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_ap_ssid_visibility(device, ssid)

    def get_association_status(self, device:str, method='gui') -> str:
        """
        Get the association status of the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_association_status(device)

    def get_ssid_AKMAllowed(self, device: str, index: str, method='gui') -> str:
        """
        Get the AKM allowed for the given SSID and index of a specific device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_ssid_AKMAllowed(device, index)

    def get_ssid_MFPConfig(self, device: str, index: str, method='gui') -> str:
        """
        Get the MFP config for the given SSID and index of a specific device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_ssid_MFPConfig(device, index)

    def get_ssid_KeyPassphrase(self, device: str, index: str, method='gui') -> str:
        """
        Get the key passphrase for the given SSID and index of a specific device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_ssid_KeyPassphrase(device, index)

    def get_dhcpv4_server_enable(self, device: str, method='gui') -> str:
        """
        Get the DHCPv4 server enable status for a specific device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_dhcpv4_server_enable(device)

    def get_dhcpv4_server_pool_Minaddress(self, device: str, index: str, method='gui') -> str:
        """
        Get the DHCPv4 server pool minimum address for a given device and index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_dhcpv4_server_pool_Minaddress(device, index)

    def get_dhcpv4_server_pool_Maxaddress(self, device: str, index: str, method='gui') -> str:
        """
        Get the DHCPv4 server pool maximum address for a given device and index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_dhcpv4_server_pool_Maxaddress(device, index)

    def get_dhcpv4_server_pool_client_Chaddr(self, device: str, index: str, sta_index: str, method='gui') -> str:
        """
        Get the DHCPv4 server pool client Chaddr for a given device, index, and sta_index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_dhcpv4_server_pool_client_Chaddr(device, index, sta_index)

    def get_dhcpv4_server_pool_clientNumberOfEntries(self, device: str, index: str, method='gui') -> str:
        """
        Get the number of entries in the DHCPv4 server pool for a given device and index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_dhcpv4_server_pool_clientNumberOfEntries(device, index)

    def get_IP_Interface_Enable(self, device: str, index: str, method='gui') -> str:
        """
        Get the enable status of the IP interface for a given device and index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_IP_Interface_Enable(device, index)

    def get_IP_Interface_IPv4Address_IPAddress(self, device: str, index: str, ip_index: str, method='gui') -> str:
        """
        Get the IPv4 address of the IP interface for a given device, index, and ip_index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_IP_Interface_IPv4Address_IPAddress(device, index, ip_index)

    def get_Router_Enable(self, device: str, index: str, method='gui') -> str:
        """
        Get the enable status of the router for a given device and index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_Router_Enable(device, index)

    def get_DHCPv4_Server_Pool_Client_IPv4Address_IPAddress(self, device: str, index: str, sta_index: str, ip_index: str, method='gui') -> str:
        """
        Get the IPv4 address of the DHCPv4 server pool client for a given device, index, sta_index, and ip_index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_DHCPv4_Server_Pool_Client_IPv4Address_IPAddress(device, index, sta_index, ip_index)

    def get_sta_BytesSent(self, device: str, index: str, radio_index: str, bss_index: str, sta_index: str, method='gui') -> str:
        """
        Get the number of bytes sent by a specific station for a given device, index, radio_index, bss_index, and sta_index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_sta_BytesSent(device, index, radio_index, bss_index, sta_index)

    def get_sta_BytesReceived(self, device: str, index: str, radio_index: str, bss_index: str, sta_index: str, method='gui') -> str:
        """
        Get the number of bytes received by a specific station for a given device, index, radio_index, bss_index, and sta_index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_sta_BytesReceived(device, index, radio_index, bss_index, sta_index)
    
    def get_radioNumberofentries(self, device: str, index: str, method='gui') -> str:
        """
        Get the number of radio entries for a given device and index.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_radioNumberofentries(device, index)

    def verify_dhcp_process(self, device: str, method='gui') -> str:
        """
        Verify the DHCP process for a specific device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.verify_dhcp_process(device)

    def get_default_route(self, device: str, method='gui') -> str:
        """
        Get the default route of the device.
        """
        zi_logger.print_context()
        iface_obj = self.get_feature_interface_module_object(method)
        return iface_obj.get_default_route(device)
