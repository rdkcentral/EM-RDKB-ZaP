# Test Case 1: EM_Backhaul_Wireless_Formation_LinkType
## Objective
Verify that a Wi-Fi (wireless) backhaul link is successfully established between Agent 1 and its upstream Multi-AP device, and that LinkType is correctly reported as "Wi-Fi" in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 1 | EasyMesh Agent configured for Wi-Fi backhaul onboarding |
| Packet Capture | `tcpdump` run locally on Agent 1's backhaul radio interface (e.g., `wlan1`) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Agent 1 has backhaul Wi-Fi credentials (SSID/passphrase) provisioned via WPS/M1-M2 or manual configuration.
3. DataElements object is accessible through rbuscli on the Controller.
4. Shell/console access to Agent 1 is available to run `tcpdump`.
5. Agents 2–4 are held powered-off / factory-reset so they do not interfere with this single-Agent test.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul Variant | Wireless (Wi-Fi) |
| Agent Under Test | Agent 1 |
| Verification Method | rbuscli DataElements get + local tcpdump on Agent 1 |
| Network Topology | Agent 1 --Wi-Fi backhaul--> Controller |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent 1, start capture before onboarding: `tcpdump -i wlan1 -w /tmp/backhaul_wireless.pcap ether proto 0x888e` | tcpdump begins listening for EAPOL frames on Agent 1's backhaul radio interface |
| 2 | Power on/trigger Agent 1 to associate to the backhaul BSS | Agent 1 begins 802.11 authentication/association to the backhaul BSS |
| 3 | **[Packet Capture]** Stop capture after onboarding completes; inspect with `tcpdump -r /tmp/backhaul_wireless.pcap -n` | Capture shows 4 EAPOL-Key frames (M1–M4) exchanged on `wlan1` between Agent 1's bSTA and the backhaul BSS, confirming the 4-Way Handshake completed |
| 4 | Verify link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent 1's Device instance) | rbuscli returns "Wi-Fi", confirming the backhaul medium is wireless |
| 5 | Verify backhaul status using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulMACAddress` (Agent 1's Device instance) | Both near-end and far-end MAC addresses are returned as valid, non-null MAC addresses, confirming the backhaul link endpoints are populated |
| 6 | Verify BSS backhaul usage flag using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulUse` (Agent 1's backhaul BSS instance) | Value returned is "true" , confirming this BSS is actively in use as a backhaul BSS |

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

# Test Case 5: EM_Backhaul_ALID_Verification
## Objective
Verify that after backhaul formation, Agent 1 correctly reports the IEEE 1905.1 Abstraction Layer ID (ALID) of the upstream Agent/Controller providing its backhaul, and that this is consistent with the topology discovered on the wire/air.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 1 | EasyMesh Agent with backhaul link already established (per Test Case 1) |
| Packet Capture | `tcpdump` run locally on Agent 1's active backhaul interface (Wi-Fi, per Test Case 1) |
---
## Pre-Requisites
1. Backhaul link is already formed between Agent 1 and Controller.
2. DataElements object is accessible through rbuscli on the Controller.
3. Shell/console access to Agent 1 is available to run `tcpdump`.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agent Under Test | Agent 1 |
| Verification Method | rbuscli DataElements get + local tcpdump cross-check |
| Network Topology | Agent 1 --Backhaul--> Controller (ALID known) |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent 1, capture 1905.1 traffic on its active backhaul interface: `tcpdump -i <backhaul_intf> -w /tmp/alid_check.pcap ether proto 0x893a` while a fresh Topology Query/Response cycle occurs | Capture records Topology Discovery/Response CMDUs on Agent 1's active backhaul interface |
| 2 | Inspect capture with `tcpdump -r /tmp/alid_check.pcap -n -v` | Capture shows the AL MAC Address TLV in the Topology Discovery/Response frames from the upstream device |
| 3 | Verify ALID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulALID` (Agent 1's Device instance) | rbuscli returns a MAC address value matching the AL MAC Address TLV observed in the capture, confirming Agent 1 correctly identifies its backhaul-providing device |
| 4 | Cross-check Controller identity using `rbuscli get Device.WiFi.DataElements.Network.ControllerID` | rbuscli returns the Controller's unique identifier, which should match the BackhaulALID reported by Agent 1 as a directly-connected Agent |

---

# Test Case 6: EM_Backhaul_Stats_Verification
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

# Test Case 7: EM_Backhaul_SteerWiFiBackhaul_Command
## Objective
Verify that the Controller can request Agent 1's Wi-Fi backhaul STA to steer (re-associate) to a different target BSS using the SteerWiFiBackhaul() command, and that the backhaul topology updates to reflect the new association.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 1 | EasyMesh Agent with an active Wi-Fi backhaul link (per Test Case 1), and credentials already valid for a second target BSS |
| Packet Capture | `tcpdump` run locally on Agent 1's backhaul radio interface (e.g., `wlan1`) |
---
## Pre-Requisites
1. Agent 1's Wi-Fi backhaul is currently associated to BSS-A.
2. A second candidate backhaul BSS (BSS-B) is available and Agent 1 already holds credentials for it.
3. Shell/console access to Agent 1 is available to run `tcpdump`.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agent Under Test | Agent 1 |
| Command | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.SteerWiFiBackhaul()` (Agent 1's Device instance) |
| Input | TargetBSS = BSSID of BSS-B |
| Verification Method | rbuscli DataElements get + local tcpdump on Agent 1 |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current association using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent 1's Device instance) | rbuscli returns a MAC address matching BSS-A, confirming baseline association |
| 2 | On Agent 1, start capture: `tcpdump -i wlan1 -w /tmp/steer_check.pcap ether proto 0x888e` | tcpdump begins listening for EAPOL frames on Agent 1's backhaul radio interface |
| 3 | Invoke `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.SteerWiFiBackhaul() TargetBSS=<BSSID of BSS-B>` (Agent 1's Device instance) | Command is accepted for asynchronous execution |
| 4 | **[Packet Capture]** Stop capture after steering completes; inspect with `tcpdump -r /tmp/steer_check.pcap -n` | Capture shows a fresh EAPOL-Key (M1–M4) exchange on `wlan1`, evidencing Agent 1's bSTA completed a new 4-Way Handshake consistent with a re-association to BSS-B |
| 5 | Verify command result using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Status` (Agent 1's Device instance) | rbuscli returns "Success", confirming the steering request completed |
| 6 | Verify updated association using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent 1's Device instance) | rbuscli returns a MAC address matching BSS-B, confirming Agent 1's backhaul topology updated to the new target BSS |

---

# Test Case 8: EM_Backhaul_PreferredBackhauls_Configuration
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

# Test Case 9: EM_Backhaul_AKM_Security_Configuration
## Objective
Verify that the backhaul BSS's allowed AKM suite for backhaul STA connections can be configured, and that Agent 1's Wi-Fi backhaul link only forms successfully when its bSTA's security credentials match the configured AKM.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 1 | EasyMesh Agent attempting Wi-Fi backhaul association |
| Packet Capture | `tcpdump` run locally on Agent 1's backhaul radio interface (e.g., `wlan1`) |
---
## Pre-Requisites
1. Backhaul BSS is up and advertising a backhaul-capable BSSID.
2. Agent 1's bSTA is provisioned with credentials matching the AKM to be configured.
3. Shell/console access to Agent 1 is available to run `tcpdump`.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agent Under Test | Agent 1 |
| Parameter Under Test | `Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulAKMsAllowed` |
| Verification Method | rbuscli DataElements set/get + local tcpdump on Agent 1 |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current AKM configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulAKMsAllowed` (backhaul BSS instance) | rbuscli returns the currently configured AKM suite list |
| 2 | Configure AKM using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulAKMsAllowed "<AKM suite value>"` | Configuration is accepted and applied on the backhaul BSS |
| 3 | On Agent 1, start capture: `tcpdump -i wlan1 -w /tmp/akm_check.pcap ether proto 0x888e`, then trigger Agent 1's bSTA to (re)associate to this backhaul BSS | tcpdump begins listening; Agent 1 begins association using credentials matching the configured AKM |
| 4 | **[Packet Capture]** Stop capture; inspect with `tcpdump -r /tmp/akm_check.pcap -n -v` | Capture confirms a full EAPOL-Key (M1–M4) exchange completed on `wlan1`, evidencing the handshake succeeded under the configured AKM |
| 5 | Verify successful backhaul formation using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulUse` (Agent 1's backhaul BSS instance) | rbuscli returns "true", confirming the backhaul BSS is now in use with the configured AKM |

---

# Test Case 10: EM_Backhaul_Topology_DeviceCount_Update
## Objective
Verify that when Agent 4 successfully forms a backhaul link (joining Agents 1–3, already onboarded), the Controller's network topology (Device table) updates to include Agent 4.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 1–3 | EasyMesh Agents already onboarded and backhauled to the Controller |
| Agent 4 | New EasyMesh Agent not yet part of the network |
| Packet Capture | `tcpdump` run locally on the Controller's interface facing Agent 4's backhaul medium |
---
## Pre-Requisites
1. Controller is running with an existing, known topology: Controller + Agent 1, Agent 2, Agent 3 (4 devices).
2. Agent 4 has valid backhaul credentials for the medium under test (Wireless/Ethernet/Hybrid).
3. Shell/console access to the Controller is available to run `tcpdump`.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agent Under Test | Agent 4 |
| Verification Method | rbuscli DataElements get + local tcpdump on Controller |
| Network Topology (Before) | 4 devices (Controller + Agent 1, Agent 2, Agent 3) |
| Network Topology (After) | 5 devices (Controller + Agent 1, Agent 2, Agent 3, Agent 4) |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify baseline device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | rbuscli returns "4", the current device count before Agent 4 joins |
| 2 | On the Controller, start capture: `tcpdump -i <uplink_intf> -w /tmp/topology_check.pcap ether proto 0x893a` | tcpdump begins listening for IEEE 1905.1 CMDU frames on the Controller's own interface |
| 3 | Power on and onboard Agent 4 so it forms its backhaul link | Agent 4 begins backhaul association on the configured medium |
| 4 | **[Packet Capture]** Stop capture after onboarding; inspect with `tcpdump -r /tmp/topology_check.pcap -n -v` | Capture shows Topology Discovery, Topology Query, and Topology Response CMDUs, followed by a Topology Notification CMDU received by the Controller announcing Agent 4 |
| 5 | Verify updated device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | rbuscli returns "5", confirming the topology was updated with Agent 4 |
| 6 | Verify Agent 4's identity using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` (Agent 4's new Device instance) | rbuscli returns a valid MAC address uniquely identifying Agent 4, confirming it is correctly represented in the topology |

---

# Test Case 11: EM_Backhaul_DownstreamAgent_MACList_Verification
## Objective
Verify that when Agent 2 forms its backhaul through Agent 1 as an intermediate hop, Agent 1 correctly reports Agent 2's backhaul MAC address, confirming a multi-hop topology.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 1 | Intermediate EasyMesh Agent (already backhauled to Controller) |
| Agent 2 | Downstream EasyMesh Agent (backhauls through Agent 1) |
| Packet Capture | `tcpdump` run locally on Agent 1's downstream-facing backhaul interface |
---
## Pre-Requisites
1. Agent 1 already has an established backhaul link to the Controller.
2. Agent 2 is configured to backhaul through Agent 1 (multi-hop topology).
3. Shell/console access to Agent 1 is available to run `tcpdump`.
4. Agents 3 and 4 are held powered-off / factory-reset so they do not interfere with this multi-hop test.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Agents Under Test | Agent 1 (intermediate), Agent 2 (downstream) |
| Network Topology | Controller <--Backhaul-- Agent 1 <--Backhaul-- Agent 2 |
| Verification Method | rbuscli DataElements get + local tcpdump on Agent 1 |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent 1, start capture on its downstream-facing interface: `tcpdump -i <downstream_intf> -w /tmp/multihop_check.pcap` (add `ether proto 0x893a` for Ethernet, or `ether proto 0x888e` for Wi-Fi) | tcpdump begins listening on Agent 1's downstream backhaul interface |
| 2 | Power on Agent 2 and allow it to form backhaul through Agent 1 | Agent 2 begins backhaul association to Agent 1 on the configured medium |
| 3 | **[Packet Capture]** Stop capture after onboarding; inspect with `tcpdump -r /tmp/multihop_check.pcap -n` | Capture on Agent 1 confirms successful EAPOL handshake (Wi-Fi) or Topology Discovery/Response CMDUs (Ethernet) exchanged between Agent 1 and Agent 2 |
| 4 | Verify downstream MAC list on Agent 1 using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulDownMACAddress` (Agent 1's Device instance) | rbuscli returns a comma-separated list containing Agent 2's backhaul link MAC address |
| 5 | Verify Agent 2's upstream reference using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulALID` (Agent 2's Device instance) | rbuscli returns Agent 1's AL MAC address, confirming Agent 2 correctly identifies Agent 1 as its backhaul provider |
| 6 | Verify overall device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | rbuscli returns 3 (Controller + Agent 1 + Agent 2), confirming the multi-hop topology is fully reflected |

---

# Test Case 12: EM_Backhaul_Wireless_Formation_Negative_InvalidCredentials
## Objective
Verify that a Wi-Fi backhaul link fails to form when Agent 4's bSTA presents invalid credentials, and that the data model correctly reflects the absence of a backhaul link (negative test).
## Test Type
**Negative**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent 4 | EasyMesh Agent intentionally provisioned with an incorrect backhaul passphrase |
| Packet Capture | `tcpdump` run locally on Agent 4's backhaul radio interface (e.g., `wlan1`) |
---
## Pre-Requisites
1. Backhaul BSS is up and advertising normally.
2. Agent 4's bSTA is deliberately configured with an invalid PSK/passphrase for the backhaul BSS.
3. Shell/console access to Agent 4 is available to run `tcpdump`.
4. Agents 1–3 are held powered-off / factory-reset so they do not interfere with this single-Agent test.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul Variant | Wireless (Wi-Fi), invalid credentials |
| Agent Under Test | Agent 4 |
| Verification Method | rbuscli DataElements get + local tcpdump on Agent 4 |
---
## Test Procedure and Expected Results
| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent 4, start capture: `tcpdump -i wlan1 -w /tmp/negative_check.pcap ether proto 0x888e` | tcpdump begins listening for EAPOL frames on Agent 4's backhaul radio interface |
| 2 | Power on Agent 4 with the invalid backhaul passphrase configured | Agent 4 attempts association to the backhaul BSS |
| 3 | **[Packet Capture]** Stop capture after the attempt; inspect with `tcpdump -r /tmp/negative_check.pcap -n -v` | Capture shows EAPOL-Key M1 (and possibly M2) exchanged, but no M3/M4 completion — consistent with a MIC failure due to the credential mismatch |
| 4 | Verify no backhaul MAC is populated using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent 4's Device instance) | rbuscli returns an empty/null value, confirming no backhaul link was successfully formed |
| 5 | Verify Agent 4 is absent from topology using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | rbuscli returns the same device count as before Agent 4's onboarding attempt, confirming the topology was not updated for the failed Agent |
| 6 | Verify BSS backhaul-use flag using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulUse` (Agent 4's bSTA-facing BSS entry) | rbuscli returns "false" for this entry (or the entry is absent), confirming no active backhaul usage was established for Agent 4 |

---
