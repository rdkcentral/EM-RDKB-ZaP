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

class FeatureRadio(DatabaseModule, ConnectionModules):
    
    def __init__(self):
        DatabaseModule.__init__(self)
        ConnectionModules.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")

    def get_radio_status(self, device: str, index: str, radio_index: str) -> str:
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        radio_index = self.db_obj.read_from_database(device, radio_index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.Status"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_radio_enabled(self, device: str, index: str, radio_index: str) -> str:
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        radio_index = self.db_obj.read_from_database(device, radio_index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.Enabled"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_radioNumberofentries(self, device: str, index: str) -> str:
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.RadioNumberOfEntries"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_radio_bss_ssid(self, device: str, index: str, radio_index: str, bss_index: str) -> str:
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        radio_index = self.db_obj.read_from_database(device, radio_index)
        bss_index = self.db_obj.read_from_database(device, bss_index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.BSS.{bss_index}.SSID"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_currentoperatingprofile_opclass(self, device: str, index: str, radio_index: str, profile1_index: str) -> str:
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        radio_index = self.db_obj.read_from_database(device, radio_index)
        profile1_index = self.db_obj.read_from_database(device, profile1_index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.CurrentOperatingProfile.{profile1_index}.OpClass"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")

        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_currentoperatingprofile_channel(self, device: str, index: str, radio_index: str, profile1_index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            radio_index = self.db_obj.read_from_database(device, radio_index)
            profile1_index = self.db_obj.read_from_database(device, profile1_index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.CurrentOperatingProfile.{profile1_index}.Channel"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            if 'Value :' not in output:
                raise RuntimeError(f"Command execution failed : {output}")
    
            return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_radio_bss_STANumberOFEntries(self, device: str, index: str, radio_index: str, bss_index: str) -> str:
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        radio_index = self.db_obj.read_from_database(device, radio_index)
        bss_index = self.db_obj.read_from_database(device, bss_index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.BSS.{bss_index}.STANumberOfEntries"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_radio_bss_STA_MACAddress(self, device: str, index: str, radio_index: str, bss_index: str, sta_index: str) -> str:
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        radio_index = self.db_obj.read_from_database(device, radio_index)
        bss_index = self.db_obj.read_from_database(device, bss_index)
        sta_index = self.db_obj.read_from_database(device, sta_index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.BSS.{bss_index}.STA.{sta_index}.MACAddress"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]



    