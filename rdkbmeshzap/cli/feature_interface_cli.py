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

import re
import shlex
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

    def get_iw_dev_info(self, device: str) -> str:
        """
        Get `iw dev` output for the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = "iw dev"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return str(output).strip()

    def get_iw_dev_interface_info(self, device: str, iface: str) -> str:
        """
        Get `iw dev <interface> info` output for the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"iw dev {shlex.quote(iface)} info"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return str(output).strip()

    def get_iw_dev_sta_dump(self, device: str, iface: str) -> str:
        """
        Get `iw dev <interface> station dump` output for the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"iw dev {iface} station dump"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return str(output).strip()

    def get_iw_dev_link_info(self, device: str, iface: str) -> str:
        """
        Get `iw dev <interface> link` output for the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"iw dev {iface} link"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != '':
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        return str(output).strip()

    def get_cpu_utilization(self, device: str) -> str:
        """
        Get one non-interactive CPU snapshot from the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = "top -b -n 1"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != '':
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        return str(output).strip()

    def get_memory_utilization(self, device: str) -> str:
        """
        Get one memory snapshot using `free -m`.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = "free -m"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != '':
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
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

    def get_fronthaul_credentials(self, device: str) -> tuple:
        """
        Return the OneWifiMesh fronthaul SSID and passphrase.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        query = (
            "SELECT SSID, PassPhrase FROM NetworkSSIDList "
            "WHERE ID LIKE '%Fronthaul%OneWifiMesh%' LIMIT 1;"
        )
        command = f"mysql -N -B -D OneWifiMesh -e {shlex.quote(query)}"
        output, error = connection_obj.execute_command(
            command, return_stderr=True
        )
        if error:
            raise RuntimeError(f"Command execution failed: {error.strip()}")
        values = str(output).strip().split("\t", 1)
        if len(values) != 2 or not all(values):
            raise RuntimeError(f"Invalid OneWifiMesh credential row: {output}")
        return values[0].strip(), values[1].strip()

    def get_fronthaul_bssids(self, device: str) -> list:
        """
        Return fronthaul BSSIDs from the device MLD interface.
        """
        zi_logger.print_context()
        output = self.get_iw_dev_interface_info(device, "mld0")
        bssids = re.findall(
            r"link\s+ID\s+\d+\s+link\s+addr\s+([0-9a-fA-F:]{17})",
            str(output),
        )
        if not bssids:
            raise RuntimeError(f"No fronthaul BSSIDs found on {device}")
        return [bssid.lower() for bssid in bssids]

    def verify_service_status(self, device: str, service_name: str):
        """
        Verify that a systemd service is active on a device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"systemctl is-active {service_name}"
        output, error = connection_obj.execute_command(
            command, return_stderr=True
        )
        if error:
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        status = str(output).strip()
        if status != "active":
            raise RuntimeError(
                f"Service {service_name} on {device} is not active: {status}"
            )

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
        command = f"python3 -c \"import os, sys; print(os.path.exists(sys.argv[1]))\" {shlex.quote(file_path)}"
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return output.strip() == 'True'

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
        command = f"ls {shlex.quote(directory_path)}"
        output, error = connection_obj.execute_command(command,
                                                   return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        entries = [entry for entry in (output or "").splitlines() if entry]
        return entries

    def get_wireless_backhaul_connection_status(self, iw_dev_link_info) -> bool:
        """
        To check the backhaul connection status of the device.
        """
        zi_logger.print_context()
        return 'Connected to' in iw_dev_link_info

    def get_mld_status(self, iw_dev_interfce_info) -> bool:
        """
        To check the MLD status of the device.
        """
        zi_logger.print_context()
        return 'MLD with links:' in iw_dev_interfce_info

    def get_operating_channel(self,
                            device: str,
                            band: str) -> int:
        """
        Get the operating channel for the specified band.

        Args:
            device: Device name.
            band: '2.4', '5', or '6'
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        band_filters = {
            "2.4": "$4 >= 2400 && $4 <= 2483.5",
            "5": "$4 >= 5000 && $4 <= 5900",
            "6": "$4 >= 5925 && $4 <= 7125"
        }
        if band not in band_filters:
            raise ValueError(f"Unsupported band: {band}")
        command = (
            f"iw dev mld0 info | "
            f"awk -F'[ ()]+' '/channel/ && {band_filters[band]} {{print $3}}'"
        )
        output, error = connection_obj.execute_command(
            command,
            return_stderr=True
        )
        if error:
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        return int(output.strip())

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
        command = f"scp {shlex.quote(local_file_path)} {shlex.quote('{}@{}:{}'.format(user, remote_device_ip, remote_file_path))}"
        _, error = connection_obj.execute_command(command,
                                              return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")

    def start_service(self,
                    device: str,
                    service_name: str) -> bool:
        """
        Start and enable the specified service on the device.
        """
        zi_logger.print_context()

        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)

        commands = [
            "systemctl daemon-reload",
            f"systemctl enable {shlex.quote(service_name)}",
            f"systemctl start {shlex.quote(service_name)}",
        ]

        for command in commands:
            _, error = connection_obj.execute_command(
                command,
                return_stderr=True
            )
            if error:
                raise RuntimeError(
                    f"Command execution failed: {command}. stderr: {error.strip()}"
                )

        command = f"systemctl status {service_name}"
        _, error = connection_obj.execute_command(
            command,
            return_stderr=True
        )
        if error:
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )

        return True


    def stop_service(self,
                    device: str,
                    service_name: str) -> bool:
        """
        Stop the specified service on the device.
        """
        zi_logger.print_context()

        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)

        command = f"systemctl stop {service_name}"

        _, error = connection_obj.execute_command(
            command,
            return_stderr=True
        )
        if error:
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        command = f"systemctl status {service_name}"
        _, error = connection_obj.execute_command(
            command,
            return_stderr=True
        )
        if error:
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        return True