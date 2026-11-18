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

import calendar
import re
import time
from collections import Counter
from scapy.all import Ether
from packet_analyzer.ieee1905_utils import MSG_TYPE_TOPOLOGY_DISCOVERY, MSG_TYPE_AP_AUTOCONFIG_SEARCH, MSG_TYPE_AP_AUTOCONFIGURATION_RESPONSE, MSG_TYPE_AP_AUTOCONFIGURATION_WSC, MSG_TYPE_AP_TOPOLOGY_QUERY, MSG_TYPE_AP_TOPOLOGY_RESPONSE
from packet_analyzer.message_verify import get_message_type_name
from packet_analyzer.packet_dissector import check_message_presence
from rdkbmeshzap.common_utils import report_logger

# Settings shared by the Backhaul_Formation test scripts.
MAC_PATTERN = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$", re.IGNORECASE)

# Linktype test settings.
# Time (seconds) to keep capturing so the IEEE 1905 messages can be collected (test plan: 60 seconds).
ONBOARDING_SETTLE_SECONDS = 60
# Maximum time (seconds) to wait for the wireless backhaul to be connected after the agent has recovered.
ONBOARDING_TIMEOUT_SECONDS = 240
# Interval (seconds) between consecutive status checks.
POLL_INTERVAL_SECONDS = 10
# Number of ICMP echo requests sent to the agent from the controller (test plan: ping <agent_ip>).
PING_COUNT = "3"

# Invalid credentials test settings.
# Agent under test. None selects the first enabled extender from infra.yaml.
AGENT = None
# File on the agent that holds the provisioned backhaul credentials (Backhaul_SSID / Backhaul_KeyPassphrase).
AGENT_BACKHAUL_CONFIG = "/nvram/EasymeshCfg.json"
# Copy of the original file, kept on the agent so the valid credentials can be restored manually after the test.
AGENT_BACKHAUL_CONFIG_BACKUP = "/nvram/EasymeshCfg.json.tc10.bak"
# Deliberately wrong backhaul passphrase. It must not contain the characters / & \ (used inside a sed expression).
INVALID_PASSPHRASE = "InvalidBackhaulPassphrase_TC10"
# Command that applies the restored configuration; used only in the manual restore instructions (plan: reboot the Agent).
AGENT_RESTART_COMMAND = "reboot"
# Time (seconds) to let the agent reboot and attempt the backhaul with the invalid credentials before the observation.
APPLY_SETTLE_SECONDS = 180
# Maximum time (seconds) after the reboot request to detect that the old backhaul session is gone (agent unreachable).
LINK_DOWN_TIMEOUT_SECONDS = 120
# Controller OneWifi HAL logs (wifiHal.txt); they record every auth frame received from a station, so the agent backhaul STA attempts show up there.
CONTROLLER_WIFI_LOG_GLOB = "/rdklogs/logs/wifiHal.txt*"
# Leading timestamp formats of the controller wifiHal log lines: (regex with the timestamp in group 1, time.strptime format). Lines without one cannot be tracked.
WIFI_LOG_TIMESTAMP_FORMATS = ((r"^(\d{6}-\d{2}:\d{2}:\d{2})", "%y%m%d-%H:%M:%S"), (r"^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})", "%Y-%m-%d %H:%M:%S"))
# Controller log lines that mention the agent backhaul MAC together with an explicit WPA rejection / unauthorized state (deauth/disassoc, a handshake/auth/assoc line with failure or timeout wording, wrong key, MIC failure, or a nonzero status code); tune it to the wording of the platform log.
WPA_REJECTION_PATTERN = r"deauth|disassoc|(4-?way|handshake|auth(entication)?|assoc(iation)?)\b.*(fail|reject|denied|time(d)? ?out)|(wrong|incorrect) (key|pass)|mic (failure|fail)|unauthori[sz]ed|status[ _]?code\s*[=:]?\s*[1-9]\d*"
# Controller reply that rejects the agent: the OneWifi HAL logs the auth frame it sends to the agent with a status code ("sc"); a nonzero sc in the seq:2 reply (e.g. "send auth frame from:<bssid> to:<agent mac> alg:3 seq:2 sc:15") is a rejected authentication. {mac} is replaced by the escaped agent backhaul MAC. The seq:1 commit codes (e.g. sc:126) and the agent's own frames are not matched.
WPA_AUTH_REJECT_TEMPLATE = r"send auth frame from:\S+ to:{mac}\b.*\bseq:2\s+sc:(?!0\b)\d+"
# Lines that report success are never rejection evidence (e.g. "pairwise key handshake completed", status_code=0), even if they also contain a rejection keyword.
WPA_SUCCESS_PATTERN = r"\b(completed|succeeded|success|successful(ly)?)\b|status[ _]?code\s*[=:]?\s*0\b"
# Lines that show the agent completed the WPA handshake / reached the authorized state. With invalid credentials this must never happen: it means the passphrase was accepted, so it fails the test (never discard these lines).
WPA_HANDSHAKE_COMPLETED_PATTERN = r"(4-?way|pairwise|handshake|\bptk\b|\bgtk\b)\b.*\b(complete[d]?|success(ful(ly)?)?|established|done)\b|\bport (is )?authori[sz]ed\b|\bstate\s*[=:]?\s*authori[sz]ed\b"
WPA_HANDSHAKE_NEGATION_PATTERN = r"\b(not|never|fail(ed|ure)?|unsuccessful)\b"
# Tolerance (seconds) applied before the link-down time when looking for completed handshakes (log timestamps have 1 s resolution).
COMPLETION_START_TOLERANCE_SECONDS = 1.0
# Time (seconds) during which the agent must NOT form the backhaul with the invalid credentials.
OBSERVATION_SECONDS = 240
# Interval (seconds) between the samples taken during the observation window.
OBSERVATION_POLL_INTERVAL_SECONDS = 30
# Number of ICMP echo requests sent to the agent from the controller during the observation window.
OBSERVATION_PING_COUNT = "2"
# Onboarding related CMDUs. With invalid credentials the first ones may still be exchanged (partial onboarding) while
# the agent is going down for the reboot. They are informational evidence only; onboarding
# is considered completed only by the AP Autoconfiguration WSC sent by the controller to the agent.
ONBOARDING_MESSAGE_TYPES = (MSG_TYPE_AP_AUTOCONFIG_SEARCH, MSG_TYPE_AP_AUTOCONFIGURATION_RESPONSE, MSG_TYPE_AP_AUTOCONFIGURATION_WSC)

