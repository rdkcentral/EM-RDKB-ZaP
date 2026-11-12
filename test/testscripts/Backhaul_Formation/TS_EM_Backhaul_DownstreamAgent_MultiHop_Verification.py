# # Copyright 2026 RDK Management
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# # http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.


import math
import re
import shlex
import sys
import time

import pytest

from rdkbmeshzap.common_utils import report_logger as report

_MAC = r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}"

def _settings(api):
    """Read optional case-specific settings from the existing database."""
    settings = api.read_from_database("controller").get("multihop", {})
    assert isinstance(settings, dict), "controller.multihop must be a mapping"
    return settings

def _duration(settings, name, default):
    """Require positive finite durations so polling remains bounded."""
    value = float(settings.get(name, default))
    assert math.isfinite(value) and value > 0, (
        f"Invalid duration {name}: {value}"
    )
    return value

def _run(api, device, command):
    """Execute a Linux-device command using Zaero's stdout/stderr/rc API."""
    out, err, rc = api.execute_command(
        device,
        command,
        return_stderr=True,
        return_rc=True,
    )
    assert rc == 0, (
        f"{device}: {command}\n"
        f"rc={rc}\nstdout={out}\nstderr={err}"
    )
    report.print_info(f"{device}: {command}\n{out or ''}")
    return str(out or "")

def _connect(api, device):
    """Reuse a live SSH connection or establish one using testbed credentials."""
    try:
        alive = api.is_device_alive(device)
    except RuntimeError:
        alive = False

    if not alive:
        api.connect_with_device(device)

    assert api.is_device_alive(device), f"{device}: SSH not ready"

def _interfaces(output):
    """Parse iw dev or iw dev INTERFACE info into interface records."""
    parts = re.split(
        r"(?m)^[ \t]*Interface[ \t]+(\S+)[ \t]*\r?$",
        output,
    )
    records = {}

    for name, block in zip(parts[1::2], parts[2::2]):
        fields = {}
        for key in ("addr", "type", "ssid"):
            match = re.search(
                rf"(?m)^[ \t]*{key}[ \t]+([^\r\n]+)",
                block,
            )
            fields[key] = match.group(1).strip() if match else ""

        fields["addr"] = fields["addr"].lower()
        records[name] = fields

    return records

def _parent(output, ssid):
    """Require an active link to the exact SSID and return its BSSID."""
    mac = re.search(
        rf"(?im)^[ \t]*Connected to ({_MAC})\b",
        output,
    )
    name = re.search(
        r"(?m)^[ \t]*SSID:[ \t]*([^\r\n]*)",
        output,
    )
    assert mac and name, f"No active wireless association:\n{output}"
    assert name.group(1).strip() == ssid, (
        f"Expected SSID {ssid!r}:\n{output}"
    )
    return mac.group(1).lower()

