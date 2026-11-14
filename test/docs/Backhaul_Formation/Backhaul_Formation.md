# Test Case 1: EM_Backhaul_Wireless_Formation_LinkType
## Objective
Verify that a Wi-Fi (Wireless) backhaul link is successfully established between the Agent under test and the Controller after the Agent reboots, and that the backhaul link type is Wi-Fi, by validating wireless association, backhaul SSID, signal strength, link type (bridge forwarding table), connectivity, and IEEE1905 topology formation.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent configured for Wi-Fi backhaul |
| Packet Capture | tcpdump running on Controller (brlan0) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh services are running.
2. Agent 1 is already onboarded and configured for wireless backhaul.
3. Shell access to Controller and Agent 1 is available.
4. Backhaul SSID (mesh_backhaul) is configured.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul Variant | Wireless (Wi-Fi) |
| Agent Under Test | Agent 1 |
| Verification Method | iw link status, bridge fdb, ping, IEEE1905 packet capture |
| Network Topology | Agent 1 → Wi-Fi Backhaul → Controller |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | Start packet capture on Controller using `tcpdump -i brlan0 -w /tmp/ieee1905.pcap ether proto 0x893a` | Packet capture starts successfully. |
| 2 | Reboot Agent 1 (CLI reboot) to trigger wireless backhaul onboarding and wait for the Wi-Fi backhaul on wifi1.3 to come up | Agent comes back up and initiates wireless backhaul onboarding. |
| 3 | Verify the backhaul link using `iw dev wifi1.3 link` | Agent is connected to a backhaul BSSID, the connected SSID is mesh_backhaul, and a signal strength value is displayed. |
| 4 | Verify the backhaul link type on Agent 1 using `bridge fdb show \| grep -i <controller_al_mac>` | The Controller AL MAC is learned on port `wifi1.3` (`dev wifi1.3`), confirming that the path to the Controller is the Wi-Fi backhaul, so the link type is Wi-Fi. If it is learned on a wired port (e.g. `eth*`/`lan*`) or not learned at all, the test fails. |
| 5 | Verify connectivity by running `ping <agent_ip>` from the Controller | Successful ping response is observed. |
| 6 | Stop capture after the IEEE1905 onboarding exchange completes and inspect using Wireshark | IEEE1905 Topology Discovery and AP Autoconfiguration Search messages for Agent 1 are observed, followed by a completed Topology Query/Response exchange between Agent 1 and the Controller, correlated using Agent 1's AL MAC. Topology Notification is logged for information only; its absence does not fail the test. |

---