def wait_until(check, timeout=ONBOARDING_TIMEOUT_SECONDS):
    """
    Syntax: wait_until(check, timeout)
    Description: Poll check() every POLL_INTERVAL_SECONDS until it returns a truthy value or the timeout expires.
        Exceptions raised by check() are treated as "not ready yet".
    Parameters:
        check : Callable evaluated on every poll.
        timeout : Maximum time in seconds to wait.
    Return Value: True when check() succeeded in time; otherwise False.
    Example: wait_until(lambda: initialize.get_wireless_backhaul_connection_status(agent, iface))
    """
    deadline = time.monotonic() + timeout
    while True:
        try:
            if check():
                return True
        except Exception as error:
            report_logger.print_info(f"INFO: Not ready yet: {error}")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))

def last_line(text):
    """
    Syntax: last_line(text)
    Description: Return the last non-empty line of text.
    Parameters:
        text : Command output.
    Return Value: The stripped last non-empty line, or an empty string.
    Example: last_line(ssh_exec(initialize, "extender1", "grep -c key file"))
    """
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    return lines[-1] if lines else ""

def ssh_exec(initialize, device, command):
    """
    Syntax: ssh_exec(initialize, device, command)
    Description: Run a command on a device over its framework connection.
        Uses the same API as rdkbmeshzap/cli/feature_interface_cli.py: execute_command(device, command, return_stderr=True).
        stderr is only logged, so callers that check the last output line are not affected by it.
    Parameters:
        initialize : Testbed interface.
        device : Device name.
        command : Shell command to run.
    Return Value: The command stdout as a string.
    Example: ssh_exec(initialize, "controller", "date +%s")
    """
    connection = initialize.read_from_database(device, "connection")
    connection_obj = initialize.get_connection_module_object(connection)
    output, error = connection_obj.execute_command(device, command, return_stderr=True)
    if error and str(error).strip():
        report_logger.print_info(f"INFO: stderr of '{command}' on {device}: {str(error).strip()}")
    return str(output or "")

def ping_from_controller(initialize, dst_ip, count):
    """
    Syntax: ping_from_controller(initialize, dst_ip, count)
    Description: Ping dst_ip from the controller and return the packet loss. initialize.ping_ipv4 cannot be used for the
        controller: it loads zaero.<platform> and the controller platform is rdkbmeshzap, which is not a zaero module.
    Parameters:
        initialize : Testbed interface.
        dst_ip : Destination IPv4 address.
        count : Number of ICMP echo requests.
    Return Value: Packet loss in percent as a float. Raises ValueError when the loss is not in the output.
    Example: ping_from_controller(initialize, agent_ip, PING_COUNT)
    """
    output = ssh_exec(initialize, "controller", f"ping -4 -c {count} -W 2 {dst_ip}")
    match = re.search(r"(\d+(?:\.\d+)?)% packet loss", output)
    if not match:
        raise ValueError(f"packet loss not found in the ping output: {output.strip()!r}")
    return float(match.group(1))

def get_fdb_ports(initialize, agent, mac):
    """
    Syntax: get_fdb_ports(initialize, agent, mac)
    Description: Find the bridge ports on which the agent bridge has learned mac (bridge fdb show).
        The port that leads to the controller is the agent's backhaul, so its type gives the backhaul link type.
    Parameters:
        initialize : Testbed interface.
        agent : Agent device name.
        mac : MAC address to look up.
    Return Value: Tuple (ports, output) with the learned ports and the raw command output.
    Example: get_fdb_ports(initialize, "extender1", controller_al_mac)
    """
    output = ssh_exec(initialize, agent, f"bridge fdb show | grep -i '{mac}'")
    ports = []
    for line in output.splitlines():
        if line.lower().startswith(mac.lower()):
            port_match = re.search(r"\bdev\s+(\S+)", line)
            if port_match and port_match.group(1) not in ports:
                ports.append(port_match.group(1))
    return ports, output

