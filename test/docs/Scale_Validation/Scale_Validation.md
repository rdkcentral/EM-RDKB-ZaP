# Scale Profile Definitions

The scale profile counts are taken from the test platform configuration:

| Scale Profile | Expected Agents | Expected WLAN Clients |
|---------------|-----------------|-----------------------|
| Small | 2 | 5 |
| Medium | 5 | 25 |
| Large | 10 | 50 |

Stability test duration is **1 hour** with a **10-minute polling interval**.
Baseline tests are one-time measurements. Agent and Controller recovery tests
reboot the target at every polling interval and validate recovery at every poll.

# Test Case 1: EM_Scale_ControllerAgent_Connectivity_Baseline

## Objective

Verify the configured number of scale Extenders is present and connected.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are onboarded.
3. EasyMesh services are running.
4. The testbed can read the configured Extender list and backhaul state.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Controller and Extender presence for the selected scale profile |
| Measured Metrics | Configured Extender count and connected Extender count |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | Enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Read the enabled scale profile and expected Extender count. | Enumerate enabled Extenders and capture their backhaul presence. | The selected scale profile and active Extender list are available. |
| 2 | Compare the connected Extender count with the configured expected count. | Remain available during the presence check. | The connected Extender count meets the expected count. |

---

# Test Case 2: EM_Scale_ControllerAgent_Connectivity_Stability

## Objective

Verify the active Extender set remains stable for the configured stability
duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are onboarded.
3. EasyMesh services are running.
4. The testbed can read Extender presence at the configured polling interval.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Active Extender presence stability |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Connected Extender count and Extender membership compared with baseline |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | Enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Read the selected scale profile and capture the baseline active Extender set. | Report each enabled Extender's current backhaul presence. | The baseline meets the expected Extender count. |
| 2 | Monitor the active Extender set at the configured polling interval until the configured duration ends. | Remain connected to the Controller. | The Extender count and membership match the baseline at every poll. |
| 3 | Capture the final active Extender set. | Report final backhaul presence. | The final Extender set matches the baseline. |

---

# Test Case 3: EM_Scale_Client_Association_Baseline

## Objective

Capture and validate the initial WLAN client associations for the selected
scale profile.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are onboarded.
3. Enabled WLAN clients and their MAC addresses are configured.
4. Controller fronthaul credentials are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Initial WLAN client associations across the Controller and Extenders |
| Measured Metrics | Connected client count and station MAC associations by device |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with fronthaul SSID |
| Agents | Enabled EasyMesh Extenders |
| Clients | Enabled WLAN clients |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Retrieve the Controller fronthaul credentials. | Enumerate enabled Extenders. | Enumerate enabled WLAN clients and reconnect them. | Credentials and connected clients are available. |
| 2 | Capture station MAC associations from the Controller and Extenders. | Report fronthaul station MACs. | Remain connected during capture. | The observed client count meets the selected scale profile and associations are recorded. |

---

# Test Case 4: EM_Scale_Client_Association_Stability

## Objective

Verify WLAN client associations remain unchanged for the configured stability
duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are onboarded.
3. Enabled WLAN clients and their MAC addresses are configured.
4. Controller fronthaul credentials are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | WLAN client association stability across all mesh devices |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Client count, station MAC membership, and association mapping compared with baseline |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with fronthaul SSID |
| Agents | Enabled EasyMesh Extenders |
| Clients | Enabled WLAN clients |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Retrieve fronthaul credentials and prepare the topology. | Verify each Extender is reachable. | Reconnect enabled WLAN clients and capture the baseline associations. | The baseline client count and station MAC sets meet the selected scale profile. |
| 2 | Monitor client associations at the configured polling interval until the configured duration ends. | Report station MACs from each fronthaul interface. | Remain connected. | Client count and station MAC membership match the baseline at every poll. |
| 3 | Capture final station associations. | Report final station MACs. | Remain connected. | Final client associations match the baseline. |

---

# Test Case 5: EM_Scale_ClientTraffic_Throughput_Baseline

## Objective

