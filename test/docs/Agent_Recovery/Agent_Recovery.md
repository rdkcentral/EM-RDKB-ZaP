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
| Network Topology Type | Hybrid Topology |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. The Controller and all Extenders are reachable over SSH.
3. The capture interface, IEEE 1905 filter, remote capture directory, and local capture directory are configured for the Controller and every Extender.
4. Packet analyzer dependencies are installed.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `agent_recovery_kpi_seconds` (240 seconds by default) |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | N/A | Discover all Extenders and store each Extender's AL MAC address for capture validation. | The Extenders and their AL MAC addresses are recorded. |
| 2 | Record one monotonic recovery start time and initiate reboot of all Extenders concurrently. | Reboot all Extenders concurrently. | Reboot commands are issued and all Extenders share the same recovery KPI window. |
| 3 | Start IEEE 1905 packet capture on the Controller after the Extender reboot commands are issued. | N/A | A Controller capture is running while the Extenders recover. |
| 4 | N/A | Reconnect to each Extender over SSH concurrently. Close its previous connection and retry every 5 seconds until the recovery KPI deadline. | Each Extender's SSH connection is restored within the KPI, or its recovery is recorded as failed. |
| 5 | N/A | After SSH reconnects, verify `onewifi`, `ieee1905_em_agent`, and `em_agent` every 2 seconds until the KPI deadline. Record elapsed time from Step 2. | All required services become active and a recovery duration is recorded for each Extender. |
| 6 | N/A | Validate each Extender's recovery KPI and reachability. | Every Extender is reachable and recovered within the configured KPI. |
| 7 | N/A | Identify each recovered Extender's upstream parent device. | An upstream parent is identified for each recovered Extender. |
| 8 | Keep the Controller capture running for 60 seconds after recovery to allow topology traffic to propagate. | N/A | Recovery topology traffic is present in the capture. |
| 9 | Stop and collect the IEEE 1905 capture from the Controller. | N/A | The Controller capture is saved locally for analysis. |
| 10 | Reassemble the Controller capture. For each recovered and reachable Extender AL MAC, check for Topology Query and Topology Response messages whose source or destination matches that AL MAC. | N/A | Both message types are found for every recovered and reachable Extender in the Controller capture. |
| 11 | Review accumulated recovery, reachability, parent-link, and capture-validation results. | N/A | The test fails if any Extender recovery or validation check failed. |

---

# Test Case 2: EM_AgentRecovery_ConsecutiveReboots

## Objective

Verify that all Extenders recover reliably and within the configured KPI across five consecutive reboot cycles, with no cumulative degradation or stale-state buildup over repeated recovery cycles.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid Topology |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. The Controller and all Extenders are reachable over SSH.
3. The capture interface, IEEE 1905 filter, remote capture directory, and local capture directory are configured for the Controller and every Extender.
4. Packet analyzer dependencies are installed.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `agent_recovery_kpi_seconds` (240 seconds by default, each cycle) |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Extender Reboot Cycles | 5 |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | N/A | Discover all Extenders and store each Extender's AL MAC address for later capture validation. | The Extenders and their AL MAC addresses are recorded. |
| 2 | For each cycle, record a common monotonic start time and reboot all Extenders still participating in the test concurrently. Before the Cycle 5 reboot, start the Controller's single IEEE 1905 capture. | Reboot the participating Extenders concurrently for up to five cycles. | The capture covers Cycle 5 if the test reaches that cycle. An Extender that fails a cycle is excluded from subsequent cycles and recorded as failed. |
| 3 | N/A | After each reboot, reconnect to every participating Extender over SSH concurrently. Close its previous connection and retry every 5 seconds until the cycle's KPI deadline. | SSH connectivity is restored for each participating Extender within that cycle's KPI. |
| 4 | N/A | After each Extender reconnects, verify `onewifi`, `ieee1905_em_agent`, and `em_agent` every 2 seconds until the cycle's KPI deadline. Record recovery time from that cycle's start. | Required services become active and recovery time is recorded for each participating Extender in that cycle. |
| 5 | N/A | Validate each participating Extender's recovery KPI and reachability after every cycle. | Only Extenders that meet the KPI in all five cycles pass; a failed Extender is recorded with its first failed cycle. |
| 6 | After Cycle 5, identify each Extender's upstream parent device, then keep the capture running for 60 seconds to allow topology traffic to propagate. | N/A | An upstream parent is identified for every Extender, and the Cycle 5 capture includes the propagation period. |
| 7 | Stop and collect the Controller capture. | N/A | The capture covering Cycle 5 and the following propagation period is saved locally. |
| 8 | Reassemble the Cycle 5 capture. For each Extender AL MAC, check for Topology Query and Topology Response messages whose source or destination matches that AL MAC. | N/A | Both message types are found for every Extender in the Cycle 5 capture. |
| 9 | Review the final per-Extender recovery summary across all five cycles and the Cycle 5 topology validation. | N/A | An Extender passes the recovery summary only if it met the KPI in every cycle; otherwise, the summary identifies its first failed cycle. The test also fails if Cycle 5 topology validation fails. |

