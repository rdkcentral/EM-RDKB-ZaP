# Test Case 1: EM_ControllerRecovery_AgentReconnection

## Objective

Verify that all EasyMesh Extenders reconnect after a Controller reboot, restore required services and parent relationships, exchange IEEE 1905 topology messages, and complete recovery within the configured KPI.

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
| Recovery KPI | `controller_recovery_kpi_seconds` (300 seconds by default) |
| IEEE 1905 Messages Validated | Topology Query and Topology Response |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|-----------|-----------------|
| 1 | N/A | Discover all Extenders from the database. | At least one Extender is found. The test fails if no Extender is found. |
| 2 | N/A | For each Extender, create a device-specific capture name and start IEEE 1905 capture on the configured backhaul interface. | Capture starts successfully for every Extender. |
| 3 | N/A | Read and store the AL MAC address of each Extender for packet-capture validation after recovery. | The AL MAC address is obtained and retained for every Extender. |
| 4 | Record one monotonic start time and reboot the Controller through the CLI. | Use the same Controller reboot timestamp as the recovery start time for every Extender. | The reboot command is executed and the Controller and all Extenders share one KPI measurement window. |
| 5 | Wait 30 seconds before attempting Controller reconnection. | N/A | The initial Controller reboot wait is completed. |
| 6 | Close the existing Controller connection and retry SSH reconnection every 5 seconds until the KPI deadline. | N/A | Controller SSH connectivity is restored within the KPI. If the Controller does not reconnect, the test fails and no further recovery validations are performed. |
| 7 | After Controller SSH recovery, validate `onewifi`, `ieee1905_em_agent`, `ieee1905_em_ctrl`, and `em_ctrl` every 2 seconds until the KPI deadline. | N/A | All four Controller services become active within the KPI. Extender and topology validations proceed only after successful Controller service recovery. |
| 8 | N/A | Recover all Extenders concurrently. For each Extender, close the existing connection and retry SSH every 5 seconds until the KPI deadline. | SSH connectivity is restored for every Extender within the KPI. Service validation for an Extender starts only after its SSH connection is restored. |
| 9 | N/A | After each Extender reconnects, validate `onewifi`, `ieee1905_em_agent`, and `em_agent` every 2 seconds until the KPI deadline, then record elapsed time from Step 4. | All three services become active and a recovery duration is recorded for every Extender after all recovery threads complete. |
| 10 | N/A | For each Extender, reject missing or exceptional results, verify that the Extender is reachable, and compare its recovery duration with the configured KPI. | Recovered Extenders continue through the remaining validation steps. Unrecovered Extenders are skipped and recorded as failures for the final aggregate result. |
| 11 | N/A | Continue IEEE 1905 capture and wait 60 seconds for topology traffic propagation. | Recovery topology traffic is available in the captures. |
| 12 | N/A | Stop each recovered Extender capture, download it locally, and delete the remote capture. | A local capture path is recorded for every recovered Extender. Capture collection failures are retained for final failure. |
| 13 | N/A | For each recovered Extender, reassemble the local capture and use the stored Extender AL MAC to validate its Topology Query and Topology Response exchange with the Controller. | Both topology message types are present and associated with every recovered Extender. Missing messages and decode failures are retained for final failure. |
| 14 | N/A | Identify the upstream device for every Extender after recovery. | An upstream device is identified for every recovered Extender. The test fails for any accumulated recovery, capture, packet-validation, or upstream-device identification error. |
| 15 | N/A | Review the recovery results for all Extenders. | The test fails at the final step if any Extender failed to recover or any recovery validation error was recorded. |

---

# Test Case 2: EM_ControllerRecovery_ConsecutiveReboots

## Objective

