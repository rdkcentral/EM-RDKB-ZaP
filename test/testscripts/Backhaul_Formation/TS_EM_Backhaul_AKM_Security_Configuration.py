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


from contextlib import contextmanager
from ipaddress import IPv4Address
from pathlib import Path, PurePosixPath
import re
import shlex
import sys
import time
from uuid import uuid4

import pytest

from rdkbmeshzap.common_utils import report_logger

def _run(initialize, device, command):
    """Run a remote command and require a successful exit status."""
    stdout, stderr, rc = initialize.execute_command(
        device,
        command,
        return_stderr=True,
        return_rc=True,
    )

    assert rc == 0, (
        f"{device}: command failed: {command}\n"
        f"Exit status: {rc}\n"
        f"stdout: {stdout}\n"
        f"stderr: {stderr}"
    )

    output = str(stdout or "")
    report_logger.print_info(output)
    return output

def _verify_association(output, expected_ssid):
    """Verify active wireless association to the expected SSID."""
    assert re.search(
        r"^\s*Connected to (?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b",
        output,
        re.MULTILINE,
    ), f"Agent 1 is not connected:\n{output}"

    ssid = re.search(
        r"^\s*SSID:\s*(.*?)\s*$",
        output,
        re.MULTILINE,
    )

    assert ssid, f"SSID not found in link output:\n{output}"
    assert ssid.group(1).strip() == expected_ssid, (
        f"Agent 1 is not connected to expected SSID "
        f"{expected_ssid!r}:\n{output}"
    )

# PUBLIC_INTERFACE
def test_em_backhaul_akm_security_configuration(initialize):
    """
    Verify configured backhaul AKM and successful wireless
    backhaul association.
    """
    agent = "extender1"
    parameter = (
        "Device.WiFi.DataElements.Network.Device.1.Radio.1."
        "BSS.1.BackhaulAKMsAllowed"
    )
    link_command = "iw dev wifi1.3 link"

    report_logger.print_test("EM_Backhaul_AKM_Security_Configuration")

    report_logger.print_step("STEP 1: Verify AKM configuration")
    output = _run(
        initialize,
        "controller",
        f"rbuscli get {parameter}",
    )

    akm = re.search(
        rf"^\s*Name\s*:\s*{re.escape(parameter)}[ \t]*\r?\n"
        rf"\s*Type\s*:[^\r\n]+\r?\n"
        rf"\s*Value\s*:\s*([^\r\n]*)",
        output,
        re.MULTILINE,
    )

    assert akm, f"AKM property/value was not returned:\n{output}"

    value = akm.group(1).strip().strip("\"'")
    assert value, f"Configured AKM value is empty:\n{output}"
    report_logger.print_success(f"PASS: Configured AKM: {value}")

    report_logger.print_step(
        "STEP 2: Verify wireless backhaul association"
    )
    expected_ssid = initialize.read_from_database(
        "controller",
        "mesh_backhaul_ssid",
    )

    assert (
        isinstance(expected_ssid, str) and expected_ssid.strip()
    ), "controller.mesh_backhaul_ssid must be configured"

    expected_ssid = expected_ssid.strip()
    output = _run(initialize, agent, link_command)
    _verify_association(output, expected_ssid)

    report_logger.print_success(
        "PASS: Agent 1 is connected to the backhaul SSID"
    )

    report_logger.print_step(
        "STEP 3: Verify signal strength and link parameters"
    )
    output = _run(initialize, agent, link_command)
    _verify_association(output, expected_ssid)

    signal = re.search(
        r"^\s*signal:\s*(-?\d+(?:\.\d+)?)\s+dBm\b",
        output,
        re.MULTILINE,
    )
    frequency = re.search(
        r"^\s*freq:\s*(\d+(?:\.\d+)?)",
        output,
        re.MULTILINE,
    )
    tx_bitrate = re.search(
        r"^\s*tx bitrate:\s*(\d+(?:\.\d+)?)",
        output,
        re.MULTILINE,
    )

    assert signal, f"Signal strength information missing:\n{output}"
    assert frequency and float(frequency.group(1)) > 0, (
        f"Frequency information missing:\n{output}"
    )
    assert tx_bitrate and float(tx_bitrate.group(1)) > 0, (
        f"Transmit bitrate information missing:\n{output}"
    )
    report_logger.print_success("PASS: Valid link information displayed")

    report_logger.print_step(
        "STEP 4: Verify Controller-Agent connectivity"
    )
    controller_ip = initialize.read_from_database(
        "controller",
        "bridge_ip",
    )
    assert (
        isinstance(controller_ip, str) and controller_ip.strip()
    ), "controller.bridge_ip must be configured"

    ping_output = _run(
        initialize,
        agent,
        f"ping -c 4 -W 2 {shlex.quote(controller_ip.strip())}",
    )
    assert (
        "0% packet loss" in ping_output
        or "4 packets transmitted, 4 received" in ping_output
        or "4 received" in ping_output
    ), f"Controller-Agent connectivity failed:\n{ping_output}"

    report_logger.print_success(
        "PASS: Controller-Agent connectivity established"
    )

    report_logger.print_step("STEP 5: Verify Agent remains connected")
    time.sleep(30)

    output = _run(initialize, agent, link_command)
    _verify_association(output, expected_ssid)
    report_logger.print_success(
        "PASS: Agent remained connected to the backhaul SSID"
    )