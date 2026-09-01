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
import cmd
from curses import raw
from operator import index
from zaero.bridge.database_module import DatabaseModule
from zaero.bridge.connection_modules import ConnectionModules
import zaero.utils.zi_logger as zi_logger   
class FeatureBackhaul(DatabaseModule,
                        ConnectionModules):
    def __init__(self):
        zi_logger.print_context()
        ConnectionModules.__init__(self)
        DatabaseModule.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")   
    def get_backhaul_linktype(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.LinkType"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Linktype: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_MACaddress(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.MACAddress "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul MAC Address: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_backhaulMACAddress(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.BackhaulMAC "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul BackhaulMAC: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_backhauluse(self, device: str, index: str,radio_index: str,BSS_index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            radio_index = self.db_obj.read_from_database(device, radio_index)
            BSS_index = self.db_obj.read_from_database(device, BSS_index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.BSS.{BSS_index}.BackhaulUse "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul BackhaulUse: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaulsta_MACaddress(self, device: str, index: str,radio_index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            radio_index = self.db_obj.read_from_database(device, radio_index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.BackhaulSTA.MACAddress"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul MAC Address: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_stats_signalstrength(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.Stats.SignalStrength "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Signal Strength: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_controller_id(self, device: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.ControllerID "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get controller ID: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_stats_bytessent(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.Stats.BytesSent "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Bytes Sent: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_stats_bytesreceived(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.Stats.BytesReceived "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Bytes Received: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_stats_linkutilization  (self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.Stats.LinkUtilization "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Link Utilization: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_stats_lastdatadownlinkrate(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.Stats.LastDataDownlinkRate "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Last Data Downlink Rate: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_stats_lastdatauplinkrate(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.Stats.LastDataUplinkRate "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Last Data Uplink Rate: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_status(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.Status "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Status: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_numberofentries(self, device: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.PreferredBackhaulsNumberOfEntries"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Number of Entries: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_preferredbackhauls_MACaddress(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.PreferredBackhauls.{index}.BackhaulMACAddress"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul MAC Address: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_preferredbackhauls_bstaMACaddress(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.PreferredBackhauls.{index}.bSTAMACAddress"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul bSTA MAC Address: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_downMACaddress(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Backhaul.DownMACAddress "
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Down MAC Address: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_alid(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.BackhaulALID"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul ALID: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_mediatype(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.BackhaulMediaType"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul MediaType: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_akmsallowed(self, device: str, index: str,radio_index: str,BSS_index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            radio_index = self.db_obj.read_from_database(device, radio_index)
            BSS_index = self.db_obj.read_from_database(device, BSS_index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.Radio.{radio_index}.BSS.{BSS_index}.BackhaulAKMSAllowed"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul AKMSAllowed: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_backhaulmediatype(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.BackhaulMediaType"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul MediaType: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_backhaulphyrate(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.BackhaulPHYRate"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul PHY Rate: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_backhauldeviceid(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.BackhaulDeviceID"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul Device ID: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
    def get_backhaul_backhaulALID(self, device: str, index: str) -> str:
            zi_logger.print_context()
            connection = self.db_obj.read_from_database(device, 'connection')
            connection_obj = self.get_connection_module_object(connection)
            connection_obj.switch_connection(device)
            index = self.db_obj.read_from_database(device, index)
            cmd = f"rbuscli get Device.WiFi.DataElements.Network.Device.{index}.MultiAPDevice.Backhaul.BackhaulALID"
            output, error = connection_obj.execute_command(cmd, return_stderr=True)
            # No 'Value' in the output 
            if 'Value :' not in output:
                  raise RuntimeError(f"Failed to get Backhaul ALID: {output.strip()}")      
             # 'Value' found -> extract and return just the value
            return output.partition('Value')[2].lstrip(' :').split()[0]