def _reboot_agent1(api, a1, cfg, uplink, ssid):
    """Reboot Agent 1 and wait for a new boot, SSH, and upstream backhaul.

    Args:
        api: Existing Zaero database/device-interface fixture.
        a1: Agent 1 device name from the existing testbed database.
        cfg: Case-specific controller.multihop settings.
        uplink: Existing command used to inspect Agent 1's upstream link.
        ssid: Expected backhaul SSID.

    Returns:
        None. Raises AssertionError if recovery is not observed before the
        polling deadline. Individual SSH/API calls retain their own timeouts.
    """
    timeout = _duration(cfg, "reboot_timeout", 300)
    interval = _duration(cfg, "reboot_poll_interval", 5)
    initial_delay = _duration(cfg, "reboot_initial_delay", 10)
    assert initial_delay < timeout, (
        "reboot_initial_delay must be smaller than reboot_timeout"
    )

    boot_command = "cat /proc/sys/kernel/random/boot_id"
    boot_pattern = (
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
        r"[0-9a-f]{4}-[0-9a-f]{12}"
    )

    def _close_stale_connection():
        """Remove the old SSH alias before another connection attempt."""
        try:
            api.close_connection(a1)
        except Exception as error:
            # Cleanup must not hide the recovery failure or stop retries.
            report.print_info(
                f"{a1}: connection cleanup during reboot: {error}"
            )

    report.print_info(
        f"PREPARATION: Reboot {a1} before tool checks and STEP 1"
    )
    _connect(api, a1)
    boot_before = _run(api, a1, boot_command).strip().lower()
    assert re.fullmatch(boot_pattern, boot_before), (
        f"{a1}: Invalid pre-reboot Linux boot ID: {boot_before!r}"
    )

    deadline = time.monotonic() + timeout
    last_error = "No recovery observation yet"

    try:
        api.reboot_device(a1, method="cli")
    except Exception as error:
        # The asynchronous reboot can disconnect SSH before the API returns.
        # Recovery is accepted only after observing a different boot ID.
        last_error = f"Reboot API returned an error: {error}"
        report.print_info(f"{a1}: {last_error}")
    finally:
        _close_stale_connection()

    time.sleep(min(initial_delay, max(0, deadline - time.monotonic())))

    while time.monotonic() < deadline:
        try:
            _connect(api, a1)
            boot_after = _run(api, a1, boot_command).strip().lower()
            assert re.fullmatch(boot_pattern, boot_after), (
                f"{a1}: Invalid post-reboot Linux boot ID: {boot_after!r}"
            )
            assert boot_after != boot_before, (
                f"{a1}: Linux boot ID has not changed yet"
            )

            parent = _parent(_run(api, a1, uplink), ssid)
            report.print_info(
                f"{a1}: Reboot preparation complete; "
                f"boot ID {boot_before} -> {boot_after}; "
                f"upstream backhaul parent={parent}"
            )
            return
        except Exception as error:
            # Zaero may raise a generic Exception for connection failures.
            # Discard stale aliases so the next retry can reconnect cleanly.
            last_error = f"{type(error).__name__}: {error}"
            report.print_info(
                f"{a1}: Waiting for reboot/SSH/backhaul recovery: "
                f"{last_error}"
            )
            _close_stale_connection()

        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(interval, remaining))

    raise AssertionError(
        f"{a1}: Timed out after {timeout:g}s waiting for a changed Linux "
        f"boot ID, SSH recovery, and upstream backhaul SSID {ssid!r}. "
        f"Last observation: {last_error}"
    )

def _stations(output):
    """Return exact station MACs rather than incidental MAC text."""
    return {
        mac.lower()
        for mac in re.findall(
            rf"(?im)^[ \t]*Station[ \t]+({_MAC})\b",
            output,
        )
    }

def _wait(check, timeout, interval, description):
    """Poll an observation using a monotonic deadline."""
    deadline = time.monotonic() + timeout

    while True:
        result = check()
        if result:
            return result

        remaining = deadline - time.monotonic()
        assert remaining > 0, f"Timed out waiting for {description}"
        time.sleep(min(interval, remaining))

def _learned_ports(output, mac, downstream):
    """Require nonlocal bridge-master learning on a downstream-facing port."""
    ports = set()

    for line in output.lower().splitlines():
        words = line.split()
        if not words or words[0] != mac:
            continue

        # Local/static entries do not establish downstream traffic learning.
        if {"self", "permanent", "static", "local"} & set(words):
            continue
        if "dev" not in words or "master" not in words:
            continue

        index = words.index("dev") + 1
        if index < len(words):
            port = words[index]
            # Some drivers create a per-station port below the backhaul AP.
            if port == downstream or port.startswith(downstream + "."):
                ports.add(port)

    return ports

def _alive(api, device, pid):
    """Treat reaped or zombie capture processes as stopped."""
    state = _run(
        api,
        device,
        f"if kill -0 {pid} 2>/dev/null && "
        f"! grep -q '^State:.*Z' /proc/{pid}/status 2>/dev/null; "
        "then printf running; else printf stopped; fi",
    )
    return state == "running"

def _stop(api, device, pid, path):
    """Flush this capture and forcibly clean up if graceful shutdown fails."""
    if not _alive(api, device, pid):
        return

    # Check the exact output-path argument before signalling a reused PID.
    _run(
        api,
        device,
        f"tr '\\000' '\\n' < /proc/{pid}/cmdline | "
        f"grep -Fxq -- {shlex.quote(path)}",
    )
    _run(api, device, f"kill -INT {pid}")

    try:
        _wait(
            lambda: not _alive(api, device, pid),
            5,
            0.5,
            "tcpdump flush/shutdown",
        )
    except AssertionError:
        _run(api, device, f"kill -KILL {pid} 2>/dev/null || true")
        raise AssertionError(
            "tcpdump required forced termination; pcap may be incomplete"
        )

def _find_sta_interface(api, device, downstream):
    output = _run(api, device, "ip link show")
    match = re.search(
        rf"({re.escape(downstream)}\.sta\d+):",
        output,
    )
    return match.group(1) if match else None

