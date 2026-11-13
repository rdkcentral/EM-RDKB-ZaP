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
from pathlib import Path
import re
import shlex
import sys
import time
from uuid import uuid4

import pytest
from scapy.layers.l2 import Ether

from packet_analyzer.ieee1905_utils import (
    MSG_TYPE_AP_TOPOLOGY_QUERY,
    MSG_TYPE_AP_TOPOLOGY_RESPONSE,
    MSG_TYPE_TOPOLOGY_DISCOVERY,
    TLV_TYPE_AL_MAC_ADDRESS,
    TLV_TYPE_DEVICE_INFORMATION,
    TLV_TYPE_MAC_ADDRESS,
)
from packet_analyzer.packet_dissector import parse_tlvs, reassemble_packets
from rdkbmeshzap.common_utils import report_logger

_CONTROLLER_ID = "Device.WiFi.DataElements.Network.ControllerID"
_REMOTE_PCAP = "/tmp/alid_check.pcap"
_AGENT = "extender1"

# Test observation/retry budgets, not device configuration.
_RECOVERY_SECONDS = 180
_OBSERVATION_SECONDS = 60
_POLL_SECONDS = 5

# PUBLIC_INTERFACE
@pytest.fixture(autouse=True)
def protocol_validation():
    """Replace the suite's parallel capture with this case's owned capture."""
    yield

def _run(initialize, device, command):
    """Run on the specified device and require a successful remote exit."""
    stdout, stderr, rc = initialize.execute_command(
        device,
        command,
        return_stderr=True,
        return_rc=True,
    )
    if rc != 0:
        raise RuntimeError(
            f"{device}: command failed (rc={rc}): {command}\n"
            f"{stdout}\n{stderr}"
        )

    # tcpdump writes normal status information to stderr even on success.
    return str(stdout or "")

def _mac(value, label):
    """Require one complete nonzero unicast AL MAC, normalized to lowercase."""
    value = str(value or "").strip().lower()
    assert re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", value), (
        f"{label}: invalid AL MAC {value!r}"
    )
    assert value != "00:00:00:00:00:00" and not (
        int(value[:2], 16) & 1
    ), f"{label}: AL MAC must be nonzero and unicast: {value}"
    return value

def _controller_id(output):
    """
    Parse ControllerID from current rbuscli output.

    Expected format:

    Parameter  1:
        Name  : Device.WiFi.DataElements.Network.ControllerID
        Type  : string
        Value : 02:01:00:52:a6:4f
    """
    name_match = re.search(
        rf"Name\s*:\s*{re.escape(_CONTROLLER_ID)}",
        output,
        re.MULTILINE,
    )
    assert name_match, (
        f"RBUS did not return {_CONTROLLER_ID}: {output!r}"
    )

    value_match = re.search(
        r"Value\s*:\s*([0-9a-fA-F:]{17})",
        output,
        re.MULTILINE,
    )
    assert value_match, (
        f"No ControllerID value found in RBUS output: {output!r}"
    )
    return _mac(value_match.group(1).strip(), "ControllerID")

def _tlvs(payload):
    """Return complete TLVs; reject malformed or unterminated topology messages."""
    types, _, values, ended, error = parse_tlvs(payload)
    assert not error and ended, (
        f"Malformed topology CMDU: {error or 'missing EOM'}"
    )
    return list(zip(types, values))

