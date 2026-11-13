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

import json
import re
import shlex
import uuid
from rdkbmeshzap.common_utils import device_utils, report_logger

# Duration of each client iperf measurement in seconds.
IPERF_SAMPLE_DURATION_SEC = 10
# Maximum packet loss allowed during link validation.
MAX_PACKET_LOSS_PERCENT = 5.0
# Maximum average latency allowed relative to the baseline.
MAX_LATENCY_MULTIPLIER = 2.0
# Time between stability checks in seconds.
POLL_INTERVAL_SEC = 600
# Total link stability monitoring duration in seconds.
TEST_DURATION_SEC = 3600
# Number of packets used for regular ping measurements.
PING_COUNT = 10
# Number of packets used for the final ping measurement.
FINAL_PING_COUNT = 1000
# Maximum time allowed for the final ping in seconds.
FINAL_PING_DEADLINE_SEC = 120
# Remote log file used by the controller iperf server.
IPERF_SERVER_LOG = "/tmp/end_to_end_iperf_server.log"
# Minimum throughput ratio required against the baseline.
MIN_THROUGHPUT_RATIO = 0.8
# Maximum PHY-rate reduction allowed from the baseline (%).
PHY_RATE_DROP_PERCENT = 50
# Maximum RSSI degradation allowed from the baseline (dB).
MAX_RSSI_DEGRADATION_DB = 10
# Minimum RSSI required for a stable link (dBm).
MIN_RSSI_DBM = -80

def parse_ping_metrics(output: str) -> dict:
    """
    Syntax : parse_ping_metrics(output)
    Description : Extracts packet loss and round-trip timing from Linux ping output.
    Parameters :
        output - Raw Linux ping command output.
    Return Value: A dictionary containing loss_percent, min_ms, avg_ms, and max_ms.
    """
    loss_match = re.search(r"([0-9]+(?:\.[0-9]+)?)%\s*packet loss", output)
    rtt_match = re.search(
        r"(?:rtt|round-trip).*?=\s*"
        r"([0-9.]+)/([0-9.]+)/([0-9.]+)",
        output)
    if not loss_match or not rtt_match:
        raise ValueError(f"Unable to parse ping statistics: {output}")
    return {
        "loss_percent": float(loss_match.group(1)),
        "min_ms": float(rtt_match.group(1)),
        "avg_ms": float(rtt_match.group(2)),
        "max_ms": float(rtt_match.group(3))}

def parse_iperf_throughput(output: str) -> float:
    """
    Syntax : parse_iperf_throughput(output)
    Description : Extracts final receiver throughput from iperf3 JSON or text output.
    Parameters :
        output - Raw iperf3 command output in JSON or text format.
    Return Value: The receiver throughput in Mbps.
    """
    try:
        result = json.loads(output)
        bits_per_second = result["end"]["sum_received"]["bits_per_second"]
        return float(bits_per_second) / 1_000_000
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        matches = re.findall(r"([0-9]+(?:\.[0-9]+)?)\s+([KMG]?)bits/sec",output,flags=re.IGNORECASE)
        if not matches:
            raise ValueError(f"Unable to parse iperf3 throughput: {output}")
        value, unit = matches[-1]
        multiplier = {"": 0.000001, "K": 0.001, "M": 1.0, "G": 1000.0}[unit.upper()]
        return float(value) * multiplier

def run_ping(initialize, client: str, gateway_ip: str, count: int,
             deadline: int | None = None) -> dict:
    """
    Syntax : run_ping(initialize, client, gateway_ip, count, deadline=None)
    Description : Runs ping from a WLAN client to the specified gateway.
    Parameters :
        initialize - Testbed initialization and database interface.
        client - WLAN client device used to run ping.
        gateway_ip - Destination gateway IPv4 address.
        count - Number of echo requests to send.
        deadline - Optional ping deadline in seconds.
    Return Value: Parsed ping metrics from parse_ping_metrics().
    """
    deadline_option = f" -w {deadline}" if deadline else ""
    command = (f"ping -n -c {count} -W 1{deadline_option} {shlex.quote(gateway_ip)}")
    connection = initialize.read_from_database(client, "connection")
    connection_obj = initialize.get_connection_module_object(connection)
    output, error = connection_obj.execute_command(
        client, command, return_stderr=True)
    if not isinstance(output, str):
        output = str(output)
    if error:
        raise Exception(str(error).strip())
    return parse_ping_metrics(output)