Capture one valid client-to-Controller throughput sample for each eligible
WLAN client.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are onboarded.
3. Enabled Controller-owned and Extender-owned WLAN clients are configured.
4. Controller fronthaul credentials, bridge IP, and `iperf3` are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Initial client-to-Controller traffic throughput |
| Measured Metrics | Client association, Extender presence, and throughput in Mbps |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with `iperf3` server |
| Agents | Enabled EasyMesh Extenders |
| Clients | WLAN clients owned by the Controller or selected Extenders |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Retrieve the Controller fronthaul credentials and start the Controller `iperf3` server. | Verify the expected Extender count and presence. | Reconnect eligible Controller-owned and Extender-owned WLAN clients. | The selected scale topology and connected clients are ready for traffic testing. If `iperf3` cannot start, the test fails. |
| 2 | Validate baseline client associations and Extender presence. | Report station associations. | Remain associated. | Baseline topology and associations meet the selected scale profile. |
| 3 | Receive `iperf3` traffic from each client and collect one sample. | Remain operational. | Send traffic to the Controller bridge IP. | A positive throughput sample is collected for every eligible client. |
| 4 | In a `finally` cleanup block, stop the Controller `iperf3` server whether sampling succeeds or fails. | N/A | N/A | Temporary traffic service is stopped and cleanup errors are reported. |

---

# Test Case 6: EM_Scale_ClientTraffic_Throughput_Stability

## Objective

Verify client associations, Extender presence, and throughput remain stable for
the configured stability duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are onboarded.
3. Enabled Controller-owned and Extender-owned WLAN clients are configured.
4. Controller fronthaul credentials, bridge IP, and `iperf3` are available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Client traffic, association, and scale-topology stability |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Extender presence, client association, and throughput compared with baseline |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with `iperf3` server |
| Agents | Enabled EasyMesh Extenders |
| Clients | WLAN clients owned by the Controller or selected Extenders |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Start the Controller `iperf3` server and capture the baseline. | Validate baseline Extender presence. | Reconnect Controller-owned and Extender-owned clients and capture baseline associations and throughput. | Baseline topology, associations, and throughput are valid. If `iperf3` cannot start, the test fails. |
| 2 | Monitor the topology and traffic at the configured polling interval until the configured duration ends. | Report Extender presence and station associations. | Send periodic `iperf3` traffic samples. | Extender presence and associations match baseline; each throughput sample remains above the implemented baseline floor. |
| 3 | Capture final topology, associations, and throughput. | Report final presence and station associations. | Complete the final throughput sample. | Final topology and associations match baseline and final throughput passes validation. |
| 4 | In a `finally` cleanup block, stop the Controller `iperf3` server whether sampling succeeds or fails. | N/A | N/A | Temporary traffic service is stopped and cleanup errors are reported. |

---

# Test Case 7: EM_Scale_CPU_Utilization_Baseline

## Objective

Capture and validate one CPU utilization snapshot for every scale device.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are reachable.
3. CPU utilization can be collected from every scale device.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Initial CPU utilization on the Controller and Extenders |
| Measured Metrics | CPU idle percentage, CPU utilization percentage, and high-CPU processes |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | Enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Discover the enabled scale profile and scale devices. | Remain reachable. | The expected number of Extenders is discovered. |
| 2 | Capture one CPU snapshot from `top`. | Capture one CPU snapshot from `top` on every Extender. | Calculate `CPU utilization (%) = 100 - CPU idle (%)`. Each device must have CPU idle greater than 20% (equivalent to utilization below 80%). Record processes using more than 50% CPU for stability monitoring. |
| 3 | Summarize the baseline results. | N/A | A baseline is available for every scale device. |

---

# Test Case 8: EM_Scale_CPU_Utilization_Stability

## Objective

Verify CPU utilization remains within limits and does not increase abnormally
for the configured stability duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are reachable.
3. CPU utilization can be collected at the configured polling interval.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | CPU utilization stability across the Controller and Extenders |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | CPU idle percentage, CPU utilization percentage, high-CPU process history, and change from baseline |

---

## Test Environment

