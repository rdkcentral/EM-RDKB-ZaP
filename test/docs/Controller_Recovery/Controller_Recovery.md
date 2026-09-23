# Test Case 1: EM_ControllerRecovery_AgentReconnection

## Objective

Verify that onboarded EasyMesh Agents automatically reconnect after Controller reboot, topology and IEEE 1905 connectivity are restored, and recovery completes within the configured KPI.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 180 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-----------|-----------------|
| 1 | Record the baseline topology using RDKB-CLI and DataElements via `rbuscli get Device.WiFi.DataElements.Network.Topology` | Start IEEE 1905 packet capture on each Extender. | Baseline topology is recorded and packet capture is started on all Extenders. |
| 2 | Reboot the Controller. | Start per-Extender timers at reboot trigger: capture **t0-Ext1**, **t0-Ext2**, and **t0-Ext3**. | Controller reboot is triggered and per-Extender **t0** timestamps are recorded. |
| 3 | Verify Controller reachability. If the Controller is not reachable, wait 5 seconds and retry until it becomes accessible. | N/A | Controller becomes reachable after reboot. If the Controller remains unreachable beyond the KPI threshold, mark the test case as **Failed**. |
| 4 | Verify that the EasyMesh and IEEE 1905 services are operational. If any service is not operational, wait 5 seconds and retry until all required services are running. | N/A | EasyMesh and IEEE 1905 services are running and ready to accept all Extender connections. |
| 5 | Verify direct Extender backhaul re-association using `brctl show <bridge_intf>` and `iw dev <sta_intf> station dump`. | On the parent Extender of the daisy-chained Extender, verify child Extender association using `brctl show <bridge_intf>` and `iw dev <sta_intf> station dump`. Verify that the backhaul link is operational using `iw dev <mesh_bh_intf> link`. For each Extender, stop the timer when the link shows connected and capture **t1-ExtN**. | Directly connected Extenders are associated with the Controller, the daisy-chained Extender is associated with its parent Extender, all backhaul links are operational, and per-Extender **t1** timestamps are captured. |
| 6 | N/A | Stop IEEE 1905 packet capture on each Extender. | Packet capture is stopped successfully on each Extender after backhaul connection is established. |
| 7 | Re-read the topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology` | N/A | Topology matches the baseline with no missing, stale, or duplicate entries. |
| 8 | Analyze IEEE 1905 packet captures from each Extender. | N/A | Topology Query and Topology Response messages are exchanged successfully following Controller recovery across all Extenders. |
| 9 | Compare per-Extender recovery duration (**t1-ExtN − t0-ExtN**) against the KPI threshold. | N/A | Recovery time for each Extender is less than **180 seconds**. |

---

# Test Case 2: EM_ControllerRecovery_ClientContinuity

## Objective

Verify that a client connected to an onboarded EasyMesh Agent maintains or automatically regains network connectivity following a Controller reboot, while ensuring the Agent successfully re-establishes its connection to the Controller, topology information is correctly restored, and recovery is completed within the defined KPI threshold.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Wi-Fi Client | 3 Associated STAs (one STA per Extender) |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and all 3 Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. Each Extender has one associated client (total 3 STAs).
4. All Extenders and all 3 STAs are visible in the Controller topology.
5. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 180 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Controller, 3 Extenders, and 3 associated STAs in an active EasyMesh Hybrid topology |
| Client Connectivity Checks | Continuous ping to Gateway IP and `8.8.8.8` from each STA |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Associated STA | Expected Result |
|-------------|------------|-----------|----------------|-----------------|
| 1 | Record baseline topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology` | Verify client association on all Extenders using `iw dev <mld_if> station dump`. Start IEEE 1905 packet capture on each Extender. | Verify each STA is connected to its mapped Extender. | Baseline topology is recorded and all Extenders show associated client STAs in station dump output. |
| 2 | N/A | N/A | Start continuous ping to Gateway IP and `8.8.8.8` from each STA, and keep monitoring. | Started continuous ping from STAs associated with each Extender. |
| 3 | Reboot the Controller. | Start per-Extender timers at reboot trigger: capture **t0-Ext1**, **t0-Ext2**, and **t0-Ext3**. | Continue both pings without stopping. | Controller reboot starts and per-Extender **t0** timestamps are recorded while ping monitoring remains active. |
| 4 | Verify Controller reachability. If the Controller is not reachable, wait 5 seconds and retry until it becomes accessible. | N/A | Continue both pings without stopping. | Controller becomes reachable after reboot. If the Controller remains unreachable beyond the KPI threshold, mark the test case as **Failed**. |
| 5 | Verify that the EasyMesh and IEEE 1905 services are operational. If any service is not operational, wait 5 seconds and retry until all required services are running. | N/A | Continue ping monitoring. | EasyMesh and IEEE 1905 services are running and ready to accept all Extender connections. |
| 6 | Verify direct Extender backhaul re-association using `brctl show <bridge_intf>` and `iw dev <sta_intf> station dump`. | On the parent Extender of the daisy-chained Extender, verify child Extender association using `brctl show <bridge_intf>` and `iw dev <sta_intf> station dump`. Verify that the backhaul link is operational using `iw dev <mesh_bh_intf> link`. For each Extender, stop the timer when the link shows connected and capture **t1-ExtN**. | Continue ping monitoring. | Directly connected Extenders are associated with the Controller, the daisy-chained Extender is associated with its parent Extender, all backhaul links are operational, and per-Extender **t1** timestamps are captured. |
| 7 | N/A | Verify client association again on all Extenders using `iw dev <mld_if> station dump`. | Continue ping monitoring. | All Extenders show client STA association in station dump output. |
| 8 | N/A | Stop IEEE 1905 packet capture on each Extender. | Stop ping monitoring and save outputs. | Packet capture is stopped successfully on each Extender after backhaul connection is established. |
| 9 | Re-read topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology` | N/A | N/A | Topology matches baseline with no missing, stale, or duplicate entries for all Extenders and associated STAs. |
| 10 | Analyze IEEE 1905 packet captures from each Extender. | N/A | N/A | Topology Query/Response messages are exchanged for each Extender. |
| 11 | Compare per-Extender recovery duration (**t1-ExtN − t0-ExtN**) against KPI. | N/A | N/A | Recovery time for each Extender is less than 180 seconds. |
| 12 | N/A | N/A | Check ping statistics for Gateway and `8.8.8.8` from all STAs. | Ping may show temporary unreachable responses during Controller reboot, but ping traffic must recover successfully after Controller recovery for all Extenders and associated STAs. |

---

# Test Case 3: EM_ControllerRecovery_DaisyChainTopology

## Objective

Verify that a Daisy Chain EasyMesh topology is restored after Controller reboot, with parent-child relationships and multi-hop backhaul paths recovered within the configured KPI.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Daisy Chain |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Daisy Chain EasyMesh topology is operational with active backhaul connections.
2. EasyMesh and IEEE 1905 services are running on all devices.
3. Parent and Child Agents are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 180 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Daisy-chain topology with Controller and 3 Extenders connected in parent-child relationships. |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-----------|-----------------|
| 1 | Record the baseline topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology` | Start IEEE 1905 packet capture on each Extender. | Baseline topology is recorded and all Extenders are present with correct parent-child relationships. Packet capture is started on all Extenders. |
| 2 | Reboot the Controller. | Start per-Extender timers at reboot trigger: capture **t0-Ext1**, **t0-Ext2**, and **t0-Ext3**. | Controller reboot is triggered and per-Extender **t0** timestamps are recorded. |
| 3 | Verify Controller reachability. If the Controller is not reachable, wait 5 seconds and retry until it becomes accessible. | N/A | Controller becomes reachable after reboot. If the Controller remains unreachable beyond the KPI threshold, mark the test case as **Failed**. |
| 4 | Verify that the EasyMesh and IEEE 1905 services are operational. If any service is not operational, wait 5 seconds and retry until all required services are running. | N/A | EasyMesh and IEEE 1905 services are running and ready to accept all Extender connections. |
| 5 | Verify the Controller's direct child Extender association using `brctl show <bridge_intf>` and `iw dev <sta_intf> station dump`. | N/A | The Controller shows its immediate child Extender as associated, confirming successful controller-side backhaul re-association. |
| 6 | N/A | On each Extender, verify the association of its direct child Extender using `brctl show <bridge_intf>` and `iw dev <sta_intf> station dump`. Verify the backhaul link status using `iw dev <mesh_bh_intf> link`. For each Extender, stop the timer when the backhaul link shows connected and record **t1-ExtN**. | Each Extender shows its immediate child Extender as associated, all multi-hop backhaul links are connected across the Daisy Chain path, and per-Extender **t1-ExtN** timestamps are captured. |
| 7 | N/A | Stop IEEE 1905 packet capture on each Extender. | Packet capture is stopped successfully on each Extender after backhaul connection is established. |
| 8 | Re-read the topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology` | N/A | Topology matches the baseline with no missing, stale, or duplicate entries, and all Extenders retain correct parent-child relationships. |
| 9 | Analyze IEEE 1905 packet captures from each Extender. | N/A | Topology Query and Topology Response messages are exchanged successfully following Controller recovery, and topology synchronization is completed for all Extenders. |
| 10 | Compare per-Extender recovery duration (**t1-ExtN − t0-ExtN**) against the KPI threshold. | N/A | Recovery time for each Extender is less than **180 seconds**. |

---

# Test Case 4: EM_ControllerRecovery_WiredBackhaul

## Objective

Verify that Agents connected to the Controller over an Ethernet (wired) backhaul reconnect and restore topology after a Controller reboot within the configured KPI.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents (Wired backhaul) |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extenders are onboarded with active Ethernet (wired) backhaul connections.
2. EasyMesh and IEEE 1905 services are running on all devices.
3. All Agents are visible in the Controller topology over the wired backhaul.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 180 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Backhaul Type | Ethernet (Wired) |
| DataElements | Device.WiFi.DataElements.Network.Topology <br> Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Ethernet Backhaul topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record baseline topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Read `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`. | Start IEEE 1905 packet capture on each Extender. | Baseline topology is recorded with wired backhaul links and `BackhaulMediaType` values are available for active links. |
| 2 | Reboot the Controller. | Start per-Extender timers at reboot trigger: **t0-Ext1**, **t0-Ext2**, and **t0-Ext3**. | Controller reboot is triggered and per-Extender **t0** timestamps are recorded. |
| 3 | Verify Controller reachability. If the Controller is not reachable, wait 5 seconds and retry until it becomes accessible. | N/A | Controller becomes reachable after reboot. If the Controller remains unreachable beyond KPI threshold, mark the test case as **Failed**. |
| 4 | Verify that the EasyMesh and IEEE 1905 services are operational. If any service is not operational, wait 5 seconds and retry until all required services are running. | N/A | EasyMesh and IEEE 1905 services are running and ready to accept all Extender connections. |
| 5 | Verify Extender re-association using wired Backhaul links | Verify BH link status for each Extender and capture **t1-ExtN** when each wired backhaul link is connected. | Re-association is restored for all Extenders and per-Extender **t1** timestamps are captured. |
| 6 | N/A | Stop IEEE 1905 packet capture on each Extender. | Packet capture is stopped successfully on each Extender after wired backhaul recovery verification. |
| 7 | Re-read topology and verify `BackhaulMediaType` values for active backhaul links using `rbuscli get Device.WiFi.DataElements.Network.Topology` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType` | N/A | Topology reflects correct wired parent-child links and media type remains Ethernet for all active links. |
| 8 | Analyze IEEE 1905 packet captures from each Extender and correlate Ethernet media type in IEEE 1905 messages with `BackhaulMediaType`. | N/A | Topology Query and Topology Response messages are exchanged successfully for each Extender, and IEEE 1905 media type is consistent with `BackhaulMediaType`. |
| 9 | Compare per-Extender recovery duration (**t1-ExtN − t0-ExtN**) against KPI requirement. | N/A | Recovery time for each Agent is less than 180 seconds. |

