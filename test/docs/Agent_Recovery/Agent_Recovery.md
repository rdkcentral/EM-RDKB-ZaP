# Test Case 1: EM_AgentRecovery_ControllerRediscovery

## Objective

Verify that all onboarded EasyMesh Extenders automatically recover after reboot, reconnect to the Controller, restore IEEE 1905 connectivity, rebuild topology information, and complete recovery within the configured KPI.

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
2. EasyMesh and IEEE 1905 services are running on the Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible through `rbuscli`.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 120 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record the baseline topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Start IEEE 1905 packet capture. | N/A | Baseline topology is recorded and packet capture is started. |
| 2 | Capture **t0** (timer start) at the instant the Extender reboot is initiated. | Reboot all Extenders simultaneously. | All Extenders reboot successfully and **t0** is recorded on the Controller. |
| 3 | N/A | Wait for all Extenders to complete the boot-up sequence. | All Extenders complete boot-up and become reachable. |
| 4 | N/A | Verify that EasyMesh and IEEE 1905 services are operational on all Extenders. If any service is not operational, wait 5 seconds and retry until all required services are running. | EasyMesh and IEEE 1905 services are operational on all Extenders. |
| 5 | Record **t1-Ext1**, **t1-Ext2**, and **t1-Ext3** when the backhaul link of each Extender is successfully re-established. | Verify that the backhaul link of each extender is operational using `iw dev <mesh_backhaul_intf> link`. | All Extenders have an active backhaul connection to their respective parent nodes, and individual recovery timestamps are recorded. |
| 6 | Verify reachability of all Extenders from the Controller using `ping <extender_ip>`. | N/A | All Extenders are reachable from the Controller. If any Extender is unreachable, mark the test case as **Failed**. |
| 7 | Stop IEEE 1905 packet capture. | N/A | Packet capture is stopped successfully. |
| 8 | Re-read the topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Compare the recovered topology against the baseline topology. | N/A | All Extenders are present in the topology with correct connectivity information. No missing, stale, or duplicate entries are observed. |
| 9 | Analyze the captured IEEE 1905 packets. | N/A | Topology Query and Topology Response messages are exchanged successfully between controller and all the extenders. |
| 10 | Compare the measured recovery duration (**t1-ExtN − t0**) for each Extender against the KPI threshold. | N/A | Recovery time for each Extender is less than **120 seconds**. |

---

# Test Case 2: EM_AgentRecovery_ParentAgent_DaisyChainTopology

## Objective

Verify that a parent Agent in a Daisy Chain topology recovers successfully after reboot and that downstream Agents become reachable again through the restored hierarchy.

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

1. Daisy Chain topology is operational.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 120 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Daisy-chain topology with 1 Controller and 3 Extenders connected in parent-child relationships |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record baseline Daisy Chain topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Start IEEE 1905 packet capture. | N/A | Baseline topology is recorded and packet capture is started on the Controller. |
| 2 | Record **t0** (timer start) at reboot trigger time for the Parent Extender. | Reboot the Parent Extender. | Parent Extender reboot is triggered and **t0** is recorded on the Controller. |
| 3 | N/A | Wait for the Parent Extender to complete the boot-up sequence. | Parent Extender completes boot-up and becomes reachable. |
| 4 | N/A | Verify that EasyMesh and IEEE 1905 services are operational on the Parent Extender. If any service is not operational, wait 5 seconds and retry until all required services are running. | EasyMesh and IEEE 1905 services are operational on the Parent Extender. |
| 5 | Record **t1-Parent** when the Parent Extender backhaul link is successfully re-established. | Verify that the Parent Extender backhaul link is operational using `iw dev <mesh_backhaul_intf> link`. | Parent Extender has an active backhaul connection to the Controller and **t1-Parent** is recorded. |
| 6 | Verify reachability of the Parent Extender and all affected downstream Extenders from the Controller using `ping <extender_ip>`. | N/A | Parent Extender and all downstream Extenders are reachable from the Controller. If any Extender is unreachable, mark the test case as **Failed**. |
| 7 | Stop IEEE 1905 packet capture. | N/A | Packet capture is stopped successfully. |
| 8 | Re-read the topology using RDKB-CLI and DataElements via `rbuscli get Device.WiFi.DataElements.Network.Topology`. Now compare with the baseline parent-child hierarchy. | N/A | Daisy Chain hierarchy and backhaul paths are restored correctly with no missing, stale, or duplicate entries. |
| 9 | Analyze the captured IEEE 1905 packets. | N/A | Topology Query and Topology Response messages are exchanged successfully following Parent Extender recovery. |
| 10 | Compare the measured recovery duration (**t1-Parent − t0**) against the KPI threshold. | N/A | Parent Extender recovery time is less than **120 seconds**. |