---

# Test Case 3: EM_AgentRecovery_SurvivorIsolation

## Objective

Confirm that a Controller-connected Extender remains reachable during peer reboot checks and periodic recovery polling, while each rebooted Extender reconnects within the configured KPI.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | N enabled EasyMesh Agents (N >= 2; one remains active and N-1 reboot) |
| Network Topology Type | Active EasyMesh topology |

---

## Pre-Requisites

1. The Controller and at least two Extenders are onboarded and have active EasyMesh backhaul connections.
2. All enabled Extenders are reachable over SSH before the test starts.
3. EasyMesh and IEEE 1905 services are available on all enabled devices.
4. The `agent_recovery_kpi_seconds` test parameter is configured.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `agent_recovery_kpi_seconds` (240 seconds by default) |
| Minimum Enabled Extenders | 2 |
| Survivor Polling Interval | 5 seconds |
| Recovery Trigger | Concurrent reboot of all enabled Extenders except the survivor |
| Survivor Selection | First eligible Extender |
| Network Topology | Controller and N enabled Extenders with active EasyMesh backhaul connections |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | N/A | Discover the enabled Extenders. | At least two enabled Extenders are found; otherwise, the test stops. |
| 2 | Identify each Extender's active upstream parent. | Select the first Extender whose active parent is the Controller as the survivor; set all other enabled Extenders as reboot targets. | A survivor and N-1 reboot targets are identified; otherwise, the test stops before rebooting peers. |
| 3 | Check the survivor reachability. | Keep the survivor running and exclude it from the reboot targets. | The survivor is reachable before peer reboot begins; otherwise, the test stops before rebooting peers. |
| 4 | Record a common monotonic recovery start time, then issue CLI reboot commands concurrently to the targets. Check survivor reachability as each reboot command completes. | Reboot the N-1 targets concurrently; leave the survivor running. | Reboot command errors and failed survivor checks are reported and fail the test. |
| 5 | After all reboot commands complete, start survivor polling at 5-second intervals. Wait 30 seconds before starting peer recovery checks. | Keep the survivor running while monitoring is active. | Polling covers the post-reboot wait and peer recovery checks; each failed poll logs its reason and marks the test as failed. |
| 6 | Recover the rebooted Extenders concurrently within the shared KPI window. | Reconnect over SSH and verify required mesh services. | Every rebooted Extender reconnects and restores the required services within the configured KPI. |
| 7 | Stop polling after all peer recovery workers finish. Check each rebooted Extender's reachability and identify its active upstream parent. | N/A | Each rebooted Extender is reachable and has an identified upstream parent; failed checks are reported. |
| 8 | Summarize the survivor's recorded post-command checks and polling result. | N/A | The survivor passes only if every recorded reachability check and poll succeeded.Report each rebooted Extender's recovery result separately. |

---

# Test Case 4: EM_AgentRecovery_LeafExtender

## Objective

Verify that each terminal Extender, with no downstream Extenders, recovers after reboot within the configured KPI and retains an identifiable active upstream parent.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | Enabled EasyMesh Agents in an active topology |
| Network Topology Type | Active EasyMesh topology with one or more terminal Extenders |

---

## Pre-Requisites