def wait_for_fdb_ports(initialize, agent, mac, timeout):
    """
    Syntax: wait_for_fdb_ports(initialize, agent, mac, timeout)
    Description: Wait until the agent bridge has learned mac on at least one port (bridge fdb show).
    Parameters:
        initialize : Testbed interface.
        agent : Agent device name.
        mac : MAC address to look up.
        timeout : Maximum time in seconds to wait.
    Return Value: Tuple (ports, output) of the last lookup; ports is empty when mac was not learned within timeout.
    Example: wait_for_fdb_ports(initialize, agent, controller_al_mac, ONBOARDING_SETTLE_SECONDS * 2)
    """
    result = {"ports": [], "output": ""}
    def learned():
        result["ports"], result["output"] = get_fdb_ports(initialize, agent, mac)
        return bool(result["ports"])
    wait_until(learned, timeout)
    return result["ports"], result["output"]

def get_controller_epoch(initialize):
    """
    Syntax: get_controller_epoch(initialize)
    Description: Read the current time (epoch seconds) on the controller. The capture is taken on the controller, so its
        packet timestamps are on the same clock; using it avoids any clock offset between the test host and the controller.
    Parameters:
        initialize : Testbed interface.
    Return Value: Controller epoch time as a float.
    Example: get_controller_epoch(initialize)
    """
    try:
        return float(initialize.get_time_stamp("controller"))
    except Exception:
        report_logger.print_info("INFO: initialize.get_time_stamp is not available on the controller; reading the time with date")
    output = last_line(ssh_exec(initialize, "controller", "date +%s.%N"))
    if not re.match(r"^\d+\.\d+$", output):
        output = last_line(ssh_exec(initialize, "controller", "date +%s"))
    return float(output)

def wait_for_agent_link_down(initialize, agent_ip):
    """
    Syntax: wait_for_agent_link_down(initialize, agent_ip)
    Description: Confirm the reboot/link-down boundary after a non-blocking reboot request: poll the agent from the
        controller until a ping gets no reply. The controller epoch taken just before that failed ping is returned, so
        the old session (valid credentials) is before it and everything after it belongs to the new boot.
    Parameters:
        initialize : Testbed interface.
        agent_ip : Agent IP address.
    Return Value: Controller epoch of the confirmed link-down, or None when the agent did not become unreachable within LINK_DOWN_TIMEOUT_SECONDS.
    Example: wait_for_agent_link_down(initialize, agent_ip)
    """
    down = {}
    def unreachable():
        checked_at = get_controller_epoch(initialize)
        if ping_from_controller(initialize, agent_ip, OBSERVATION_PING_COUNT) >= 100.0:
            down["at"] = checked_at
        return "at" in down
    wait_until(unreachable, LINK_DOWN_TIMEOUT_SECONDS)
    return down.get("at")

def get_1905_sender_al_mac(payload, default_src):
    """
    Syntax: get_1905_sender_al_mac(payload, default_src)
    Description: Return the IEEE 1905 sender AL MAC of a CMDU. The AL MAC address TLV (type 0x01, 6-byte value) that follows
        the 8-byte CMDU header is used when present (Topology Discovery carries it). Otherwise the Ethernet source address is
        returned, which is only correct when the sender uses its AL MAC as the source.
    Parameters:
        payload : Ethernet payload (CMDU bytes, starting with the CMDU header).
        default_src : Ethernet source address used as fallback.
    Return Value: Lower case MAC address string.
    Example: get_1905_sender_al_mac(bytes(eth.payload), eth.src)
    """
    data = bytes(payload)
    offset = 8
    while offset + 3 <= len(data):
        tlv_type = data[offset]
        tlv_length = (data[offset + 1] << 8) | data[offset + 2]
        if tlv_type == 0x00:
            break
        if tlv_type == 0x01 and tlv_length == 6 and offset + 3 + 6 <= len(data):
            return ":".join(f"{b:02x}" for b in data[offset + 3:offset + 9])
        offset += 3 + tlv_length
    return str(default_src).lower()

def get_agent_1905_messages(packets, agent_al_mac, observation_start, observation_end=None):
    """
    Syntax: get_agent_1905_messages(packets, agent_al_mac, observation_start, observation_end)
    Description: Collect the IEEE 1905 messages sent by or addressed to the agent AL MAC, split at observation_start
        (controller epoch). Packets after observation_end (controller epoch, when given) are ignored.
    Parameters:
        packets : Reassembled capture packets.
        agent_al_mac : Agent AL MAC address.
        observation_start : Controller epoch at which the observation window starts.
        observation_end : Controller epoch at which the observation window ends, or None.
    Return Value: Tuple (before_observation, during_observation); every entry is (message_type, sent_by_agent, timestamp).
    Example: get_agent_1905_messages(packets, agent_al_mac, observation_start, observation_end)
    """
    agent_mac = agent_al_mac.lower()
    before, during = [], []
    for pkt in packets:
        if not pkt.haslayer(Ether):
            continue
        eth = pkt[Ether]
        payload = bytes(eth.payload)
        from_agent = get_1905_sender_al_mac(payload, eth.src) == agent_mac
        if not from_agent and eth.dst.lower() != agent_mac:
            continue
        if len(payload) < 4:
            continue
        entry = ((payload[2] << 8) | payload[3], from_agent, float(pkt.time))
        if observation_end is not None and entry[2] > observation_end:
            continue
        (during if entry[2] >= observation_start else before).append(entry)
    return before, during

