### Topology: 1 Controller + 3 Agents (Agent-1, Agent-2, Agent-3)

---

# Test Case 1: EM_Topology_Baseline_DeviceCount

## Objective

Verify the baseline number of devices maintained in the Controller's topology for the full 1 Controller + 3 Agent deployment.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1 | Onboarded EasyMesh Agent |
| Agent-2 | Onboarded EasyMesh Agent |
| Agent-3 | Onboarded EasyMesh Agent |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. All 3 Agents (Agent-1, Agent-2, and Agent-3) are already onboarded and stable in the network.
3. DataElements object is accessible through rbuscli on the Controller.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller + 3 onboarded Agents (4 total devices) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Get device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Value returned is **4**, matching the Controller + 3 Agents currently in the network. |
| 2 | Get each device identifier using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` for all 4 instances | Each of the 4 instances returns a unique MAC Address (1905 AL MAC): 1 for the Controller, 1 for Agent-1, 1 for Agent-2, and 1 for Agent-3. |

---

# Test Case 2: EM_Topology_AgentAddition_NewDeviceEntry

## Objective

Verify that when Agent-3 joins the EasyMesh network, a corresponding Device.{i} entry is dynamically created in the Controller's topology with correct identification.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent-1, Agent-2 | Already onboarded EasyMesh Agents |
| Agent-3 | Un-onboarded EasyMesh Agent to be added |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. Agent-1 and Agent-2 are onboarded to the network.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | rbuscli DataElements get + tcpdump |
| Network Topology | Controller + Agent-1/Agent-2 (existing) + Agent-3 (new) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Query baseline count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Returns baseline value **3** (Controller + Agent-1 + Agent-2). |
| 2 | Start packet capture on Controller: `tcpdump -i eth0_virt_peer ether proto 0x893a -w /tmp/topo_agent3_add.pcap` | Capture starts successfully and runs during onboarding. |
| 3 | Power on Agent-3 and trigger onboarding (WPS/DPP push button or credentials) | Agent-3 completes onboarding and joins the Multi-AP network. |
| 4 | Wait 5 seconds for topology propagation | Topology update is processed by the Controller. |
| 5 | Verify updated device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Value increments to **4** (Controller + 3 Agents), confirming Agent-3's entry was added. |
| 6 | Verify new device ID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` (Agent-3's new instance) | Returns Agent-3's 1905 AL MAC Address, matching the physically added device. |
| 7 | Verify Agent operation mode using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.EasyMeshAgentOperationMode` (Agent-3's instance) | Returns "Running", confirming the Agent role is active. |
| 8 | Stop packet capture | Captured pcap shows a Topology Notification/Topology Discovery frame from Agent-3's AL MAC. |

---

# Test Case 3: EM_Topology_AgentBackhaulPopulation

## Objective

Verify that Backhaul link details are correctly populated in the Controller's topology for all 3 Agents.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-2, Agent-3 | Onboarded EasyMesh Agents with known backhaul connections |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. All 3 Agents (Agent-1, Agent-2, Agent-3) are onboarded.
3. Each Agent is connected via a known backhaul medium (e.g., Wi-Fi or Ethernet).

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Expected Backhaul LinkType | Wi-Fi / Ethernet (as per physical setup) |
| Verification Method | rbuscli DataElements get |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify Agent-1 backhaul link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-1's instance) | Returns the correct medium matching Agent-1's physical backhaul connection. |
| 2 | Verify Agent-1 backhaul MAC address using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-1's instance) | Returns a valid MAC address corresponding to Agent-1's backhaul interface. |
| 3 | Verify Agent-1 upstream backhaul device MAC using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulMACAddress` (Agent-1's instance) | Returns the MAC address of the device Agent-1 connected through. |
| 4 | Verify Agent-2 backhaul link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-2's instance) | Returns the correct medium matching Agent-2's physical backhaul connection. |
| 5 | Verify Agent-2 backhaul MAC address using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-2's instance) | Returns a valid MAC address corresponding to Agent-2's backhaul interface. |
| 6 | Verify Agent-2 upstream backhaul device MAC using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulMACAddress` (Agent-2's instance) | Returns the MAC address of the device Agent-2 connected through. |
| 7 | Verify Agent-3 backhaul link type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-3's instance) | Returns the correct medium matching Agent-3's physical backhaul connection. |
| 8 | Verify Agent-3 backhaul MAC address using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-3's instance) | Returns a valid MAC address corresponding to Agent-3's backhaul interface. |
| 9 | Verify Agent-3 upstream backhaul device MAC using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulMACAddress` (Agent-3's instance) | Returns the MAC address of the device Agent-3 connected through. |
| 10 | Verify last contact time for all 3 Agents using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` | All 3 Agents show recent timestamps, confirming active control protocol contact. |

---

# Test Case 4: EM_Topology_AgentRemoval_GracefulDeregistration

## Objective

Verify that when one Agent (Agent-3) is gracefully removed from the network, its Device.{i} entry is removed from the Controller's topology.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-2 | Agents remaining in the network |
| Agent-3 | Agent to be removed |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. All 3 Agents are onboarded and stable.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | rbuscli DataElements get + tcpdump |
| Removal Method | Factory reset / administrative de-registration of Agent-3 |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify pre-removal device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Value is **4** (Controller + Agent-1 + Agent-2 + Agent-3). |
| 2 | Verify Agent-3's current Backhaul MAC using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-3's instance) | Returns a valid MAC address prior to removal. |
| 3 | Start packet capture on Controller: `tcpdump -i eth0_virt_peer ether proto 0x893a -w /tmp/topo_agent3_remove.pcap` | Capture starts successfully. |
| 4 | Trigger removal of Agent-3 (factory reset or administratively de-register from Controller UI/CLI) | Agent-3 is removed from the network; connection is terminated. |
| 5 | Wait 5 seconds for topology propagation | Topology update is processed; Controller updates its Device table. |
| 6 | Verify updated device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Value decrements to **3** (Controller + Agent-1 + Agent-2). |
| 7 | Verify Agent-3's Device instance is removed by querying its previous index | `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-3's former index) returns an error (non-existent instance). |
| 8 | Verify Agent-1 and Agent-2 are intact using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` | Both Agent-1 and Agent-2 return valid, unchanged AL MAC Addresses. |
| 9 | Stop packet capture | Captured pcap shows a Topology Notification from the Controller reflecting Agent-3's removal. |

---


# Test Case 5: EM_Topology_BackhaulRecovery_LinkFailover

## Objective

Verify that when an Agent's backhaul link is interrupted and recovers, the Controller detects the reconnection and updates the backhaul path information.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-2 | Backhaul Access Point for Agent-3 |
| Agent-3 | Agent with backhaul link to be interrupted |

---

## Pre-Requisites

1. Controller and all 3 Agents are onboarded and stable.
2. Agent-3 is connected via Wi-Fi or Ethernet backhaul to Agent-1 or Agent-2 (or Controller).
3. Network is at baseline state: Controller + 3 Agents.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | rbuscli DataElements get + tcpdump |
| Failure Trigger | Disconnect Agent-3's backhaul (Wi-Fi or Ethernet) and reconnect |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Start packet capture on Controller: `tcpdump -i eth0_virt_peer ether proto 0x893a -w /tmp/topo_backhaul_recovery.pcap` | Capture starts successfully. |
| 2 | Verify Agent-3's pre-interruption backhaul information using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulMACAddress` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.LinkType` (Agent-3's instance) | Returns Agent-3's upstream device MAC and valid LinkType (Wi-Fi/Ethernet). |
| 3 | Interrupt Agent-3's backhaul link (e.g., disconnect Wi-Fi or unplug Ethernet cable from Agent-3 or its upstream device)`ip link set <wlan_iface> down` / `ip link set <eth_iface> down` | Agent-3 loses connection to its upstream backhaul device. |
| 4 | Wait 10 seconds for the Controller to detect the backhaul disconnection event | Controller processes the link loss; Agent-3 may attempt to reconnect via another path or wait for link recovery. |
| 5 | Restore Agent-3's backhaul link (e.g., re-connect Wi-Fi or re-plug Ethernet cable) | Agent-3 re-establishes connection to the backhaul network. |
| 6 | Wait 10 seconds for backhaul re-establishment | Control protocol re-establishes multi-AP communication via the restored link. |
| 7 | Verify Agent-3 remains in the topology using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Value is **4** (Agent-3 not removed despite transient backhaul loss). |
| 8 | Verify Agent-3's Last Contact Time is recent using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` (Agent-3's instance) | Timestamp reflects the post-recovery re-establishment. |
| 9 | Verify Agent-3's backhaul information post-recovery using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.BackhaulMACAddress` and `LinkType` (Agent-3's instance) | Returns valid backhaul information; may be the same or different upstream MAC (depending on failover behavior). |
| 10 | Stop packet capture | Captured pcap shows Topology Notification/Discovery frames reflecting Agent-3's backhaul recovery. |

---

# Test Case 6: EM_Topology_Refresh_OnDemandQuery

## Objective

Verify that an on-demand Topology Refresh accurately updates the Controller's DataElements to reflect the current 1 Controller + 3 Agent network state.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-2, Agent-3 | All 3 onboarded Agents |

---

## Pre-Requisites

1. Controller and all 3 Agents are onboarded and stable.
2. Network is at baseline state: Controller + 3 Agents.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | rbuscli DataElements get + tcpdump |
| Refresh Trigger | 1905 Topology Query / Topology Discovery exchange |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Start packet capture on Controller: `tcpdump -i eth0_virt_peer ether proto 0x893a -w /tmp/topo_refresh.pcap` | Capture starts successfully. |
| 2 | Trigger a topology refresh via: `meshctl topology-query` or equivalent CLI/REST API | Controller sends Topology Query frames to all 3 known 1905 Agent devices. |
| 3 | Wait 5 seconds for responses to arrive | Topology responses are processed. |
| 4 | Verify updated device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Value returns **4** (Controller + Agent-1 + Agent-2 + Agent-3), accurately reflecting the current active topology. |
| 5 | Verify each device's identity using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` for all 4 instances | Each of the 4 active devices returns a valid, current AL MAC Address with no stale/duplicate entries. |
| 6 | Verify Last Contact Time refreshed using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` for all 3 Agent instances | All 3 Agents show updated (recent) timestamps following the refresh exchange. |
| 7 | Stop packet capture | Captured pcap confirms Topology Query and corresponding Topology Response frames exchanged between the Controller and all 3 Agents' AL MACs. |

---

# Test Case 7: EM_Topology_Refresh_RadioAndBSSConsistency

## Objective

Verify that Radio and BSS-level identifiers remain consistent and accurate across all 3 Agents after a topology refresh.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-2, Agent-3 | All 3 onboarded Agents with active Radios/BSS |

---

## Pre-Requisites

1. Controller and all 3 Agents are onboarded and stable.
2. Each of the 3 Agents has at least one active Radio and BSS configured.
3. Network is at baseline state: Controller + 3 Agents.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | rbuscli DataElements get |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Trigger topology refresh using: `meshctl topology-query` or equivalent | Controller initiates Topology Query/Response exchange with all 3 Agents. |
| 2 | Wait 5 seconds for responses to be processed | Topology data is updated. |
| 3 | Verify Radio identifiers using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ID` for all Radio instances across Agent-1, Agent-2, and Agent-3 | Each Radio instance returns a unique, valid Radio identifier; values are unchanged from pre-refresh baseline. |
| 4 | Verify BSS identifiers using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BSSID` for all BSS instances across Agent-1, Agent-2, and Agent-3 | Each BSS instance returns a valid BSSID consistent with SSIDs currently broadcast; values are unchanged from pre-refresh baseline. |
| 5 | Verify no duplicate Radio IDs exist across all 3 Agents by comparing all returned values | All Radio.{i}.ID values across Agent-1, Agent-2, and Agent-3 are unique; no collisions. |
| 6 | Verify no duplicate BSS BSSIDs exist across all 3 Agents by comparing all returned values | All BSS BSSIDs across all 3 Agents are unique; no duplicates or stale entries. |

---

# Test Case 8: EM_Topology_MultipleAgents_SimultaneousPresence

## Objective

Verify that when all 3 Agents (Agent-1, Agent-2, and Agent-3) are present and active simultaneously in the Controller's topology, their Device entries are correctly tracked without duplication or loss.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-2, Agent-3 | All 3 EasyMesh Agents active in the network |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh services are running.
2. All 3 Agents are onboarded and present in the network.
3. DataElements object is accessible through rbuscli on the Controller.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Number of Agents | 3 (Agent-1, Agent-2, and Agent-3) |
| Verification Method | rbuscli DataElements get |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Query device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Returns value **4** (Controller + Agent-1 + Agent-2 + Agent-3). |
| 2 | Verify each Agent's ID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` for all 3 Agent instances | Each instance returns a distinct, valid AL MAC Address — one for Agent-1, one for Agent-2, one for Agent-3; no shared IDs. |
| 3 | Verify Agent-1 operation mode using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.EasyMeshAgentOperationMode` (Agent-1's instance) | Returns "Running". |
| 4 | Verify Agent-2 operation mode using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.EasyMeshAgentOperationMode` (Agent-2's instance) | Returns "Running". |
| 5 | Verify Agent-3 operation mode using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.EasyMeshAgentOperationMode` (Agent-3's instance) | Returns "Running". |
| 6 | Query all Agents' Last Contact Time using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.LastContactTime` | All 3 Agents show recent timestamps, confirming active multi-AP control protocol contact. |
| 7 | Verify backhaul information is present for all 3 Agents using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` | All 3 Agents return valid backhaul MAC addresses. |

---

# Test Case 9: EM_Topology_AgentRemoval_QueryNonExistentDevice

## Objective

Verify that querying a Device instance that no longer exists returns a proper error rather than stale or incorrect data.

## Test Type

**Negative**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Agent-1, Agent-2 | Agents remaining in the topology |
| Agent-3 | Agent that will be removed |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. All 3 Agents are initially onboarded and stable.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Verification Method | rbuscli DataElements get |

---

## Test Procedure and Expected Results

| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify Agent-3's Backhaul MAC exists before removal using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-3's instance) | Returns a valid MAC address, confirming the instance exists. |
| 2 | Remove Agent-3 from the network (factory reset or administrative de-registration) | Agent-3 is removed from the topology. |
| 3 | Wait 5 seconds for topology propagation | Controller updates its Device table; Agent-3's Device instance is deleted. |
| 4 | Query removed Agent-3's Backhaul MAC using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.Backhaul.MACAddress` (Agent-3's former instance) | rbuscli returns an error/failure response (e.g., "Non-existent parameter/instance" or "CCSP error"), confirming Agent-3's entry is fully purged. |
| 5 | Query removed Agent-3's Radio using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ID` (Agent-3's former instance) | rbuscli returns an error/failure response, confirming child objects (Radios) were removed along with Agent-3's parent Device instance. |
| 6 | Query removed Agent-3's MultiAPDevice information using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.MultiAPDevice.EasyMeshAgentOperationMode` (Agent-3's former instance) | rbuscli returns an error/failure response, confirming the entire Agent entry is no longer accessible. |
| 7 | Verify remaining device count using `rbuscli get Device.WiFi.DataElements.Network.DeviceNumberOfEntries` | Value is **3** (Controller + Agent-1 + Agent-2), confirming only Agent-3 was removed. |
| 8 | Verify Agent-1 and Agent-2 instances are accessible using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.ID` | Both agents return valid AL MAC Addresses; no errors. |

---