1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. The Controller and all Extenders are reachable over SSH.
3. At least one terminal Extender with no downstream Extenders is present.
4. The `agent_recovery_kpi_seconds` test parameter is configured.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `agent_recovery_kpi_seconds` (240 seconds by default) |
| Reboot Targets | All enabled Extenders with no downstream Extenders |
| Recovery Trigger | Concurrent reboot of all selected terminal Extenders |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|-----------|-----------------|
| 1 | Discover enabled Extenders. | N/A | At least one enabled Extender is found; otherwise, the test stops. |
| 2 | Match each Extender's connected backhaul BSSID against the Controller and Extenders' interface MAC addresses to identify its parent, then select terminal Extenders. | Read each Extender's active backhaul link to obtain its connected BSSID. | Parent relationships are identified and Extenders with no downstream Extenders are selected; otherwise, the test stops. |
| 3 | Record one monotonic recovery start time and issue CLI reboot commands concurrently to all selected terminal Extenders. | Reboot all selected terminal Extenders concurrently. | Reboot commands are issued; command errors are reported and the affected Extender fails. |
| 4 | Wait 30 seconds after the reboot commands complete. | N/A | The post-reboot boot-up wait completes before recovery checks start. |
| 5 | Recover each terminal Extender concurrently within the shared KPI window. | Reconnect over SSH and verify the required mesh services. | Each selected Extender reconnects and restores required services within the KPI. |
| 6 | Check post-recovery reachability for each selected Extender and report individual recovery outcomes. | N/A | Every passing Extender has a successful recovery result and is reachable; failed or unavailable results fail that Extender. |
| 7 | Query the active upstream parent of each recovered terminal Extender. | N/A | An active parent is identified for every recovered terminal Extender. |

---

# Test Case 5: EM_AgentRecovery_ParentAgent_DaisyChainTopology

## Objective

Verify that a Parent Extender recovers after reboot, restores its backhaul connection to the Controller, and preserves the downstream Daisy Chain topology within the configured KPI.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Daisy Chain Topology |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Daisy Chain topology is operational.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.
5. The Controller and all Extenders are reachable over SSH.
6. The capture interface, IEEE 1905 filter, remote capture directory, and local capture directory are configured for the Controller and every Extender.
7. Packet analyzer dependencies are installed.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `agent_recovery_kpi_seconds` (240 seconds by default) |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Daisy-chain topology with 1 Controller and 3 Extenders connected in parent-child relationships |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
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
| 10 | Compare the measured recovery duration (**t1-Parent − t0**) against the KPI threshold. | N/A | Parent Extender recovery time is less than **240 seconds**. |

---

# Test Case 6: EM_AgentRecovery_AllAgents_DaisyChainTopology

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
| Network Topology Type | Daisy Chain Topology |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Daisy Chain topology is operational.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.
5. The Controller and all Extenders are reachable over SSH.
6. The capture interface, IEEE 1905 filter, remote capture directory, and local capture directory are configured for the Controller and every Extender.
7. Packet analyzer dependencies are installed.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `agent_recovery_kpi_seconds` (240 seconds by default) |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Daisy-chain topology with 1 Controller and 3 Extenders connected in parent-child relationships |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
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
| 10 | Compare the measured recovery duration (**t1-ExtN − t0**) against the KPI threshold. | N/A | Recovery time for each Extender is less than **240 seconds**. |

---

# Test Case 7: EM_AgentRecovery_WiredBackhaul

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
| Network Topology Type | Hybrid Topology |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. All Agents are onboarded with an active Ethernet (wired) backhaul connection.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.
5. The Controller and all Extenders are reachable over SSH.
6. The capture interface, IEEE 1905 filter, remote capture directory, and local capture directory are configured for the Controller and every Extender.
7. Packet analyzer dependencies are installed.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `agent_recovery_kpi_seconds` (240 seconds by default) |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Backhaul Type | Ethernet (Wired) |
| DataElements | Device.WiFi.DataElements.Network.Topology <br> Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType |
| Network Topology | Controller and 3 Extenders in an active EasyMesh wired backhaul topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
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
| 10 | Compare the measured recovery duration (**t1-ExtN − t0**) for each Extender against the KPI threshold. | N/A | Recovery time for each Extender is less than **240 seconds**. |

---

# Test Case 8: EM_AgentRecovery_PartialSimultaneousReboot

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
| Network Topology Type | Hybrid Topology |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Multiple Agents are onboarded with active EasyMesh backhaul connections.
2. All Agents are visible in the Controller topology.
3. EasyMesh and IEEE 1905 services are running on all devices.
4. DataElements is accessible via rbuscli.
5. The Controller and all Extenders are reachable over SSH.
6. The capture interface, IEEE 1905 filter, remote capture directory, and local capture directory are configured for the Controller and every Extender.
7. Packet analyzer dependencies are installed.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `agent_recovery_kpi_seconds` (240 seconds by default) |
| IEEE 1905 Messages Validated | Topology Query, Topology Response |
| Recovery Trigger | Simultaneous reboot of a subset of Agents (remaining Agents stay up) |
| DataElements | Device.WiFi.DataElements.Network.Topology |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
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
| 10 | Compare the measured recovery duration (**t1-ExtN − t0**) for each rebooted Extender against the KPI threshold. | N/A | Recovery time for each rebooted Extender is less than **240 seconds**. |

---


---