Verify that the Controller restores SSH connectivity and required services after five consecutive reboot cycles, and that all Extenders recover with valid IEEE 1905 topology traffic and identifiable upstream devices after the final cycle.

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
| Recovery KPI | `controller_recovery_kpi_seconds` (300 seconds by default) |
| Controller Reboot Cycles | 5 |
| IEEE 1905 Messages Validated | Topology Query and Topology Response |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|-----------|-----------------|
| 1 | N/A | Discover all Extenders from the database. | At least one Extender is found. The test fails if no Extender is found. |
| 2 | N/A | For each Extender, create a device-specific capture name and start IEEE 1905 capture on the configured backhaul interface. Keep the captures running across all five reboot cycles. | Capture starts successfully for every Extender. |
| 3 | For each of Cycles 1 through 4, record the cycle start time and reboot the Controller through the CLI. | Continue IEEE 1905 capture. | The Controller reboot is initiated and a new KPI measurement starts for each cycle. |
| 4 | After each reboot, wait 30 seconds before attempting Controller reconnection. | Continue IEEE 1905 capture. | The initial Controller reboot wait is completed for each cycle. |
| 5 | Close the existing Controller connection and retry SSH reconnection every 5 seconds until the KPI deadline. | Continue IEEE 1905 capture. | Controller SSH connectivity is restored within the KPI for each cycle. If the Controller does not reconnect, the test fails and no further recovery validations are performed. |
| 6 | After Controller SSH recovery, validate `onewifi`, `ieee1905_em_agent`, `ieee1905_em_ctrl`, and `em_ctrl` every 2 seconds until the KPI deadline, then proceed to the next cycle. | Continue IEEE 1905 capture. | All four Controller services become active within the KPI for Cycles 1 through 4. |
| 7 | Record the Cycle 5 start time, retain it as the Extender recovery baseline, and reboot the Controller through the CLI. | Continue IEEE 1905 capture. | The fifth Controller reboot is initiated and the final KPI measurement starts. |
| 8 | Wait 30 seconds before attempting Controller reconnection. | Continue IEEE 1905 capture. | The initial Controller reboot wait for Cycle 5 is completed. |
| 9 | Close the existing Controller connection and retry SSH reconnection every 5 seconds until the KPI deadline. | Continue IEEE 1905 capture. | Controller SSH connectivity is restored within the KPI for Cycle 5. |
| 10 | After Controller SSH recovery, validate `onewifi`, `ieee1905_em_agent`, `ieee1905_em_ctrl`, and `em_ctrl` every 2 seconds until the KPI deadline. | Continue IEEE 1905 capture. | All four Controller services become active within the KPI. Extender and topology validations proceed only after successful Controller service recovery. |
| 11 | N/A | Recover all Extenders concurrently. For each Extender, close the existing connection and retry SSH every 5 seconds until the KPI deadline. | SSH connectivity is restored for every Extender within the KPI. Service validation for an Extender starts only after its SSH connection is restored. |
| 12 | N/A | After each Extender reconnects, validate `onewifi`, `ieee1905_em_agent`, and `em_agent` every 2 seconds until the KPI deadline, then record elapsed time from the Cycle 5 start time. | All three services become active and a recovery duration is recorded for every Extender after all recovery threads complete. |
| 13 | N/A | For each Extender, reject missing or exceptional results, verify that the Extender is reachable, and compare its recovery duration with the configured KPI. | Recovered Extenders continue through the remaining validation steps. Unrecovered Extenders are skipped and recorded as failures for the final aggregate result. |
| 14 | N/A | Continue IEEE 1905 capture and wait 60 seconds for topology traffic propagation. | Recovery topology traffic is available in the captures. |
| 15 | N/A | Stop each recovered Extender capture, download it locally, and delete the remote capture. | A local capture path is recorded for every recovered Extender. Capture collection failures are retained for final failure. |
| 16 | N/A | For each recovered Extender, reassemble the local capture and validate the presence of Topology Query and Topology Response messages. | Both topology message types are present in every collected capture. Missing messages and decode failures are retained for final failure. |
| 17 | N/A | Identify the upstream device for every Extender after recovery. | An upstream device is identified for every recovered Extender. The test fails for any accumulated Extender recovery, capture, packet-validation, or upstream-device identification error. |
| 18 | N/A | Review the recovery results for all Extenders after the final reboot cycle. | The test fails at the final step if any Extender failed to recover or any recovery validation error was recorded. |