def describe_messages(entries):
    """
    Syntax: describe_messages(entries)
    Description: Describe IEEE 1905 message entries as 'Message name (direction) xcount'.
    Parameters:
        entries : Entries returned by get_agent_1905_messages.
    Return Value: Compact description string, or "none".
    Example: describe_messages(during)
    """
    counts = Counter((get_message_type_name(message_type), "agent->controller" if from_agent else "controller->agent") for message_type, from_agent, _ in entries)
    return "; ".join(f"{name} ({direction}) x{count}" for (name, direction), count in sorted(counts.items())) or "none"

def verify_onboarding_message_order(agent, agent_al_mac, packets, reboot_requested_at):
    """
    Syntax: verify_onboarding_message_order(agent, agent_al_mac, packets, reboot_requested_at)
    Description: Plan check: the Topology Discovery and AP Autoconfiguration Search messages of the agent are followed by the
        Topology Query/Response exchange, i.e. the first Topology Response is not earlier than the first Topology Discovery
        and the first AP Autoconfiguration Search of the agent. Only the current reboot/onboarding attempt is validated:
        messages before reboot_requested_at (e.g. a routine Topology Response while the agent was still connected) are ignored.
    Parameters:
        agent : Agent device name.
        agent_al_mac : Agent AL MAC address.
        packets : Reassembled capture packets.
        reboot_requested_at : Controller epoch (get_controller_epoch) taken just before the reboot request.
    Return Value: None. Results are reported through report_logger.
    Example: verify_onboarding_message_order(agent, agent_al_mac, packets, reboot_requested_at)
    """
    _, entries = get_agent_1905_messages(packets, agent_al_mac, reboot_requested_at)
    first = lambda message_type: min((entry[2] for entry in entries if entry[0] == message_type and entry[1]), default=None)
    discovery, search, response = first(MSG_TYPE_TOPOLOGY_DISCOVERY), first(MSG_TYPE_AP_AUTOCONFIG_SEARCH), first(MSG_TYPE_AP_TOPOLOGY_RESPONSE)
    if None in (discovery, search, response):
        report_logger.print_error(f"FAIL: The message order for {agent} cannot be verified; Topology Discovery, AP Autoconfiguration Search or Topology Response is missing")
    elif response >= discovery and response >= search:
        report_logger.print_success(f"PASS: Topology Discovery and AP Autoconfiguration Search of {agent} are followed by the Topology Query/Response exchange")
    else:
        report_logger.print_error(f"FAIL: The Topology Response of {agent} was seen before its Topology Discovery or AP Autoconfiguration Search")

def verify_topology_exchange(agent, agent_al_mac, controller_al_mac, packets):
    """
    Syntax: verify_topology_exchange(agent, agent_al_mac, controller_al_mac, packets)
    Description: Plan check: a Topology Query/Response exchange between the controller and the agent is completed, i.e. at
        least one Topology Response has the same CMDU message ID as a Topology Query, reversed endpoints (the response goes
        back to the sender of the query) and is not earlier than the query. Retried queries and unrelated responses
        do not count.
    Parameters:
        agent : Agent device name.
        agent_al_mac : Agent AL MAC address.
        controller_al_mac : Controller AL MAC address.
        packets : Reassembled capture packets.
    Return Value: None. Results are reported through report_logger.
    Example: verify_topology_exchange(agent, agent_al_mac, controller_al_mac, packets)
    """
    peers = {agent_al_mac.lower(), controller_al_mac.lower()}
    queries, responses = [], []
    for pkt in packets:
        if not pkt.haslayer(Ether):
            continue
        eth = pkt[Ether]
        payload = bytes(eth.payload)
        sender = get_1905_sender_al_mac(payload, eth.src)
        if len(payload) < 6 or {sender, eth.dst.lower()} != peers:
            continue
        entry = (sender, eth.dst.lower(), (payload[4] << 8) | payload[5], float(pkt.time))
        message_type = (payload[2] << 8) | payload[3]
        if message_type == MSG_TYPE_AP_TOPOLOGY_QUERY:
            queries.append(entry)
        elif message_type == MSG_TYPE_AP_TOPOLOGY_RESPONSE:
            responses.append(entry)
    completed = [(q, r) for q in queries for r in responses if r[2] == q[2] and r[0] == q[1] and r[1] == q[0] and r[3] >= q[3]]
    if completed:
        report_logger.print_success(f"PASS: Topology Query/Response exchange completed for {agent} (AL MAC {agent_al_mac}); message ID 0x{completed[0][0][2]:04x}, queries: {len(queries)}, responses: {len(responses)}")
    else:
        report_logger.print_error(f"FAIL: No completed Topology Query/Response exchange (same message ID, reversed endpoints, response not before query) observed for {agent} (AL MAC {agent_al_mac}); queries: {len(queries)}, responses: {len(responses)}")