# Local overrides preserve the shared database initialization while allowing
# Agent 2 to remain powered off until capture has started.
@pytest.fixture(scope="session", name="validate_setup_accessibility")
def _case_accessibility(initialize):
    """Connect only devices required before downstream power-on."""
    agent1 = _settings(initialize).get("agent1", "extender1")
    for device in ("controller", agent1):
        _connect(initialize, device)

@pytest.fixture(scope="session", name="update_runtime_database")
def _case_runtime(validate_setup_accessibility):
    """Replace all-agent discovery with the test's explicit iw discovery."""
    return True

@pytest.fixture(scope="session", name="verify_test_environment")
def _case_environment(update_runtime_database):
    """Use case-specific checks rather than requiring every agent online."""
    return True

@pytest.fixture(name="test_setup")
def _case_setup(verify_test_environment):
    """Avoid browser setup for this shell-only test."""
    yield

@pytest.fixture(name="protocol_validation")
def _case_protocol_validation():
    """Use Agent 1's unfiltered capture instead of a controller-only filter."""
    yield

# PUBLIC_INTERFACE
def test_em_backhaul_downstreamagent_multihop_verification(initialize):
    """Run twelve multi-hop observation and verification steps.

    Args:
        initialize: Existing Zaero database/device-interface fixture.

    Returns:
        None. Assertions report missing evidence or failed commands.
        Agent 2 physical power-on remains an external lab action at Step 5.
        Disabled checks remain disabled; success logs describe active checks.
    """
    api = initialize
    cfg = _settings(api)

    a1 = str(cfg.get("agent1", "extender1"))
    a2 = str(cfg.get("agent2", "extender2"))
    assert len({"controller", a1, a2}) == 3, "Device names must be distinct"

    upstream = str(cfg.get("upstream_interface", "wifi1.3"))
    downstream = str(cfg.get("downstream_interface", "wifi1.1"))
    sta = str(cfg.get("agent2_interface", "wifi1.3"))
    path = str(cfg.get("capture_path", "/tmp/multihop_check.pcap"))

    assert path.startswith("/") and "\n" not in path, (
        "Use an absolute remote pcap path"
    )
    qpath = shlex.quote(path)
    qlog = shlex.quote(path + ".tcpdump.log")

    ssid = api.read_from_database("controller", "mesh_backhaul_ssid")
    assert isinstance(ssid, str) and ssid.strip(), (
        "Configure controller.mesh_backhaul_ssid"
    )
    ssid = ssid.strip()

    timeout = _duration(cfg, "onboarding_timeout", 300)
    interval = _duration(cfg, "poll_interval", 2)
    fdb_timeout = _duration(cfg, "fdb_timeout", 60)
    ssh_delay = _duration(cfg, "ssh_ready_delay", 60)
    observation = _duration(cfg, "observation_seconds", 15)

    uplink = f"iw dev {shlex.quote(upstream)} link"
    link2 = f"iw dev {shlex.quote(sta)} link"
    stations = f"iw dev {shlex.quote(downstream)} station dump"

    report.print_test("EM_Backhaul_DownstreamAgent_MultiHop_Verification")
    report.print_info(
        "Precondition: Agent 2 OFF; Agents 3/4 off/reset and isolated. "
        "Physical power state is externally managed, not inferred from SSH."
    )

    _reboot_agent1(api, a1, cfg, uplink, ssid)
    _wait(
        lambda: (
            downstream in _interfaces(_run(api, a1, "iw dev"))
            and _interfaces(_run(api, a1, "iw dev"))[downstream]["ssid"]
            == ssid
        ),
        120,
        5,
        "downstream AP interface readiness",
    )

    for tool in ("iw", "bridge", "tcpdump", "nohup", "grep", "tr"):
        _run(api, a1, f"command -v {tool}")

    report.print_success(
        f"PASS: PREPARATION: {a1} reboot recovery, downstream interface "
        "readiness, and required tool checks completed"
    )

    report.print_step("STEP 1: Verify Agent 1 upstream backhaul")
    parent1 = _parent(_run(api, a1, uplink), ssid)

    controller = _interfaces(_run(api, "controller", "iw dev"))
    controller_bssids = {
        record["addr"]
        for record in controller.values()
        if record["type"] == "AP" and record["ssid"] == ssid
    }
    assert parent1 in controller_bssids, (
        f"Agent 1 parent {parent1} is not a Controller backhaul AP: "
        f"{controller_bssids}"
    )
    report.print_success(
        f"PASS: STEP 1: {a1} is associated with Controller "
        f"backhaul AP {parent1} on SSID {ssid!r}"
    )

    report.print_step("STEP 2: Identify downstream backhaul AP")
    interfaces = _interfaces(_run(api, a1, "iw dev"))
    assert downstream in interfaces, (
        f"Missing downstream interface: {interfaces}"
    )

    ap = interfaces[downstream]
    assert ap["type"] == "AP" and ap["ssid"] == ssid, (
        f"Invalid backhaul AP: {ap}"
    )
    bssid = ap["addr"]
    assert re.fullmatch(_MAC, bssid), f"Invalid AP BSSID: {bssid}"
    assert bssid not in controller_bssids, (
        "Agent 1 and Controller backhaul BSSIDs overlap"
    )
    report.print_success(
        f"PASS: STEP 2: Downstream AP {downstream} has BSSID "
        f"{bssid} and SSID {ssid!r}, distinct from Controller BSSIDs"
    )

    report.print_step("STEP 3: Check existing downstream topology")
    existing_sta = _find_sta_interface(api, a1, downstream)

    if existing_sta:
        report.print_info(
            f"Existing STA interface found: {existing_sta}"
        )
    else:
        report.print_info("No downstream STA interface present")

    report.print_success(
        "PASS: STEP 3: Downstream topology observation completed; "
        f"existing station interface={existing_sta or 'none'}. "
        "No-station isolation was not asserted"
    )

    _run(api, a1, f"rm -f {qpath} {qlog}")

    pid = None
    try:
        report.print_step("STEP 4: Start downstream packet capture")
        output = _run(
            api,
            a1,
            f"nohup tcpdump -U -s 0 -i {shlex.quote(downstream)} "
            f"-w {qpath} > {qlog} 2>&1 < /dev/null & echo $!",
        )
        assert output.strip().isdigit(), (
            f"Invalid capture PID: {output!r}"
        )
        pid = int(output.strip())
        assert pid > 1, "Unsafe capture PID"

        def _ready():
            """Require a live tcpdump and its listening confirmation."""
            assert _alive(api, a1, pid), (
                f"tcpdump exited; inspect {path}.tcpdump.log"
            )
            return _run(
                api,
                a1,
                f"if grep -Fq 'listening on' {qlog}; "
                "then printf READY; else printf WAIT; fi",
            ) == "READY"

        _wait(_ready, 5, 0.5, "capture readiness")
        report.print_success(
            f"PASS: STEP 4: tcpdump PID {pid} is running and "
            f"listening on {a1}:{downstream}"
        )

        report.print_step(
            "STEP 5 READY: Power on Agent 2 externally now"
        )
        sta_if = _wait(
            lambda: _find_sta_interface(api, a1, downstream),
            timeout,
            interval,
            "downstream association after Agent 2 power-on",
        )
        assert sta_if, "No downstream station interface detected"
        report.print_info(
            f"Detected downstream station interface: {sta_if}"
        )

        # Association may precede availability of Agent 2's management shell.
        time.sleep(ssh_delay)
        report.print_info(
            f"Extender2 IP: {api.read_from_database(a2, 'login_ip')}"
        )
        report.print_info(
            f"Tunnel Device: "
            f"{api.read_from_database(a2, 'tunnel_device')}"
        )
        report.print_info(
            f"SSH Tunnel: {api.read_from_database(a2, 'ssh_tunnel')}"
        )

        _connect(api, a2)
        _run(api, a2, "command -v iw")
        report.print_success(
            f"PASS: STEP 5: Downstream station interface {sta_if} "
            f"detected; {a2} SSH and iw availability verified. "
            "Agent identity and parent are checked in STEP 6"
        )

        report.print_step(
            "STEP 6: Verify Agent 2 association to Agent 1 BSSID"
        )
        assert _parent(_run(api, a2, link2), ssid) == bssid, (
            "Agent 2 has the wrong parent"
        )

        info = _interfaces(
            _run(api, a2, f"iw dev {shlex.quote(sta)} info")
        )
        assert sta in info and info[sta]["type"] == "managed", (
            f"Invalid Agent 2 station interface: {info}"
        )
        mac2 = info[sta]["addr"]
        assert re.fullmatch(_MAC, mac2), (
            f"Invalid Agent 2 station MAC: {mac2}"
        )

        report.print_info(
            f"Downstream station interface detected: {sta_if}"
        )
        report.print_success(
            f"PASS: STEP 6: {a2} managed interface {sta}, MAC {mac2}, "
            f"is associated with {a1} BSSID {bssid} on SSID {ssid!r}"
        )

        report.print_step(
            "STEP 7: Verify dynamic downstream bridge learning"
        )

        def _fdb():
            """Observe the AP or its driver-created per-station port."""
            return _learned_ports(
                _run(api, a1, "bridge fdb show"),
                mac2,
                downstream,
            )

        ports = _wait(
            _fdb,
            fdb_timeout,
            interval,
            "Agent 2 dynamic downstream FDB entry",
        )
        time.sleep(observation)
        assert _alive(api, a1, pid), "tcpdump stopped unexpectedly"
        report.print_success(
            f"PASS: STEP 7: Dynamic FDB learning for {mac2} observed "
            f"on downstream ports {sorted(ports)}; "
            f"capture remained active during the {observation:g}s observation"
        )

        report.print_step("STEP 8: Stop capture and verify file")
        _stop(api, a1, pid, path)
        pid = None
        _run(api, a1, f"test -s {qpath}")
        report.print_success(
            f"PASS: STEP 8: Capture process stopped; "
            f"nonempty capture file verified at {a1}:{path}"
        )

        read = f"tcpdump -e -nn -vvv -r {qpath}"

        report.print_step(
            "STEP 9: Verify IEEE1905 traffic on the downstream link"
        )
        ieee = _run(
            api,
            a1,
            f"{read} " + shlex.quote("ether proto 0x893a"),
        )
        assert re.search(
            rf"(?i)\b{_MAC}\s*>\s*{_MAC}\b",
            ieee,
        ), "No IEEE1905 frame was captured"
        report.print_success(
            "PASS: STEP 9: IEEE1905 Ethernet traffic "
            "(EtherType 0x893a) found in the downstream capture"
        )

        # IEEE1905 can use the AL MAC instead of the wireless station MAC.
        # Do not incorrectly require those two identities to be equal.
        report.print_step(
            "STEP 10: Verify Agent 2 EAPOL key messages"
        )
        eapol = _run(
            api,
            a1,
            f"{read} "
            + shlex.quote(f"ether proto 0x888e and ether host {mac2}"),
        )
        assert re.search(
            r"(?i)\bEAPOL(?:[- ]+)?key\b",
            eapol,
        ), (
            "No Agent 2 EAPOL-Key message. Power on only after capture "
            "readiness; the driver must expose EAPOL on this interface."
        )
        report.print_success(
            f"PASS: STEP 10: EAPOL-Key traffic involving "
            f"Agent 2 MAC {mac2} found in the capture"
        )

        report.print_step(
            "STEP 11: Verify Agent 2 source MAC activity"
        )
        activity = _run(
            api,
            a1,
            f"{read} " + shlex.quote(f"ether host {mac2}"),
        )
        assert re.search(
            rf"(?i)\b{re.escape(mac2)}\s*>\s*{_MAC}\b",
            activity,
        ), "No traffic sourced by Agent 2"

        report.print_success(
            f"PASS: STEP 11: Traffic sourced by Agent 2 MAC {mac2} "
            "found in the capture. Reverse-direction traffic was not asserted"
        )

        report.print_step(
            "STEP 12: Correlate and recheck the complete multi-hop path"
        )
        assert _parent(_run(api, a1, uplink), ssid) == parent1, (
            "Agent 1 upstream changed"
        )
        assert _parent(_run(api, a2, link2), ssid) == bssid, (
            "Agent 2 parent changed"
        )

        sta_if_check = _find_sta_interface(api, a1, downstream)
        assert sta_if_check, (
            "Downstream station interface disappeared"
        )
        report.print_info(
            f"Verified downstream station interface: {sta_if_check}"
        )

        assert _fdb(), "Agent 2 dynamic FDB learning disappeared"
        report.print_success(
            "PASS: STEP 12: Agent 1 upstream parent and Agent 2 parent "
            "remain unchanged; downstream station interface and "
            "Agent 2 dynamic FDB learning remain present"
        )

        report.print_success(
            f"PASS: Active multi-hop checks completed: "
            f"Controller ({parent1}) <-> {a1} ({bssid}) <-> "
            f"{a2} ({mac2}); FDB ports={sorted(ports)}; "
            f"IEEE1905/EAPOL-Key/source-MAC evidence={a1}:{path}"
        )
    finally:
        if pid is not None:
            failing = sys.exc_info()[0] is not None
            try:
                _stop(api, a1, pid, path)
            except Exception as error:
                if not failing:
                    raise
                report.print_error(
                    f"Capture cleanup also failed: {error}"
                )

        report.print_info(
            f"Evidence retained on {a1}: "
            f"{path}, {path}.tcpdump.log"
        )