---

# Test Case 3: EM_ControllerRecovery_ClientContinuity

## Objective

Verify that WLAN clients associated with the EasyMesh Extenders regain connectivity after a Controller reboot, while the Extenders recover within the configured KPI and exchange the required IEEE 1905 topology messages.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| WLAN Clients | One configured WLAN client per Extender |
| Network Topology Type | Hybrid Topology |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. The Controller and all Extenders are reachable over SSH.
3. Each Extender has at least one configured WLAN client.
4. The capture interface, IEEE 1905 filter, remote capture directory, and local capture directory are configured for every Extender.
5. The configured WLAN clients can be associated with their assigned Extenders.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `controller_recovery_kpi_seconds` (300 seconds by default) |
| IEEE 1905 Messages Validated | Topology Query and Topology Response |
| Network Topology | Controller, 3 Extenders, and one WLAN client per Extender in an active EasyMesh Hybrid topology |
| Client Connectivity Check | Continuous client ping during Controller and Extender recovery |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | WLAN Clients | Expected Result |
|-------------|------------|-----------|--------------|-----------------|
| 1 | N/A | Identify all onboarded Extenders and map one configured WLAN client to each Extender. | N/A | Every Extender has one WLAN client assigned. The test fails if no Extender, no WLAN client, or any Extender-to-client mapping is unavailable. |
| 2 | N/A | Associate the mapped WLAN client with each Extender and record its initial connected BSSID. | Remain associated with the assigned Extender. | Each WLAN client is associated with its assigned Extender and its initial BSSID is recorded. |
| 3 | N/A | Start one device-specific IEEE 1905 capture on each Extender and record each Extender AL MAC address. | N/A | Capture starts and the AL MAC address is recorded for every Extender. |
| 4 | N/A | Start continuous client ping for the mapped WLAN client on each Extender. | Continue responding to the ping during the recovery window. | Continuous ping is running for every mapped WLAN client before the Controller reboot. |
| 5 | Record one monotonic start time and reboot the Controller through the CLI. | Use the same Controller reboot timestamp as the recovery start time for every Extender. | Continue the client ping without interruption. | The Controller reboot starts and the Controller and all Extenders share one KPI measurement window. |
| 6 | Wait 30 seconds, then reconnect through SSH and validate the required Controller services within the KPI. | Continue capture and client ping. | Continue the client ping. | Controller SSH connectivity and required Controller services are restored within the KPI. |
| 7 | N/A | Recover all Extenders concurrently. For each Extender, restore SSH connectivity, validate the required services, and record its recovery duration. | Continue the client ping. | Recovered Extenders become operational and record a recovery duration. Extenders that do not reconnect are recorded for the final aggregate result. |
| 8 | N/A | For each recovered Extender, stop and collect its capture, reconnect its mapped WLAN client, and download the client ping output. | Reconnect and remain reachable after the Extender recovery. | A local capture and ping output are collected for every recovered Extender, and each recovered Extender's mapped WLAN client is reachable. Unrecovered Extenders are skipped. |
| 9 | N/A | For each recovered Extender, identify the parent or upstream device, either the Controller or any Extender in the testbed, to which the recovered WLAN client is connected. | Remain connected through any available testbed device. | The actual parent or upstream device for each recovered WLAN client is identified as the Controller or an Extender in the testbed. The client is not required to reconnect through its original Extender. Unrecovered Extenders are skipped. |
| 10 | N/A | For each recovered Extender, reassemble its collected capture and validate Topology Query and Topology Response messages using the recovered Extender AL MAC address. | N/A | Both topology message types are present for every recovered Extender. Unrecovered Extenders are skipped; missing messages and decode failures are recorded for the final aggregate result. |
| 11 | N/A | N/A | Validate the downloaded ping output for every recovered WLAN client. | Ping may show a temporary outage during recovery, but successful replies resume for every recovered WLAN client. Unrecovered Extenders are included in the final failure result. |
| 12 | N/A | N/A | Review the recovery results for all Extenders and recovered WLAN clients. | The test fails at the final step if any Extender failed to recover or any recovery, capture, client-connectivity, or topology-validation error was recorded. |