def collect_ping_samples(initialize, agent, agent_ip):
    """
    Syntax: collect_ping_samples(initialize, agent, agent_ip)
    Description: Observation window: every OBSERVATION_POLL_INTERVAL_SECONDS, for OBSERVATION_SECONDS, sample from the
        controller whether the agent answers a ping. The controller station dump / station count is not used: on this
        platform it is not refreshed when an agent leaves (stale entries stay until the controller reboots).
        Nothing is judged here.
    Parameters:
        initialize : Testbed interface.
        agent : Agent device name.
        agent_ip : Agent IP address.
    Return Value: List of sample dicts with the keys poll, elapsed, reachable and ping_output.
    Example: collect_ping_samples(initialize, "extender1", agent_ip)
    """
    samples = []
    started = time.monotonic()
    deadline = started + OBSERVATION_SECONDS
    while True:
        sample = {"poll": len(samples) + 1, "elapsed": time.monotonic() - started}
        try:
            loss = ping_from_controller(initialize, agent_ip, OBSERVATION_PING_COUNT)
            sample["reachable"], sample["ping_output"] = loss < 100.0, f"packet loss: {loss}%"
        except Exception as error:
            sample["reachable"], sample["ping_output"] = None, f"ping could not be evaluated: {error}"
        samples.append(sample)
        report_logger.print_info(f"INFO: Poll {sample['poll']} (+{sample['elapsed']:.0f}s): {agent} reachable from the controller: {sample['reachable']}")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return samples
        time.sleep(min(OBSERVATION_POLL_INTERVAL_SECONDS, remaining))

def verify_agent_not_reachable(agent, agent_ip, samples):
    """
    Syntax: verify_agent_not_reachable(agent, agent_ip, samples)
    Description: Plan check: the agent is not reachable from the controller (every sample, including the final one).
    Parameters:
        agent : Agent device name.
        agent_ip : Agent IP address.
        samples : Samples returned by collect_ping_samples.
    Return Value: None. Results are reported through report_logger.
    Example: verify_agent_not_reachable(agent, agent_ip, samples)
    """
    reachable_polls = [s for s in samples if s["reachable"]]
    unevaluated_polls = [s for s in samples if s["reachable"] is None]
    for sample in unevaluated_polls:
        report_logger.print_error(f"FAIL: Poll {sample['poll']}: ping from the Controller to {agent} ({agent_ip}) could not be evaluated: {sample['ping_output']}")
    for sample in reachable_polls:
        report_logger.print_error(f"FAIL: Poll {sample['poll']}: {agent} ({agent_ip}) is reachable from the Controller although its backhaul credentials are invalid:\n{sample['ping_output']}")
    if reachable_polls:
        report_logger.print_error(f"FAIL: {agent} is reachable from the Controller in {len(reachable_polls)} of {len(samples)} polls; the backhaul link must not form with invalid credentials")
    elif not unevaluated_polls:
        report_logger.print_success(f"PASS: {agent} ({agent_ip}) is not reachable from the Controller in all {len(samples)} polls over {OBSERVATION_SECONDS}s")

def get_agent_backhaul_mac(initialize, agent, backhaul_iface):
    """
    Syntax: get_agent_backhaul_mac(initialize, agent, backhaul_iface)
    Description: Read the MAC address of the agent backhaul STA interface (the address it uses to associate with the controller).
    Parameters:
        initialize : Testbed interface.
        agent : Agent device name.
        backhaul_iface : Agent backhaul interface name.
    Return Value: Lower case MAC address, or None when it cannot be read.
    Example: get_agent_backhaul_mac(initialize, "extender1", backhaul_iface)
    """
    mac = last_line(ssh_exec(initialize, agent, f"cat /sys/class/net/{backhaul_iface}/address")).lower()
    return mac if MAC_PATTERN.match(mac) else None

def get_controller_utc_offset(initialize):
    """
    Syntax: get_controller_utc_offset(initialize)
    Description: Read the controller UTC offset (date +%z) so that local timestamps in its logs can be converted to epoch seconds.
    Parameters:
        initialize : Testbed interface.
    Return Value: Offset in seconds east of UTC, or None when it cannot be read.
    Example: get_controller_utc_offset(initialize)
    """
    zone = last_line(ssh_exec(initialize, "controller", "date +%z"))
    match = re.match(r"^([+-])(\d{2})(\d{2})$", zone)
    if not match:
        return None
    seconds = int(match.group(2)) * 3600 + int(match.group(3)) * 60
    return -seconds if match.group(1) == "-" else seconds

def parse_log_timestamp(line, utc_offset):
    """
    Syntax: parse_log_timestamp(line, utc_offset)
    Description: Convert the leading timestamp of a controller log line to controller epoch seconds (see WIFI_LOG_TIMESTAMP_FORMATS).
    Parameters:
        line : Log line.
        utc_offset : Controller UTC offset in seconds (get_controller_utc_offset).
    Return Value: Epoch seconds as a float, or None when the line has no recognised timestamp.
    Example: parse_log_timestamp(line, utc_offset)
    """
    for pattern, time_format in WIFI_LOG_TIMESTAMP_FORMATS:
        match = re.match(pattern, line.strip())
        if match:
            try:
                return float(calendar.timegm(time.strptime(match.group(1).replace("T", " "), time_format)) - utc_offset)
            except ValueError:
                return None
    return None

