# EM_BackhaulFailover — Test Cases
### Topology: 1 Controller + 3 Agents (Agent-1, Agent-2, Agent-3)

# Test Case 1: EM_BackhaulFailover_Baseline_EthernetActive

## Objective

Verify the baseline state where Ethernet backhaul is the active link on Agent-2, confirming LinkType, MAC endpoints, and stats are all healthy before the failover test begins, while Agent-1, Agent-3 remain stable on their own backhauls.

## Test Type 

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1 | Onboarded EasyMesh Agent, stable backhaul, not involved in failover |
| Agent-2 | EasyMesh Agent with both Ethernet backhaul (active) and Wi-Fi backhaul (standby) provisioned — failover DUT |
| Agent-3 | Onboarded EasyMesh Agent, stable backhaul, not involved in failover |

---

## Prerequisites

1. Full topology is established: Controller + Agent-1 + Agent-2 + Agent-3 (device count = 4).
2. Agent-2 is onboarded with Ethernet as the active backhaul, and holds valid Wi-Fi backhaul credentials as standby.
3. Agent-1, Agent-3 are onboarded and stable on their own (non-failover) backhaul links.
4. DataElements object is accessible through rbuscli on the Controller.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Backhaul State | Agent-2: Ethernet active |
| Verification Method | rbuscli DataElements get |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-2's Device instance) | rbuscli returns "Ethernet", confirming Agent-2's active backhaul is wired |
| 2 | Verify media type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType` (Agent-2's instance) | rbuscli returns an Ethernet media type ("IEEE 802.3u" or "IEEE 802.3ab") |
| 3 | Verify backhaul endpoints using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulMACAddress` (Agent-2's instance) | Both return valid, non-null MAC addresses for Agent-2's Ethernet link |
| 4 | Verify Wi-Fi backhaul is standby but ready using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BackhaulSta.MACAddress` (Agent-2's instance) | rbuscli returns a valid MAC address for the logical backhaul STA, confirming Agent-2's Wi-Fi standby path exists and is ready to take over |
| 5 | Record baseline device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | rbuscli returns **4** (Controller + Agent-1 + Agent-2 + Agent-3), the healthy baseline topology size, to be used for continuity checks in later steps |
| 6 | Confirm Agent-1, Agent-3 backhaul is unrelated to this test using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` for each of the three instances | Each returns its own stable, unchanged LinkType, confirming they are not part of the Ethernet/Wi-Fi failover scenario under test |

---

# Test Case 2: EM_BackhaulFailover_EthernetDisconnect_WirelessActivation_KPI

## Objective

Verify that disconnecting Agent-2's active Ethernet backhaul triggers automatic activation of the Wi-Fi backhaul link, that failover completes within the 60-second KPI, and that Agent-1, Agent-3 are unaffected.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-3 | Onboarded Agents, stable backhaul throughout, used as isolation check |
| Agent-2 | EasyMesh Agent with Ethernet active (per Test Case 1) — failover DUT |
| Packet Capture | `tcpdump` run locally on Agent-2's backhaul radio interface (e.g., `wlan1`) |

---

## Pre-Requisites

1. Baseline verified per Test Case 1 (Agent-2: Ethernet active, LinkType = "Ethernet"; full topology count = 4).
2. Shell/console access to Agent-2 is available to run `tcpdump` and `date`.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Trigger | Physical disconnection of Agent-2's Ethernet cable |
| KPI (Key Performance Indicator) | Failover < 60 seconds |
| Verification Method | rbuscli DataElements get (polled) + local tcpdump timestamp correlation |

---

## Test Procedure and Expected Results

| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent-2, start capture: `tcpdump -i wlan1 -w /tmp/failover_activation.pcap ether proto 0x888e` | tcpdump begins listening for EAPOL frames on Agent-2's backhaul radio interface |
| 2 | Record disconnect time `T0=$(date +%s)`, then physically disconnect Agent-2's Ethernet backhaul cable | Agent-2's Ethernet link goes down at T0; Agent-1, Agent-3,  are physically untouched |
| 3 | Poll `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-2's instance) at short intervals until the value changes; record the timestamp `T1=$(date +%s)` when it returns "Wi-Fi" | rbuscli reports Agent-2's LinkType transitioning from "Ethernet" to "Wi-Fi" |
| 4 | Compute elapsed time `T1 - T0` | Elapsed time is less than 60 seconds, satisfying the failover KPI |
| 5 | [Packet Capture] Stop capture; inspect with `tcpdump -r /tmp/failover_activation.pcap -n -v` | Capture shows EAPOL-Key frames (M1–M4) on `wlan1` completing the 4-Way Handshake, with the frame timestamps falling within the T0–T1 window, corroborating the rbuscli-reported failover time |
| 6 | Verify backhaul MAC updated using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-2's instance) | rbuscli returns a MAC address consistent with the Wi-Fi backhaul BSS, confirming Agent-2's active link is now wireless |
| 7 | Confirm Agent-1, Agent-3 remain unaffected using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` for each instance | Each of the three returns the same LinkType as their Test Case 1 baseline, confirming Agent-2's failover did not disturb the rest of the topology |

---

# Test Case 3: EM_BackhaulFailover_Wireless_Stats_Verification

## Objective

Verify that once Wi-Fi backhaul is active on Agent-2 following failover, the DataElements data model correctly reports link-quality and traffic statistics for the new active link.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-3 | Onboarded Agents, unaffected by the Agent-2 failover |
| Agent-2 | EasyMesh Agent with Wi-Fi backhaul now active (per Test Case 2) — failover DUT |

---

## Pre-Requisites

1. Agent-2's Wi-Fi backhaul is confirmed active per Test Case 2.
2. Client traffic is flowing through Agent-2.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Backhaul State | Agent-2: Wi-Fi active (post-failover) |
| Verification Method | rbuscli DataElements get |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify signal strength using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.SignalStrength` (Agent-2's instance) | rbuscli returns a valid dBm RCPI value, confirming Agent-2's Wi-Fi backhaul link is passing measurable radio stats |
| 2 | Verify byte counters using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.BytesSent` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.BytesReceived` (Agent-2's instance) | Both counters return non-zero, increasing values, confirming traffic is flowing over Agent-2's new active Wi-Fi backhaul |
| 3 | Verify data rates using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.LastDataDownlinkRate` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.LastDataUplinkRate` (Agent-2's instance) | Both return non-zero kbps values consistent with the negotiated Wi-Fi backhaul link speed |
| 4 | Verify link utilization using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.LinkUtilization` (Agent-2's instance) | rbuscli returns a valid percentage value for Agent-2's active Wi-Fi medium |
| 5 | Verify BSS backhaul-use flag using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulUse` (Agent-2's backhaul BSS instance) | rbuscli returns "true", confirming this BSS is actively serving as Agent-2's backhaul |
| 6 | Spot-check Agent-1, Agent-3 backhaul stats remain nominal using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.SignalStrength` for each | Each returns a stable value consistent with its own backhaul baseline, confirming no side effects from Agent-2's failover |

---

# Test Case 4: EM_BackhaulFailover_EthernetRestore_Recovery_KPI

## Objective

Verify that restoring Agent-2's Ethernet backhaul link after a failover causes it to return to Ethernet as the active backhaul path within the 60-second recovery KPI, without affecting Agent-1, Agent-3.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-3 | Onboarded Agents, stable backhaul throughout, used as isolation check |
| Agent-2 | EasyMesh Agent currently on Wi-Fi backhaul  — failover DUT |
| Packet Capture | `tcpdump` run locally on Agent-2's Ethernet backhaul interface (e.g., `eth0`) |

---

## Pre-Requisites

1. Agent-2 is currently active on Wi-Fi backhaul following the disconnect scenario.
2. Shell/console access to Agent-2 is available to run `tcpdump` and `date`.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Trigger | Physical reconnection of Agent-2's Ethernet cable |
| KPI | Recovery < 60 seconds |
| Verification Method | rbuscli DataElements get (polled) + local tcpdump timestamp correlation |

---

## Test Procedure and Expected Results

| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent-2, start capture: `tcpdump -i eth0 -w /tmp/recovery_check.pcap ether proto 0x893a` | tcpdump begins listening for IEEE 1905.1 CMDU frames on Agent-2's Ethernet interface |
| 2 | Record reconnect time `T0=$(date +%s)`, then physically reconnect Agent-2's Ethernet backhaul cable | Agent-2's Ethernet link comes back up at T0 |
| 3 | Poll `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-2's instance) at short intervals until the value returns to "Ethernet"; record the timestamp `T1=$(date +%s)` | rbuscli reports Agent-2's LinkType transitioning back from "Wi-Fi" to "Ethernet" |
| 4 | Compute elapsed time `T1 - T0` | Elapsed time is less than 60 seconds, satisfying the recovery KPI |
| 5 | **[Packet Capture]** Stop capture; inspect with `tcpdump -r /tmp/recovery_check.pcap -n -v` | Capture shows Topology Discovery/Query/Response CMDUs on `eth0` with frame timestamps falling within the T0–T1 window, corroborating the rbuscli-reported recovery time |
| 6 | Verify backhaul MAC updated using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-2's instance) | rbuscli returns a MAC address matching Agent-2's Ethernet interface, confirming the active link has returned to wired |
| 7 | Confirm Agent-1, Agent-3 remain unaffected using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` for each instance | Each of the three returns the same LinkType as their established baseline, confirming Agent-2's recovery did not disturb the rest of the topology |

---

# Test Case 5: EM_BackhaulFailover_WirelessStandby_Deactivation

## Objective

Verify that once Agent-2 returns to Ethernet backhaul, its previously-active Wi-Fi backhaul link is correctly marked as no longer in use (returns to standby), avoiding a dual-active state, while Agent-1, Agent-3 remain unaffected.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-3 | Onboarded Agents, unaffected by the Agent-2 recovery |
| Agent-2 | EasyMesh Agent that has just recovered to Ethernet — failover DUT |

---

## Pre-Requisites

1. Agent-2's Ethernet backhaul recovery is confirmed per Test Case 4.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Backhaul State | Agent-2: Ethernet active, Wi-Fi returned to standby |
| Verification Method | rbuscli DataElements get |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify BSS backhaul-use flag using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulUse` (Agent-2's Wi-Fi backhaul BSS instance used during failover) | rbuscli returns "false", confirming Agent-2's Wi-Fi backhaul BSS is no longer marked in-use |
| 2 | Verify link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-2's instance) | rbuscli returns "Ethernet", confirming only one backhaul medium is reported active for Agent-2 |
| 3 | Verify Wi-Fi backhaul STA is still provisioned (not torn down, only idled) using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BackhaulSta.MACAddress` (Agent-2's instance) | rbuscli returns a valid MAC address, confirming Agent-2's Wi-Fi standby path remains available for a future failover |
| 4 | Confirm Agent-1, Agent-3 BSS backhaul-use flags are unchanged using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BackhaulUse` for their respective backhaul BSS instances | Each returns the same value as its established baseline, confirming no unintended change to their backhaul-use state |

---

# Test Case 6: EM_BackhaulFailover_PreferredBackhaul_ReturnToPath

## Objective

Verify that when a preferred backhaul link is configured via SetPreferredBackhauls() for Agent-2, Agent-2 returns to that preferred path (Ethernet) rather than remaining on Wi-Fi once Ethernet is restored, and that this configuration has no effect on Agent-1, Agent-3.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-3| Onboarded Agents, not targeted by this preferred-backhaul configuration |
| Agent-2 | EasyMesh Agent capable of both Ethernet and Wi-Fi backhaul — failover DUT |

---

## Pre-Requisites

1. Ethernet is the intended preferred backhaul path for Agent-2.
2. Agent-2 is currently active on Wi-Fi backhaul.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Command | `Device.WiFi.DataElements.Network.SetPreferredBackhauls()` |
| Input | BackhaulMACAddress = Agent-2's Ethernet interface MAC, bSTAMACAddress = Agent-2's Ethernet-side identifier |
| Verification Method | rbuscli DataElements set/get |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Configure preference using `rbuscli set Device.WiFi.DataElements.Network.SetPreferredBackhauls() BackhaulMACAddress=<Agent-2 Ethernet MAC> bSTAMACAddress=<Agent-2 identifier>` | Command is accepted for asynchronous execution, scoped to Agent-2 only |
| 2 | Verify entry stored using `rbuscli get Device.WiFi.DataElements.Network.PreferredBackhauls.{i}.BackhaulMACAddress` | rbuscli returns the Agent-2 Ethernet MAC address submitted, confirming the preferred backhaul link is recorded |
| 3 | Reconnect the Ethernet cable on Agent-2 (currently active on Wi-Fi) | Agent-2's Ethernet link comes back up |
| 4 | Poll `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-2's instance) until it stabilizes | rbuscli returns "Ethernet", confirming Agent-2 returned to the configured preferred path rather than remaining on Wi-Fi |
| 5 | Verify backhaul MAC matches the preferred entry using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-2's instance) | rbuscli returns the same MAC address configured in `PreferredBackhauls.{i}.BackhaulMACAddress`, confirming preference precedence was honored for Agent-2 |
| 6 | Confirm Agent-1, Agent-3 backhaul preference is untouched using `rbuscli get Device.WiFi.DataElements.Network.PreferredBackhauls.{i}.BackhaulMACAddress` for any entries associated with them | No entries exist (or existing entries are unchanged) for Agent-1, Agent-3, confirming the preferred-backhaul configuration was scoped only to Agent-2 |

---

# Test Case 7: EM_BackhaulFailover_Topology_Continuity

## Objective

Verify that during Agent-2's Ethernet-to-Wi-Fi failover and subsequent recovery, Agent-2's identity is retained in the Controller's topology (no false device removal/re-addition), even though the backhaul medium changes — and that the overall 1 Controller + 3 Agent topology count remains stable throughout.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-3 | Onboarded Agents, stable throughout, contributing to the total device count |
| Agent-2 | EasyMesh Agent undergoing failover and recovery |

---

## Pre-Requisites

1. Baseline device count (4) and Agent-2's Device ID recorded.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | rbuscli DataElements get, sampled at each workflow stage |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Record Agent-2's Device ID and total count before failover using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` (Agent-2's instance) and `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | rbuscli returns Agent-2's MAC-based ID and total count **4** (Controller + Agent-1 + Agent-2 + Agent-3) |
| 2 | Disconnect Agent-2's Ethernet, allow Wi-Fi failover to complete, then re-check `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` (Agent-2's instance) and `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | rbuscli returns the same Device ID for Agent-2 and the same total count **4**, confirming Agent-2's topology entry persisted across the medium change rather than being removed and re-added |
| 3 | Verify continuity of upstream reference using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulALID` (Agent-2's instance) | rbuscli returns the same Controller ALID as before failover, confirming logical continuity of the mesh relationship |
| 4 | Confirm Agent-1, Agent-3 Device IDs are unchanged using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` for each | Each returns the same MAC-based ID as its established baseline, confirming none of the three were affected by Agent-2's medium change |
| 5 | Restore Agent-2's Ethernet and re-check `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` (Agent-2's instance) and `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | rbuscli again returns the same Device ID for Agent-2 and total count **4**, confirming topology stability through both transitions |

---

# Test Case 8: EM_BackhaulFailover_LastContactTime_KPI_CrossCheck

## Objective

Cross-verify the failover and recovery KPIs for Agent-2 using the Controller's own record of last contact, independent of the LinkType polling method, and confirm Agent-1, Agent-3 last-contact times are undisturbed.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-3 | Onboarded Agents, used as isolation check |
| Agent-2 | EasyMesh Agent undergoing failover and recovery |



## Test Configuration

| Parameter | Value |
|-----------|-------|
| Parameter Under Test | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` |
| KPI(Key Performance Indicator) | Failover < 60 seconds, Recovery < 60 seconds |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Immediately after Agent-2's Ethernet disconnect (T0 from Test Case 2), poll `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` (Agent-2's instance) until it updates to a timestamp later than T0 | The updated LastContactTime reflects the Controller's next successful contact with Agent-2 over the new Wi-Fi backhaul |
| 2 | Compute the difference between the updated LastContactTime and T0 | The difference is less than 60 seconds, cross-confirming the failover KPI measured in Test Case 2 |
| 3 | Immediately after Agent-2's Ethernet reconnect, poll `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` (Agent-2's instance) until it updates again | The updated LastContactTime reflects the Controller's next successful contact with Agent-2 over the restored Ethernet backhaul |
| 4 | Compute the difference between this updated LastContactTime and the recovery T0 | The difference is less than 60 seconds, cross-confirming the recovery KPI measured in Test Case 4 |
| 5 | Confirm Agent-1, Agent-3 LastContactTime values remain on their normal reporting cadence using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` for each | Each returns a recent, steadily-updating timestamp consistent with normal operation, confirming the Agent-2 failover/recovery events did not delay or disrupt Controller contact with the other three Agents |

---

# Test Case 9: EM_BackhaulFailover_ClientTraffic_Continuity

## Objective

Verify that client traffic through Agent-2 experiences no more than a brief interruption during backhaul failover, correlating local packet capture with the DataElements traffic counters, while client traffic through Agent-1, Agent-3 is unaffected.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-3 | Onboarded Agents, each with an associated client generating independent baseline traffic, used as isolation check |
| Agent-2 | EasyMesh Agent with an active client generating continuous traffic — failover DUT |
| Packet Capture | `tcpdump` run locally on Agent-2's LAN-facing (client-side) interface |

---

## Pre-Requisites

1. A client is associated to Agent-2 and generating continuous traffic (e.g., ICMP ping or iperf stream) directed off-network through the backhaul.
2. Clients associated to Agent-1, Agent-3 are each generating their own independent baseline traffic.
3. Shell/console access to Agent-2 is available to run `tcpdump`.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | Local tcpdump gap analysis + rbuscli DataElements get |

---

## Test Procedure and Expected Results

| Step Number | Controller/Agent | Expected Result |
|-------------|------------|-----------------|
| 1 | On Agent-2, start capture on the client-facing interface: `tcpdump -i <lan_intf> -w /tmp/client_continuity.pcap` while client traffic is running | tcpdump records the ongoing client traffic stream with per-packet timestamps |
| 2 | Disconnect Agent-2's Ethernet backhaul to trigger failover, and keep the client traffic running throughout on all three Agents | Failover to Wi-Fi backhaul proceeds on Agent-2 as in Test Case 2; Agent-1, Agent-3 continue passing their own client traffic without interruption |
| 3 | [Packet Capture] Stop capture after failover stabilizes; inspect with `tcpdump -r /tmp/client_continuity.pcap -tttt` | Capture timestamps show a gap in successfully forwarded packets no larger than the measured failover time, confirming Agent-2's client traffic resumed once the Wi-Fi backhaul came up |
| 4 | Verify traffic resumed on the new path using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.BytesSent` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.BytesReceived` (Agent-2's instance) | Both counters continue incrementing post-failover, confirming Agent-2's client traffic is flowing over the new active backhaul link |
| 5 | Verify Agent-1, Agent-3 traffic counters show no gap using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.Stats.BytesSent` and `...BytesReceived` for each | Each of the three shows continuously incrementing counters across the entire Agent-2 failover window, confirming their client traffic was never interrupted |

---