---

# Test Case 3: EM_AgentRecovery_AllAgents_DaisyChainTopology

## Objective

Verify that all Agents in a Daisy Chain topology recover successfully after simultaneous Agent reboot and that the original Daisy Chain hierarchy is restored.

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

1. Daisy Chain topology is operational.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 120 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Daisy-chain topology with 1 Controller and 3 Extenders connected in parent-child relationships |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record baseline Daisy Chain topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Start IEEE 1905 packet capture. | N/A | Baseline topology is recorded and packet capture is started on the Controller. |
| 2 | Record common **t0** (timer start) at the instant simultaneous reboot is triggered. | Reboot all Extenders simultaneously. | All Extenders reboot successfully and common **t0** is recorded on the Controller. |
| 3 | N/A | Wait for all Extenders to complete the boot-up sequence. | All Extenders complete boot-up and become reachable. |
| 4 | N/A | Verify that EasyMesh and IEEE 1905 services are operational on all Extenders. If any service is not operational, wait 5 seconds and retry until all required services are running. | EasyMesh and IEEE 1905 services are operational on all Extenders. |
| 5 | Record **t1-Ext1**, **t1-Ext2**, and **t1-Ext3** when the backhaul link of each Extender is successfully re-established. | Verify that the backhaul link of each Extender is operational using `iw dev <mesh_backhaul_intf> link`. | All Extenders have an active backhaul connection to their respective parent nodes, and individual recovery timestamps **(t1-ExtN)** are recorded. |
| 6 | Verify reachability of all Extenders from the Controller using `ping <extender_ip>`. | N/A | All Extenders are reachable from the Controller. If any Extender is unreachable, mark the test case as **Failed**. |
| 7 | Stop IEEE 1905 packet capture. | N/A | Packet capture is stopped successfully. |
| 8 | Re-read the topology using RDKB-CLI and DataElements via `rbuscli get Device.WiFi.DataElements.Network.Topology`. Compare with the baseline Daisy Chain hierarchy. | N/A | Daisy Chain hierarchy and backhaul paths are restored correctly with no missing, stale, or duplicate entries. |
| 9 | Analyze the captured IEEE 1905 packets. | N/A | Topology Query and Topology Response messages are exchanged successfully following Extender recovery. |
| 10 | Compare the measured recovery duration (**t1-ExtN − t0**) against the KPI threshold. | N/A | Recovery time for each Extender is less than **120 seconds**. |

---

# Test Case 4: EM_AgentRecovery_ChildAgent_DaisyChainTopology

## Objective

Verify that when a single mid-chain child Agent reboots while its parent and the Controller remain operational, the child Agent rejoins the Daisy Chain, downstream Agents behind it are restored, and recovery completes within the configured KPI.

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

1. A Daisy Chain topology is operational with a parent Agent, a mid-chain child Agent, and downstream Agents.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 120 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Daisy-chain topology with 1 Controller and 3 Extenders connected in parent-child relationships |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record baseline Daisy Chain topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Start IEEE 1905 packet capture. | N/A | Baseline topology is recorded and packet capture is started on the Controller. |
| 2 | Record **t0** (timer start) at reboot trigger time for the Child Extender. | Reboot the mid-chain Child Extender while keeping the Parent Extender and downstream Extenders operational. | Child Extender reboot is triggered and **t0** is recorded on the Controller. |
| 3 | N/A | Wait for the Child Extender to complete the boot-up sequence. | Child Extender completes boot-up and becomes reachable. |
| 4 | N/A | Verify that EasyMesh and IEEE 1905 services are operational on the Child Extender. If any service is not operational, wait 5 seconds and retry until all required services are running. | EasyMesh and IEEE 1905 services are operational on the Child Extender. |
| 5 | Record **t1-Child** when the Child Extender backhaul link is successfully re-established. | Verify that the Child Extender backhaul link is operational using `iw dev <mesh_backhaul_intf> link`. | Child Extender backhaul link to its Parent Extender is operational and **t1-Child** is recorded. |
| 6 | Verify reachability of the Child Extender and all affected downstream Extenders from the Controller using `ping <extender_ip>`. | N/A | Child Extender and all affected downstream Extenders are reachable from the Controller. If any Extender is unreachable, mark the test case as **Failed**. |
| 7 | Stop IEEE 1905 packet capture. | N/A | Packet capture is stopped successfully. |
| 8 | Re-read the topology using RDKB-CLI and DataElements via `rbuscli get Device.WiFi.DataElements.Network.Topology`. Compare with the baseline branch hierarchy. | N/A | Parent-child hierarchy and backhaul paths are restored correctly for the rebooted branch with no missing, stale, or duplicate entries. |
| 9 | Analyze the captured IEEE 1905 packets. | N/A | Topology Query and Topology Response messages are exchanged successfully following Child Extender recovery. |
| 10 | Compare the measured recovery duration (**t1-Child − t0**) against the KPI threshold. | N/A | Child Extender recovery time is less than **120 seconds**. |