| Component | Description |
|-----------|------------|
| Controller | EasyMesh Controller |
| Agents | Enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Capture the Controller CPU baseline from `top`. | Capture CPU baselines from all Extenders using `top`. | Calculate `CPU utilization (%) = 100 - CPU idle (%)`. Each baseline must have CPU idle greater than 20% (equivalent to utilization below 80%); record processes using more than 50% CPU. |
| 2 | Monitor CPU at the configured polling interval until the configured duration ends. | Report CPU snapshots at each poll. | Recalculate CPU utilization at every poll. CPU idle must remain greater than 20%, utilization must remain below 80%, and utilization must not increase by more than 20 percentage points from baseline. A process using more than 50% CPU for 2 consecutive samples fails the test. |
| 3 | Capture final CPU snapshots and calculate `CPU utilization (%) = 100 - CPU idle (%)`. | Report final CPU values. | Apply the same idle, utilization, baseline-change, and high-CPU-process limits to the final values. |

---

# Test Case 9: EM_Scale_Memory_Utilization_Baseline

## Objective

Capture and validate one memory utilization snapshot for every scale device.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are reachable.
3. Memory utilization can be collected from every scale device.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Initial memory utilization on the Controller and Extenders |
| Measured Metrics | Available memory percentage, used memory percentage, total memory, and used memory |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | Enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Discover the enabled scale profile and scale devices. | Remain reachable. | The expected number of Extenders is discovered. |
| 2 | Capture one memory snapshot using `free -m`. | Capture one memory snapshot using `free -m` from every Extender. | Calculate `used memory (%) = used / total × 100` and `available memory (%) = available / total × 100`. Each device must have available memory greater than 20% and used memory less than 80%; the snapshot becomes the stability baseline. |
| 3 | Summarize the baseline results. | N/A | A baseline is available for every scale device. |

---

# Test Case 10: EM_Scale_Memory_Utilization_Stability

## Objective

Verify memory utilization remains within limits without sustained growth for
the configured stability duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are reachable.
3. Memory utilization can be collected at the configured polling interval.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Memory utilization stability across the Controller and Extenders |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Available memory, used memory, baseline change, and used-memory growth history |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | Enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Capture the Controller memory baseline using `free -m`. | Capture memory baselines from all Extenders using `free -m`. | Calculate `used memory (%) = used / total × 100` and `available memory (%) = available / total × 100`. Each baseline must have available memory greater than 20% and used memory less than 80%. |
| 2 | Monitor memory at the configured polling interval until the configured duration ends. | Report memory snapshots at each poll. | Recalculate used and available percentages at every poll. Available memory must remain greater than 20%, used memory must remain less than 80%, and used memory must not increase by more than 20 percentage points from baseline. Three consecutive increasing used-memory samples totaling at least 50 MB fail the test as sustained growth. |
| 3 | Capture final memory snapshots. | Report final memory values. | Recalculate both percentages and apply the same absolute, baseline, and sustained-growth limits to the final values. |

---

# Test Case 11: EM_Scale_ConfigurationPropagation_Baseline

## Objective

Validate one Controller-to-Extender configuration propagation cycle for each
supported configuration parameter.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are onboarded.
3. Supported configuration parameters are available on the Controller and
   Extenders.
4. Client connectivity can be checked after configuration restoration.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Initial consistency and one propagation cycle for supported Controller configuration |
| Parameters Changed | Fronthaul SSID; 2.4 GHz, 5 GHz, and 6 GHz operating channels |
| Measured Metrics | Controller values, Extender values, propagation result, and restoration result |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | Enabled EasyMesh Extenders |
| Clients | Configured WLAN clients |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Read the original value for each supported parameter. | Report the corresponding parameter values. | Remain available for connectivity checks. | Original Controller and Extender values are captured. |
| 2 | Change the fronthaul SSID and each supported radio channel parameter (`channel_2_4`, `channel_5`, and `channel_6`) once, then verify the Controller update. Use channel 1 or 6 for 2.4 GHz, 42, 58, or 106 for 5 GHz, and 7, 23, or 39 for 6 GHz. | Verify each changed value propagates. | Verify connectivity is not unexpectedly lost. | Each SSID and channel update is accepted and propagated to all available Extenders. |
| 3 | Restore the original values and verify propagation. | Confirm restored values. | Confirm client connectivity. | All original values are restored consistently. |

