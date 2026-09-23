# Test Case 1: EM_Backhaul_Link_Stability
## Objective
Verify the Agent maintains a stable backhaul connection with the Controller throughout the test duration

## Test Type

**Positive**

---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
5. Backhaul and fronthaul status information can be retrieved using ` iw dev <interface>`
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Backhaul connectivity stability across all Agents |
| Monitoring Commands | `iw dev <backhaul_interface> link`, `iw dev <backhaul_interface> station dump` |
| Verification Method | Baseline capture and interval-based connected state/parent BSSID/connected-time validation |
| Pass Criteria | Backhaul remains connected, parent BSSID unchanged, and connected time continuously increases |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | 3 EasyMesh Agents |
| Clients |  Wireless Clients distributed across the Controller and Agents |
| Topology | Hybrid Topology (Star and Daisy Chain) |
---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify all Agents are onboarded successfully and visible in the topology | Execute `iw dev` on each Agent and identify the wireless backhaul interface operating in **managed** mode (e.g., `wifi1.3`) | Wireless backhaul interface is identified successfully on all Agents |
| 2 | N/A | Execute `iw dev <backhaul_interface> link` on all Agents and record the baseline link information | All backhaul interfaces show **Connected** state and backhaul link details are available |
| 3 | N/A | At defined intervals during the test duration, execute `iw dev <backhaul_interface> link` on all Agents and record the Connection Status and Parent BSSID | All Agents remain in **Connected** state throughout the test duration and Parent BSSID remains unchanged for each Agent |
| 4 | N/A | Execute `iw dev <backhaul_interface> station dump` on all Agents and monitor the **connected time** value | Connected time continuously increases without resetting for all Agents, indicating stable backhaul connectivity |

---
# Test Case 2: EM_Backhaul_RSSI_Stability

## Objective
Verify that backhaul RSSI remains stable across all Agents during steady-state traffic.

## Test Type
**Positive**

---
## Pre-Requisites
1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
5. Backhaul and fronthaul status information can be retrieved using iw dev <interface>
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Backhaul RSSI stability across all Agents |
| Monitoring Command | `iw dev <backhaul_interface> link` |
| RSSI Threshold | Maintain RSSI above -80 dBm with no sustained degradation |
| Verification Method | Baseline RSSI capture and interval trend comparison |
| Pass Criteria | RSSI remains stable and within defined threshold for all Agents |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | 3 EasyMesh Agents |
| Clients |  Wireless Clients distributed across the Controller and Agents |
| Topology | Hybrid Topology (Star and Daisy Chain) |
---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify all Agents are onboarded successfully and visible in the topology | Execute `iw dev <backhaul_interface> link` on all Agents and record the baseline **RSSI** values | Baseline RSSI values are available for all Agents |
| 2 | N/A | At defined intervals during the test duration, execute `iw dev <backhaul_interface> link` on all Agents and record **RSSI** values | RSSI remains above **-80 dBm** and does not show significant deviation from baseline values |
| 3 | N/A | Compare the collected RSSI values against the baseline for each Agent | No sustained RSSI degradation trend is observed on any Agent |
| 4 | N/A | Continue monitoring RSSI across all Agents throughout the test duration | Backhaul RSSI remains stable across all Agents without abnormal drops or fluctuations |

---

# Test Case 3: EM_Backhaul_PHYRate_Stability

## Objective
Verify that backhaul Tx and Rx PHY rates remain stable across all Agents during steady-state traffic.

## Test Type
**Positive**

---

## Pre-Requisites
1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
5. Backhaul and fronthaul status information can be retrieved using iw dev <interface>
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Backhaul Tx/Rx PHY rate stability across all Agents |
| Monitoring Command | `iw dev <backhaul_interface> link` |
| Measured Metrics | Tx Bitrate, Rx Bitrate |
| Verification Method | Baseline capture and periodic PHY-rate trend comparison |
| Pass Criteria | No sustained Tx/Rx PHY rate degradation for any Agent |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | 3 EasyMesh Agents |
| Clients |  Wireless Clients distributed across the Controller and Agents |
| Topology | Hybrid Topology (Star and Daisy Chain) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify all Agents are onboarded successfully and visible in the topology | Execute `iw dev <backhaul_interface> link` on all Agents and record the baseline **Tx Bitrate** and **Rx Bitrate** values | Baseline Tx and Rx PHY rate values are available for all Agents |
| 2 | N/A | At defined intervals during the test duration, execute `iw dev <backhaul_interface> link` on all Agents and record **Tx Bitrate** and **Rx Bitrate** values | Tx and Rx PHY rates remain within the expected range compared to baseline values |
| 3 | N/A | Compare the collected PHY rate values against the baseline for each Agent | No sustained degradation trend is observed in Tx Bitrate or Rx Bitrate on any Agent |
| 4 | N/A | Continue monitoring Tx Bitrate and Rx Bitrate across all Agents throughout the test duration | Backhaul PHY rates remain stable across all Agents without abnormal drops or fluctuations |

