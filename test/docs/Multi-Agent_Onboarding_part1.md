# Multi-Agent Onboarding
---

## Test Case 1: EM_MultiAgentOnboarding_Sequential3Agents

## Objective

Verify that 3 EasyMesh Agents can successfully complete Multi-AP onboarding (AP-Autoconfiguration Search/Response, WSC M1/M2 exchange, 1905 Ack) to a single Controller when onboarded one at a time, in sequence, and that the Controller's Data Elements model reflects each Agent immediately after it joins.

---

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents (onboarded one at a time) |

---

## Pre-Requisites

1. Controller is powered up and in a clean/reset state (0 onboarded Agents).
2. All 3 Agents are factory-reset (unconfigured / no prior credentials).
3. Controller and Agents share the same 1905.1 AL MAC-reachable backhaul medium (Ethernet/Wi-Fi).
4. Packet capture (tcpdump) tool available on Controller and/or backhaul link for CMDU verification.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Number of Agents | 3 |	
| Onboarding order | Agent 1 → Agent 2 → Agent 3 |
| Onboarding method | AP-Autoconfiguration Search/Response + WSC M1/M2 |
| Wait between onboardings | Sufficient time for one Agent to fully complete before starting the next |
| Query object (count) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |
| Query object (per-device ID) | `Device.WiFi.DataElements.Network.Device.{i}.ID` |
| Query object (onboarding record) | `Device.WiFi.DataElements.Network.Device.{i}.IEEE1905Security.{j}.OnboardingProtocol` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Start packet capture (tcpdump) on Controller/backhaul link. | N/A | Capture is running and ready to record CMDU traffic for the full onboarding sequence. |
| 2 | Query `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries`. | All Agents held in factory-reset/unconfigured state. | Returns 1 (Controller only). |
| 3 | Listen for AP-Autoconfiguration Search CMDU. | Power on Agent 1; Agent 1 broadcasts AP-Autoconfiguration Search. | Controller receives Search, sends AP-Autoconfiguration Response. |
| 4 | Send WSC M2 in response to Agent 1's WSC M1 (AP-Autoconfiguration WSC CMDU). | Agent 1 sends WSC M1, receives WSC M2, applies configuration. | Agent 1 completes onboarding; 1905 Ack exchanged. |
| 5 | Query `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` and `rbuscli get Device.WiFi.DataElements.Network.Device.2.IEEE1905Security.1.OnboardingProtocol`. | N/A | `DeviceNumberOfEntries` = 2 (Controller + Agent 1); `OnboardingProtocol` entry exists for Agent 1. |
| 6 | Repeat Steps 3–5 for Agent 2 (only after Agent 1 onboarding fully completes). | Power on Agent 2. | `DeviceNumberOfEntries` = 3. |
| 7 | Repeat Steps 3–5 for Agent 3. | Power on Agent 3. | `DeviceNumberOfEntries` = 4. |
| 8 | Stop packet capture. | N/A | Capture file saved, covering the complete sequential onboarding window. |
| 9 | Analyze the stopped packet capture for the full sequence: 3× AP-Autoconfiguration Search/Response, 3× WSC M1/M2, 3× 1905 Ack. | N/A | Exactly one complete CMDU sequence per Agent is present, in the same order the Agents were onboarded; no retries, drops, or out-of-order CMDUs. |

---

# Test Case 2: EM_MultiAgentOnboarding_Parallel4Agents

## Objective

Verify that 3 EasyMesh Agents can successfully complete Multi-AP onboarding to a single Controller when powered on and onboarded simultaneously (parallel/near-concurrent CMDU exchanges).

---

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents (powered on together) |

---

## Pre-Requisites

