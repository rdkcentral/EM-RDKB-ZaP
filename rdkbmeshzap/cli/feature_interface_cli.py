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

# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 RDK Management
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

from importlib.resources import path
import time
import re
import shlex
from paramiko import file
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
        if device == 'controller':
            interface = "eth0_virt_peer"
        else:
            interface = "eth1_virt_peer"
        command = f"cat /sys/class/net/{interface}/address"
        output, error = connection_obj.execute_command(device, command,
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
        command = "iw dev"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return str(output).strip()

    def get_wireless_interfaces_list(self, device: str) -> list:
        """
        Return wireless interfaces reported by ``iw dev``.
        """
        interfaces = (
            line.split(maxsplit=1)[1]
            for line in self.get_iw_dev_info(device).splitlines()
            if line.strip().startswith("Interface ")
            and len(line.split(maxsplit=1)) == 2
        )
        return list(
            dict.fromkeys(
                interface
                for interface in interfaces
                if not interface.lower().startswith("mld")
            )
        )

    def get_iw_dev_interface_info(self, device: str, iface: str) -> str:
        """
        Get `iw dev <interface> info` output for the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        command = f"iw dev {shlex.quote(iface)} info"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
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
        command = f"iw dev {iface} station dump"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
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
        command = f"iw dev {iface} link"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
        if error != '':
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        return str(output).strip()

    def get_iw_interface_details(self, device: str, interface: str, iw_dev_output: str | None = None) -> dict:
        """
        Return normalized interface, link, MAC, and radio details from ``iw dev`` output.
        """
        output = (
            iw_dev_output
            if iw_dev_output is not None
            else self.get_iw_dev_interface_info(device, interface)
        )
        all_lines = [line.strip() for line in str(output or "").splitlines()]
        if iw_dev_output is not None:
            start = next(
                (index for index, line in enumerate(all_lines) if line == f"Interface {interface}"),
                None,
            )
            if start is None:
                lines = []
            else:
                end = next(
                    (index for index in range(start + 1, len(all_lines)) if all_lines[index].startswith("Interface ")),
                    len(all_lines),
                )
                lines = all_lines[start:end]
        else:
            lines = all_lines
        fields = {
            key: value.strip()
            for line in lines if " " in line
            for key, value in [line.split(" ", 1)]
        }
        link_ids = {
            int(match.group(1))
            for line in lines
            if (match := re.match(r"- link ID\s+(\d+)\s+link addr\s+\S+", line))
        }
        link_macs = {}
        for line in lines:
            match = re.match(r"- link ID\s+(\d+)\s+link addr\s+(\S+)", line)
            if match:
                link_macs[int(match.group(1))] = match.group(2).lower()
        radios = set()
        for line in lines:
            if line.startswith("Radios:"):
                radios = {int(radio) for radio in line.split(":", 1)[1].split()}
                break
        return {
            "device": device, "interface": interface,
            "exists": f"Interface {interface}" in lines,
            "ssid": fields.get("ssid", ""), "addr": fields.get("addr", "").lower(),
            "type": fields.get("type", ""), "four_addr": fields.get("4addr:", ""),
            "lines": lines,
            "link_ids": link_ids, "link_macs": link_macs, "radios": radios,
        }

    def get_iw_link_details(self, device: str, interface: str, value: str) -> list:
        """
        Return normalized details from ``iw dev <interface> link`` output.
        """
        lines = [
            line.strip()
            for line in self.get_iw_dev_link_info(device, interface).splitlines()
        ]
        if value not in {"bssid", "ssid", "signal", "rates"}:
            raise ValueError(f"Unsupported iw link value: {value}")
        patterns = {
            "bssid": (r"Connected\s+to\s+([0-9a-f:]{17})", (1,)),
            "ssid": (r"SSID:\s*(.+?)\s*$", (1,)),
            "signal": (r"signal:\s*(-?\d+)\s*dBm", (1,)),
            "rates": (
                r"(tx|rx) bitrate:\s*([\d.]+)\s+([MGK]Bit/s)",
                (1, 2, 3),
            ),
        }
        pattern, groups = patterns[value]
        return [
            tuple(match.group(group) for group in groups)
            if len(groups) > 1
            else match.group(groups[0])
            for line in lines
            if (match := re.match(pattern, line, re.IGNORECASE))
        ]

    def get_iw_station_details(self, device: str, interface: str, value: str) -> list:
        """
        Get normalized details from ``iw dev <interface> station dump``.
        """
        lines = [
            line.rstrip()
            for line in self.get_iw_dev_sta_dump(device, interface).splitlines()
        ]
        valid_values = {
            "records", "macs", "connected_time", "tx_rate", "rx_rate"
        }
        if value not in valid_values:
            raise ValueError(f"Unsupported iw station value: {value}")
        if value in {"records", "macs"}:
            records = []
            current = None
            for line in lines:
                station = re.match(r"^Station\s+([0-9a-f:]{17})\b", line, re.IGNORECASE)
                if station:
                    if current:
                        records.append(current)
                    current = [station.group(1), []]
                elif current:
                    current[1].append(line)
            if current:
                records.append(current)
            if value == "records":
                return [(mac, "\n".join(details)) for mac, details in records]
            return [mac for mac, _ in records]
        patterns = {
            "connected_time": r"^\s*connected time:\s*(\d+) seconds",
            "tx_rate": r"^\s*tx bitrate:\s*([\d.]+)\s+([MGK]Bit/s)",
            "rx_rate": r"^\s*rx bitrate:\s*([\d.]+)\s+([MGK]Bit/s)",
        }
        pattern = re.compile(patterns[value], re.IGNORECASE)
        matches = [match for line in lines if (match := pattern.match(line))]
        if value in {"tx_rate", "rx_rate"}:
            return [(match.group(1), match.group(2)) for match in matches]
        return [match.group(1) for match in matches]

    def get_backhaul_interface_details(self, device: str, interface: str) -> dict:
        """
        Return connection, BSSID, RSSI, rates, and uptime for a backhaul interface.
        """
        bssids = self.get_iw_link_details(device, interface, "bssid")
        signals = self.get_iw_link_details(device, interface, "signal")
        rates = self.get_iw_link_details(device, interface, "rates")
        tx_rate = next((rate[1:] for rate in rates if rate[0] == "tx"), None)
        rx_rate = next((rate[1:] for rate in rates if rate[0] == "rx"), None)
        connected_times = self.get_iw_station_details(
            device, interface, "connected_time"
        )
        return {
            "connected": bool(bssids),
            "bssid": bssids[0] if bssids else None,
            "rssi_dbm": int(signals[0]) if signals else None,
            "tx_rate": tx_rate,
            "rx_rate": rx_rate,
            "connected_time": (
                int(connected_times[0]) if connected_times else None
            ),
        }

    def get_cpu_utilization(self, device: str) -> str:
        """
        Get one non-interactive CPU snapshot from the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        command = "top -b -n 1"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
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
        command = "free -m"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
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
        try:
            index = self.db_obj.read_from_database(device, index)
            #interface = self.db_obj.read_from_database(device, "wifi_iface").format(index)
        except Exception as err: # pylint: disable=broad-except
            zi_logger.log(f"ERROR: {err}")
            raise RuntimeError(f"Could not find out the Radio of the device : {device}")

        command = f"dmcli eRT setv Device.WiFi.SSID.{index}.SSID string {ssid}"
        zi_logger.log(f"COMMAND : {command}")
        _, error = connection_obj.execute_command(device, command,
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
        try:
            index = self.db_obj.read_from_database(device, index)
            #interface = self.db_obj.read_from_database(device, "wifi_iface").format(index)
        except Exception as err: # pylint: disable=broad-except
            zi_logger.log(f"ERROR: {err}")
            raise RuntimeError(f"Could not find out the Radio of the device : {device}")
        cutVal = '{print $3}'
        command = f"dmcli eRT getv Device.WiFi.SSID.{index}.SSID | grep 'value:' | awk -F': ' '{cutVal}'"
        output, error = connection_obj.execute_command(device, command,
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
        output, error = connection_obj.execute_command(device, command,
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
        command = "reboot >/dev/null 2>&1 &"
        zi_logger.log(f"COMMAND : {command}")
        connection_obj.execute_command(device, command,
                                       blocking_call = False)

    def get_fronthaul_credentials(self, device: str) -> tuple:
        """
        Return the OneWifiMesh fronthaul SSID and passphrase.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        query = (
            "SELECT SSID, PassPhrase FROM NetworkSSIDList "
            "WHERE ID LIKE '%Fronthaul%OneWifiMesh%' LIMIT 1;"
        )
        command = f"mysql -N -B -D OneWifiMesh -e {shlex.quote(query)}"
        output, error = connection_obj.execute_command(
            device, command, return_stderr=True
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
        command = f"systemctl is-active {service_name}"
        output, error = connection_obj.execute_command(
            device, command, return_stderr=True
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
        command = f"python3 -c \"import glob, sys; print(bool(glob.glob(sys.argv[1])))\" {shlex.quote(file_path)}"
        output, error = connection_obj.execute_command(device, command,
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
        # command = "date +%s"
        command = "python3 -c \"from datetime import datetime; print(datetime.now().timestamp())\""
        output, error = connection_obj.execute_command(device, command,
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
        command = f"ls {shlex.quote(directory_path)}"
        output, error = connection_obj.execute_command(device, command,
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
            device, command,
            return_stderr=True
        )
        if error:
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        output = output.strip()
        if not output:
            raise RuntimeError(
                f"No operating channel found for band {band} on device {device}. "
                f"Command: {command}"
            )
        return int(output)

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
        command = f"scp {shlex.quote(local_file_path)} {shlex.quote('{}@{}:{}'.format(user, remote_device_ip, remote_file_path))}"
        _, error = connection_obj.execute_command(device, command,
                                              return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed : {command}. stderr: {error.strip()}")
        return True

    def start_service(self,
                    device: str,
                    service_name: str) -> bool:
        """
        Start and enable the specified service on the device.
        """
        zi_logger.print_context()

        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)

        commands = [
            "systemctl daemon-reload",
            f"systemctl enable {shlex.quote(service_name)}",
            f"systemctl start {shlex.quote(service_name)}",
        ]

        for command in commands:
            _, error = connection_obj.execute_command(
                device, command,
                return_stderr=True
            )
            if error:
                raise RuntimeError(
                    f"Command execution failed: {command}. stderr: {error.strip()}"
                )

        command = f"systemctl status {shlex.quote(service_name)}"
        _, error = connection_obj.execute_command(
            device, command,
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

        command = f"systemctl stop {shlex.quote(service_name)}"

        _, error = connection_obj.execute_command(
            device, command,
            return_stderr=True
        )
        if error:
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        command = f"systemctl status {shlex.quote(service_name)}"
        _, error = connection_obj.execute_command(
            device, command,
            return_stderr=True
        )
        if error:
            raise RuntimeError(
                f"Command execution failed: {command}. stderr: {error.strip()}"
            )
        return True

    def get_ap_ssid_visibility(self, device:str, ssid:str) -> str:
        """
        To get the SSID visibility of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        cmd = f"nmcli -f SSID,FREQ dev wifi list --rescan yes | grep -i {shlex.quote(ssid)}"
        output, error = connection_obj.execute_command(device, cmd, return_stderr=True)
        if ssid not in output:
            raise RuntimeError(f"Command execution failed : {output}")        
        return output

    def get_association_status(self, device: str) -> str:
        """
        To get the association status of the device.
        """
        zi_logger.print_context()
        wlan_iface = self.db_obj.read_from_database(device, 'data_iface')
        link_info = self.get_iw_dev_link_info(device, wlan_iface)
        for line in link_info.splitlines():
            if "Connected to" in line:
                return line.split()[2]
        raise RuntimeError("Command execution failed: client not associated")

    def verify_dhcp_process(self, device: str) -> str:
        """
        To verify the DHCP process of the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        wlan_iface = self.db_obj.read_from_database(device, 'data_iface')
        cmd = f"dhclient -v {wlan_iface}"
        output, error = connection_obj.execute_command(device, cmd, return_stderr=True)
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
        cmd = "ip route show | grep -m 1 default"
        output, error = connection_obj.execute_command(device, cmd, return_stderr=True)
        if 'default via' not in output:
            raise RuntimeError(f"Command execution failed : {output}")        
        return output.split()[2]

    def set_wpa_log_level(self, device: str, level: str = "DEBUG") -> None:
        """
        Set wpa_supplicant log level using `wpa_cli -i <interface> log_level <level>`.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        interface = self.db_obj.read_from_database(device, 'data_iface')
        command = f"wpa_cli -i {shlex.quote(interface)} log_level {shlex.quote(level)}"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
        if error != '' or str(output).strip() != 'OK':
            raise RuntimeError(f"Command execution failed: {command}. output: {str(output).strip()} stderr: {error.strip()}")

    def get_wpa_cli_status(self, device: str) -> str:
        """
        Get wpa_supplicant status using `wpa_cli -i <interface> status`.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        interface = self.db_obj.read_from_database(device, 'data_iface')
        command = f"wpa_cli -i {shlex.quote(interface)} status | grep 'wpa_state=COMPLETED'"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
        if error != '':
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return str(output).strip()

    def verify_four_way_handshake_messages(self, device: str, interface: str) -> str:
        """
        Verify the WPA 4-Way Handshake messages of the Wi-Fi client.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        cmd = (
            "journalctl -u wpa_supplicant --since '5 minutes ago' --no-pager "
            f"| grep '{interface}' "
            "| awk "
            "'/RX message 1 of 4-Way Handshake/ && !m1++ {print; found++} "
            "/Sending EAPOL-Key 2\\/4/ && !m2++ {print; found++} "
            "/RX message 3 of 4-Way Handshake/ && !m3++ {print; found++} "
            "/Sending EAPOL-Key 4\\/4/ && !m4++ {print; found++} "
            "found == 4 {exit}'")
        output, error = connection_obj.execute_command(device, cmd, return_stderr=True)
        combined_output = f"{output}\n{error}"
        handshake_messages = [
            'RX message 1 of 4-Way Handshake',
            'Sending EAPOL-Key 2/4',
            'RX message 3 of 4-Way Handshake',
            'Sending EAPOL-Key 4/4'
        ]
        missing_messages = [
            message for message in handshake_messages
            if message not in combined_output
        ]
        if missing_messages:
            raise RuntimeError("WPA 4-Way Handshake verification failed. "f"Missing messages: {missing_messages}")
        return ("WPA 4-Way Handshake completed successfully. All 4 handshake messages verified.")
    
    def get_wpa_cli_capability(self, device: str, capability: str) -> list:
        """
        Get `wpa_cli -i <interface> get_capability <pairwise|group|key_mgmt|...>` as a list.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        interface = self.db_obj.read_from_database(device, 'data_iface')
        command = f"wpa_cli -i {shlex.quote(interface)} get_capability {shlex.quote(capability)}"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
        if error != '' or 'FAIL' in str(output):
            raise RuntimeError(f"Command execution failed: {command}. output: {str(output).strip()} stderr: {error.strip()}")
        return str(output).split()

    def get_wlan_ip_address(self, device: str) -> str:
        """
        To get the IP address of the device for a specific interface.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        interface = self.db_obj.read_from_database(device, 'data_iface')
        cmd = f"ip -4 addr show {shlex.quote(interface)} | grep 'inet ' | awk '{{print $2}}' | cut -d'/' -f1"
        output, error = connection_obj.execute_command(device, cmd, return_stderr=True)
        if not output.strip():
            raise RuntimeError(f"Command execution failed : {output}")        
        return output.strip()
    
    def get_wifi_generation(self, device: str) -> str:
        """
        Identify the highest Wi-Fi generation supported by the device.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        command = (
            "iw list | grep -iE "
            "'EHT MAC CAPABILITIES|EHT IFTYPES|"
            "HE MAC CAPABILITIES|HE IFTYPES|"
            "VHT CAPABILITIES|HT20/HT40|HT TX/RX MCS|HT CAPABILITIES' || true")
        output, error = connection_obj.execute_command(device, command,
                                                        return_stdout=True,
                                                        return_stderr=True)
        if error:
            raise ValueError("Error: Device is not active.")
        if not output:
            zi_logger.print_error("Unable to retrieve Wi-Fi capabilities")
            return "Unable to determine"
        output = output.upper()
        if "EHT MAC CAPABILITIES" in output or "EHT IFTYPES" in output:
            return "Wi-Fi 7"
        elif "HE MAC CAPABILITIES" in output or "HE IFTYPES" in output:
            return "Wi-Fi 6"
        elif "VHT CAPABILITIES" in output:
            return "Wi-Fi 5"
        elif "HT20/HT40" in output or "HT TX/RX MCS" in output or "HT CAPABILITIES" in output:
            return "Wi-Fi 4"
        return "Unable to determine"

    def get_operating_radio_details(self, device: str, band: str) -> dict:
        """
        Get operating channel, operating class, and operating bandwidth
        for the specified radio band.    
        """
        zi_logger.print_context()    
        # Get operating channel using the existing function
        channel = self.get_operating_channel(device, band)    
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)    
        command = "iw dev mld0 info | grep 'channel'"    
        output, error = connection_obj.execute_command( device, command, return_stderr=True)    
        if error:
            raise RuntimeError( f"Command execution failed: {command}. stderr: {error.strip()}")    
        # Find the bandwidth corresponding to the requested channel
        bandwidth = None    
        for line in output.splitlines():
            if f"channel {channel} " in line:
                match = re.search(r"width:\s*(\d+)\s*MHz", line)
                if match:
                    bandwidth = int(match.group(1))
                    break                
        if bandwidth is None:
            raise RuntimeError(f"Operating bandwidth not found for channel {channel}")    
        # Operating class mapping
        operating_classes = {
            "2.4": {20: 81,40: 83},
            "5": {20: 115,40: 116,80: 128,160: 129},
            "6": {20: 131,40: 132,80: 133,160: 134,320: 137}}    
        operating_class = operating_classes.get(band, {}).get(bandwidth)    
        if operating_class is None:
            raise RuntimeError(f"Operating class not found for band {band}, channel {channel}, bandwidth {bandwidth} MHz")    
        return {
            "operating_channel": channel,
            "operating_class": operating_class,
            "operating_bandwidth": bandwidth }

    def get_nmcli_scan_output(self, device: str) -> str:
        """
        To get the nmcli scan output of the device.
        """
        zi_logger.print_context()
        client_username = self.db_obj.read_from_database(device, "username")
        client_password = self.db_obj.read_from_database(device, "password")
        wifi_interface = self.db_obj.read_from_database(device, "data_iface")
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        zi_logger.log("Executing nmcli scan command")
        command_scan = (
            f"nmcli device wifi rescan ifname {shlex.quote(wifi_interface)}"
            if client_username == "root"
            else (
                f"printf '%s\\n' {shlex.quote(client_password)} | "
                f"sudo -S -p '' sh -c "
                f"\"nmcli device wifi rescan ifname {shlex.quote(wifi_interface)}\""
            )
        )
        output, error = connection_obj.execute_command(
            device, command_scan, return_stderr=True, timeout=60
        )
        if error:
            raise RuntimeError(f"nmcli scan command failed on {device}: {error.strip()}")
        time.sleep(5)
        command_list = (
            f"nmcli -f BSSID,SECURITY device wifi list ifname {shlex.quote(wifi_interface)}"
            if client_username == "root"
            else (
                f"printf '%s\\n' {shlex.quote(client_password)} | "
                f"sudo -S -p '' sh -c "
                f"\"nmcli -f BSSID,SECURITY device wifi list ifname {shlex.quote(wifi_interface)}\""
            )
        )
        previous_log_state = zi_logger.enable_log
        zi_logger.set_log_state(False)
        try:
            network_list, error = connection_obj.execute_command(device, command_list, return_stderr=True, timeout=60)
        finally:
             zi_logger.set_log_state(previous_log_state)
        if error:
            raise RuntimeError(f"nmcli list command failed on {device}: {error.strip()}")
        return network_list
    def get_bridge_info(self, device: str, bridge_iface: str) -> str:
        """
        Get the interfaces attached to the specified bridge.
        """
        zi_logger.print_context()
        connection = self.db_obj.read_from_database(device, 'connection')
        connection_obj = self.get_connection_module_object(connection)
        command = f"brctl show {shlex.quote(bridge_iface)}"
        output, error = connection_obj.execute_command(device, command, return_stderr=True)
        if error:
            raise RuntimeError(f"Command execution failed: {command}. stderr: {error.strip()}")
        return str(output).strip()

    def get_bridge_station_interfaces(self, device: str, bridge_iface: str) -> list[str]:
        """
        Return wireless station interfaces attached to the specified bridge.
        """
        interfaces = []
        bridge_found = False
        for line in self.get_bridge_info(device, bridge_iface).splitlines():
            fields = line.split()
            if not fields or fields[0] == "bridge":
                continue
            if fields[0].startswith("br"):
                bridge_found = fields[0] == bridge_iface
                if bridge_found:
                    candidate = fields[-1]
                    if candidate.startswith("wifi") and ".sta" in candidate:
                        interfaces.append(candidate)
                continue
            if bridge_found:
                candidate = fields[-1]
                if candidate.startswith("wifi") and ".sta" in candidate:
                    interfaces.append(candidate)
        return list(dict.fromkeys(interfaces))
