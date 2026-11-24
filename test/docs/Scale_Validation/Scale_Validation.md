# Test Case 1: EM_Scale_ControllerAgent_Connectivity

## Objective

Verify the expected Agent count is displayed in the topology.

## Test Type

**Positive**

---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Expected Agent Count | Small: 2, Medium: 5, Large: 10 |
| Expected Client Count | Small: 5, Medium: 25, Large: 50 |
| Topology Source | Device.WiFi.DataElements.Network.Topology |
| Verification Method | Topology baseline capture and periodic comparison |
---


# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless Clients |

---

# Scale Topologies

## Small Scale
- 1 Controller
- 2 Agents
- 5 Clients

## Medium Scale
- 1 Controller
- 5 Agents
- 25 Clients

## Large Scale
- 1 Controller
- 10 Agents
- 50 Clients

---
## Test Procedure and Expected Results


| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|--------|--------|-----------------|
| 1 | Verify all expected Agents and Clients are onboarded. Capture and store the baseline topology information using Device.WiFi.DataElements.Network.Topology, including Controller ID, Agent Count, Agent MAC Addresses, Backhaul Stations, Fronthaul Client Count, Client MAC Addresses, Parent-Child Relationships, and Connection Status. | Verify backhaul connectivity to the Controller and record Agent information. | Connect the required number of clients for the target scale topology and record client information. | All expected Agents and Clients are onboarded and visible in the topology. Baseline topology information is captured and stored successfully. |
| 2 | Establish the required scale topology (Small / Medium / Large) and maintain network operation for the configured test duration[4-6 hrs]. | Ensure Agents remain operational and maintain backhaul connectivity. | Generate and maintain normal client traffic/activity. | Network remains stable and all devices remain operational throughout the test duration. |
| 3 | Periodically[every 30mins] collect and compare the current topology information against the baseline, including Agent Count, Agent MAC Addresses, Backhaul Stations, Fronthaul Client Count, Client MAC Addresses, Parent-Child Relationships, and Connection Status. | Verify backhaul connectivity remains active and stable. | Remain connected and continue traffic generation. | The current topology matches the baseline topology. No expected Agent or Client is missing from the network. |
| 4 | Monitor Controller  logs em_ctrl for disconnect, reconnect, join, leave, re-onboarding, topology changes, and backhaul link events. | Monitor Agent logs em_agent  for backhaul disconnects, reconnects, and re-onboarding events. | Monitor client connectivity status. | No unexpected topology events, Agent disconnects, or re-onboarding events are observed during the test duration. |
| 5 | Capture the final topology information at the end of the test duration and compare it with the stored baseline topology. Verify Agent Count, Agent MAC Addresses, Backhaul Stations, Fronthaul Client Count, Client MAC Addresses, Parent-Child Relationships, and Connection Status. | Verify backhaul connectivity is maintained until the end of the test. | Verify all expected clients remain connected. | Final topology matches the baseline topology. No unexpected topology changes, Agent loss, Client loss, or connectivity issues are observed. |
---
# Test Case 2: EM_Scale_Client_Association

## Objective

Verify all clients remain associated to their respective Agents throughout the test duration.

## Test Type

**Positive**
---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Expected Agent Count | Small: 2, Medium: 5, Large: 10 |
| Expected Client Count | Small: 5, Medium: 25, Large: 50 |
| Association Check Method | iw station dump + topology comparison |
| Verification Method | Baseline capture and periodic association validation |
| Pass Criteria | Agent and client association set remains unchanged throughout test duration |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless Clients |

---

# Scale Topologies

## Small Scale
- 1 Controller
- 2 Agents
- 5 Clients

## Medium Scale
- 1 Controller
- 5 Agents
- 25 Clients

## Large Scale
- 1 Controller
- 10 Agents
- 50 Clients

---