1. Controller is powered up and in a clean/reset state (0 onboarded Agents).
2. All 3 Agents are factory-reset (unconfigured).
3. All Agents connected to the same shared backhaul medium as the Controller.
4. Packet capture tool available on Controller/backhaul to observe concurrent CMDU exchanges.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Number of Agents | 3 |
| Onboarding trigger | All 3 Agents powered on within the same short window |
| Onboarding method | AP-Autoconfiguration Search/Response + WSC M1/M2 |
| Query object (count) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |
| Query object (per-device ID) | `Device.WiFi.DataElements.Network.Device.{i}.ID` |
| Query object (contact freshness) | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Start packet capture (tcpdump) on Controller/backhaul link. | N/A | Capture is running and ready to record concurrent CMDU traffic. |
| 2 | Query `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries`. | All 3 Agents held in factory-reset state. | Returns 1 (Controller only). |
| 3 | Monitor for multiple concurrent AP-Autoconfiguration Search CMDUs. | Power on all 3 Agents simultaneously (or within the same short window). | Controller receives Search CMDUs from all 3 Agents. |
| 4 | Respond to each Agent's AP-Autoconfiguration Search with an AP-Autoconfiguration Response, and process each Agent's WSC M1 with a corresponding WSC M2. | Each Agent sends WSC M1, receives WSC M2, applies configuration independently. | Controller processes all 4 exchanges without dropping, misrouting, or cross-assigning CMDUs between Agents. |
| 5 | Query `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries`. | N/A | Returns 4 (Controller + 3 Agents), matching Test Case 1's end state. |
| 6 | Query `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` for all entries. | N/A | All 3 Agent AL MAC addresses present, each mapped to the correct physical Agent; no CMDU collisions or misattributed entries. |
| 7 | Query `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` for each Agent entry. | N/A | All 3 timestamps fall within the same short onboarding window, confirming near-simultaneous contact with no Agent left un-contacted. |
| 8 | Stop packet capture. | N/A | Capture file saved, covering the complete parallel onboarding window. |
| 9 | Analyze the stopped packet capture for retransmissions/timeouts caused by concurrency. | N/A | No onboarding failures; any retries (if present) still result in successful completion for all 3 Agents. |

---

# Test Case 3: EM_MultiAgentOnboarding_TopologyDeviceCount

## Objective

Verify that after onboarding, the Controller's topology data model reflects exactly 3 onboarded Agents (plus the Controller itself), with each Agent represented by a distinct Device entry.

---

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents (already onboarded) |

---

## Pre-Requisites

1. All 3 Agents have completed onboarding to the Controller .
2. rbuscli is available on the Controller.
3. Packet capture (tcpdump) from the Test Case 1/2 onboarding sequence retained (already started and stopped there), for cross-referencing the reported device count against the actual number of AP-Autoconfiguration/1905 Ack exchanges observed. No new capture is started in this test case — it reuses the retained capture.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Expected total Device entries | 4 (1 Controller + 3 Agents) |
| Query object (count) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |
| Query object (per-entry ID) | `Device.WiFi.DataElements.Network.Device.{i}.ID` |
| Query object (per-entry radio count) | `Device.WiFi.DataElements.Network.Device.{i}.RadioNumberOfEntries` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Query `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries`. | N/A | Returns 4. |
| 2 | Query `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` for i = 1 through 3. | N/A | Returns 4 distinct AL MAC addresses (1 Controller + 3 Agents). |
| 3 | Cross-reference each returned AL MAC address against the known MAC address of each physical Controller/Agent. | N/A | Every entry maps 1:1 to a known device; no unknown or unmapped entries. |
| 4 | Query `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.RadioNumberOfEntries` for each of the 3 Agent entries. | N/A | Each Agent entry reports a non-zero Radio count matching that Agent's actual radio configuration. |
| 5 | Confirm no entry count drift by re-querying `DeviceNumberOfEntries` after a short idle period. | N/A | Count remains 4 (stable, not fluctuating). |
| 6 | Analyze the retained (already-stopped) packet capture from the onboarding run, counting the number of distinct AL MAC addresses that completed a full AP-Autoconfiguration/WSC/1905 Ack sequence. | N/A | Count = 3, matching the number of Agent entries reported by `DeviceNumberOfEntries` minus the Controller. |

---

# Test Case 4: EM_MultiAgentOnboarding_NoDuplicateEntries

## Objective

Verify that no duplicate Agent entries are created in the Controller's topology after all 3 Agents complete onboarding.