# Test Case 2: EM_Backhaul_Ethernet_Formation_LinkType
## Objective
Verify that an Ethernet backhaul link is successfully established between Agent 2 and the network, and that LinkType is correctly reported as "Ethernet" in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 2 | EasyMesh Agent with Ethernet uplink connected |
| Packet Capture | `tcpdump` run locally on Agent 2's Ethernet backhaul interface (e.g., `eth0`) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Agent 2's Ethernet backhaul port is physically connected to the same L2 segment as the Controller.
3. DataElements object is accessible through rbuscli on the Controller.
4. Shell/console access to Agent 2 is available to run `tcpdump`.
5. Agents 1, 3, and 4 are held powered-off / factory-reset so they do not interfere with this single-Agent test.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul Variant | Ethernet |
| Agent Under Test | Agent 2 |
| Verification Method | rbuscli DataElements get + local tcpdump on Agent 2 |
| Network Topology | Agent 2 --Ethernet backhaul--> Controller |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent 2, start capture before connecting the cable: `tcpdump -i eth0 -w /tmp/backhaul_eth.pcap ether proto 0x893a` | tcpdump begins listening for IEEE 1905.1 CMDU frames on Agent 2's Ethernet backhaul interface |
| 2 | Connect Agent 2's Ethernet backhaul port and power on Agent 2 | Agent 2's link comes up at the physical layer |
| 3 | **[Packet Capture]** Stop capture after onboarding; inspect with `tcpdump -r /tmp/backhaul_eth.pcap -n` | Capture shows Topology Discovery, Topology Query, and Topology Response CMDUs exchanged between Agent 2 and Controller on `eth0` |
| 4 | Verify link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent 2's Device instance) | rbuscli returns "Ethernet", confirming the backhaul medium is wired |
| 5 | Verify media type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType` (Agent 2's Device instance) | rbuscli returns an Ethernet media type value ("IEEE 802.3u" or "IEEE 802.3ab"), consistent with the physical link speed negotiated |
| 6 | Verify PHY rate using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate` (Agent 2's Device instance) | rbuscli returns a non-zero PHY rate in Mb/s consistent with the negotiated Ethernet link speed |

---

# Test Case 3: EM_Backhaul_Hybrid_Formation_LinkType_Verification
## Objective
Verify that in a hybrid backhaul deployment (Agent 3 has both Ethernet and Wi-Fi backhaul capability), Agent 3 forms its backhaul link over the intended active medium and reports the correct LinkType, while the alternate medium remains available as standby option.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 3 | EasyMesh Agent with both Ethernet port and backhaul Wi-Fi radio provisioned |
| Packet Capture | `tcpdump` run locally on Agent 3, on both `eth0` and the backhaul radio interface (e.g., `wlan1`) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Agent 3 has valid Wi-Fi backhaul credentials AND an Ethernet uplink cabled, both physically available.
3. DataElements object is accessible through rbuscli on the Controller.
4. Shell/console access to Agent 3 is available to run `tcpdump`.
5. Agents 1, 2, and 3 are held powered-off / factory-reset so they do not interfere with this single-Agent test.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul Variant | Hybrid (Ethernet + Wi-Fi both available) |
| Agent Under Test | Agent 3 |
| Verification Method | rbuscli DataElements get + local tcpdump on Agent 3 (dual interface) |
| Network Topology | Agent 3 --Ethernet + Wi-Fi backhaul available--> Controller |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent 3, start two parallel captures: `tcpdump -i <eth_iface> -w /tmp/hybrid_eth.pcap ether proto 0x893a` and `tcpdump -i <wlan_iface> -w /tmp/hybrid_wifi.pcap ether proto 0x888e` | Both captures begin listening simultaneously on Agent 3's respective backhaul interfaces |
| 2 | Connect Ethernet cable and enable backhaul Wi-Fi radio on Agent 3 simultaneously; power on Agent 3 | Agent 3 has both mediums physically/logically available |
| 3 | **[Packet Capture]** Stop both captures after onboarding; inspect each with `tcpdump -r <file> -n` | The active medium's capture file shows IEEE 1905.1 Topology Discovery/EAPOL frames as applicable; the standby medium's capture file shows link-layer presence only, with no completed backhaul handshake |
| 4 | Verify the active link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent 3's Device instance) | rbuscli returns the medium Agent 3 actually formed backhaul on (e.g., "Ethernet"), confirming hybrid preference logic selected one active backhaul path, matching the interface that showed traffic in Step 3 |
| 5 | Correlate the reported LinkType with the corresponding interface/capture. | The interface corresponding to the reported active LinkType carries the backhaul traffic, while the other medium remains available as the standby/alternate backhaul. |
| 6 | Verify the standby Wi-Fi backhaul STA MAC is populated using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BackhaulSta.MACAddress` (Agent 3's Device instance) | A valid MAC address is returned for the logical backhaul STA, confirming Agent 3's Wi-Fi backhaul interface exists even though it is not the active path |
| 7 | Verify backhaul device reference using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulDeviceID` (Agent 3's Device instance) | rbuscli returns a valid Device ID (MAC) identifying the upstream device providing backhaul on the active medium |

---

# Test Case 4: EM_Backhaul_Ethernet_To_Wireless_Failover
## Objective
Verify that in a hybrid backhaul configuration, when Agent 3's active Ethernet backhaul link is disconnected, Agent 3 fails over to the Wi-Fi backhaul link and the LinkType updates accordingly.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 3 | EasyMesh Agent with hybrid backhaul (Ethernet primary, Wi-Fi standby) already formed |
| Packet Capture | `tcpdump` run locally on Agent 3's backhaul radio interface (e.g., `wlan1`) |
---
## Pre-Requisites
1. Agent 3 is already onboarded with Ethernet as the active backhaul (per Test Case 3).
2. Wi-Fi backhaul credentials are already provisioned on Agent 3 as a standby path.
3. Shell/console access to Agent 3 is available to run `tcpdump`.
4. Agents 1, 2, and 4 are held powered-off / factory-reset so they do not interfere with this single-Agent test.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul Variant | Hybrid (failover scenario) |
| Agent Under Test | Agent 3 |
| Verification Method | rbuscli DataElements get + local tcpdump on Agent 3 |
| Trigger | Physical disconnection of Agent 3's Ethernet cable |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify baseline using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent 3's Device instance) | rbuscli returns "Ethernet", confirming baseline active backhaul medium |
| 2 | On Agent 3, start capture: `tcpdump -i wlan1 -w /tmp/failover_wifi.pcap ether proto 0x888e`, then physically disconnect Agent 3's Ethernet backhaul cable | Ethernet link goes down; tcpdump begins listening on Agent 3's standby Wi-Fi interface |
| 3 | **[Packet Capture]** Stop capture after failover; inspect with `tcpdump -r /tmp/failover_wifi.pcap -n` | Capture shows EAPOL-Key frames (M1–M4) on `wlan1`, confirming Agent 3's bSTA completed the 4-Way Handshake to the backhaul BSS as failover proceeded |
| 4 | Verify updated link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent 3's Device instance) | rbuscli returns "Wi-Fi", confirming failover to the wireless backhaul medium |
| 5 | Verify backhaul stats update using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.SignalStrength` (Agent 3's Device instance) | rbuscli returns a valid dBm signal-strength value, confirming stats are now being reported for Agent 3's active Wi-Fi backhaul path |

---

# Test Case 5: EM_Backhaul_Stats_Verification
## Objective
Verify that once backhaul is established, the Controller's DataElements data model correctly populates traffic and link-quality statistics for Agent 2's backhaul link.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 2 | EasyMesh Agent with backhaul link established (per Test Case 2) and passing traffic |
| Packet Capture | `tcpdump` run locally on Agent 2's active backhaul interface, used only to independently confirm traffic flow |
---
## Pre-Requisites
1. Agent 2's backhaul link is established (Ethernet, per Test Case 2).
2. Traffic is flowing across Agent 2's backhaul link (e.g., a connected client generating upstream/downstream traffic).
3. Shell/console access to Agent 2 is available to run `tcpdump`.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agent Under Test | Agent 2 |
| Verification Method | rbuscli DataElements get + local tcpdump byte-count cross-check |
| Network Topology | Agent 2 --Backhaul (active)--> Controller, with client traffic traversing the link |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent 2, run `tcpdump -i <backhaul_intf> -w /tmp/stats_check.pcap` while generating client traffic through Agent 2 | tcpdump captures the traffic traversing Agent 2's backhaul interface |
| 2 | Stop the capture and check packet/byte totals with `tcpdump -r /tmp/stats_check.pcap -n \| wc -l` | A non-zero, growing packet count confirms traffic actually crossed Agent 2's backhaul interface |
| 3 | Verify byte counters using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.BytesSent` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.BytesReceived` (Agent 2's Device instance) | Both counters return non-zero, increasing values consistent with the traffic observed in the local capture |
| 4 | Verify link utilization using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.LinkUtilization` (Agent 2's Device instance) | rbuscli returns a percentage value reflecting current medium utilization |
| 5 | Verify data rates using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.LastDataDownlinkRate` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.LastDataUplinkRate` (Agent 2's Device instance) | Both return non-zero values in kbps, consistent with the negotiated backhaul link speed |
| 6 | Since Agent 2 is on Ethernet backhaul, `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.SignalStrength` is indeterminate per spec — rely on the Ethernet stats fields above instead; for reference, re-run this check against Agent 1 (Wi-Fi backhaul, Test Case 1) | For Agent 1's Device instance, rbuscli returns a valid dBm RCPI value, confirming the field is populated for the Wi-Fi backhaul variant |

---

# Test Case 6: EM_Backhaul_Reassociation
## Objective
Verify that Agent 1's Wi-Fi backhaul STA successfully re-associates and restores connectivity after a controlled backhaul interface restart, and that a new authentication sequence is completed.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent with active Wi-Fi backhaul link |
| Packet Capture | tcpdump running on Agent 1 backhaul interface (wifi1.3) |
---
## Pre-Requisites
1. Agent 1 backhaul connection is operational.
2. SSH access to Agent 1 is available.
3. tcpdump utility is available on Agent 1.
4. Backhaul interface is identified (e.g., wifi1.3).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agent Under Test | Agent 1 |
| Trigger Method | Backhaul Interface Restart |
| Interface | wifi1.3 |
| Verification Method | iw, tcpdump, interface status verification |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent Action | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current association using `iw dev wifi1.3 link` | Current BSSID and connection state are displayed. |
| 2 | Start capture using `tcpdump -i wifi1.3 -w /tmp/backhaul_reassoc.pcap ether proto 0x888e` | Packet capture starts successfully and monitors EAPOL traffic. |
| 3 | Trigger re-association using `ifconfig wifi1.3 down`, then `ifconfig wifi1.3 up` | Backhaul link disconnects and initiates reconnection. |
| 4 | Verify connection using `iw dev wifi1.3 link` | Agent reconnects successfully to a valid backhaul BSSID. |
| 5 | Stop packet capture and inspect using `tcpdump -r /tmp/backhaul_reassoc.pcap -n` | Fresh EAPOL 4-Way Handshake (M1-M4) is observed. |
| 6 | Compare pre- and post-reassociation connection details | Backhaul connectivity is restored successfully and link becomes operational. |

---

# Test Case 7: EM_Backhaul_PreferredBackhauls_Configuration
## Objective
Verify that the Controller can configure a preferred backhaul link for Agent 4 using SetPreferredBackhauls(), and that the PreferredBackhauls table is correctly populated and honored during backhaul (re)formation.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 4 | EasyMesh Agent capable of both Wi-Fi and Ethernet backhaul |
---
## Pre-Requisites
1. Controller and Agent 4 are onboarded with EasyMesh services running.
2. Agent 4 supports multiple backhaul candidate links (bSTA and/or Ethernet interface).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agent Under Test | Agent 4 |
| Command | `Device.WiFi.DataElements.Network.SetPreferredBackhauls()` |
| Verification Method | rbuscli DataElements get |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify baseline entries using `rbuscli get Device.WiFi.DataElements.Network.PreferredBackhaulsNumberOfEntries` | rbuscli returns the current number of preferred backhaul entries (e.g., "0") |
| 2 | Invoke `rbuscli set Device.WiFi.DataElements.Network.SetPreferredBackhauls() BackhaulMACAddress=<BSS/Ethernet MAC> bSTAMACAddress=<Agent 4's bSTA MAC>` | Command is accepted for asynchronous execution |
| 3 | Verify entry count using `rbuscli get Device.WiFi.DataElements.Network.PreferredBackhaulsNumberOfEntries` | rbuscli returns an incremented count, confirming a new preferred backhaul entry was added for Agent 4 |
| 4 | Verify entry content using `rbuscli get Device.WiFi.DataElements.Network.PreferredBackhauls.{i}.BackhaulMACAddress` and `rbuscli get Device.WiFi.DataElements.Network.PreferredBackhauls.{i}.bSTAMACAddress` | Both values match the MAC addresses submitted in Step 2, confirming Agent 4's preferred backhaul pairing was correctly stored |
| 5 | Restart/re-trigger backhaul formation on Agent 4 and verify `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent 4's Device instance) | rbuscli returns the MAC address matching the configured preferred backhaul, confirming the preference was honored for Agent 4 |

---

# Test Case 8: EM_Backhaul_AKM_Security_Configuration
## Objective
Verify that the configured backhaul AKM is used and that successful WPA authentication occurs during wireless backhaul association.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | Wi-Fi Backhaul Agent |
| Packet Capture | tcpdump running on Agent 1 |
---
## Pre-Requisites
1. Backhaul SSID is available.
2. Agent 1 contains valid credentials.
3. Shell access to Agent 1 is available.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agent Under Test | Agent 1 |
| Verification Method | AKM verification and connection validation |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify AKM configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.1.BackhaulAKMsAllowed` | Configured AKM value is displayed. |
| 2 | Verify wireless association using `iw dev wifi1.3 link` | Agent connects successfully to the backhaul SSID. |
| 3 | Verify signal strength and connection parameters using `iw dev wifi1.3 link` | Valid link information is displayed. |
| 4 | Verify connectivity between Controller and Agent using ping | Connectivity is established successfully. |
| 5 | Verify Agent remains connected to the backhaul SSID | Stable wireless backhaul connection is maintained. |

---

# Test Case 9: EM_Backhaul_DownstreamAgent_MultiHop_Verification
## Objective
Verify that when Agent 2 forms its backhaul through Agent 1 as an intermediate hop, Agent 1 correctly identifies the downstream backhaul connection using link status, bridge FDB learning, and packet capture analysis, confirming a multi-hop topology without relying on DataElements parameters.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | Intermediate EasyMesh Agent |
| Agent 2 | Downstream EasyMesh Agent |
| Packet Capture | tcpdump running on Agent 1 downstream-facing backhaul interface |
---
## Pre-Requisites
1. Agent 1 already has an established backhaul link to the Controller.
2. Agent 2 is configured to backhaul through Agent 1.
3. Shell access to Agent 1 and Agent 2 is available.
4. tcpdump, iw, and bridge utilities are available.
5. Agents 3 and 4 are powered off or factory reset.
6. DataElements parameters are unavailable in the current build.
7. Agent 2 remains powered OFF until Step 5.
8. Existing packet capture files can be removed before test execution.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agents Under Test | Agent 1 (Intermediate), Agent 2 (Downstream) |
| Network Topology | Controller ←→ Agent 1 ←→ Agent 2 |
| Verification Method | Link Status + Bridge FDB + Packet Capture |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify Agent 1 upstream backhaul using `iw dev wifi1.3 link` | Agent 1 shows active connection with SSID mesh_backhaul. |
| 2 | Identify downstream backhaul AP interface using `iw dev` | Backhaul AP interface (wifi1.1) is identified with the expected SSID and valid BSSID. |
| 3 | Check existing downstream topology by searching for dynamically created downstream STA interfaces | Existing downstream STA interface is logged if present; otherwise no downstream STA interface is detected. |
| 4 | Start packet capture using `tcpdump -i wifi1.1 -w /tmp/multihop_check.pcap` | Packet capture starts successfully on Agent 1 downstream interface. |
| 5 | Power on Agent 2 and allow onboarding through Agent 1 | Agent 2 associates through Agent 1 and a downstream STA interface (wifi1.1.staXX) is detected on Agent 1. |
| 6 | Verify Agent 2 backhaul association using `iw dev wifi1.3 link` | Agent 2 is connected to Agent 1's backhaul BSSID and station interface is operational. |
| 7 | Verify dynamic bridge learning using `bridge fdb show` | Agent 2 MAC address is dynamically learned on the downstream interface or driver-created per-station port. |
| 8 | Stop packet capture and verify capture file | Packet capture stops successfully and the pcap file is generated with valid content. |
| 9 | Analyze pcap using `tcpdump -r /tmp/multihop_check.pcap -n` | IEEE1905 traffic (EtherType 0x893a) is observed on the downstream link. |
| 10 | Verify EAPOL authentication traffic | EAPOL-Key authentication messages associated with Agent 2 are observed in the capture. |
| 11 | Verify Agent 2 MAC activity in capture | Traffic sourced by Agent 2 backhaul MAC address is observed, confirming active downstream communication through Agent 1. |
| 12 | Correlate all observations and re-validate topology | Agent 1 remains connected to the Controller, Agent 2 remains connected to Agent 1, downstream STA interface persists, FDB learning remains valid, and the multi-hop topology is successfully verified. |


---

# Test Case 10: EM_Backhaul_Wireless_Formation_Negative_InvalidCredentials
## Objective
Verify that wireless backhaul onboarding fails when invalid credentials are configured and confirm that the Agent does not establish a wireless backhaul connection, does not complete onboarding, and does not rejoin the active EasyMesh topology.
## Test Type
**Negative**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent with invalid backhaul credentials |
| Packet Capture | tcpdump running on Controller |
---
## Pre-Requisites
1. Controller and Agent are successfully onboarded.
2. Wireless backhaul connection is operational.
3. SSH access to Controller and Agent is available.
4. Backhaul SSID is available.
5. Packet capture utilities are available.
6. Agent backhaul configuration file can be modified through automation.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul Variant | Wireless |
| Agent Under Test | Agent 1 |
| Verification Method | Ping and IEEE1905 packet capture |
| Network Topology | Agent 1 → Wi-Fi Backhaul → Controller |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify Agent is connected to Controller and reachable before test execution | Agent backhaul is operational and Agent is reachable. |
| 2 | Start packet capture on Controller using IEEE1905 filter | Capture starts successfully. |
| 3 | Configure invalid backhaul credentials on Agent (`/nvram/EasymeshCfg.json`, backup kept) and reboot the Agent (`sync; reboot`) | Agent boots with only the invalid credentials and attempts to form the backhaul. |
| 4 | Observe Agent state for the configured timeout period by pinging the Agent from the Controller | Agent does not successfully establish backhaul and remains unreachable from the Controller throughout the observation window. |
| 5 | Stop packet capture | Capture file is generated successfully. |
| 6 | Analyze the captured IEEE1905 traffic for the Agent | Onboarding does not complete (no AP Autoconfiguration WSC from the Controller to the Agent) and the Agent does not rejoin the active topology (no topology messages from the Agent). Partial onboarding traffic may be present and is informational only. |

---
