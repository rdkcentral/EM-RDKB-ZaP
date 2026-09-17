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

import os
import re
import shlex
import time
from pathlib import Path

import pytest
from packet_analyzer.ieee1905_utils import *  # noqa: F401,F403
from packet_analyzer.packet_dissector import *  # noqa: F401,F403
from zaero.utils import zi_logger


RECOVERY_KPI_SECONDS = 300
RETRY_INTERVAL_SECONDS = 5
MAX_RETRIES = RECOVERY_KPI_SECONDS // RETRY_INTERVAL_SECONDS


class FeatureRecoveryCLI:

    def create_capture_name(self, prefix, extender, extension="pcapng"):
        return f"{prefix}_{extender}_{int(time.time())}.{extension}"

    def get_extenders_by_topology_role(self, initialize, role):
        extenders = []
        for device in initialize.get_testbed_devices():
            if not device.startswith("extender") or "_client_" in device:
                continue
            if not initialize.read_from_database(device, "device_present"):
                continue
            configured_role = initialize.read_from_database(device, "topology_role")
            if configured_role == role:
                extenders.append(device)
            elif configured_role is None and role == "star":
                tunnel_device = initialize.read_from_database(device, "tunnel_device")
                if tunnel_device == "controller":
                    extenders.append(device)
        return extenders

    def get_interface_mac_address(self, initialize, device, interface_name):
        ssh = initialize.get_connection_module_object("ssh")
        ssh.switch_connection(device)
        output = ssh.execute_command(f"ifconfig {shlex.quote(interface_name)}")
        match = re.search(
            r"(?:HWaddr|ether)\s+([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})",
            str(output),
        )
        if not match:
            raise RuntimeError(
                f"{device}: could not read MAC address for interface {interface_name}"
            )
        return match.group(1).lower()

    def get_backhaul_capture_interface(self, initialize, device):
        try:
            capture_interface = initialize.read_from_database(
                device, "backhaul_capture_iface"
            )
            if capture_interface:
                return capture_interface
        except Exception:
            pass

        ssh = initialize.get_connection_module_object("ssh")
        ssh.switch_connection(device)
        output = ssh.execute_command("ifconfig")
        candidates = re.findall(r"\b([A-Za-z0-9_.]+_virt_peer)\b", str(output))
        if "eth1_virt_peer" in candidates:
            return "eth1_virt_peer"
        if "eth0_virt_peer" in candidates:
            return "eth0_virt_peer"
        if candidates:
            return candidates[0]

        raise RuntimeError(f"{device}: could not determine backhaul capture interface")

    def _get_wifi_candidates_from_bridge_output(self, bridge_output):
        candidates = []
        for match in re.finditer(r"\b(wifi[^\s]*)\b", str(bridge_output)):
            interface_name = match.group(1)
            if interface_name not in candidates:
                candidates.append(interface_name)
        return candidates

    def get_station_wifi_interface(self, initialize, device, bridge_iface):
        ssh = initialize.get_connection_module_object("ssh")
        ssh.switch_connection(device)
        bridge_output = ssh.execute_command(
            f"brctl show {shlex.quote(bridge_iface)}"
        )
        candidates = self._get_wifi_candidates_from_bridge_output(bridge_output)
        for interface_name in candidates:
            station_output = ssh.execute_command(
                f"iw dev {shlex.quote(interface_name)} station dump"
            )
            if "Station " in str(station_output) and "associated:" in str(station_output):
                return interface_name
        raise RuntimeError(
            f"{device}: could not find an active station interface under {bridge_iface}"
        )

    def get_link_wifi_interface(self, initialize, device, bridge_iface):
        ssh = initialize.get_connection_module_object("ssh")
        ssh.switch_connection(device)
        bridge_output = ssh.execute_command(
            f"brctl show {shlex.quote(bridge_iface)}"
        )
        candidates = self._get_wifi_candidates_from_bridge_output(bridge_output)
        for interface_name in candidates:
            link_output = ssh.execute_command(f"iw dev {shlex.quote(interface_name)} link")
            if "Connected to" in str(link_output):
                return interface_name
        raise RuntimeError(
            f"{device}: could not find a connected Wi-Fi interface under {bridge_iface}"
        )

    def reconnect_device(self, initialize, device, logger=zi_logger, step=None):
        message = f"{device}: waiting for SSH recovery"
        if step is None:
            logger.print_step(message)
        else:
            logger.print_step(f"STEP {step}: {message}")
        for attempt in range(1, MAX_RETRIES + 1):
            initialize.close_connection(device)
            try:
                initialize.connect_with_device(device)
            except Exception as error:
                logger.print_step(f"{device} connect attempt {attempt} failed: {error}")
                time.sleep(RETRY_INTERVAL_SECONDS)
                continue
            logger.print_success(f"PASS: {device} connection restored on attempt {attempt}")
            return
        pytest.fail(f"Could not reconnect {device} within {RECOVERY_KPI_SECONDS} seconds")

    def get_fronthaul_credentials(self, initialize, ssh=None, table="NetworkSSIDList"):
        return initialize.get_fronthaul_credentials("controller")

    def get_extender_bssids(self, initialize, extender, ssh):
        return initialize.get_fronthaul_bssids(extender)

    def get_client_bssids(self, initialize, client, ssid, ssh):
        ssh.switch_connection(client)
        result = ssh.execute_command(
            "nmcli -t --escape no -f BSSID,SSID device wifi list"
        )
        bssids = []
        for row in (result or "").splitlines():
            row = row.replace("\\:", ":")
            if len(row) >= 19 and row[17] == ":" and row[18:] == ssid:
                bssid = row[:17]
                if re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", bssid):
                    bssids.append(bssid.lower())
        return bssids

    def get_connected_bssid(self, initialize, client, ssh):
        wifi_interface = initialize.read_from_database(client, "data_iface")
        ssh.switch_connection(client)
        output = ssh.execute_command(
            f"iw dev {shlex.quote(wifi_interface)} link"
        )
        match = re.search(
            r"Connected to ((?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})",
            output or "",
        )
        return match.group(1).lower() if match else None

    def connect_client_to_bssid(self, initialize, client, ssid, passphrase, bssid, ssh):
        client_password = initialize.read_from_database(client, "password")
        wifi_interface = initialize.read_from_database(client, "data_iface")
        bssid = bssid.upper()
        ssh.switch_connection(client)
        command = (
            f"printf '%s\\n' {shlex.quote(client_password)} | "
            f"sudo -S -p '' nmcli device wifi connect {shlex.quote(ssid)} "
            f"password {shlex.quote(passphrase)} bssid {shlex.quote(bssid)} "
            f"ifname {shlex.quote(wifi_interface)}"
        )
        output = ssh.execute_command(command)
        if "successfully activated" not in output.lower():
            raise RuntimeError(f"Failed to connect {client} to BSSID {bssid}: {output}")

    def start_client_ping(self, initialize, client_devices, output_path):
        ssh = initialize.get_connection_module_object("ssh")
        for client in client_devices:
            wifi_interface = initialize.read_from_database(client, "data_iface")
            ssh.switch_connection(client)
            ssh.execute_command(
                f"rm -f {shlex.quote(output_path)}; "
                f"nohup ping -4 -I {shlex.quote(wifi_interface)} "
                f"-i 1 8.8.8.8 > {shlex.quote(output_path)} 2>&1 </dev/null &"
            )

    def start_extender_capture(self, initialize, extender, capture_prefix, step):
        capture_name = self.create_capture_name(capture_prefix, extender)
        capture_interface = self.get_backhaul_capture_interface(initialize, extender)
        capture_filter = initialize.read_from_database(extender, "filter_1905")
        initialize.start_frame_capture(
            extender, capture_interface, capture_filter, capture_name
        )
        message = f"{extender}: capture started on {capture_interface}; file {capture_name}"
        zi_logger.print_step(f"STEP {step}: {message}")
        return capture_name

    def recover_device(self, initialize, device, started_at, results, step, logger=zi_logger):
        logger.print_step_with_number(step, f"{device}: waiting for SSH recovery")
        try:
            self.reconnect_device(initialize, device, logger, step=step)
            recovery_time = time.monotonic() - started_at
            if device == "controller":
                self.verify_controller_services(initialize, step)
            else:
                self.verify_extender_services(initialize, device, step)
            results[device] = recovery_time
            logger.print_success(f"PASS: {device} connection restored in {recovery_time:.1f}s")
            return recovery_time
        except Exception as error:
            results[device] = error
            return error

    def stop_and_collect_capture(self, initialize, extender, capture_name):
        initialize.stop_frame_capture(extender)
        local_path = initialize.download_captured_pcap(extender, capture_name)
        initialize.delete_captured_pcap(extender, capture_name)
        return local_path

    def stop_collect_reassemble_and_validate_topology_capture(
        self,
        initialize,
        extender,
        capture_name,
        step,
        extender_al_mac=None,
    ):
        local_path = self.stop_and_collect_capture(initialize, extender, capture_name)
        packets = reassemble_packets(local_path)
        self.validate_topology_capture(packets, extender, step, extender_al_mac)
        return local_path

    def validate_ping_recovery(self, ping_output, client):
        lines = ping_output.splitlines()
        outage_indexes = [
            index for index, line in enumerate(lines)
            if "unreachable" in line.lower() or "100% packet loss" in line.lower()
        ]
        if not outage_indexes:
            pytest.fail(f"{client}: ping did not show an outage during recovery")
        last_outage = outage_indexes[-1]
        if not any("bytes from" in line for line in lines[last_outage + 1:]):
            pytest.fail(
                f"{client}: ping produced no successful replies after the outage:\n"
                f"{ping_output}"
            )

    def download_client_pings(self, initialize, clients, extender):
        ssh = initialize.get_connection_module_object("ssh")
        remote_path = f"/tmp/controller_recovery_{extender}_client_ping.txt"
        local_directory = Path(os.environ.get("TEST_RUN_DIR", "Reports"), "ping_logs")
        local_directory.mkdir(parents=True, exist_ok=True)
        outputs = {}

        for client in clients:
            ssh.switch_connection(client)
            safe_path = shlex.quote(remote_path)
            ssh.execute_command("killall ping", return_stdout=False, return_stderr=True)
            output = ssh.execute_command(f"cat {safe_path}")
            local_path = local_directory / f"{extender}_{client}_ping.txt"
            local_path.write_text(output, encoding="utf-8")
            outputs[client] = output
            zi_logger.print_step(f"{client}: ping output stored at {local_path}")

        return outputs

    def validate_topology_capture(self, packets, extender, step, extender_al_mac=None):
        if extender_al_mac:
            zi_logger.print_step(
                f"STEP {step}: {extender} capture validation using AL MAC {extender_al_mac}"
            )
        else:
            zi_logger.print_step(f"STEP {step}: {extender} capture validation")
        message_checks = (
            (MSG_TYPE_AP_TOPOLOGY_QUERY, "Topology Query"),
            (MSG_TYPE_AP_TOPOLOGY_RESPONSE, "Topology Response"),
        )
        for message_type, message_name in message_checks:
            if extender_al_mac:
                present = check_message_presence(
                    packets, message_type, src_mac=extender_al_mac
                ) or check_message_presence(
                    packets, message_type, dst_mac=extender_al_mac
                )
            else:
                present = check_message_presence(packets, message_type) or []
            if not present:
                pytest.fail(f"{extender}: expected {message_name} after recovery")
        zi_logger.print_success(f"PASS: {extender} capture contains Topology Query and Response")

    def map_clients_to_extenders(self, client_devices, extenders):
        client_groups = {extender: [] for extender in extenders}
        for extender in extenders:
            client_groups[extender] = next(
                ([client] for client in client_devices if client.startswith(f"{extender}_")),
                [],
            )
        missing = [extender for extender in extenders if not client_groups[extender]]
        if missing:
            pytest.fail(
                "No enabled WLAN client is configured for extender(s): "
                f"{', '.join(missing)}"
            )
        return client_groups

    def connect_clients_to_extender(self, initialize, client_devices, extender):
        ssh = initialize.get_connection_module_object("ssh")
        ssid, passphrase = self.get_fronthaul_credentials(initialize, ssh)
        extender_bssids = self.get_extender_bssids(initialize, extender, ssh)

        for client in client_devices:
            password = initialize.read_from_database(client, "password")
            interface = initialize.read_from_database(client, "data_iface")
            ssh.switch_connection(client)
            try:
                ssh.execute_command(
                    f"printf '%s\\n' {shlex.quote(password)} | "
                    f"sudo -S -p '' nmcli device disconnect {shlex.quote(interface)}"
                )
            except Exception:
                zi_logger.print_step(f"{client}: Wi-Fi interface already disconnected")

            time.sleep(2)
            for attempt in range(3):
                try:
                    initialize.check_ap_ssid_visibility(client, ssid)
                    visible_bssids = self.get_client_bssids(initialize, client, ssid, ssh)
                    target_bssid = next(
                        (bssid for bssid in extender_bssids if bssid in visible_bssids),
                        None,
                    )
                    if not target_bssid:
                        raise RuntimeError(f"BSSID for '{ssid}' was not found")
                    break
                except Exception as error:
                    if attempt == 2:
                        pytest.fail(
                            f"{client}: SSID '{ssid}' was not visible after retries: {error}"
                        )
                    zi_logger.print_step(f"{client}: SSID scan attempt {attempt + 1} failed; retrying")
                    time.sleep(5)
            try:
                self.connect_client_to_bssid(
                    initialize, client, ssid, passphrase, target_bssid, ssh
                )
            except Exception as error:
                pytest.fail(f"{client}: failed to connect to '{ssid}': {error}")

    def verify_service_status(self, initialize, device, service_names):
        for service_name in service_names:
            initialize.verify_service_status(device, service_name)

    def verify_services(self, initialize, device, service_names):
        retry_interval = 2
        max_attempts = 5
        last_error = None
        for attempt in range(1, max_attempts + 1):
            try:
                self.verify_service_status(initialize, device, service_names)
                zi_logger.print_success(f"PASS: {device} services are active on attempt {attempt}")
                return
            except Exception as error:
                last_error = error
                if attempt == max_attempts:
                    break
                zi_logger.print_step(f"{device}: services not active; retrying in {retry_interval}s (attempt {attempt}/{max_attempts})")
                time.sleep(retry_interval)
        raise RuntimeError(
            f"{device}: services did not become active after {max_attempts} attempts: "
            f"{last_error}"
        )

    def verify_controller_services(self, initialize, step):
        zi_logger.print_step(f"STEP {step}: Checking controller services")
        self.verify_services(
            initialize,
            "controller",
            ("onewifi", "ieee1905_em_agent", "ieee1905_em_ctrl", "em_ctrl"),
        )

    def verify_extender_services(self, initialize, extender, step):
        zi_logger.print_step(
            f"STEP {step}: {extender}: checking onewifi, ieee1905_em_agent, and em_agent"
        )
        self.verify_services(
            initialize,
            extender,
            ("onewifi", "ieee1905_em_agent", "em_agent"),
        )
