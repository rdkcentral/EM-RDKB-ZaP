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

    def get_file_presence_status(self,
                          device: str,
                          file_path: str) -> bool:
        """
        To check if a specific file exists on the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"python3 -c \"import os; print(os.path.exists('{file_path}'))\""
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return output.strip() == 'True'

    def get_file_list(self,
                   device: str,
                   directory_path: str) -> list:
        """
        To list all files in a specific directory on the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"ls {directory_path}"
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        # Normalize output and return a clean list. If the directory is empty,
        # `ls` produces no stdout (empty string) so return an empty list instead
        # of ['']. Use splitlines() to handle different newline styles and
        # filter out any empty strings.
        # If there's no stdout (empty directory), return None as requested.
        if not output:
            return None
        entries = [entry for entry in output.splitlines() if entry]
        return entries if entries else None

    def get_backhaul_status(self,
                                 device: str) -> bool:
        """
        To check the backhaul connection status of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = "iw dev wifi1.3 link"  # Replace with the actual command
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return 'Connected' in output  # Adjust the condition based on the actual command output

    def send_file(self,
                  device: str,
                  file_path: str):
        """
        To send a file to the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"scp {file_path} {device}:/tmp/"
        _, error = connection_obj.execute_command(command,
                                              return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")

    def copy_file_to_remote(self,
                            device: str,
                            remote_device_ip: str,
                            user: str,
                            local_file_path: str,
                            remote_file_path: str):
        """
        To copy a file from the local system to the remote device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"scp {local_file_path} {user}@{remote_device_ip}:{remote_file_path}"
        _, error = connection_obj.execute_command(command,
                                              return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")
    def start_monitoring_service(self,
                                 device: str) -> bool:
        """
        To start the monitoring service on the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        commands = ["systemctl daemon-reload",
        "systemctl enable monitor_service.service",
        "systemctl start monitor_service.service",
        ]

        for command in commands:
            _, error = connection_obj.execute_command(command,
                                                return_stderr=True)
            if error != '':
                raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")

        command  = "systemctl status monitor_service.service"
        _, error = connection_obj.execute_command(command,
                                              return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")
        return True

    def stop_monitoring_service(self,
                                device: str) -> bool:
        """
        To stop the monitoring service on the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = "systemctl stop monitor_service.service"

        _, error = connection_obj.execute_command(command,
                                            return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")

        command  = "systemctl status monitor_service.service"
        _, error = connection_obj.execute_command(command,
                                              return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")
        return True

    def get_time_stamp(self,
                       device: str) -> float:
        """
        To get the current timestamp from the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        # command = "date +%s"
        command = "python3 -c \"from datetime import datetime; print(datetime.now().timestamp())\""
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")
        return float(output.strip())

    def get_file_modified_time(self,
                               device: str,
                               file_path: str) -> float:
        """
        To get the last modified time of a specific file on the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = (
            f"python3 -c \"from pathlib import Path; "
            f"print(Path('{file_path}').stat().st_mtime)\""
        )
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")
        return float(output.strip())

    def get_operating_channel(self,
                            device: str) -> int:
        """
        To get the operating channel of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = r"iw dev mld0 info | awk -F'[ ()]+' '/channel/ && $4 >= 2400 && $4 <= 2483.5 {print $3}'"
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")
        return int(output.strip())

    def get_mld_status(self,
                        device: str) -> bool:
        """
        To get the current SSID status on the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"iw dev mld0 info | grep -q 'MLD with links:' && echo True || echo False"
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")
        return str(output).strip() == 'True'
    
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
