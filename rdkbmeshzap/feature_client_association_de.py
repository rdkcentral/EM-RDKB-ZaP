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

import zaero.utils.zi_logger as zi_logger


class FeatureClientAssociation(DatabaseModule, ConnectionModules):

    def __init__(self):
        DatabaseModule.__init__(self)
        ConnectionModules.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")

    def get_ssid_AKMAllowed(self, device: str, index: str) -> str:
        """
        Get the SSID AKM Allowed for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.SSID.{index}.AKMAllowed"
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

    def get_ssid_KeyPassphrase(self, device: str, index: str) -> str:
        """
        Get the SSID Key Passphrase for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.SSID.{index}.KeyPassphrase"
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

    def get_dhcpv4_server_pool_Maxaddress(self, device: str,index: str) -> str:
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

    def get_Router_Enable(self, device: str, index: str) -> str:
        """
        Get the Router Enable status for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.Router.{index}.Enable"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_DHCPv4_Server_Pool_Client_IPv4Address_IPAddress(self, device: str,index: str,sta_index: str,ip_index: str) -> str:
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
    
    def get_sta_BytesSent(self, device: str, index: str,radio_index: str,bss_index: str,sta_index: str) -> str:
        """
        Get the STA Bytes Sent for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        radio_index = self.db_obj.read_from_database(device, radio_index)
        bss_index = self.db_obj.read_from_database(device, bss_index)
        sta_index = self.db_obj.read_from_database(device, sta_index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.BSS.{bss_index}.STA.{sta_index}.BytesSent"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_sta_BytesReceived(self, device: str, index: str,radio_index: str,bss_index: str,sta_index: str) -> str:
        """
        Get the STA Bytes Received for the specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        radio_index = self.db_obj.read_from_database(device, radio_index)
        bss_index = self.db_obj.read_from_database(device, bss_index)
        sta_index = self.db_obj.read_from_database(device, sta_index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.BSS.{bss_index}.STA.{sta_index}.BytesReceived"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")
        return output.partition('Value')[2].lstrip(' :').split()[0]
    