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


from operator import index

from zaero.bridge.database_module import DatabaseModule
from zaero.bridge.connection_modules import ConnectionModules

import zaero.utils.zi_logger as zi_logger


class FeatureOnboarding(DatabaseModule, ConnectionModules):
    
    def __init__(self):
        DatabaseModule.__init__(self)
        ConnectionModules.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")

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
        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_device_id(self, 
                           device: str, index: str) -> str:
        """
        Get the device ID for a given device index.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.ID"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_onboarding_protocol(self , device: str, index: str) -> str:
        """
        Get the onboarding protocol for a given device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.OnboardingProtocol"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")

        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_last_contact_time(self, device: str, index: str) -> str:
        """
        Get the last contact time for a given device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.LastContactTime"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)

        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output}")
        
        return output.partition('Value')[2].lstrip(' :').split()[0]

    def get_easymesh_operation_mode(self, device: str, index: str) -> str:
        """
        Get the EasyMesh operation mode for a given device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        index = self.db_obj.read_from_database(device, index)
        cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.EasyMeshAgentOperationMode"
        output, error = connection_obj.execute_command(cmd, return_stderr=True)
        if 'Value :' not in output:
            raise RuntimeError(f"Command execution failed : {output.strip()}")

        return output.partition('Value')[2].lstrip(' :').split()[0]
        