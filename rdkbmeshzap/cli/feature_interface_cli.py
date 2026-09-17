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


class FeatureInterfaceCLI(DatabaseModule,
                          ConnectionModules,
                          UiModules):
    
    def __init__(self):
        zi_logger.print_context()
        ConnectionModules.__init__(self)
        DatabaseModule.__init__(self)
        UiModules.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")

    def get_al_mac_address(self, device: str) -> str:
        """
        To get AL MAC address of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        if device == 'controller':
            interface = "eth0_virt_peer"
        else:
            interface = "eth1_virt_peer"
        command = f"cat /sys/class/net/{interface}/address"
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return str(output).strip()

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

        command = f"dmcli eRT setv Device.WiFi.SSID.{index}.SSID string {ssid}"
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
        command = f"dmcli eRT getv Device.WiFi.SSID.{index}.SSID | grep 'value:' | awk -F': ' '{cutVal}'"
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
        output = str(output).strip()
        zi_logger.log(f"output : {output}, ssid : {ssid}")
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}")
        if output != ssid:
            raise RuntimeError(f"Expected ssid {ssid} is not matched with {output}")

    def reboot_device(self,
                      device : str):
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = "reboot >/dev/null 2>&1 &"
        zi_logger.log(f"COMMAND : {command}")
        connection_obj.execute_command(command,
                                       blocking_call = False)

    def get_ap_ssid_visibility(self, device:str, ssid:str) -> str:
        """
        To get the SSID visibility of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        wlan_iface = self.db_obj.read_from_database(device, 'data_iface')
        cmd = f"iw dev {wlan_iface} scan  | grep -B100 {ssid} | grep -E [[:space:]]*freq:"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'freq:' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return [line.split(':')[1].strip() for line in output.splitlines()]

    def get_association_status(self, device:str) -> str:
        """
        To get the association status of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        wlan_iface = self.db_obj.read_from_database(device, 'data_iface')
        cmd = f"iw dev {wlan_iface} link | grep 'Connected to' | awk '{{print $3}}'"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        output = output.strip()

        if not output:
            raise RuntimeError(f"Command execution failed : client not associated")

        return output

    def verify_dhcp_process(self, device: str) -> str:
        """
        To verify the DHCP process of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        wlan_iface = self.db_obj.read_from_database(device, 'data_iface')
        cmd = f"dhclient -v {wlan_iface}"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        # dhclient -v writes its verbose transaction log to stderr, not stdout
        combined_output = f"{output}\n{error}"

        full_dora = ['DHCPDISCOVER', 'DHCPOFFER', 'DHCPREQUEST', 'DHCPACK']
        renewal = ['DHCPREQUEST', 'DHCPACK']

        got_full_dora = all(msg in combined_output for msg in full_dora)
        got_renewal = all(msg in combined_output for msg in renewal)
        got_lease = 'bound to' in combined_output

        if (got_full_dora or got_renewal) and got_lease:
            return combined_output

        raise RuntimeError(f"DHCP process verification failed : {combined_output}")

    def get_default_route(self, device: str) -> str:
        """
        To get the default route of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        cmd = "ip route show | grep -m 1 default"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'default via' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return output.split()[2]