---

# Test Case 4: EM_ControllerRecovery_WiredBackhaul

## Objective

Verify that EasyMesh Extenders connected through Ethernet backhaul reconnect after a Controller reboot, restore the wired topology, and recover within the configured KPI.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents with wired backhaul |
| Network Topology Type | Hybrid Topology |
| Backhaul Type | Ethernet (Wired) |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. The Controller and all Extenders are onboarded with active Ethernet backhaul connections.
2. The Controller and all Extenders are reachable over SSH.
3. All Extenders are visible in the Controller topology over the wired backhaul.
4. DataElements is accessible via rbuscli for backhaul media validation.
5. The capture interface, IEEE 1905 filter, remote capture directory, and local capture directory are configured for the Controller and every Extender.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Recovery KPI | `controller_recovery_kpi_seconds` (300 seconds by default) |
| IEEE 1905 Messages Validated | Topology Query and Topology Response |
| Backhaul Type | Ethernet (Wired) |
| DataElements | `Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType` |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Ethernet Backhaul topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|-----------|-----------------|
| 1 | Record the baseline active backhaul media types using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`. | Start one device-specific IEEE 1905 capture on each Extender. | The baseline Ethernet backhaul media types are recorded, and capture starts successfully on every Extender. |
| 2 | Record one monotonic start time and reboot the Controller through the CLI. | Use the same Controller reboot timestamp as the recovery start time for every Extender. | The Controller reboot starts and the Controller and all Extenders share one KPI measurement window. |
| 3 | Wait 30 seconds, then close the existing Controller connection and retry SSH reconnection every 5 seconds until the KPI deadline. | Continue capture. | Controller SSH connectivity and required Controller services are restored within the KPI. |
| 4 | Verify that the Controller is ready to accept Extender connections. | Verify the wired backhaul link for each Extender and stop its recovery timer when the link is connected. | Each recovered wired backhaul link is restored and records a recovery completion time. Extenders that do not reconnect are recorded for the final aggregate result. |
| 5 | N/A | For each recovered Extender, verify reachability, validate required services, and compare its recovery duration with the configured KPI. | Each recovered Extender is reachable, its services are operational, and its recovery completes within the KPI. Unrecovered Extenders are skipped. |
| 6 | N/A | Stop each recovered Extender capture, download it locally, and delete the remote capture. | A local capture path is recorded for every recovered Extender. Unrecovered Extenders are skipped; capture collection failures are retained for final failure. |
| 7 | Re-read the backhaul media types using the DataElements command `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`. | N/A | Every active recovered backhaul link reports Ethernet media type. |
| 8 | N/A | Reassemble each recovered Extender capture and validate Topology Query and Topology Response messages. | Both topology message types are present for every recovered Extender. Unrecovered Extenders are skipped; missing messages and decode failures are retained for final failure. |
| 9 | Compare each recovered Extender recovery duration with the configured KPI and compare the recovered topology with the baseline. | N/A | The final result fails if any Extender did not recover or if any recovery, capture, packet-validation, or topology comparison error was recorded. |
| 10 | Fail the test if any Extender recovery failed or any recovery validation error was recorded. | N/A | The final Wired Backhaul test result fails when any Extender did not recover or any recovery, capture, packet-validation, or topology comparison error was recorded. |