## Test Procedure and Expected Results
| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|---------|---------|-----------------|
| 1 | Verify topology is formed and capture baseline topology information  using iw dev commands. | Verify all Agents are operational and connected. | Connect the required number of Clients. | All Agents are connected and all Clients are associated successfully. |
| 2 | Maintain the scale topology for the test duration. | Maintain backhaul connectivity on all Agents. | Generate normal traffic. | Network remains stable throughout the test duration. |
| 3 | Periodically verify topology information and collect Controller-associated client details using `iw dev <controller_interface> station dump`. | Repeat the following on all Agents to collect associated client details from `iw dev <interface> station dump` | Remain connected. | Agent count, Client count, and associated MAC addresses match the baseline. |
| 4 | Monitor topology and connectivity events. | Monitor all Agent logs for disconnect, reconnect, deauth, disassoc, and reassociation events. | N/A | No unexpected client or Agent connectivity events are observed. |
| 5 | Capture final topology information and compare it with the baseline. | Re-run the client association commands on all Agents and compare results with the baseline. | N/A | Agent count, Client count, and associated MAC addresses remain unchanged. |

---
# Test Case 3: EM_Scale_ClientTraffic_Throughput

## Objective

Verify that client traffic continues to flow normally through the Agents throughout the test duration under scale conditions.

## Test Type

**Positive**
---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Expected Agent Count | Small: 2, Medium: 5, Large: 10 |
| Expected Client Count | Small: 5, Medium: 25, Large: 50 |
| Traffic Tool | iperf3 |
| Traffic Profile | iperf3 client-to-agent traffic with periodic validation |
| Pass Criteria | Traffic continues without interruption and topology/client counts remain consistent with baseline |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents/Extenders |
| Clients | Wireless Clients |
| Traffic Tool | iperf3 |

---

# Scale Topologies

## Small Scale
- 1 Controller
- 2 Agents
- 5 Clients

## Medium Scale
- 1 Controller
- 5 Agents
- 25 Clients

## Large Scale
- 1 Controller
- 10 Agents
- 50 Clients

---

## Test Procedure and Expected Results
| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|---------|---------|-----------------|
| 1 | Verify all Agents are onboarded and the scale topology is formed. Capture baseline topology information in json format(Agent Count, Agent MAC Addresses, Client Count, Client MAC Addresses, Connection Status). | Verify all Clients are connected to the respective Agents. | Connect to the required Agent/Controller SSIDs. | All Agents and Clients are connected successfully. |
| 2 | Establish the required scale topology (Small / Medium / Large). | Verify associated Client count and MAC addresses. | Remain connected. | Scale topology is established successfully. |
| 3 | Record Agent IP addresses and maintain topology throughout the test duration. | Start an iperf3 server on all Agents:<br>`iperf3 -s -D` | Start traffic towards the corresponding Agent:<br>`iperf3 -c <Agent-IP> -t 60 -P 2` | Traffic generation starts successfully. |
| 4 | Every 60 minutes during the test, verify topology, client associations, and traffic status on the Controller and all Agents. Compare Agent Count, Client Count, and MAC addresses with the baseline. | Verify client associations and traffic reception. | Continue generating iperf3 traffic. | All Agents and Clients remain connected and traffic continues without interruption. |
| 5 | Capture final topology and throughput information and compare with the baseline. | Re-run client association checks on all Agents and collect throughput results. | Complete the final traffic run. | Agent count, Client count, connection status, and associated MAC addresses remain unchanged. |

---
# Test Case 4: EM_Scale_CPU_Utilization

## Objective

Verify CPU utilization remains stable and within acceptable limits throughout the test duration under scale conditions.

## Test Type

**Positive**
---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| CPU Sample Interval | Every 30 minutes |
| CPU Tools | top |
| CPU Thresholds | CPU Idle > 20%, CPU Utilization < 80%, No sustained process > 50% |
| Verification Method | Baseline, periodic trend monitoring, and final comparison |
| Pass Criteria | CPU remains within thresholds with no abnormal sustained spikes |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless Clients |

---

# Scale Topologies

## Small Scale
- 1 Controller
- 2 Agents
- 5 Clients