def run_iperf(initialize, client: str, gateway_ip: str) -> float:
    """
    Syntax : run_iperf(initialize, client, gateway_ip)
    Description : Runs an iperf3 client sample from a WLAN client to the gateway.
    Parameters :
        initialize - Testbed initialization and database interface.
        client - WLAN client device used to run iperf3.
        gateway_ip - Destination gateway IPv4 address.
    Return Value: The measured receiver throughput in Mbps.
    """
    bind_ip = initialize.get_wlan_ip_address(client, "cli")
    if not bind_ip:
        raise Exception("client has no assigned IPv4 address")
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", client)
    remote_log = f"/tmp/end_to_end_iperf_{safe_name}_{uuid.uuid4().hex}.log"
    connection = initialize.read_from_database(client, "connection")
    connection_obj = initialize.get_connection_module_object(connection)
    try:
        initialize.start_iperf_client(client,gateway_ip,bind_ip,"tcp",remote_log,time=IPERF_SAMPLE_DURATION_SEC)
        output, error = connection_obj.execute_command(client, f"cat {remote_log}", return_stderr=True)
        if error and not output:
            raise Exception(str(error).strip())
        return parse_iperf_throughput(str(output))
    finally:
        try:
            connection_obj.execute_command(client, f"rm -f {remote_log}")
        except Exception:
            pass

def validate_link_metrics(metrics: dict, baseline: dict) -> list:
    """
    Syntax : validate_link_metrics(metrics, baseline)
    Description : Validates packet loss and latency against link stability thresholds.
    Parameters :
        metrics - Current parsed ping metrics.
        baseline - Baseline parsed ping metrics for comparison.
    Return Value: A list of threshold violation descriptions, empty when valid.
    """
    errors = []
    if metrics["loss_percent"] > MAX_PACKET_LOSS_PERCENT:
        errors.append(
            f"packet loss {metrics['loss_percent']:.2f}% exceeds {MAX_PACKET_LOSS_PERCENT:.2f}%")
    if metrics["avg_ms"] > baseline["avg_ms"] * MAX_LATENCY_MULTIPLIER:
        errors.append(f"average latency {metrics['avg_ms']:.2f} ms exceeds {MAX_LATENCY_MULTIPLIER:.1f}x baseline{baseline['avg_ms']:.2f} ms")
    return errors

def get_device_advertising_bssid(initialize, bssid: str):
    """
    Syntax : get_device_advertising_bssid(initialize, bssid)
    Description : Identifies the mesh device advertising the specified fronthaul BSSID.
    Parameters :
        initialize - Testbed initialization and database interface.
        bssid - BSSID to locate within the mesh network.
    Return Value: Device name advertising the BSSID, or None if not found.
    """
    connected_bssid = str(bssid or "").strip().lower()
    if not connected_bssid:
        report_logger.print_error(
            "FAIL: Cannot identify the mesh device because the BSSID is empty")
        return None
    if not re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", connected_bssid):
        report_logger.print_error(f"Invalid BSSID format: {bssid}")
        return None
    devices = ["controller", *device_utils.get_enabled_extenders(initialize)]
    for device in devices:
        try:
            bssids = {
                str(device_bssid).strip().lower()
                for device_bssid in initialize.get_fronthaul_bssids(device)
                if device_bssid}
        except Exception as err:
            report_logger.print_info(
                f"INFO: Could not read fronthaul BSSIDs from '{device}': {err}")
            continue
        if connected_bssid in bssids:
            return device
    report_logger.print_info(
        f"INFO: No mesh device advertises fronthaul BSSID {connected_bssid}")
    return None

def rate_to_mbps(rate: str | float, unit: str) -> float:
    """
    Syntax : rate_to_mbps(rate, unit)
    Description : Converts a parsed `iw` bitrate to megabits per second.
    Parameters :
        rate - Numeric bitrate value returned by the parser.
        unit - Bitrate unit returned by the parser.
    Return Value: The bitrate in Mbps.
    """
    rate_mbps = float(rate)
    unit = unit.lower()
    if unit == "gbit/s":
        return rate_mbps * 1000
    if unit == "kbit/s":
        return rate_mbps / 1000
    return rate_mbps