---

# Test Case 5: EM_AgentRecovery_WiredBackhaul

## Objective

Verify that an onboarded EasyMesh Extender connected through an Ethernet (wired) backhaul successfully recovers after reboot, re-establishes wired backhaul and IEEE 1905 connectivity, restores topology information, and completes recovery within the configured KPI.

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

1. All Agents are onboarded with an active Ethernet (wired) backhaul connection.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 120 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Backhaul Type | Ethernet (Wired) |
| DataElements | Device.WiFi.DataElements.Network.Topology <br> Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType |
| Network Topology | Controller and 3 Extenders in an active EasyMesh wired backhaul topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record baseline topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Start IEEE 1905 packet capture. | N/A | Baseline topology is recorded and packet capture is started on the Controller. |
| 2 | Record **t0** (timer start) at reboot trigger time. | Reboot all wired Extenders simultaneously. | All wired Extenders reboot successfully and **t0** is recorded on the Controller. |
| 3 | N/A | Wait for all wired Extenders to complete the boot-up sequence. | All wired Extenders complete boot-up and become reachable. |
| 4 | N/A | Verify that EasyMesh and IEEE 1905 services are operational on all wired Extenders. If any service is not operational, wait 5 seconds and retry until all required services are running. | EasyMesh and IEEE 1905 services are operational on all wired Extenders. |
| 5 | Record **t1-Ext1**, **t1-Ext2**, and **t1-Ext3** when the wired backhaul connection of each Extender is successfully re-established. Verify wired backhaul type using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`. | Verify that the wired backhaul interface link is operational on all Extenders. | Backhaul media type is reported as Ethernet for all Extenders, wired backhaul links are operational, Extenders are successfully re-associated, and per-Extender **t1** timestamps are recorded. |
| 6 | Verify reachability of all Extenders from the Controller using `ping <extender_ip>`. | N/A | All Extenders are reachable from the Controller. If any Extender is unreachable, mark the test case as **Failed**. |
| 7 | Stop IEEE 1905 packet capture. | N/A | Packet capture is stopped successfully. |
| 8 | Re-read the topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Compare the recovered topology against the baseline topology. | N/A | Topology matches the baseline with no missing, stale, or duplicate entries. |
| 9 | Analyze the captured IEEE 1905 packets. | N/A | Topology Query and Topology Response messages are exchanged successfully following recovery of all wired Extenders. |
| 10 | Compare the measured recovery duration (**t1-ExtN − t0**) for each Extender against the KPI threshold. | N/A | Recovery time for each Extender is less than **120 seconds**. |

---

# Test Case 6: EM_AgentRecovery_ConsecutiveReboots

## Objective

Verify that an Agent recovers reliably and within the configured KPI across multiple consecutive reboots, with no cumulative degradation or stale-state buildup over repeated recovery cycles.

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

1. The target Agent is onboarded with an active EasyMesh backhaul connection.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 120 seconds (each cycle) |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Reboot Cycles | Multiple consecutive reboots (5 cycles) |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record the baseline topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Start IEEE 1905 packet capture. | N/A | Baseline topology is recorded and packet capture is started on the Controller. |
| 2 | Trigger reboot of the target Extender (Cycle 1). | Reboot the target Extender. | Extender reboot is initiated successfully. |
| 3 | N/A | Verify Extender boot completion and EasyMesh/IEEE 1905 service status. If any service is not operational, wait 5 seconds and retry until recovery is complete. | Extender becomes operational and all required services are running. |
| 4 | Repeat Steps 2 and 3 for Cycles 2, 3, and 4. | N/A | Extender recovers successfully after each reboot cycle. |
| 5 | Record **t0-Cycle5** (timer start) at reboot trigger time. | Reboot the target Extender (Cycle 5). | Extender reboot is triggered and **t0-Cycle5** is recorded on the Controller. |
| 6 | N/A | Wait for the Extender to complete the boot-up sequence. | Extender completes boot-up and becomes reachable. |
| 7 | N/A | Verify that EasyMesh and IEEE 1905 services are operational on the rebooted Extender. If any service is not operational, wait 5 seconds and retry until all required services are running. | EasyMesh and IEEE 1905 services are operational on the Extender. |
| 8 | Record **t1-Cycle5** when the Extender backhaul link is successfully re-established. | Verify that the Extender backhaul link is operational using `iw dev <mesh_backhaul_intf> link`. | Extender backhaul link is operational and **t1-Cycle5** is recorded. |
| 9 | Verify reachability of the recovered Extender from the Controller using `ping <extender_ip>`. | N/A | The Extender is reachable from the Controller. If the Extender is unreachable, mark the test case as **Failed**. |
| 10 | Stop IEEE 1905 packet capture. | N/A | Packet capture is stopped successfully. |
| 11 | Re-read the topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. | N/A | Topology matches the baseline with no missing, stale, or duplicate entries after the final reboot cycle. |
| 12 | Analyze the captured IEEE 1905 packets. | N/A | Topology Query and Topology Response messages are exchanged successfully during Extender recovery. |
| 13 | Compare the measured recovery duration (**t1-Cycle5 − t0-Cycle5**) against the KPI threshold. | N/A | Recovery time is less than **120 seconds** and no service degradation, stale topology entries, or accumulated recovery issues are observed after five consecutive Extender reboot cycles. |

---

# Test Case 7: EM_AgentRecovery_PartialSimultaneousReboot

## Objective

Verify that when a subset of Agents (more than one, but not all) reboot simultaneously while the remaining Agents stay operational, all rebooted Agents rejoin and topology fully restores within the configured KPI.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents (a subset rebooted, the remaining Agents stay up) |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Multiple Agents are onboarded with active EasyMesh backhaul connections.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | Less than 120 seconds |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Recovery Trigger | Simultaneous reboot of a subset of Agents (remaining Agents stay up) |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record baseline topology using RDKB-CLI and DataElements using `rbuscli get Device.WiFi.DataElements.Network.Topology`. Start IEEE 1905 packet capture. | N/A | Baseline topology is recorded and packet capture is started on the Controller. |
| 2 | Record common **t0** (timer start) at reboot trigger time for the selected Extender subset. | Reboot the selected Extenders simultaneously while non-selected Extenders remain operational. | Reboot of the selected Extenders is triggered and common **t0** is recorded on the Controller. |
| 3 | N/A | Wait for all rebooted Extenders to complete the boot-up sequence. | All rebooted Extenders complete boot-up and become reachable. |
| 4 | N/A | Verify that EasyMesh and IEEE 1905 services are operational on all rebooted Extenders. If any service is not operational, wait 5 seconds and retry until all required services are running. | EasyMesh and IEEE 1905 services are operational on all rebooted Extenders. |
| 5 | Record **t1-ExtN** for each rebooted Extender when its backhaul link is successfully re-established. | Verify that the backhaul link of each rebooted Extender is operational using `iw dev <mesh_backhaul_intf> link`. | All rebooted Extenders have active backhaul connections to their respective parent nodes, and per-Extender **t1** timestamps are recorded. |
| 6 | Verify reachability of all Extenders from the Controller using `ping <extender_ip>`. | N/A | All Extenders, including both the rebooted and non-rebooted Extenders, are reachable from the Controller. If any Extender is unreachable, mark the test case as **Failed**. |
| 7 | Stop IEEE 1905 packet capture. | N/A | Packet capture is stopped successfully. |
| 8 | Re-read the topology using RDKB-CLI and DataElements via `rbuscli get Device.WiFi.DataElements.Network.Topology`. Compare the recovered topology against the baseline topology. | N/A | All Extenders are present in the topology with correct connectivity information. Unaffected segments remain unchanged, and no missing, stale, or duplicate entries are observed. |
| 9 | Analyze the captured IEEE 1905 packets. | N/A | Topology Query and Topology Response messages are exchanged successfully following recovery of the rebooted Extenders. |
| 10 | Compare the measured recovery duration (**t1-ExtN − t0**) for each rebooted Extender against the KPI threshold. | N/A | Recovery time for each rebooted Extender is less than **120 seconds**. |

---