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
        """
        Initialize database, connection, and UI module dependencies.
        """
        zi_logger.print_context()
        ConnectionModules.__init__(self)
        DatabaseModule.__init__(self)
        UiModules.__init__(self)
        self.db_obj = self.get_database_module_object()
        zi_logger.log(f"==== db_obj : {self.db_obj}")

    def get_al_mac_address(
        self,
        device: str,
    ) -> str:
        """
        Return the device AL MAC address.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, "connection")
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        interface = "eth0_virt_peer" if device == "controller" else "eth1_virt_peer"
        command = f"cat /sys/class/net/{interface}/address"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != "":
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

    def get_fronthaul_credentials(
        self,
        device: str,
    ) -> tuple:
        """
        Return the OneWifiMesh fronthaul SSID and passphrase.
        """
        connection = self.db_obj.read_from_database(device, "connection")
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        query = (
            "SELECT SSID, PassPhrase FROM NetworkSSIDList "
            "WHERE ID LIKE '%Fronthaul%OneWifiMesh%' LIMIT 1;"
        )
        command = f"mysql -N -B -D OneWifiMesh -e {shlex.quote(query)}"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error:
            raise RuntimeError(f"Command execution failed: {error.strip()}")
        values = str(output).strip().split("\t", 1)
        if len(values) != 2 or not all(values):
            raise RuntimeError(f"Invalid OneWifiMesh credential row: {output}")
        return values[0].strip(), values[1].strip()

    def get_fronthaul_bssids(
        self,
        device: str,
    ) -> list:
        """
        Return fronthaul BSSIDs from the device MLD interface.
        """
        connection = self.db_obj.read_from_database(device, "connection")
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        output, error = connection_obj.execute_command(
            "iw dev mld0 info", return_stderr=True
        )
        if error:
            raise RuntimeError(f"Command execution failed: {error.strip()}")
        bssids = re.findall(r"link addr ([0-9a-fA-F:]{17})", str(output))
        if not bssids:
            raise RuntimeError(f"No fronthaul BSSIDs found on {device}")
        return [bssid.lower() for bssid in bssids]

    def check_ssid(
        self,
        device: str,
        index: str,
        ssid: str,
    ):
        """
        Verify the SSID assigned to a device Wi-Fi interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, "connection")
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        try:
            index_value = self.db_obj.read_from_database(device, index)
            if "mld" in index:
                interface = self.db_obj.read_from_database(device, "mld_ifname") + str(index_value)
            else:
                interface = self.db_obj.read_from_database(device, "wifi_ifname") + str(index_value)
        except Exception as error:
            zi_logger.log(f"ERROR: {error}")
            raise RuntimeError(
                f"Could not find out the Radio of the device: {device}"
            )
        command = f"iw dev {interface} info | grep ssid | awk '{{print $2}}'"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != "":
            raise RuntimeError(f"Command execution failed: {command}")
        output = str(output).strip()
        if output != ssid:
            raise RuntimeError(f"Expected ssid {ssid} is not matched with {output}")

    def reboot_device(
        self,
        device: str,
    ):
        """
        Reboot a device through its configured connection.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, "connection")
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        connection_obj.execute_command(
            "reboot >/dev/null 2>&1 &", blocking_call=False
        )

    def verify_service_status(
        self,
        device: str,
        service_name: str,
    ):
        """
        Verify that a systemd service is active on a device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, "connection")
        connection_obj = self.get_connection_module_object(connection)
        connection_obj.switch_connection(device)
        command = f"systemctl is-active {service_name}"
        output, error = connection_obj.execute_command(command, return_stderr=True)
        if error != "":
            raise RuntimeError(f"Command execution failed: {command}")
        status = str(output).strip()
        if status != "active":
            raise RuntimeError(
                f"Service {service_name} on {device} is not active: {status}"
            )

    def get_wifi_interfaces_from_bridge(
        self,
        bridge_output,
    ):
        """
        Return unique Wi-Fi interface names found in bridge output.
        """
        interface_names = []
        for match in re.finditer(r"\b(wifi[^\s]*)\b", str(bridge_output)):
            interface_name = match.group(1)
            if interface_name not in interface_names:
                interface_names.append(interface_name)
        return interface_names

    def get_associated_station_interface(
        self,
        initialize,
        device,
        bridge_iface,
    ):
        """
        Find the Wi-Fi interface with an associated station.
        """
        ssh = initialize.get_connection_module_object("ssh")
        ssh.switch_connection(device)
        bridge_output = ssh.execute_command(f"brctl show {shlex.quote(bridge_iface)}")
        for interface_name in self.get_wifi_interfaces_from_bridge(bridge_output):
            station_output = ssh.execute_command(
                f"iw dev {shlex.quote(interface_name)} station dump"
            )
            if "Station " in str(station_output) and "associated:" in str(station_output):
                return interface_name
        raise RuntimeError(
            f"{device}: could not find an active station interface under {bridge_iface}"
        )

    def get_connected_wifi_interface(
        self,
        initialize,
        device,
        bridge_iface,
    ):
        """
        Find the Wi-Fi interface reporting an active connection.
        """
        ssh = initialize.get_connection_module_object("ssh")
        ssh.switch_connection(device)
        bridge_output = ssh.execute_command(f"brctl show {shlex.quote(bridge_iface)}")
        for interface_name in self.get_wifi_interfaces_from_bridge(bridge_output):
            link_output = ssh.execute_command(
                f"iw dev {shlex.quote(interface_name)} link"
            )
            if "Connected to" in str(link_output):
                return interface_name
        raise RuntimeError(
            f"{device}: could not find a connected Wi-Fi interface under {bridge_iface}"
        )