def get_client_phy_rates(initialize, client: str, host: str | None) -> dict | None:
    """
    Syntax : get_client_phy_rates(initialize, client, host)
    Description : Reads a client's primary transmit and receive PHY rates.
    Parameters :
        initialize - Testbed initialization and database interface.
        client - Name of the configured WLAN client.
        host - Present mesh device advertising the client's associated BSSID.
    Return Value: A PHY-rate state dictionary, or None when no station matches.
    """
    if host is None:
        return None
    client_mac = initialize.read_from_database(client, "mac").lower()
    interface = device_utils.get_fronthaul_interface(initialize, host)
    for station_mac, _ in initialize.get_iw_station_details(host, interface, "records"):
        station_mac = station_mac.lower()
        if station_mac != client_mac:
            continue
        tx_rates = initialize.get_iw_station_details(host, interface, "tx_rate")
        rx_rates = initialize.get_iw_station_details(host, interface, "rx_rate")
        return {
            "host": host,
            "interface": interface,
            "tx_mbps": rate_to_mbps(*tx_rates[0]) if tx_rates else None,
            "rx_mbps": rate_to_mbps(*rx_rates[0]) if rx_rates else None,
        }
    return None

def validate_phy_rates(current_rates: dict | None, baseline_rates: dict | None = None, drop_percent_limit: float = PHY_RATE_DROP_PERCENT) -> str | None:
    """
    Syntax : validate_phy_rates(current_rates, baseline_rates=None, drop_percent_limit=PHY_RATE_DROP_PERCENT)
    Description : Validates PHY rates and optional baseline degradation.
    Parameters :
        current_rates - Current PHY-rate dictionary.
        baseline_rates - Optional baseline PHY-rate dictionary.
        drop_percent_limit - Maximum allowed rate reduction percentage.
    Return Value: An error message, or None when the sample is valid.
    """
    if current_rates is None:
        return "client PHY-rate sample is unavailable"
    if current_rates["tx_mbps"] is None or current_rates["rx_mbps"] is None:
        return f"station record has no TX/RX PHY rate: {current_rates}"
    if baseline_rates is not None:
        for direction in ("tx_mbps", "rx_mbps"):
            baseline_rate = baseline_rates[direction]
            current_rate = current_rates[direction]
            if baseline_rate <= 0:
                continue
            drop_percent = (baseline_rate - current_rate) / baseline_rate * 100
            if drop_percent > drop_percent_limit:
                return (f"{direction[:-5].upper()} PHY rate dropped by {drop_percent:.1f}% from {baseline_rate:.1f} to {current_rate:.1f} Mbps")
    return None

def get_client_rssi(initialize, client: str, host: str | None) -> dict | None:
    """
    Syntax : get_client_rssi(initialize, client, host)
    Description : Reads a client's fronthaul RSSI and station state.
    Parameters :
        initialize - Testbed initialization and database interface.
        client - Name of the configured WLAN client.
        host - Present mesh device advertising the client's associated BSSID.
    Return Value: An RSSI state dictionary, or None when no station matches.
    """
    if host is None:
        return None
    interface = device_utils.get_fronthaul_interface(initialize, host)
    client_mac = initialize.read_from_database(client, "mac").lower()
    for station_mac, details in initialize.get_iw_station_details(
        host, interface, "records"):
        station_mac = station_mac.lower()
        if station_mac != client_mac:
            continue
        signal = re.search(
            r"^\s*signal:\s*(-?\d+)\s*dBm\s*$",
            details,
            re.IGNORECASE | re.MULTILINE)
        return {
            "host": host,
            "interface": interface,
            "rssi_dbm": int(signal.group(1)) if signal else None}
    return None

def validate_client_rssi(current_rssi: dict | None, baseline_rssi: int | None = None, max_rssi_degradation_db: int = MAX_RSSI_DEGRADATION_DB) -> str | None:
    """
    Syntax : validate_client_rssi(current_rssi, baseline_rssi=None, max_rssi_degradation_db=MAX_RSSI_DEGRADATION_DB)
    Description : Validates RSSI data and degradation.
    Parameters :
        current_rssi - Current RSSI dictionary.
        baseline_rssi - Optional baseline RSSI value in dBm.
        max_rssi_degradation_db - Maximum allowed RSSI degradation in dB.
    Return Value: An error message, or None when the sample is valid.
    """
    if current_rssi is None:
        return "client RSSI sample is unavailable"
    if current_rssi["rssi_dbm"] is None:
        return "station record has no primary signal value"
    if baseline_rssi is not None:
        degradation = baseline_rssi - current_rssi["rssi_dbm"]
        if degradation > max_rssi_degradation_db:
            return (f"RSSI degraded by {degradation} dB from {baseline_rssi} dBm to {current_rssi['rssi_dbm']} dBm")
    return None