## Medium Scale
- 1 Controller
- 5 Agents
- 25 Clients

## Large Scale
- 1 Controller
- 10 Agents
- 50 Clients

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|---------|---------|-----------------|
| 1 | Verify all Agents are onboarded and the scale topology is formed. Record baseline CPU statistics on the Controller using `top`. | Record baseline CPU statistics on all Agents using `top`. | Connect the required number of Clients and start normal traffic generation. | Baseline CPU statistics are recorded on all devices. CPU Idle is greater than 20%. |
| 2 | Establish and maintain the required scale topology throughout the test duration. | Verify all associated Clients remain connected. | Generate and maintain normal network traffic. | Scale topology is operational and all devices remain connected. |
| 3 | Every 30 minutes during the test, execute `top` and record CPU statistics. | Every 30 minutes during the test, execute `top` and record CPU statistics on all Agents. | Continue traffic generation. | CPU Idle remains above 20%, CPU utilization remains below 80%, and no process continuously consumes more than 50% CPU. |
| 4 | Monitor CPU utilization trends and compare the recorded values against the baseline throughout the test duration. | Monitor CPU utilization trends on all Agents. | Continue normal traffic activity. | CPU utilization remains stable with no abnormal spikes or sustained high CPU usage. |
| 5 | At the end of the test duration, collect final CPU statistics using `top` and compare them with the baseline. | Collect and compare final CPU statistics on all Agents. | N/A | No sustained process consumes more than 50% CPU, CPU Idle remains above 20%, and no abnormal increase in CPU utilization is observed. |
---
# Test Case 5: EM_Scale_Memory_Utilization

## Objective

Verify memory utilization remains stable and no memory leak is observed during scale testing.

## Test Type

**Positive**
---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Memory Sample Interval | Every 30 minutes |
| Memory Tools | free -m |
| Memory Thresholds | Available Memory > 20% of total, Used Memory < 80% of total |
| Verification Method | Baseline, periodic trend monitoring, and final comparison |
| Pass Criteria | Memory usage remains stable with no monotonic increase indicating leak |
---

# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless Clients |

---

# Scale Topologies

## Small Scale
- 1 Controller
- 2 Agents
- 5 Clients

## Medium Scale
- 1 Controller
- 5 Agents
- 25 Clients

## Large Scale
- 1 Controller
- 10 Agents
- 50 Clients

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|---------|---------|-----------------|
| 1 | Verify all Agents are onboarded and the scale topology is formed. Record baseline memory statistics using `free -m`. | Record baseline memory statistics using `free -m` on all Agents. | Connect the required number of Clients and start normal traffic generation. | Baseline memory statistics are recorded successfully on the Controller and all Agents. |
| 2 | Establish and maintain the required scale topology (Small / Medium / Large) throughout the test duration. | Verify all associated Clients remain connected. | Generate and maintain normal network traffic. | Scale topology remains operational and all devices remain connected. |
| 3 | Every 30 minutes during the test, execute `free -m` and record memory statistics. Compare the values with the baseline. | Every 30 minutes during the test, execute `free -m` and record memory statistics on all Agents. | Continue normal traffic generation. | Available Memory remains above **20% of Total Memory**, Used Memory remains below **80% of Total Memory**, and memory utilization remains stable. |
| 4 | Monitor memory utilization trends throughout the test duration and compare against the baseline. | Monitor memory utilization trends on all Agents. | Continue traffic generation. | No abnormal memory growth or sudden drop in available memory is observed. |
| 5 | At the end of the test duration, execute `free -m`, collect final memory statistics, and compare them with the baseline and periodic measurements. | Execute `free -m` on all Agents and compare final values with the recorded data. | N/A | Memory utilization remains stable with no monotonic increase in used memory, indicating no memory leak. |
---
# Test Case 6: EM_Scale_AgentRecovery_AfterReboot

## Objective

Verify that an Agent successfully rejoins the EasyMesh topology and restores client connectivity after reboot under scale conditions.