---

# Test Case 5: EM_ControllerRecovery_ConsecutiveReboots

## Objective

Verify that onboarded EasyMesh Agents automatically reconnect following multiple consecutive Controller reboot cycles, and that the topology, IEEE 1905 connectivity, and network services are fully restored after the final reboot without topology inconsistencies, stale states, or service degradation.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on all devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 180 seconds (Final Cycle) |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Reboot Cycles | 5 consecutive Controller reboot cycles |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record the baseline topology using RDKB CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology` | Start IEEE 1905 packet capture on each Extender. | Baseline topology is recorded and packet capture is started on all Extenders. |
| 2 | Reboot the Controller (Cycle 1). | Wait for Controller recovery. | Controller reboot is initiated successfully. |
| 3 | Verify Controller reachability and EasyMesh/IEEE 1905 service status. If not operational, wait 5 seconds and retry until recovery is complete. | N/A | Controller becomes reachable and all required services are operational. |
| 4 | Repeat Steps 2 and 3 for Cycles 2, 3, and 4. | N/A | Controller recovers successfully after each reboot cycle. |
| 5 | Reboot the Controller (Cycle 5). | Start per-Extender timers at reboot trigger: capture **t0-Ext1**, **t0-Ext2**, and **t0-Ext3**. | Controller reboot is triggered and per-Extender **t0** timestamps are recorded. |
| 6 | Verify Controller reachability. If the Controller is not reachable, wait 5 seconds and retry until it becomes accessible. | N/A | Controller becomes reachable after reboot. If the Controller remains unreachable beyond the KPI threshold, mark the test case as **Failed**. |
| 7 | Verify that the EasyMesh and IEEE 1905 services are operational. If any service is not operational, wait 5 seconds and retry until all required services are running. | N/A | EasyMesh and IEEE 1905 services are running and ready to accept all Extender connections. |
| 8 | Verify direct Extender backhaul re-association using `brctl show <bridge_intf>` and `iw dev <sta_intf> station dump`. | On the parent Extender of the daisy-chained Extender, verify child Extender association using `brctl show <bridge_intf>` and `iw dev <sta_intf> station dump`. Verify that the backhaul link is operational using `iw dev <mesh_bh_intf> link`. For each Extender, stop the timer when the link shows connected and capture **t1-ExtN**. | Directly connected Extenders are associated with the Controller, the daisy-chained Extender is associated with its parent Extender, all backhaul links are operational, and per-Extender **t1** timestamps are captured. |
| 9 | N/A | Stop IEEE 1905 packet capture on each Extender. | Packet capture is stopped successfully on each Extender after backhaul connection is established. |
| 10 | Re-read the topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology` | N/A | Topology matches the baseline with no missing, stale, or duplicate entries. |
| 11 | Analyze IEEE 1905 packet captures from each Extender. | N/A | Topology Query and Topology Response messages are exchanged successfully following Controller recovery across all Extenders. |
| 12 | Compare per-Extender recovery duration (**t1-ExtN − t0-ExtN**) against KPI threshold. | N/A | Recovery time for each Extender is less than **180 seconds** and no service degradation, stale topology entries, or accumulated recovery issues are observed after five consecutive Controller reboot cycles. |

---