---

## Test Type

**Negative**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents (already onboarded) |

---

## Pre-Requisites

1. All 3 Agents have completed onboarding to the Controller.
2. rbuscli available on the Controller.
3. Packet capture (tcpdump) tool available on Controller/backhaul to be started around the topology refresh/poll cycle, to confirm no duplicate Topology Response CMDU processing occurs.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Expected unique AL MAC entries | 4 (Agents only, excluding Controller) |
| Query object | `Device.WiFi.DataElements.Network.Device.{i}.ID` |
| Cross-check object | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Query `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` for all entries. | N/A | Returns 4 entries total (1 Controller + 3 Agents). |
| 2 | Extract the AL MAC address value from each entry and compare against the full list for exact-match duplicates. | N/A | All 4 AL MAC addresses are unique; no two entries share the same MAC address. |
| 3 | Cross-check the count of unique AL MAC addresses against `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries`. | N/A | Unique count equals `DeviceNumberOfEntries` ; no discrepancy indicating a hidden duplicate. |
| 4 | Start packet capture on Controller/backhaul. | N/A | Capture is running and ready to record the topology refresh/poll cycle. |
| 5 | Repeat the query after a topology refresh/poll cycle. | N/A | Duplicate check still passes; no new duplicate entries introduced by a refresh cycle. |
| 6 | Stop packet capture. | N/A | Capture file saved, covering the refresh/poll cycle. |
| 7 | Analyze the stopped packet capture from the Step 5 refresh/poll cycle for repeated/duplicate Topology Response CMDUs from any single Agent. | N/A | Exactly one Topology Response CMDU is processed per Agent per refresh cycle; no duplicate processing that could explain a duplicate topology entry. |

---

# Test Case 5: EM_MultiAgentOnboarding_TopologyRefreshAccuracy

## Objective

Verify that the Controller's topology update/refresh mechanism (triggered by Topology Notification/Topology Query-Response CMDUs) correctly reflects the current number of onboarded Agents and their links after onboarding completes.

---

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents |

---

## Pre-Requisites