## Test Type

**Positive**
---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Reboot Method | One Agent at a time |
| Recovery Validation | Topology rejoin, backhaul connected state, client reachability |
| Recovery Targets | Small: 30-60 sec, Medium: 1-2 min, Large: 2-5 min |
| Verification Method | Baseline capture, timed recovery observation, and post-recovery comparison |
| Pass Criteria | Agent rejoins within target window and baseline topology/client connectivity is restored |
---

# Test Environment

| Component | Description |
|------------|------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless Clients |

---

# Scale Topologies

## Small Scale
- 1 Controller
- 2 Agents
- 5 Clients

## Medium Scale
- 1 Controller
- 5 Agents
- 25 Clients

## Large Scale
- 1 Controller
- 10 Agents
- 50 Clients

---
## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|-------------|---------|---------|-----------------|
| 1 | Verify all Agents are onboarded and the topology is healthy using Data Elements topology information (`Device.WiFi.DataElements.Network.Topology`) or the topology UI. Capture baseline topology information (Agent Count, Agent MAC Addresses, Connection Status). | Verify all Agents are operational and backhaul links are connected using `iw dev <backhaul_intf> link`. | Connect Clients to the Agents under test. | Scale topology is established successfully and all nodes are reachable. |
| 2 | Record baseline topology and connectivity information. | Verify client associations on all Agents using `station_dump`. | Verify client connectivity using ping to the gateway/server. | All backhaul links are connected and all Clients are reachable. |
| 3 | Select one Agent at a time and initiate a reboot. Repeat the procedure for each Agent in the topology. | Reboot the selected Agent using the `reboot` command. | Continuously run ping during the reboot and recovery period. | The rebooted Agent goes offline temporarily and client traffic is briefly interrupted. |
| 4 | Monitor topology information and Agent recovery status using `Device.WiFi.DataElements.Network.Topology`. Record the time taken for the Agent to rejoin the topology. | Verify the rebooted Agent rejoins the Controller and the backhaul link returns to the Connected state using `iw dev <backhaul_intf> link`. Repeat for each rebooted Agent. | Continue ping verification during recovery. | The Agent successfully rejoins the EasyMesh topology and connectivity is restored automatically. Typical recovery time: Small Scale: 30-60 sec, Medium Scale: 1-2 min, Large Scale: 2-5 min. |
| 5 | Verify the recovered Agent is present in the topology and that the expected Agent Count is maintained. | Verify backhaul status remains Connected and clients are associated using `iw dev <backhaul_intf> link` and `station_dump`. | Verify client connectivity using ping and application traffic if applicable. | Agent Count matches the baseline, clients reconnect automatically, and normal network operation resumes. |
---

# Test Case 7: EM_Scale_ControllerRecovery_AfterReboot

## Objective

Verify that all Agents automatically reconnect and topology is restored after Controller reboot under scale conditions.

## Test Type

**Positive**
---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Reboot Method | Controller reboot |
| Recovery Validation | Controller service recovery, topology sync, agent/client reconnect |
| Recovery Targets | Typical recovery time: 1-2 min |
| Verification Method | Baseline capture, reboot timing, and post-recovery topology comparison |
| Pass Criteria | All agents/clients reconnect and topology matches baseline without unexpected disconnects |
---

# Test Environment

| Component | Description |
|------------|------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless Clients |

---

# Scale Topologies

## Small Scale
- 1 Controller
- 2 Agents
- 5 Clients

## Medium Scale
- 1 Controller
- 5 Agents
- 25 Clients

## Large Scale
- 1 Controller
- 10 Agents
- 50 Clients

---

## Test Procedure and Expected Results

| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|---------|---------|-----------------|
| 1 | Verify the scale topology is established and capture baseline topology information using `Device.WiFi.DataElements.Network.Topology`. Record Agent Count, Agent MAC Addresses, Client Count, and Client MAC Addresses. | Verify all Agents are connected and operational. | Verify all Clients are connected and reachable. | Baseline topology is captured successfully and all devices are operational. |
| 2 | Reboot the Controller and monitor Controller availability. Record the reboot start time. | Monitor Controller reachability and maintain Agent status monitoring. | Run continuous ping to monitor connectivity. | Controller becomes temporarily unavailable. |
| 3 | Verify Controller services recover successfully and record the time taken for the Controller to become operational. | Wait for Controller recovery and automatic topology synchronization. | Continue connectivity monitoring. | Controller services recover successfully and topology synchronization starts automatically. |
| 4 | Verify topology information after recovery and compare it with the baseline. Record Controller recovery time. | Verify all Agents are visible in the topology and backhaul status is Connected. | Verify Clients reconnect and are reachable. | Controller successfully restores the topology. Typical recovery time: 1-2 min|
| 5 | Verify topology stability during the observation period and compare final topology information with the baseline. | Verify all Agents remain connected. | Verify Clients remain connected and traffic operates normally. | Agent Count, Client Count, and topology information match the baseline with no unexpected disconnects. |

---
# Test Case 8:  EM_Scale_ConfigurationPropagation_Stability

## Objective

Verify that configuration changes applied on the Controller are successfully propagated to all Agents and reflected on all connected clients across the scale topology.

## Test Type

**Positive**
---
## Pre-Requisites

1. All Agents are successfully onboarded and visible in the EasyMesh topology.
2. EasyMesh services running on both devices.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Change Scope | `Device.WiFi.DataElements.Network.SSID.{i}.SSID`, `Device.WiFi.DataElements.Network.PassPhrase`, `Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClassProfile.{i}.Class`, `Channel`, `CountryCode`, `Enabled`, and `BSS.SSID`.  |
| Validation Scope | Controller and all Agents parameter consistency + client connectivity |
| Verification Method | Baseline capture, parameter update, propagation check, and stability observation |
| Pass Criteria | Updated values are consistent across all Agents with no connectivity impact |
---

# Test Environment

| Component | Description |
|------------|------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless Clients |

---

# Scale Topologies

## Small Scale
- 1 Controller
- 2 Agents
- 5 Clients

## Medium Scale
- 1 Controller
- 5 Agents
- 25 Clients

## Large Scale
- 1 Controller
- 10 Agents
- 50 Clients

---

## Test Procedure and Expected Results
| Step Number | Controller | Agents | Clients | Expected Result |
|-------------|------------|---------|---------|-----------------|
| 1 | Verify all Agents are onboarded and the scale topology is healthy. Record the baseline values of the Data Elements parameters under test, such as `Device.WiFi.DataElements.Network.SSID.{i}.SSID`, `Device.WiFi.DataElements.Network.PassPhrase`, `Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClassProfile.{i}.Class`, `Channel`, `CountryCode`, `Enabled`, and `BSS.SSID`. | Verify the current parameter values on all Agents. | Verify Clients are connected and network services are accessible. | Baseline parameter values are captured successfully on the Controller and all Agents. |
| 2 | Modify the selected Data Elements parameter on the Controller. | Monitor parameter propagation to all Agents. | Continue normal network activity. | The Controller accepts and applies the configuration change successfully. |
| 3 | Verify the updated parameter value on the Controller using the corresponding DE path. | Verify the propagated value on all Agents using the same DE path. | Verify network connectivity is maintained. | The configured value matches on the Controller and all Agents. |
| 4 | Compare the configured values reported by all Agents against the Controller value. | Validate parameter consistency across all Agents for the modified path (`SSID`, `PassPhrase`, `Channel`, `Operating Class`, `CountryCode`, `Enabled`, etc.). | Verify connected Clients continue normal operation. | Configuration is propagated successfully to all Agents without mismatch. |
| 5 | Verify topology and service stability after propagation. | Verify all Agents remain connected and operational after the update. | Verify Clients remain connected and can access network services. | Parameter propagation is successful across the topology with no connectivity impact. |

---
