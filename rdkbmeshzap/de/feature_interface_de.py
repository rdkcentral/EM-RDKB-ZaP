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

class FeatureInterfaceDE(DatabaseModule,
                         ConnectionModules,
                         UiModules):
    
    def __init__(self):
        zi_logger.print_context()
        ConnectionModules.__init__(self)
        DatabaseModule.__init__(self)
        UiModules.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")

    def set_ssid(self,
                 device: str,
                 index: str,
                 ssid: str):
        """
        To set SSID for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        try:
            index = self.db_obj.read_from_database(device, index)
            #interface = self.db_obj.read_from_database(device, "wifi_iface").format(index)
        except Exception as err: # pylint: disable=broad-except
            zi_logger.log(f"ERROR: {err}")
            raise RuntimeError(f"Could not find out the Radio of the device : {device}")

        command = f"dmcli eRT setv Device.WiFi.DataElements.Network.SSID.{index}.SSID string {ssid}"
        zi_logger.log(f"COMMAND : {command}")
        _, error = connection_obj.execute_command(command,
                                              return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}")

    def get_ssid(self,
                 device: str,
                 index: str) -> str:
        """
        To get SSID assigned to a specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        try:
            index = self.db_obj.read_from_database(device, index)
            #interface = self.db_obj.read_from_database(device, "wifi_iface").format(index)
        except Exception as err: # pylint: disable=broad-except
            zi_logger.log(f"ERROR: {err}")
            raise RuntimeError(f"Could not find out the Radio of the device : {device}")
        cutVal = '{print $3}'
        command = f"dmcli eRT getv Device.WiFi.DataElements.Network.SSID.{index}.SSID | grep 'value:' | awk -F': ' '{cutVal}'"
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}")
        return str(output).strip()

    def check_ssid(self,
                   device: str,
                   index: str,
                   ssid: str):
        """
        To check SSID assigned to a specific interface,
        Which will be derived from the radio index.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        try:
            index_val = self.db_obj.read_from_database(device, index)
            if 'mld' in index:
                ifname = self.db_obj.read_from_database(device, "mld_ifname") + str(index_val)
            else:
                ifname = self.db_obj.read_from_database(device, "wifi_ifname") + str(index_val)
        except Exception as err: # pylint: disable=broad-except
            zi_logger.log(f"ERROR: {err}")
            raise RuntimeError(f"Could not find out the Radio of the device : {device}")
        cutVal = '{print $2}'
        command = f"iw dev {ifname} info | grep ssid | awk '{cutVal}'"
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        zi_logger.log(f"output : {output}, ssid : {ssid}")
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}")
        if output != ssid:
            raise RuntimeError(f"Expected ssid {ssid} is not matched with {output}")

    def get_device_number_of_entries(self, device: str) -> int:
        """
        Get the number of entries for a given device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return int(output.partition('Value')[2].lstrip(' :').split()[0])

    def get_device_id(self, 
                           device: str, index: str) -> str:
        """
        Get the device ID for a given device index.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        # index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.ID"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]


    def get_ssid_AKMAllowed(self, device: str, index: str) -> str:
        """
        Get the SSID AKM Allowed for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.SSID.{index}.AKMsAllowed"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")

        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_ssid_MFPConfig(self, device: str, index: str) -> str:
        """
        Get the SSID MFP Config for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.SSID.{index}.MFPConfig"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_dhcpv4_server_enable(self, device: str) -> str:
        """
        Get the DHCPv4 Server Enable status for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        cmd = f"rbuscli get Device.DHCPv4.Server.Enable"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_dhcpv4_server_pool_Minaddress(self, device: str, index: str) -> str:
        """
        Get the DHCPv4 Server Pool Min Address for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.DHCPv4.Server.Pool.{index}.MinAddress"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_dhcpv4_server_pool_Maxaddress(self, device: str, index: str) -> str:
        """
        Get the DHCPv4 Server Pool Max Address for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.DHCPv4.Server.Pool.{index}.MaxAddress"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_dhcpv4_server_pool_client_Chaddr(self, device: str, index: str, sta_index: str) -> str:
        """
        Get the DHCPv4 Server Pool Client Chaddr for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        sta_index = self.db_obj.read_from_database(device, sta_index)
        cmd = f"rbuscli get Device.DHCPv4.Server.Pool.{index}.Client.{sta_index}.Chaddr"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_dhcpv4_server_pool_clientNumberOfEntries(self, device: str, index: str) -> str:
        """
        Get the DHCPv4 Server Pool Client Number of Entries for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.DHCPv4.Server.Pool.{index}.ClientNumberOfEntries"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]


    def get_IP_Interface_Enable(self, device: str, index: str) -> str:
        """
        Get the IP Interface Enable status for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.IP.Interface.{index}.Enable"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_IP_Interface_IPv4Address_IPAddress(self, device: str, index: str, ip_index: str) -> str:
        """
        Get the IP Interface IPv4 Address for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        ip_index = self.db_obj.read_from_database(device, ip_index)
        cmd = f"rbuscli get Device.IP.Interface.{index}.IPv4Address.{ip_index}.IPAddress"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_DHCPv4_Server_Pool_Client_IPv4Address_IPAddress(self, device: str, index: str, sta_index: str, ip_index: str) -> str:
        """
        Get the DHCPv4 Server Pool Client IPv4 Address for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        sta_index = self.db_obj.read_from_database(device, sta_index)
        ip_index = self.db_obj.read_from_database(device, ip_index)
        cmd = f"rbuscli get Device.DHCPv4.Server.Pool.{index}.Client.{sta_index}.IPv4Address.{ip_index}.IPAddress"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]
