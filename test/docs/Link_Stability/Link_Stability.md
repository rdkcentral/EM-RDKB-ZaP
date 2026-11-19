# Test Case 1: EM_Backhaul_Link_Stability

## Objective

Verify every enabled Extender remains connected to the same parent BSSID
throughout the one-hour test duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. All enabled Extenders are successfully onboarded and visible in the
   EasyMesh topology.
2. EasyMesh services are running on the Controller and Extenders.
3. The `backhaul_interface` value is configured for every enabled Extender.
4. Backhaul link details can be retrieved through the testbed initialization
   interface.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Backhaul connectivity stability across all enabled Extenders |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Connection state, parent BSSID, and connected time |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | All enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify the topology is healthy and enabled Extenders are available. | Read the configured `backhaul_interface` for each Extender. | Every required backhaul interface is identified. |
| 2 | N/A | Capture baseline backhaul state for each interface. | Each baseline link is connected and provides a parent BSSID and connected time. |
| 3 | N/A | Poll every 10 minutes for 1 hour and validate connection state, parent BSSID, and connected time. | Each link remains connected to the baseline BSSID and connected time is non-decreasing. |
| 4 | N/A | Capture and validate the final backhaul state. | Every final link satisfies the baseline connectivity, BSSID, and connected-time checks. |

---

# Test Case 2: EM_Backhaul_PHYRate_Stability

## Objective

Verify the TX and RX PHY rates of every enabled Extender backhaul link remain
available and within the allowed drop from baseline.

## Test Type

**Positive**

---

## Pre-Requisites

1. All enabled Extenders are successfully onboarded and visible in the
   EasyMesh topology.
2. EasyMesh services are running on the Controller and Extenders.
3. The `backhaul_interface` value is configured for every enabled Extender.
4. Backhaul link details, including TX and RX rates, are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Backhaul TX/RX PHY-rate stability across all enabled Extenders |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | TX PHY rate and RX PHY rate in Mbps |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | All enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify the topology is healthy and enabled Extenders are available. | Read the configured backhaul interface and capture baseline link details. | A connected link with valid TX and RX rates is accepted as the baseline. |
| 2 | N/A | Poll each backhaul link every 10 minutes for 1 hour. | The link remains connected and each rate remains within the 50% baseline-drop limit. |
| 3 | N/A | Capture and validate final TX and RX rates against baseline. | Final TX and RX rates pass the same validation. |

---

# Test Case 3: EM_Backhaul_RSSI_Stability

## Objective

Verify the RSSI of every enabled Extender backhaul link remains above the
minimum threshold and does not degrade beyond the allowed baseline limit.

## Test Type

**Positive**

---

## Pre-Requisites

1. All enabled Extenders are successfully onboarded and visible in the
   EasyMesh topology.
2. EasyMesh services are running on the Controller and Extenders.
3. The `backhaul_interface` value is configured for every enabled Extender.
4. Backhaul link details, including RSSI, are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Backhaul RSSI stability across all enabled Extenders |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metric | Backhaul RSSI in dBm |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | All enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify the topology is healthy and enabled Extenders are available. | Capture connected baseline RSSI for each configured backhaul interface. | Each accepted baseline RSSI is at least -80 dBm. |
| 2 | N/A | Poll each backhaul RSSI every 10 minutes for 1 hour. | RSSI remains available, at least -80 dBm, and no more than 10 dB below baseline. |
| 3 | N/A | Capture and validate final RSSI against baseline and threshold. | Every final RSSI sample passes both checks. |

---

# Test Case 4: EM_Fronthaul_Link_Stability

## Objective

Verify enabled WLAN clients connect to the fronthaul and remain able to reach
the Controller bridge gateway throughout the test duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The Controller and all enabled Extenders are successfully onboarded.
2. EasyMesh services and fronthaul SSIDs are operational.
3. Enabled WLAN clients are configured in the testbed database.
4. Controller fronthaul credentials and `bridge_ip` are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Fronthaul client connectivity and Controller gateway reachability |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Client connection state and Controller gateway ping reachability |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller and bridge gateway |
| Agents | All enabled EasyMesh Extenders |
| Clients | All enabled WLAN clients that connect successfully |
| Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Retrieve the Controller fronthaul credentials and bridge IP. | Verify fronthaul service availability. | Enumerate enabled WLAN clients. | Credentials, target gateway, and configured clients are available. |
| 2 | N/A | N/A | Remove and reconnect each configured client. | At least one client connects successfully; unavailable clients are reported. |
| 3 | Monitor Controller gateway availability. | Monitor topology health. | Ping the Controller gateway at baseline and every 10 minutes for 1 hour. | Every connected client reaches the gateway at each successful sample. |
| 4 | N/A | N/A | Perform the final three-packet ping from each connected client. | Clients remain reachable at the end of the test. |