---
# Test Case 4: EM_Backhaul_LinkPerformance_Stability

## Objective

Verify that the backhaul link maintains stable throughput, latency, and packet loss performance throughout the test duration.

## Test Type

**Positive**

---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
5. Backhaul and fronthaul status information can be retrieved using iw dev <interface>
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Backhaul throughput, latency, and packet-loss stability |
| Traffic Tools | `iperf3`, `ping` |
| Throughput/Latency/Loss Checks | `iperf3 -c <controller_ip> -t 300`, continuous `ping`, `ping -c 1000` |

---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | 3 EasyMesh Agents |
| Clients |  Wireless Clients distributed across the Controller and Agents |
| Topology | Hybrid Topology (Star and Daisy Chain) |
---

# Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Verify topology is healthy and all onboarded Agents are visible | Identify the backhaul interface on all Agents using `iw dev` and verify link status using `iw dev <backhaul_interface> link` | Verify client connectivity to the Controller and all Agents | All backhaul links are operational, clients are connected, and the topology is healthy |
| 2 | Start `iperf3` server (`iperf3 -s`) and monitor topology during the test | Verify all backhaul links remain in **Connected** state and capture baseline link information | N/A | Test environment is ready for performance validation |
| 3 | Monitor topology during the test | Run `iperf3 -c <controller_ip> -t 300` from all Agents (sequentially or as defined in the test setup) and record throughput results | N/A | Throughput for all Agents remains within the expected baseline range throughout the test duration |
| 4 | Monitor topology during the test | Execute continuous `ping <controller_ip>` from all Agents and record latency statistics (min/avg/max RTT) | N/A | Latency remains stable without abnormal spikes, excessive delay, or timeouts |
| 5 | Monitor topology during the test | Execute `ping <controller_ip> -c 1000` from all Agents and record packet loss statistics | N/A | Packet loss remains within acceptable limits and no excessive packet drops are observed on any Agent |
| 6 | Verify final topology health and device count | Re-verify backhaul link status using `iw dev <backhaul_interface> link` on all Agents and compare throughput, latency, and packet loss results against baseline values | Verify client connectivity to the Controller and all Agents | All backhaul links remain **Connected**, clients remain connected, and throughput, latency, and packet loss remain stable throughout the observation period |
---
# Test Case 5: EM_Fronthaul_LinkPerformance_Stability

## Objective

Verify that fronthaul links maintain stable throughput, latency, and packet loss performance for clients connected to both the Controller and Agent(s).

## Test Type

**Positive**

---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
5. Backhaul and fronthaul status information can be retrieved using iw dev <interface>
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Fronthaul throughput, latency, and packet-loss stability |
| Topology Profile | Hybrid (Star and Daisy Chain) |
| Traffic Tools | `iperf3`, `ping`, `station_dump` |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | 3 EasyMesh Agents |
| Clients |  Wireless Clients distributed across the Controller and Agents |
| Topology | Hybrid Topology (Star and Daisy Chain) |
---

# Test Procedure and Expected Results

| Step Number | Controller | Agent | Client | Expected Result |
|-------------|------------|--------|--------|-----------------|
| 1 | Verify all Agents are onboarded and topology is healthy | Verify fronthaul SSIDs are operational and clients are associated using `station_dump` | Connect clients to Controller and Agent fronthaul SSIDs | Clients are successfully connected across the topology |
| 2 | Start `iperf3` server on the Controller or test server | Verify associated clients remain connected | Verify client connectivity using ping | Test environment is ready for performance validation |
| 3 | Monitor topology during the test | Verify client associations remain stable | Execute `iperf3 -c <server_ip> -t 300` from clients connected to Controller and Agent fronthaul SSIDs and record throughput | Throughput remains stable throughout the test duration |
| 4 | Monitor topology during the test | Verify no client disconnections occur | Execute continuous `ping <server_ip>` and record latency statistics (min/avg/max RTT) | Latency remains stable with no abnormal spikes or timeouts |
| 5 | Monitor topology during the test | Verify client associations remain intact using `station_dump` | Execute `ping <server_ip> -c 1000` and record packet loss statistics | Packet loss remains within acceptable limits and no excessive packet drops are observed 
---
# Test Case 6: EM_Fronthaul_ClientConnectivity_Stability

## Objective

Verify that clients connected to Controller and Agent fronthaul SSIDs remain associated and connected throughout the observation period.

## Test Type

**Positive**

---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
5. Backhaul and fronthaul status information can be retrieved using iw dev <interface>
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Topology Profile | Hybrid (Star and Daisy Chain) |
| Monitoring Commands | `iw dev <fronthaul_interface> station dump`, client ping |
| Validation Metrics | Authorized/Authenticated/Associated state, Connected Time continuity |
| Verification Method | Baseline capture and interval-based association/connectivity validation |
| Pass Criteria | Clients remain continuously associated and reachable without unexpected disconnects |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | 3 EasyMesh Agents |
| Clients |  Wireless Clients distributed across the Controller and Agents |
| Topology | Hybrid Topology (Star and Daisy Chain) |
---