def collect_controller_wifi_events(initialize, mac, since_epoch, until_epoch=None):
    """
    Syntax: collect_controller_wifi_events(initialize, mac, since_epoch, until_epoch)
    Description: Collect the NEW, timestamped controller OneWifi HAL log entries for mac written from since_epoch (until
        until_epoch, when given), across all files matching CONTROLLER_WIFI_LOG_GLOB (rotated files included). Entries are
        selected by their own timestamp instead of comparing total match counts, so deleting older lines in a log rotation
        cannot hide fresh attempts. Lines without a recognised timestamp are not counted.
    Parameters:
        initialize : Testbed interface.
        mac : MAC address to look for.
        since_epoch : Controller epoch from which entries count (observation start).
        until_epoch : Controller epoch up to which entries count, or None.
    Return Value: Dict with auth_frames (list of epochs), completed (list of (epoch, line) WPA handshake completions), rejections (list of (epoch, line)) and untimestamped (number of
        matching lines that could not be timed), or None when the controller time zone cannot be read.
    Example: collect_controller_wifi_events(initialize, backhaul_mac, observation_start, observation_end)
    """
    utc_offset = get_controller_utc_offset(initialize)
    if utc_offset is None:
        return None
    output = ssh_exec(initialize, "controller", f"grep -a -h -i '{mac}' {CONTROLLER_WIFI_LOG_GLOB} 2>/dev/null")
    events = {"auth_frames": [], "rejections": [], "completed": [], "untimestamped": 0}
    for line in output.splitlines():
        is_auth = re.search(rf"received auth frame from:\s*{re.escape(mac)}", line, re.IGNORECASE) is not None
        is_completed = not is_auth and re.search(WPA_HANDSHAKE_COMPLETED_PATTERN, line, re.IGNORECASE) is not None and re.search(WPA_HANDSHAKE_NEGATION_PATTERN, line, re.IGNORECASE) is None
        is_auth_reject = re.search(WPA_AUTH_REJECT_TEMPLATE.format(mac=re.escape(mac)), line, re.IGNORECASE) is not None
        is_rejection = not is_auth and not is_completed and (is_auth_reject or (re.search(WPA_REJECTION_PATTERN, line, re.IGNORECASE) is not None and re.search(WPA_SUCCESS_PATTERN, line, re.IGNORECASE) is None))
        if not (is_auth or is_completed or is_rejection):
            continue
        stamp = parse_log_timestamp(line, utc_offset)
        if stamp is None:
            events["untimestamped"] += 1
        elif stamp >= since_epoch and (until_epoch is None or stamp <= until_epoch):
            if is_auth:
                events["auth_frames"].append(stamp)
            elif is_completed:
                events["completed"].append((stamp, line.strip()))
            else:
                events["rejections"].append((stamp, line.strip()))
    return events

def verify_agent_boot_attempts(initialize, agent, backhaul_mac, observation_start, observation_end=None, link_down_at=None):
    """
    Syntax: verify_agent_boot_attempts(initialize, agent, backhaul_mac, observation_start, observation_end, link_down_at)
    Description: Evidence that the agent booted, tried the backhaul with the invalid credentials and was rejected. Both are
        required in the new timestamped controller Wi-Fi log entries of the observation window (rotation aware, see
        collect_controller_wifi_events): "received auth frame" entries for the agent backhaul MAC (a join attempt) and
        Agent-specific WPA rejection / unauthorized-state entries (WPA_REJECTION_PATTERN, or a controller auth reply with a nonzero status code, WPA_AUTH_REJECT_TEMPLATE) for it. Auth frames alone only
        prove a join attempt, not that authentication failed. Without both, the absence checks are not accepted as a pass. A completed WPA handshake (WPA_HANDSHAKE_COMPLETED_PATTERN) means the invalid credentials were accepted and fails the test;
        it is looked for from the confirmed link-down of the old session (link_down_at, minus COMPLETION_START_TOLERANCE_SECONDS for the
        1 s log timestamp resolution) so a connection during the settling period is not missed. Without link_down_at it is looked for
        from observation_start. Auth frames and rejections stay scoped to the observation window.
    Parameters:
        initialize : Testbed interface.
        agent : Agent device name.
        backhaul_mac : Agent backhaul STA MAC (get_agent_backhaul_mac).
        observation_start : Controller epoch at which the observation window starts.
        observation_end : Controller epoch at which the observation window ends, or None.
        link_down_at : Controller epoch of the confirmed link-down (wait_for_agent_link_down), or None.
    Return Value: None. Results are reported through report_logger.
    Example: verify_agent_boot_attempts(initialize, agent, backhaul_mac, observation_start, observation_end, link_down_at)
    """
    completion_start = observation_start if link_down_at is None else min(observation_start, link_down_at - COMPLETION_START_TOLERANCE_SECONDS)
    events = collect_controller_wifi_events(initialize, backhaul_mac, completion_start, observation_end)
    if events is None:
        report_logger.print_error(f"FAIL: The controller Wi-Fi logs ({CONTROLLER_WIFI_LOG_GLOB}) could not be evaluated for {agent} ({backhaul_mac}); boot, join attempts and rejection are not confirmed")
        return
    if events["untimestamped"]:
        report_logger.print_info(f"INFO: {events['untimestamped']} controller Wi-Fi log lines for {backhaul_mac} have no recognised timestamp and are not counted")
    if link_down_at is None:
        report_logger.print_info(f"INFO: The link-down time of {agent} is unknown; completed handshakes are only checked from the observation start, not during the settling period")
    # Only the completion check covers the settling period; join attempts and rejections are judged in the observation window.
    events["auth_frames"] = [stamp for stamp in events["auth_frames"] if stamp >= observation_start]
    events["rejections"] = [entry for entry in events["rejections"] if entry[0] >= observation_start]
    if events["completed"]:
        report_logger.print_error(f"FAIL: {agent} ({backhaul_mac}) completed the WPA handshake / reached the authorized state after its old backhaul session went down (settling period or observation window) although its backhaul credentials are invalid: {len(events['completed'])} entries, e.g. {events['completed'][0][1]!r}")
    if events["auth_frames"]:
        report_logger.print_success(f"PASS: {agent} is up and attempting the backhaul: {len(events['auth_frames'])} new auth frames from {backhaul_mac} logged by the controller during the observation window")
    else:
        report_logger.print_error(f"FAIL: No new auth frame from {agent} ({backhaul_mac}) logged by the controller during the observation window; the agent may be stuck rebooting or its mesh service did not start, so the missing traffic is not evidence")
    if events["rejections"]:
        report_logger.print_success(f"PASS: WPA rejection / unauthorized-state evidence for {agent} ({backhaul_mac}) in the controller logs during the observation window: {len(events['rejections'])} entries, e.g. {events['rejections'][0][1]!r}")
    else:
        report_logger.print_error(f"FAIL: No WPA rejection or unauthorized-state entry for {agent} ({backhaul_mac}) in the controller logs during the observation window; a join attempt alone does not prove that wireless authentication did not complete (verify through out-of-band Agent access if the controller does not log it)")