---

# Test Case 5: EM_Fronthaul_PHYRate_Stability

## Objective

Verify each successfully connected WLAN client's TX and RX PHY rates remain
available and within the allowed drop from baseline.

## Test Type

**Positive**

---

## Pre-Requisites

1. The Controller and all enabled Extenders are successfully onboarded.
2. EasyMesh services and fronthaul SSIDs are operational.
3. Enabled WLAN clients, client MAC addresses, and connection information are
   configured in the testbed database.
4. Client association status and station TX/RX rate details are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Client TX/RX PHY-rate stability on fronthaul links |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Client TX PHY rate and RX PHY rate in Mbps |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | All enabled EasyMesh Extenders |
| Clients | Enabled WLAN clients that connect successfully |
| Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Retrieve Controller fronthaul credentials. | Verify fronthaul service availability. | Remove and reconnect enabled WLAN clients. | Connected clients are available for PHY-rate measurement. |
| 2 | N/A | Resolve each client's associated BSSID to the advertising mesh device and fronthaul interface. | Capture baseline TX/RX PHY rates. | Clients with valid TX and RX rates are accepted as baselines. |
| 3 | N/A | Resolve the current station record every 10 minutes for 1 hour. | Validate current TX/RX rates against baseline. | Neither rate drops by more than 50%. |
| 4 | N/A | Capture the final station record. | Validate final TX/RX rates against baseline. | Final rates pass the same validation. |

---

# Test Case 6: EM_Fronthaul_RSSI_Stability

## Objective

Verify each successfully connected WLAN client's fronthaul RSSI remains
available and does not degrade beyond the allowed baseline limit.

## Test Type

**Positive**

---

## Pre-Requisites

1. The Controller and all enabled Extenders are successfully onboarded.
2. EasyMesh services and fronthaul SSIDs are operational.
3. Enabled WLAN clients and client MAC addresses are configured in the
   testbed database.
4. Client association status and station RSSI details are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Client RSSI stability on fronthaul links |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metric | Client RSSI in dBm |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | All enabled EasyMesh Extenders |
| Clients | Enabled WLAN clients that connect successfully |
| Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Retrieve Controller fronthaul credentials. | Verify fronthaul service availability. | Remove and reconnect enabled WLAN clients. | Connected clients are available for RSSI measurement. |
| 2 | N/A | Resolve each client's associated BSSID to the advertising mesh device and fronthaul interface. | Capture and validate baseline RSSI. | Clients with a valid RSSI sample are accepted as baselines. |
| 3 | N/A | Resolve the current station record every 10 minutes for 1 hour. | Validate current RSSI against baseline. | Each sample is available and no more than 10 dB below baseline. |
| 4 | N/A | Capture the final station record. | Validate final RSSI against baseline. | Final RSSI passes the same degradation check. |

---

# Test Case 7: EM_End_To_End_Link_Performance_Stability

## Objective

Verify stable end-to-end latency, packet loss, and throughput between WLAN
clients owned by the Controller or enabled Extenders and the Controller
gateway.

## Test Type

**Positive**

---

## Pre-Requisites

1. The Controller and all enabled Extenders are successfully onboarded.
2. EasyMesh services and fronthaul SSIDs are operational.
3. WLAN clients owned by the Controller or enabled Extenders are configured
   and available.
4. Controller fronthaul credentials and bridge IP are available.
5. The Controller can start an `iperf3` server for throughput validation.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | End-to-end client-to-Controller performance |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Average latency, packet loss, and throughput |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with bridge gateway and `iperf3` server |
| Agents | All enabled EasyMesh Extenders |
| Clients | WLAN clients owned by the Controller or enabled Extenders |
| Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Retrieve Controller fronthaul credentials and bridge IP. | Verify enabled Extenders are available. | Select Controller-owned and enabled-Extender-owned clients and reconnect them. | At least one eligible client connects successfully. |
| 2 | Start the Controller `iperf3` server. | N/A | Capture a 10-packet ping baseline and a throughput baseline. | Clients with packet loss within 5% and valid measurements are accepted. If `iperf3` cannot start, the test fails. |
| 3 | Keep the Controller `iperf3` server running. | Monitor topology health. | Every 10 minutes for 1 hour, capture ping and applicable throughput samples. | Packet loss is at most 5%, average latency is at most 2x baseline, and throughput is at least 80% of baseline. |
| 4 | N/A | N/A | Capture the final 100-packet ping and applicable throughput sample. | Final metrics pass the same validation limits. |
| 5 | In a `finally` cleanup block, stop the Controller `iperf3` server whether sampling succeeds or fails. | N/A | N/A | The temporary performance server is stopped and cleanup failures are reported. |

---