## Test Procedure and Expected Results
| Step Number | Controller | Agents | Clients | Expected Result |
|------------|------------|----------|----------|-----------------|
| 1 | Verify topology health and confirm all onboarded Agents are visible in the topology. | Verify fronthaul interfaces are operational on all Agents. | Connect test clients across the Controller and Agents. | All clients successfully associate to the fronthaul SSIDs and appear in the topology. |
| 2 | Verify client presence in the topology. | Execute the command 'iw dev <fronthaul_interface> station dump below on all Agents and record baseline client information. | N/A | All clients show Authorized, Authenticated, and Associated status. Connected Time is populated for each client. |
| 3 | Monitor topology health during the test. | Repeat the station dump command on all Agents at defined intervals and compare the values against the baseline. | Run continuous ping to the gateway/server from all clients. | Clients remain connected and Connected Time continuously increases without resetting. |
| 4 | Continue monitoring topology stability. | Repeat Step 3 periodically throughout the test duration. | Verify uninterrupted connectivity from all clients. | No unexpected client disconnections, reassociations, authentication failures, or connectivity interruptions are observed. |
| 5 | Verify final topology health. | Execute the station dump command on all Agents and validate client states against the baseline. | Verify client connectivity. | All clients remain Authorized, Authenticated, Associated, and connected at the end of the test. |

---


# Test Case 7: EM_Fronthaul_RSSI_Stability

## Objective

Verify that the RSSI of clients connected to Controller and Agent fronthaul SSIDs remains stable throughout the observation period.

## Test Type

**Positive**

---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
5. Backhaul and fronthaul status information can be retrieved using iw dev <interface>
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Client RSSI stability on Controller and Agent fronthaul SSIDs |
| Monitoring Command | `iw dev <fronthaul_interface> station dump | grep "signal:"` |
| Measured Metric | Client RSSI trend versus baseline |
| Verification Method | Baseline RSSI capture and periodic interval comparison |
| Pass Criteria | RSSI remains relatively stable with no significant sustained degradation |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | 3 EasyMesh Agents |
| Clients |  Wireless Clients distributed across the Controller and Agents |
| Topology | Hybrid Topology (Star and Daisy Chain) |
---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Client | Expected Result |
|-------------|------------|--------|--------|-----------------|
| 1 | Verify topology is healthy | Connect a client to the Controller or Agent fronthaul SSID | Associate to the fronthaul network | Client is successfully connected |
| 2 | Record baseline RSSI value using the command below:`iw dev <fronthaul_interface> station dump \| grep "signal:"` | N/A | N/A | Initial RSSI value is recorded |
| 3 | Monitor RSSI at defined intervals throughout the observation period using the same command | Collect RSSI values periodically | Maintain normal traffic activity | RSSI measurements are collected successfully |
| 4 | Compare RSSI values against baseline measurements | Verify RSSI fluctuations remain within acceptable limits | Verify connectivity remains intact | RSSI remains relatively stable with no significant degradation |


---

# Test Case 8: EM_Fronthaul_PHYRate_Stability

## Objective

Verify that client TX and RX PHY rates remain stable throughout the observation period.

## Test Type

**Positive**

---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
5. Backhaul and fronthaul status information can be retrieved using iw dev <interface>
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Client Tx/Rx PHY rate stability on fronthaul links |
| Monitoring Commands | `iw dev <fronthaul_interface> station dump | grep "tx bitrate"`, `iw dev <fronthaul_interface> station dump | grep "rx bitrate"` |
| Measured Metrics | Tx PHY rate, Rx PHY rate |
| Verification Method | Baseline PHY capture and periodic trend comparison |
| Pass Criteria | PHY rates remain stable with uninterrupted client communication |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | 3 EasyMesh Agents |
| Clients |  Wireless Clients distributed across the Controller and Agents |
| Topology | Hybrid Topology (Star and Daisy Chain) |
---

## Test Procedure and Expected Results

| Step Number | Controller | Agent | Client | Expected Result |
|-------------|------------|--------|--------|-----------------|
| 1 | Verify topology is healthy | Connect a client to the Controller or Agent fronthaul SSID | Associate to the fronthaul network | Client is successfully connected |
| 2 | Record baseline PHY rates using the commands below:`iw dev <fronthaul_interface> station dump \| grep "tx bitrate"``iw dev <fronthaul_interface> station dump \| grep "rx bitrate"` | N/A | N/A | Initial TX and RX PHY rates are recorded |
| 3 | Monitor PHY rates at defined intervals using the same commands | Record TX and RX PHY rates throughout the observation period | Maintain normal traffic activity | PHY rate measurements are collected successfully |
| 4 | Compare PHY rates against baseline values and verify connectivity | Verify no abnormal PHY rate degradation is observed | Verify traffic flow remains uninterrupted | PHY rates remain stable and client communication is unaffected |

---