---

# Test Case 12: EM_Scale_ConfigurationPropagation_Stability

## Objective

Verify repeated Controller configuration changes continue to propagate to all
Extenders for the configured stability duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. The Controller and configured Extenders are onboarded.
3. Supported configuration parameters are available on the Controller and
   Extenders.
4. Client connectivity can be checked after each propagation cycle.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Repeated Controller-to-Extender configuration propagation stability |
| Parameters Changed | Fronthaul SSID; 2.4 GHz, 5 GHz, and 6 GHz operating channels |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Controller update result, Extender propagation result, parameter consistency, and restoration result |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | Enabled EasyMesh Extenders |
| Clients | Configured WLAN clients |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|---------|-----------------|
| 1 | Capture the initial value for each supported parameter and validate initial propagation. | Report the corresponding baseline values. | Remain available. | Initial values and propagation baseline are recorded. |
| 2 | At the configured polling interval, update the fronthaul SSID and each supported radio channel parameter (`channel_2_4`, `channel_5`, and `channel_6`). Use channel 1 or 6 for 2.4 GHz, 42, 58, or 106 for 5 GHz, and 7, 23, or 39 for 6 GHz. | Verify each new SSID and channel value propagates. | Verify normal connectivity. | Each propagation cycle completes without an Extender mismatch. |
| 3 | Continue cycles until the configured duration ends. | Maintain parameter consistency. | Remain connected. | Configuration remains consistently propagated throughout monitoring. |
| 4 | Restore the original values after monitoring. | Confirm restoration on every Extender. | Confirm connectivity. | Original configuration is restored successfully. |

---

# Test Case 13: EM_Scale_AgentRecovery_AfterReboot

## Objective

Verify all enabled Extenders recover within their configured KPI and the scale
topology is restored after each scheduled Extender reboot throughout the
stability test duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. All enabled Extenders are onboarded and connected before the test.
3. Agent recovery KPI is configured.
4. The testbed can reboot and reconnect Extenders.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Scheduled simultaneous Extender reboot and scale-topology recovery |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Extender recovery time, connected Extender count, Extender membership, and topology stabilization |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | All enabled EasyMesh Extenders rebooted concurrently |
| Clients | Not required |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Capture the initial Extender presence baseline. | Verify all enabled Extenders are connected. | Baseline count and membership meet the selected scale profile. |
| 2 | At every 10-minute poll interval during the 1-hour test, schedule the next recovery check. | Reboot all enabled Extenders concurrently and reconnect them. | Each Extender recovers within the configured Agent recovery KPI at every poll. |
| 3 | Validate the scale setup after each reboot recovery. | Report recovered presence at every poll. | Extender count and membership return to baseline at every poll. |

---

# Test Case 14: EM_Scale_ControllerRecovery_AfterReboot

## Objective

Verify the Controller recovers within its configured KPI and the scale topology
is restored after each scheduled Controller reboot throughout the stability
test duration.

## Test Type

**Positive**

---

## Pre-Requisites

1. The selected scale profile is enabled.
2. All enabled Extenders are onboarded and connected before the test.
3. Controller recovery KPI is configured.
4. The testbed can reboot and reconnect the Controller.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Observation Scope | Scheduled Controller reboot and scale-topology recovery |
| Test Duration | 1 hour |
| Poll Interval | 10 minutes |
| Measured Metrics | Controller recovery time, connected Extender count, Extender membership, and topology stabilization |

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller rebooted on schedule |
| Agents | All enabled EasyMesh Extenders |
| Clients | Not required |
| Topology | Selected Small, Medium, or Large scale profile |

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Capture the initial scale-topology baseline. | Verify all enabled Extenders are connected. | Baseline count and membership meet the selected scale profile. |
| 2 | At every 10-minute poll interval during the 1-hour test, schedule the next recovery check. | Reboot and recover the Controller, then monitor reconnection and topology synchronization. | The Controller recovers within the configured Controller recovery KPI at every poll. |
| 3 | Validate the scale setup after each Controller reboot recovery. | Report current Extender presence at every poll. | Extender count and membership return to baseline at every poll. |

---