def has_sender_message(packets, message_type, sender_al_mac):
    """
    Syntax: has_sender_message(packets, message_type, sender_al_mac)
    Description: Return True when a packet carries message_type whose IEEE 1905 sender AL MAC (AL MAC address TLV, falling back to the Ethernet source) equals sender_al_mac.
    Parameters:
        packets : Capture packets to search.
        message_type : IEEE 1905 message type to look for.
        sender_al_mac : Sender AL MAC address.
    Return Value: True when a matching packet exists; otherwise False.
    Example: has_sender_message(observation_packets, MSG_TYPE_TOPOLOGY_DISCOVERY, controller_al_mac)
    """
    sender = str(sender_al_mac).lower()
    for pkt in packets:
        if not pkt.haslayer(Ether):
            continue
        eth = pkt[Ether]
        payload = bytes(eth.payload)
        if len(payload) < 4 or ((payload[2] << 8) | payload[3]) != message_type:
            continue
        if get_1905_sender_al_mac(payload, eth.src) == sender:
            return True
    return False

def verify_onboarding_not_completed(agent, agent_al_mac, controller_al_mac, packets, observation_start, observation_end=None, link_down_at=None):
    """
    Syntax: verify_onboarding_not_completed(agent, agent_al_mac, controller_al_mac, packets, observation_start, observation_end, link_down_at)
    Description: Plan check: the capture is valid (Topology Discovery from the controller within the observation window, so a
        capture that stopped early cannot pass on missing traffic) and onboarding does not complete successfully. Onboarding completes with
        the AP Autoconfiguration WSC (M2) sent by the controller to the agent. The WSC is looked for from the confirmed link-down of the old session
        (link_down_at, when given) until the end of the observation window.
    Parameters:
        agent : Agent device name.
        agent_al_mac : Agent AL MAC address.
        controller_al_mac : Controller AL MAC address.
        packets : Reassembled capture packets.
        observation_start : Controller epoch at which the observation window starts.
        observation_end : Controller epoch at which the observation window ends, or None.
        link_down_at : Controller epoch of the confirmed link-down (wait_for_agent_link_down), or None.
    Return Value: Tuple (before_observation, during_observation) agent 1905 messages.
    Example: verify_onboarding_not_completed(agent, agent_al_mac, controller_al_mac, packets, start, end, restart)
    """
    observation_packets = [pkt for pkt in packets if float(pkt.time) >= observation_start and (observation_end is None or float(pkt.time) <= observation_end)]
    if has_sender_message(observation_packets, MSG_TYPE_TOPOLOGY_DISCOVERY, controller_al_mac):
        report_logger.print_success(f"PASS: The capture is valid: Topology Discovery from the Controller (AL MAC {controller_al_mac}) is present during the observation window")
    else:
        report_logger.print_error(f"FAIL: No Topology Discovery from the Controller (AL MAC {controller_al_mac}) during the observation window; the capture cannot be used as evidence")

    before, during = get_agent_1905_messages(packets, agent_al_mac, observation_start, observation_end)
    if link_down_at is None:
        since_reboot = during
    else:
        _, since_reboot = get_agent_1905_messages(packets, agent_al_mac, link_down_at, observation_end)
    completed = [entry for entry in since_reboot if entry[0] == MSG_TYPE_AP_AUTOCONFIGURATION_WSC and not entry[1]]
    if completed:
        report_logger.print_error(f"FAIL: Onboarding of {agent} completed successfully with invalid credentials: AP Autoconfiguration WSC from the Controller to {agent_al_mac} x{len(completed)} since the old session went down")
    else:
        report_logger.print_success(f"PASS: Onboarding of {agent} did not complete successfully: no AP Autoconfiguration WSC from the Controller to {agent_al_mac} since the old session went down")
    return before, during