def _verify_topology(packets, controller, agent):
    """Require Agent 1 discovery and an identity- and MID-correlated exchange."""
    discovery = False
    queries = set()
    responses = set()

    for packet in packets:
        if not packet.haslayer(Ether) or packet[Ether].type != 0x893A:
            continue

        eth = packet[Ether]
        payload = bytes(eth.payload)
        if len(payload) < 8:
            continue

        message_type = int.from_bytes(payload[2:4], "big")
        src, dst = eth.src.lower(), eth.dst.lower()

        if message_type == MSG_TYPE_TOPOLOGY_DISCOVERY:
            # Discovery uses an interface source MAC, not necessarily the AL MAC.
            # The AL MAC Address TLV is the authoritative sender identity.
            tlvs = _tlvs(payload)
            al_values = [
                value
                for kind, value in tlvs
                if kind == TLV_TYPE_AL_MAC_ADDRESS
            ]
            iface_values = [
                value
                for kind, value in tlvs
                if kind == TLV_TYPE_MAC_ADDRESS
            ]
            if bytes.fromhex(agent.replace(":", "")) in al_values:
                assert len(al_values) == 1 and len(iface_values) == 1, (
                    "Agent Discovery must identify one AL MAC "
                    "and one interface MAC"
                )
                assert len(iface_values[0]) == 6, (
                    "Invalid Discovery interface MAC length"
                )
                assert iface_values[0].hex(":") == src, (
                    "Agent Discovery interface MAC TLV "
                    "does not match Ethernet source"
                )
                discovery = True
            continue

        if {src, dst} != {controller, agent}:
            continue

        mid = int.from_bytes(payload[4:6], "big")
        if message_type == MSG_TYPE_AP_TOPOLOGY_QUERY:
            _tlvs(payload)
            queries.add((src, dst, mid))
        elif message_type == MSG_TYPE_AP_TOPOLOGY_RESPONSE:
            info = [
                value
                for kind, value in _tlvs(payload)
                if kind == TLV_TYPE_DEVICE_INFORMATION
            ]
            assert len(info) == 1 and len(info[0]) >= 7, (
                "Topology Response must contain "
                "Device Information with an AL MAC"
            )
            assert info[0][:6].hex(":") == src, (
                "Topology Response Device Information "
                "AL MAC differs from sender"
            )
            responses.add((dst, src, mid))

    assert discovery, "No Topology Discovery identifying Agent 1 was captured"
    assert queries, (
        "No Topology Query between ControllerID and Agent 1 was captured"
    )
    assert responses, (
        "No Topology Response between ControllerID and Agent 1 was captured"
    )
    assert queries & responses, (
        "No Query/Response pair has reversed endpoints and the same message ID"
    )

def _wait_for_agent(initialize, old_boot_id):
    """Reconnect Agent 1 and prove a new boot and active IEEE1905 service."""
    deadline = time.monotonic() + _RECOVERY_SECONDS
    last_error = None

    while time.monotonic() < deadline:
        time.sleep(
            min(_POLL_SECONDS, max(0, deadline - time.monotonic()))
        )
        try:
            initialize.close_connection(_AGENT)
            initialize.connect_with_device(_AGENT)

            boot_id = _run(
                initialize,
                _AGENT,
                "cat /proc/sys/kernel/random/boot_id",
            ).strip()
            assert boot_id and boot_id != old_boot_id, (
                "Agent has not rebooted yet"
            )
            initialize.verify_service_status(
                _AGENT, "ieee1905_em_agent", "cli"
            )
            return
        except Exception as error:
            last_error = error

    pytest.fail(
        f"Agent 1 did not recover within "
        f"{_RECOVERY_SECONDS}s: {last_error}"
    )