1. All 3 Agents have completed onboarding to the Controller.
2. Packet capture tool available to observe Topology Notification / Topology Query / Topology Response CMDUs.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Expected Device entries after refresh | 4 (1 Controller + 3 Agents) |
| Refresh trigger | Topology Notification CMDU (sent by an Agent) or periodic Topology Query/Response |
| Query object (count) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |
| Query object (contact freshness) | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` |
| Query object (link type) | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` |
| Query object (near-end/far-end link MAC) | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress`, `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulMACAddress` |
| Query object (upstream device reference) | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulDeviceID`, `Device.WiFi.DataElements.Network.Device.{i}.BackhaulALID` |
| Query object (backhaul media/rate) | `Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`, `Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Query `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` and record `MultiAPDevice.Backhaul.*` / `BackhaulALID` / `BackhaulMediaType` / `BackhaulPHYRate` for all Agents as baseline. | N/A | Baseline recorded: 4 devices, 3 backhaul links populated (directly to Controller or via another Agent). |
| 2 | Start packet capture on Controller/backhaul. | N/A | Capture is running and ready to record the topology refresh exchange. |
| 3 | Send a Topology Query to each Agent (or wait for an Agent-initiated Topology Notification). | Each Agent responds with a Topology Response CMDU containing its current neighbor/link information. | Controller receives and processes all 3 Topology Response CMDUs. |
| 4 | Stop packet capture. | N/A | Capture file saved, covering the topology refresh exchange. |
| 5 | Re-query `DeviceNumberOfEntries` and per-device `MultiAPDevice.Backhaul.LinkType` / `BackhaulMACAddress` / `MACAddress` after processing responses. | N/A | Device count remains 4; link entries match the physical backhaul connections (Agent-to-Controller or Agent-to-Agent, as applicable). |
| 6 | Query `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulDeviceID` and `Device.WiFi.DataElements.Network.Device.{i}.BackhaulALID` for any Agent connected via a backhaul hop through another Agent (multi-hop topology). | N/A | Fields show the correct upstream Agent's ID/ALID, not the Controller's, for multi-hop Agents. |
| 7 | Query `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` for all 4 entries. | N/A | All timestamps updated to reflect the refresh cycle just performed — no stale (pre-refresh) timestamps remaining. |
| 8 | Analyze the stopped packet capture for the Topology Query/Response (or Topology Notification) exchange, matching each Topology Response CMDU's neighbor/link data to the corresponding `MultiAPDevice.Backhaul.*` fields queried in Steps 5–6. | N/A | The link/relationship data read from the data model matches the link/relationship data actually carried in the captured CMDUs, for all 3 Agents. |


---

# Test Case 6: EM_MultiAgentOnboarding_StaggeredJoin

## Objective

Verify that when 2 Agents are already onboarded and a 3rd Agent joins mid-sequence (staggered onboarding), the Controller correctly onboards the new Agent without disrupting the existing 2 Agents' topology state.

---

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–2 | EasyMesh Agents (already onboarded, active) |
| Agent 3 | EasyMesh Agent (joins after Agents 1–2 are stable) |

---

## Pre-Requisites

1. Agents 1–2 are onboarded and topology is stable (verified via `DeviceNumberOfEntries` = 3).
2. Agent 3 is factory-reset (unconfigured)
3. Packet capture tool available to be started around Agent 3's join, to confirm Agents 1–2 generate no unexpected re-onboarding or CMDU traffic during Agent 3's join.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Pre-existing onboarded Agents | 2 (Agent 1–2) |
| Joining Agent | Agent 3 |
| Trigger | Power on / factory-reset-and-join Agent 3 while Agents 1–2 remain active |
| Query object (count) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |
| Query object (baseline stability) | `Device.WiFi.DataElements.Network.Device.{i}.ID`, `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime`, `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulDeviceID` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Query `DeviceNumberOfEntries` and record `Device.{i}.ID` / `MultiAPDevice.LastContactTime` / `MultiAPDevice.Backhaul.BackhaulDeviceID` for Agents 1–3 as baseline. | Agents 1–3 remain powered on and active. | Returns 3 (Controller + Agents 1–2); baseline recorded. |
| 2 | Start packet capture on Controller/backhaul. | N/A | Capture is running and ready to record Agent 3's join window. |
| 3 | Monitor for AP-Autoconfiguration Search CMDU from Agent 3. | Power on Agent 2. | Controller receives Search CMDU only from Agent 3; no re-Search from Agents 1–2. |
| 4 | Respond to Agent 3 with AP-Autoconfiguration Response and WSC M2. | Agent 3 sends WSC M1, receives WSC M2, applies configuration. | Agent 3 completes onboarding; 1905 Ack exchanged. |
| 5 | Query `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries`. | N/A | Returns 5 (Controller + Agents 1–4). |
| 6 | Stop packet capture. | N/A | Capture file saved, covering Agent 3's full join window. |
| 7 | Re-query `Device.{i}.ID`, `MultiAPDevice.LastContactTime`, and `MultiAPDevice.Backhaul.BackhaulDeviceID` for Agents 1–2. | Agents 1–2 continue normal operation. | Values match the Step 1 baseline — no re-onboarding, disconnection, or link-state change observed for Agents 1–2. |
| 8 | Query `Device.{i}.ID` and `MultiAPDevice.Backhaul.BackhaulDeviceID` for Agent 3's new entry. | N/A | Agent 3 correctly represented with accurate ID and parent link. |
| 9 | Analyze the stopped packet capture covering Agent 3's join window for any AP-Autoconfiguration Search, WSC, or Topology CMDUs originating from Agents 1–2. | N/A | No CMDU traffic is observed from Agents 1–2 during Agent 3's onboarding window, confirming they were not disturbed. |

---

# Test Case 7: EM_MultiAgentOnboarding_ControllerStability4Agents

## Objective

Verify that the Controller onboards 3 Agents (sequential or parallel) without crashing, hanging, or triggering an unintended service/process restart.

---

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents |

---

## Pre-Requisites

1. Controller logging enabled (system log and EasyMesh/Multi-AP process log).
2. Baseline Controller process uptime/PID recorded before onboarding begins.
3. All 3 Agents factory-reset and ready to onboard.
4. Packet capture (tcpdump) tool available on Controller/backhaul, to be started for the full onboarding window and used for root-cause analysis of the CMDU sequence if a crash or restart occurs.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Number of Agents | 3 |
| Onboarding method | Sequential and/or parallel (per Test Case 1 / 2 procedure) |
| Monitored Controller process(es) | EasyMesh Controller / Multi-AP service process |
| Query object (responsiveness check) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Record baseline process PID and uptime of the Controller/Multi-AP service. | N/A | Baseline PID/uptime logged. |
| 2 | Start packet capture on Controller/backhaul. | N/A | Capture is running and ready to record the full onboarding window. |
| 3 | Onboard all 3 Agents (sequential or parallel, per test design). | Agents 1–3 onboard as described in Test Case 1/2. | All 3 Agents complete onboarding successfully. |
| 4 | Stop packet capture. | N/A | Capture file saved, covering the full onboarding window. |
| 5 | Re-check the Controller/Multi-AP service PID and uptime after onboarding completes. | N/A | PID unchanged and uptime continuously increasing — confirms no crash/restart occurred. |
| 6 | Review system logs for crash indicators (segfault, core dump, watchdog restart, process respawn). | N/A | No crash, core dump, or watchdog-triggered restart logged during the onboarding window. |
| 7 | Confirm Controller remains responsive to data-model queries throughout and after onboarding by running `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries`. | N/A | Query responds normally each time, with no timeout, and returns 4 at the end. |
| 8 | Analyze the stopped packet capture covering the full onboarding window for malformed, truncated, or unexpected CMDUs that could correlate with a crash trigger, even if no crash occurred. | N/A | No malformed or anomalous CMDUs observed; capture available as a reference artifact if a crash/restart is later reported. |

---

# Test Case 8: EM_MultiAgentOnboarding_ScalabilityOnboardingTime

## Objective

Verify that onboarding time and onboarding success rate remain consistent as the number of Agents onboarding to the Controller scales from 1 to 3.

---

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents (onboarded incrementally: 1, then 2, then 3) |

---

## Pre-Requisites

1. Controller reset to a clean state before each scale point.
2. Packet capture (tcpdump) tool and/or timestamp capture available, to be started and stopped fresh at each scale point (from first AP-Autoconfiguration Search to final 1905 Ack per Agent).
3. Test repeated at each scale point (1, 2, 3 Agents) with the Controller reset between runs.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Scale points | 1, 2, 3Agents |
| Metric 1 | Per-Agent onboarding time (Search CMDU → final 1905 Ack) |
| Metric 2 | Onboarding success rate (successful onboardings / attempted onboardings) at each scale point |
| Query object (count, per scale point) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |
| Query object (contact timestamp, supplementary timing reference) | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Reset Controller to a clean state (`DeviceNumberOfEntries` = 1). | Prepare 1 factory-reset Agent. | Controller topology has only itself; onboarding attempt begins. |
| 2 | Start packet capture for the 1-Agent scale point. | N/A | Capture is running for this scale point's onboarding window. |
| 3 | Record timestamp of first AP-Autoconfiguration Search received and timestamp of final 1905 Ack; after completion, query `Device.{i}.MultiAPDevice.LastContactTime` for the new entry as a cross-check. | Agent 1 onboards. | Onboarding time for the 1-Agent scale point recorded; onboarding succeeds; `LastContactTime` falls within the measured window. |
| 4 | Stop packet capture for the 1-Agent scale point. | N/A | Capture file saved for this scale point. |
| 5 | Reset Controller; repeat with 2 Agents onboarding (sequential or parallel, as defined by test design) — starting a fresh packet capture at the beginning of this scale point and stopping it at the end (as in Steps 2 and 4), recording per-Agent onboarding time, `LastContactTime`, and success/failure. | Agents 1–2 onboard. | Onboarding times recorded for each Agent; both succeed; capture saved for this scale point. |
| 6 | Repeat Step 5 for 3 Agents, then 3 Agents, resetting the Controller and starting/stopping a fresh packet capture between each scale point. | Agents onboard per scale point. | Onboarding times and success/failure recorded for each Agent at each scale point; a capture file saved per scale point. |
| 7 | Compare average per-Agent onboarding time across all 4 scale points. | N/A | Average onboarding time remains within an acceptable, consistent range across scale points (no significant upward trend as Agent count increases). |
| 8 | Compare onboarding success rate across all 4 scale points. | N/A | Success rate remains 100% (or consistent with the defined pass criteria) at every scale point from 1 to 3 Agents. |
| 9 | Analyze each scale point's stopped packet capture, using its timestamps (first AP-Autoconfiguration Search to final 1905 Ack) as the authoritative onboarding-time measurement, cross-checked against the `LastContactTime` values recorded in Steps 3–6. | N/A | Packet-capture-derived onboarding times are consistent with the `LastContactTime` cross-check at every scale point, confirming the timing data is reliable. |

---

# Test Case 9: EM_MultiAgentOnboarding_TopologyConsistencyAcrossDevices

## Objective

Verify that the topology data model is consistent across the Controller and each of the 3 onboarded Agents — i.e., every device's local view of the Multi-AP network topology matches the Controller's authoritative topology.


## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents (already onboarded) |

---

## Pre-Requisites

1. All 3 Agents onboarded and topology stable on the Controller.
2. rbuscli available on the Controller and on each Agent.
3. Packet capture tool available to be started around the triggered topology refresh (Topology Query/Response CMDUs), to verify Controller/Agent consistency against the actual protocol exchange.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Query object (Controller, count/IDs) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries`, `Device.WiFi.DataElements.Network.Device.{i}.ID` |
| Query object (Controller, identity) | `Device.WiFi.DataElements.Network.ControllerID` |
| Query object (each Agent, local view) | Equivalent local `Device.WiFi.DataElements.Network.Device.{i}.ID` instance on that Agent |
| Query object (capability confirmation) | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPCapabilities`, `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.EasyMeshAgentOperationMode` |
| Consistency check | Device count and device list must match between Controller and each Agent's local data model |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Query `DeviceNumberOfEntries`, the full `Device.{i}.ID` list, and `ControllerID` on the Controller. | N/A | Controller reports 4 devices (Controller + 3 Agents), each with a distinct AL MAC address; `ControllerID` matches the Controller's own `Device.{i}.ID` entry. |
| 2 | N/A | On Agent 1, query the local `Device.WiFi.DataElements.Network.Device.{i}.ID` data model for its known topology (Controller + peer Agents, as visible to that Agent). | Agent 1's local view lists the same set of devices as the Controller (or the subset it is expected to be aware of, per implementation). |
| 3 | N/A | Repeat Step 2 on Agent 2 and Agent 3. | Each Agent's local topology view matches the Controller's authoritative topology for the devices it is expected to track. |
| 4 | Compare the AL MAC address values reported by the Controller against the AL MAC address values reported locally by each Agent. | N/A | AL MAC addresses match exactly between the Controller and each Agent — no mismatched or stale MAC values. |
| 5 | Query `Device.{i}.MultiAPDevice.EasyMeshAgentOperationMode` for each Agent entry on the Controller. | Each Agent confirms its own operating mode locally. | Reported as `Running` for all 3 Agents, consistent on both sides. |
| 6 | Start packet capture on Controller/backhaul. | N/A | Capture is running and ready to record the topology refresh exchange. |
| 7 | Trigger a topology refresh (Topology Query/Response) and re-verify consistency across all 5 devices. | Each Agent responds to the Topology Query. | Consistency is maintained after refresh; no drift between Controller and any Agent's local data model. |
| 8 | Stop packet capture. | N/A | Capture file saved, covering the topology refresh exchange. |
| 9 | Analyze the stopped packet capture from the Step 6–8 refresh, confirming each Agent both sent and received a Topology Response/Query CMDU. | N/A | All 3 Agents show a complete request/response exchange in the capture, corroborating the consistency result read from the data model. |

---

# Test Case 10: EM_MultiAgentOnboarding_ReOnboardingNoDuplicate

## Objective

Verify that when an already-onboarded Agent is factory-reset and re-joins the Multi-AP network, the Controller replaces/updates the existing topology entry for that Agent rather than creating a duplicate entry.

---

## Test Type

**Negative**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1–3 | EasyMesh Agents (all onboarded); Agent 4 is factory-reset and re-onboarded |

---

## Pre-Requisites

1. All 3 Agents onboarded and topology stable (`DeviceNumberOfEntries` = 4).
2. Agent 4's original AL MAC address (`Device.{i}.ID`) recorded before factory reset.
3. Packet capture (tcpdump) tool available on Controller/backhaul, to be started before Agent 3's disconnect and stopped after re-onboarding completes.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Agent under test | Agent 3 |
| Action | Factory reset Agent 3, then allow it to rejoin the Controller |
| Expected post-condition | `DeviceNumberOfEntries` remains 4; only 1 entry exists for Agent 3's AL MAC address |
| Query object (count) | `Device.WiFi.DataElements.Network.DeviceNumberOfEntries` |
| Query object (per-device ID) | `Device.WiFi.DataElements.Network.Device.{i}.ID` |
| Query object (freshness after re-onboard) | `Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` |
| Query object (onboarding record) | `Device.WiFi.DataElements.Network.Device.{i}.IEEE1905Security.{i}.OnboardingProtocol` |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Expected Result |
|-------------|-----------|-------|-----------------|
| 1 | Query `DeviceNumberOfEntries` and record Agent 4's current `Device.{i}.ID` (AL MAC address). | Agents 1–3 onboarded and active. | Returns 4; Agent 3's AL MAC address recorded as baseline. |
| 2 | Start packet capture on Controller/backhaul. | N/A | Capture is running and ready to record Agent 3's disconnect and re-onboarding. |
| 3 | N/A | Factory-reset Agent 3. | Agent 3 clears its configuration and disconnects from the Controller. |
| 4 | Query `DeviceNumberOfEntries` immediately after Agent 3 disconnects/times out. | N/A | Controller either retains a stale entry for Agent 4 pending timeout, or removes it, per implementation-defined behavior — document actual behavior observed. |
| 5 | Monitor for AP-Autoconfiguration Search CMDU from Agent 3 rejoining. | Agent 3 powers back on (factory-reset state) and initiates onboarding. | Controller processes Agent 3's rejoin as a new onboarding attempt using the same AL MAC address as before. |
| 6 | Respond to Agent 3's WSC M1 with WSC M2 and complete onboarding. | Agent 3 completes onboarding, applies new configuration. | Onboarding completes successfully; 1905 Ack exchanged. |
| 7 | Stop packet capture. | N/A | Capture file saved, covering Agent 3's full disconnect-through-re-onboarding window. |
| 8 | Query `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries`. | N/A | Returns 4 (Controller + 3 Agents) — not 5. |
| 8 | Query all `Device.WiFi.DataElements.Network.Device.{i}.ID` entries and check for duplicate AL MAC addresses matching Agent 3's known address. | N/A | Exactly one entry exists with Agent 3's AL MAC address; no duplicate/stale second entry present. |
| 10 | Query `Device.{i}.MultiAPDevice.LastContactTime` and `Device.{i}.IEEE1905Security.{i}.OnboardingProtocol` for Agent 3's re-onboarded entry. | N/A | `LastContactTime` is refreshed to the re-onboarding time (not the original onboarding time), and the onboarding record is repopulated — confirming the Controller updated the existing entry rather than leaving stale data untouched. |
| 9 | Analyze the stopped packet capture spanning Agent 3's factory reset through re-onboarding, confirming exactly one AP-Autoconfiguration Search/Response and one WSC M1/M2 exchange for Agent 3's AL MAC address. | N/A | Only a single, complete re-onboarding CMDU sequence is observed for Agent 3's AL MAC address — no duplicate or overlapping onboarding attempts that could explain a duplicate topology entry. |

---