def get_controller_topology_entry(initialize, agent, agent_al_mac):
    """
    Syntax: get_controller_topology_entry(initialize, agent, agent_al_mac)
    Description: Look up the agent AL MAC in the controller DataElements topology (initialize.get_device_index).
        None or -1 means the agent is not listed in the controller topology.
    Parameters:
        initialize : Testbed interface.
        agent : Agent device name.
        agent_al_mac : Agent AL MAC address.
    Return Value: The device index, or None when the agent is not listed.
    Example: get_controller_topology_entry(initialize, agent, agent_al_mac)
    """
    index = initialize.get_device_index("controller", agent_al_mac, "de")
    if index is None or str(index).strip() in ("", "-1"):
        return None
    return index

def verify_not_in_active_topology(agent, agent_al_mac, agent_messages, samples, initialize=None):
    """
    Syntax: verify_not_in_active_topology(agent, agent_al_mac, agent_messages, samples, initialize)
    Description: Plan check: the agent does not rejoin the active topology. It must not be reachable from the controller in
        the final sample, and must not send 1905 messages other than AP Autoconfiguration (Topology Discovery,
        Topology Notification, Topology Response, ...) during the observation window.
    Parameters:
        agent : Agent device name.
        agent_al_mac : Agent AL MAC address.
        agent_messages : Agent 1905 messages seen during the observation window.
        samples : Samples returned by collect_ping_samples.
    Return Value: None. Results are reported through report_logger.
    Example: verify_not_in_active_topology(agent, agent_al_mac, during, samples)
    """
    final = samples[-1]
    if final["reachable"] is None:
        report_logger.print_error(f"FAIL: The final ping from the Controller to {agent} could not be evaluated: {final['ping_output']}")
    elif final["reachable"]:
        report_logger.print_error(f"FAIL: {agent} rejoined the active topology: it is reachable from the Controller in the final poll")
    else:
        report_logger.print_success(f"PASS: In the final poll {agent} is not reachable from the Controller")

    if initialize is not None:
        try:
            index = get_controller_topology_entry(initialize, agent, agent_al_mac)
        except Exception as error:
            report_logger.print_error(f"FAIL: The controller topology entry of {agent} (AL MAC {agent_al_mac}) could not be read: {error}")
        else:
            if index is None:
                report_logger.print_success(f"PASS: {agent} (AL MAC {agent_al_mac}) is not listed in the controller topology")
            else:
                report_logger.print_error(f"FAIL: {agent} (AL MAC {agent_al_mac}) is still listed in the controller topology (index {index})")

    topology = [entry for entry in agent_messages if entry[1] and entry[0] not in ONBOARDING_MESSAGE_TYPES]
    if topology:
        report_logger.print_error(f"FAIL: {agent} (AL MAC {agent_al_mac}) rejoined the active topology: 1905 messages from the Agent during the observation window: {describe_messages(topology)}")
    else:
        report_logger.print_success(f"PASS: {agent} (AL MAC {agent_al_mac}) did not rejoin the active topology: no topology messages from the Agent during the observation window")

def review_onboarding_traffic(agent, agent_al_mac, before, during, link_down_at, observation_start):
    """
    Syntax: review_onboarding_traffic(agent, agent_al_mac, before, during, link_down_at, observation_start)
    Description: Plan review: partial onboarding traffic (AP Autoconfiguration Search/Response, or an early WSC) may be
        present with invalid credentials; it is reported as information only. Only a WSC from the controller to the agent
        during the observation window would be a successful onboarding, and that is already failed by the onboarding check.
    Parameters:
        agent : Agent device name.
        agent_al_mac : Agent AL MAC address.
        before : Agent 1905 messages before the observation window.
        during : Agent 1905 messages during the observation window.
        link_down_at : Controller epoch of the confirmed link-down.
        observation_start : Controller epoch at which the observation window starts.
    Return Value: None. Information is reported through report_logger.
    Example: review_onboarding_traffic(agent, agent_al_mac, before, during, link_down_at, observation_start)
    """
    early = [entry for entry in before if entry[0] in ONBOARDING_MESSAGE_TYPES]
    report_logger.print_info(f"INFO: Onboarding traffic for {agent} (AL MAC {agent_al_mac}) before the observation window (link down at {link_down_at:.0f}, observation from {observation_start:.0f}); partial onboarding is expected and is informational only: {describe_messages(early)}")
    partial = [entry for entry in during if entry[0] in ONBOARDING_MESSAGE_TYPES]
    report_logger.print_info(f"INFO: Onboarding traffic for {agent} during the observation window (partial onboarding is informational only, not a failure): {describe_messages(partial)}")