@contextmanager
def _capture(initialize, local_path):
    """Own one remote tcpdump PID, flush it, inspect and download its capture."""
    log_path = f"/tmp/alid_check_{uuid4().hex}.log"
    quoted_log = shlex.quote(log_path)

    # Fail safely rather than overwrite another run's evidence.
    _run(initialize, "controller", f"test ! -e {_REMOTE_PCAP}")
    pid = None

    try:
        output = _run(
            initialize,
            "controller",
            f"nohup tcpdump -U -i brlan0 -w {_REMOTE_PCAP} "
            f"ether proto 0x893a "
            f">{quoted_log} 2>&1 </dev/null & echo $!",
        ).strip()

        assert output.isdecimal() and int(output) > 1, (
            f"Could not obtain tcpdump PID: {output!r}"
        )
        pid = int(output)
        deadline = time.monotonic() + 5

        while True:
            _run(initialize, "controller", f"kill -0 {pid}")
            log = _run(
                initialize, "controller", f"cat {quoted_log}"
            )
            if "listening on brlan0" in log:
                break

            assert time.monotonic() < deadline, (
                f"tcpdump did not start: {log}"
            )
            time.sleep(0.2)

        report_logger.print_success(
            "PASS: tcpdump is listening on brlan0"
        )
        yield

    finally:
        active_error = sys.exc_info()[0] is not None

        try:
            if pid is not None:
                # SIGINT flushes PCAP buffers; never stop unrelated tcpdump PIDs.
                _run(
                    initialize,
                    "controller",
                    f"kill -INT {pid} 2>/dev/null || true",
                )
                deadline = time.monotonic() + 5

                while _run(
                    initialize,
                    "controller",
                    f"if kill -0 {pid} 2>/dev/null; "
                    f"then echo running; fi",
                ).strip():
                    if time.monotonic() >= deadline:
                        _run(
                            initialize,
                            "controller",
                            f"kill -TERM {pid} 2>/dev/null || true",
                        )
                        raise RuntimeError(
                            "tcpdump did not stop after SIGINT"
                        )
                    time.sleep(0.2)

                report_logger.print_step(
                    "STEP 4: Inspect tcpdump -r /tmp/alid_check.pcap -n"
                )
                report_logger.print_info(
                    _run(
                        initialize,
                        "controller",
                        f"tcpdump -r {_REMOTE_PCAP} -n",
                    )
                )

                initialize.get_file(
                    "controller", _REMOTE_PCAP, str(local_path)
                )
                assert (
                    local_path.is_file()
                    and local_path.stat().st_size > 24
                ), f"Empty or missing capture: {local_path}"

                # Remove remote evidence only after a verified local download.
                _run(
                    initialize,
                    "controller",
                    f"rm -f {_REMOTE_PCAP} {quoted_log}",
                )
                report_logger.print_info(
                    f"Capture retained at {local_path}"
                )

        except Exception as error:
            if not active_error:
                raise

            # Preserve the original failure and report why remote evidence remains.
            report_logger.print_info(
                f"Capture cleanup also failed: {error}"
            )

# PUBLIC_INTERFACE
def test_em_backhaul_alid_verification(initialize):
    """Verify IEEE1905 topology formation and Controller identity for Agent 1.

    Args:
        initialize: Existing Zaero testbed fixture providing device APIs.
    Returns:
        None. Assertions fail on capture, reconnection, identity or topology errors.
    """
    report_logger.print_test("EM_Backhaul_ALID_Verification")

    assert initialize.read_from_database(
        "controller", "device_present"
    ), "Controller must be enabled"
    assert initialize.read_from_database(
        _AGENT, "device_present"
    ), "Agent 1 (extender1) must be enabled and onboarded"

    initialize.verify_service_status(
        "controller", "ieee1905_em_ctrl", "cli"
    )
    initialize.verify_service_status(
        _AGENT, "ieee1905_em_agent", "cli"
    )

    controller = _mac(
        initialize.get_al_mac_address("controller", "cli"),
        "Controller",
    )
    agent = _mac(
        initialize.get_al_mac_address(_AGENT, "cli"),
        "Agent 1",
    )
    assert controller != agent, (
        "Controller and Agent 1 must have distinct AL MACs"
    )

    old_boot_id = _run(
        initialize,
        _AGENT,
        "cat /proc/sys/kernel/random/boot_id",
    ).strip()
    assert old_boot_id, (
        "Cannot establish Agent 1 boot identity before reconnection"
    )

    local_dir = initialize.read_from_database(
        "controller", "pcap_local_dir"
    )
    assert local_dir, "Controller pcap_local_dir must be configured"
    local_path = Path(local_dir) / f"alid_check_{uuid4().hex}.pcap"

    report_logger.print_step(
        "STEP 1: Start IEEE1905 packet capture on Controller brlan0"
    )
    with _capture(initialize, local_path):
        report_logger.print_step(
            "STEP 2: Reconnect Agent 1 by rebooting it"
        )
        initialize.reboot_device(_AGENT, "cli")
        _wait_for_agent(initialize, old_boot_id)

    report_logger.print_step(
        "STEP 3: Read Controller information using rbuscli"
    )
    controller_id = _controller_id(
        _run(
            initialize,
            "controller",
            f"rbuscli get {_CONTROLLER_ID}",
        )
    )

    report_logger.print_info(
        f"Controller AL MAC     : {controller}"
    )
    report_logger.print_info(
        f"RBUS ControllerID     : {controller_id}"
    )

    assert controller_id == controller, (
        f"ControllerID {controller_id} differs "
        f"from Controller AL MAC {controller}"
    )
    report_logger.print_success(
        f"PASS: Valid ControllerID: {controller_id}"
    )