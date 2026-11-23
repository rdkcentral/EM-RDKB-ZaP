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
# Test Case 9: EM_Scale_ServiceRestart_Recovery

## Objective

Verify that Controller and Agent EasyMesh services recover without device
reboot and restore topology, client connectivity, and active configuration.

## Test Type

**Recovery / Stability**

---
## Pre-Requisites

1. Controller, Agents, and configured Clients are reachable.
2. EasyMesh services are running.
3. Baseline topology, client associations, configuration, and traffic are captured.
4. Approved service-control commands are available.
---
## Test Configuration

| Parameter | Value |
|-----------|-------|
| Restart Target | Controller, one Agent, or multiple Agents |
| Traffic State | Normal traffic and traffic active during restart |
| Monitoring | Service state, topology, client associations, logs, and recovery time |
| Pass Criteria | Services recover and topology/client state returns to baseline |
---
# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless and LAN Clients |
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
|-------------|------------|--------|---------|-----------------|
| 1 | Capture topology, Agent count, client count, configuration, and active traffic baseline. | Confirm Agent reachability and service state. | Confirm client associations and reachability. | Baseline is captured successfully. |
| 2 | Restart the Controller or selected EasyMesh service using the approved command. | Continue monitoring connectivity. | Continue traffic and reachability checks. | Restart is recorded and the affected service becomes temporarily unavailable. |
| 3 | Monitor service status and topology synchronization. | Verify Agent reconnection. | Verify client reconnection. | Services recover and synchronization starts automatically. |
| 4 | Capture final topology and compare it with the baseline. | Verify all Agents remain operational. | Verify clients and traffic recover. | Configuration is preserved and no orphaned topology entry remains. |
| 5 | Continue monitoring the recovered topology for the observation period. | Confirm services remain operational and backhaul connectivity is stable. | Confirm clients remain connected and traffic remains available. | Recovered topology remains stable with no unexpected disconnects or repeated service restarts. |

---
# Test Case 10: EM_Scale_ConfigurationPersistence_AfterReboot

## Objective

Verify that supported configuration values persist after reboot and remain
consistent across the Controller and Agents.

## Test Type

**Configuration / Reboot Recovery**

---
## Pre-Requisites

1. The scale topology is healthy.
2. Configuration values can be read on the Controller and Agents.
3. Baseline client and topology information is stored.
---
## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration Scope | SSID, operating class, and other supported parameters |
| Recovery Action | Device reboot |
| Validation | Controller/Agent parameter and topology comparison |
| Pass Criteria | Configuration persists and topology is restored correctly |
---
# Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agents | EasyMesh Agents |
| Clients | Wireless and LAN Clients |
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
|-------------|------------|--------|---------|-----------------|
| 1 | Record SSID, operating class, topology, and client associations. | Record current Agent configuration. | Record client connectivity. | Baseline configuration is captured. |
| 2 | Change a supported configuration parameter. | Verify the value propagated to the Agents. | Continue normal connectivity checks. | Updated values are consistent across the topology. |
| 3 | Reboot the selected device and record the reboot start time. | Monitor Agent service and link recovery. | Monitor client reconnection. | The device reboots and returns to service without configuration loss. |
| 4 | Capture final configuration and topology after reboot. | Verify final Agent values. | Verify final associations and reachability. | Final state matches the configured values and topology baseline without corruption. |
| 5 | Continue monitoring the restored topology for the observation period. | Confirm Agents remain connected and operational. | Confirm Clients remain connected and reachable. | Configuration and topology remain stable after recovery. |

---
# Test Case 11: EM_Scale_WiFiReset_Recovery

## Objective

Verify that one or more Wi-Fi resets do not permanently affect the scaled
topology or connected clients.

## Test Type

**Recovery / Scale Stability**

---
## Pre-Requisites

1. Small, Medium, or Large scale topology is established.
2. WLAN Clients are associated and reachable.
3. Wi-Fi interface, radio, or service reset is supported.
4. Baseline topology, traffic, CPU, and memory values are captured.
---
## Test Configuration

| Parameter | Value |
|-----------|-------|
| Scale Profiles | Small, Medium, and Large |
| Reset Target | Agent Wi-Fi interface, radio, or Wi-Fi service |
| Monitoring | Topology, associations, traffic, CPU, memory, and recovery time |
| Pass Criteria | Agents and Clients recover without manual reconnection |
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
|-------------|------------|--------|---------|-----------------|
| 1 | Capture topology, client associations, link metrics, traffic, CPU, and memory baselines. | Confirm Wi-Fi state and Agent reachability. | Confirm WLAN associations. | Baseline is captured for the selected scale profile. |
| 2 | Trigger the approved Wi-Fi reset on one or more selected devices. | Monitor interface and backhaul state. | Monitor client associations. | Reset is detected and associated with the correct device. |
| 3 | Monitor backhaul and fronthaul recovery. | Verify Agents rejoin the topology. | Verify Clients rejoin and traffic recovers. | Expected topology and associations are restored. |
| 4 | Compare final topology and metrics with the baseline. | Verify Agent count, topology, CPU, and memory. | Verify client membership, reachability, and traffic. | Client membership, topology, traffic, CPU, and memory return within limits. |
| 5 | Continue monitoring the restored topology for the observation period. | Confirm Agents remain connected and operational. | Confirm Clients remain connected and reachable. | The scale topology remains stable after Wi-Fi recovery without manual reconnection. |

---

# Detailed Test Procedure Steps

The following instructions expand the procedure tables into operator actions.
Select one scale profile before starting a test and record the selected
Controller, Agent, and Client inventory. Replace values in angle brackets with
values from the test environment. Do not execute a command containing an
unresolved placeholder.

## Common Scale Validation Setup

1. Select the Small, Medium, or Large topology and record the expected
   Controller, Agent, and Client counts.
2. Verify that every Agent is onboarded and visible from the Controller.
3. Capture the topology baseline:
   ```text
   rbuscli get Device.WiFi.DataElements.Network.Topology
   ```
   Record Agent MAC addresses, parent-child relationships, backhaul state,
   client count, client MAC addresses, and connection status.
4. On each Agent, identify the relevant interfaces:
   ```text
   ip -br link
   iw dev
   ```
   Record interface names before collecting link or station data.
5. Capture client and link information with:
   ```text
   iw dev <interface> link
   iw dev <interface> station dump
   ```
6. From the selected Clients, verify reachability to the approved gateway or
   traffic host:
   ```text
   ping <gateway-or-server-ip>
   ```
7. Record the test start time, device inventory, baseline topology, client
   associations, active configuration, traffic state, CPU, memory, and
   relevant Controller and Agent log locations.

## Test Case 1: Controller and Agent Connectivity

1. Build the selected scale profile and confirm the expected number of Agents
   and Clients are connected.
2. Run the topology command from the Controller and save the complete output.
3. On every Agent, verify the backhaul link and station information using the
   interface identified during setup.
4. From every Client, run a reachability check to the approved gateway or
   server and record the result.
5. Maintain normal traffic for the configured observation period. Repeat the
   topology command at the defined interval and compare Agent count, Client
   count, MAC addresses, parent-child relationships, and connection status.
6. Review Controller and Agent logs for unexpected join, leave, disconnect,
   reconnect, or re-onboarding events.
7. Capture the final topology and client results. Pass only when the final
   inventory and relationships match the baseline.

## Test Case 2: Client Association

1. Establish the selected scale profile and record each Client's expected
   serving device and MAC address.
2. On the Controller and each Agent, run:
   ```text
   iw dev <fronthaul_interface> station dump
   ```
   Save the baseline station list and association details.
3. Confirm that all expected Clients are associated and can reach the approved
   gateway or server.
4. Maintain normal traffic and repeat the station dump at the configured
   interval on every serving device.
5. Compare each station list with the baseline. Check for missing MAC
   addresses, unexpected associations, authentication failures, and connected
   time resets.
6. Review logs for deauthentication, disassociation, reassociation, or Agent
   connectivity events.
7. Perform a final topology and station dump comparison. Pass only when all
   expected Clients remain associated and reachable.

## Test Case 3: Client Traffic Throughput

1. Establish the selected topology and identify an approved traffic server
   reachable through the Controller and Agents.
2. Start the traffic server on the Controller or approved external host:
   ```text
   iperf3 -s
   ```
3. From the selected Clients, start the approved throughput profile:
   ```text
   iperf3 -c <server_ip> -t 300
   ```
   Use the configured client-to-server or bidirectional profile.
4. Record throughput, retransmissions, connection failures, and timestamps for
   each Client.
5. At each interval, collect topology and station data. Confirm Agent and
   Client counts remain equal to the baseline.
6. Run concurrent reachability checks and record latency and packet loss.
7. Stop the traffic profile, capture final topology and station data, and
   compare the results with the baseline. Pass only when traffic completes
   without unexpected disconnects or topology loss.

## Test Case 4: CPU Utilization

1. Establish the selected scale profile and allow the network to reach a
   steady state before collecting measurements.
2. On the Controller and every Agent, capture the baseline:
   ```text
   top -b -n 1
   ```
   Record total CPU usage and the CPU usage of EasyMesh-related processes.
3. Confirm the baseline topology and Client associations before applying load.
4. Generate the approved normal traffic profile and collect CPU samples at the
   configured interval.
5. Record the timestamp, device, total CPU, EasyMesh process CPU, Agent count,
   Client count, and any service or connectivity event for every sample.
6. Check logs for process restarts, watchdog events, missed heartbeats, or
   topology changes that coincide with CPU increases.
7. Stop traffic and collect a final CPU and topology sample. Pass only when
   CPU remains within the configured limit and all devices remain operational.

## Test Case 5: Memory Utilization

1. Establish the selected topology and verify all expected Clients are
   associated.
2. On the Controller and every Agent, capture the baseline:
   ```text
   free -m
   ```
   Record total, used, free, available memory, and swap usage if present.
3. Maintain the approved traffic and topology workload for the observation
   period.
4. Collect `free -m` at each interval and record the values with timestamps.
5. Compare memory usage with the baseline and check for continuous growth,
   reduced available memory, swap activity, process restarts, or OOM events.
6. At each interval, confirm topology, Agent count, Client count, and traffic
   remain healthy.
7. Stop the workload and collect final memory and topology data. Pass only
   when memory returns to the expected range without service impact or
   abnormal growth.

## Test Case 6: Agent Recovery After Reboot

1. Select one Agent and capture the complete topology, link, Client, and
   reachability baseline.
2. Ensure the Agent has console or out-of-band access before rebooting it.
3. Start continuous ping from an approved Client or traffic host and record the
   reboot start time.
4. Reboot only the selected Agent using the approved platform procedure.
5. Monitor the Agent until it is reachable again. Record the time at which the
   device, EasyMesh service, backhaul, and fronthaul become available.
6. From the Controller, repeatedly query:
   ```text
   rbuscli get Device.WiFi.DataElements.Network.Topology
   ```
   Confirm that the Agent is re-onboarded under the correct parent and that no
   stale or duplicate topology entry remains.
7. Confirm expected Clients reconnect and traffic resumes. Compare final Agent
   state, Client membership, and topology relationships with the baseline.

## Test Case 7: Controller Recovery After Reboot

1. Capture the complete topology, Agent count, Client count, configuration,
   traffic, and reachability baseline.
2. Start continuous ping from representative Clients and record the Controller
   reboot start time.
3. Reboot the Controller using the approved platform procedure.
4. Monitor Controller reachability and service recovery. Record when the
   Controller becomes reachable and when EasyMesh topology synchronization
   begins.
5. Confirm that each Agent reconnects to the Controller and that the expected
   parent-child relationships are restored.
6. Query the topology and compare Agent MAC addresses, Client count, Client
   MAC addresses, and connection status with the baseline.
7. Confirm Client traffic and reachability. Continue monitoring for the
   observation period and pass only when no unexpected disconnect or topology
   corruption remains.

## Test Case 8: Configuration Propagation Stability

1. Select one supported configuration parameter and record its current value on
   the Controller and every Agent.
2. Save the topology, Client associations, and traffic baseline before making
   the change.
3. Apply the new value on the Controller using the approved configuration
   method. Record the exact parameter path, old value, new value, and time.
4. Query the updated value on the Controller and each Agent. Confirm that the
   value is identical across the topology.
5. Verify that Clients remain associated and reachable. Repeat the topology
   query and station checks after propagation.
6. Review Controller and Agent logs for rejected updates, propagation errors,
   service restarts, or unexpected Client disconnects.
7. Continue normal traffic for the observation period, then capture final
   parameter, topology, and Client results. Pass only when propagation is
   consistent and connectivity is unaffected.

## Test Case 9: Controller and Agent Service Restart

1. Complete the Common Scale Validation Setup and record the service state,
   topology, Client associations, configuration, and active traffic.
2. Select the restart target and confirm that approved service-control
   commands and console or out-of-band access are available.
3. Start normal traffic and record the restart start time.
4. Restart only the selected Controller or Agent EasyMesh service using the
   approved command. Do not reboot the device for this test.
5. Monitor service state, Controller and Agent logs, topology visibility,
   backhaul state, Client associations, and traffic while the service is down.
6. Record the time at which the service returns, the Agent re-onboards or
   synchronizes, Clients reconnect, and traffic resumes.
7. Query the final topology and configuration. Continue monitoring for the
   observation period and pass only when the state returns to baseline without
   orphaned entries or repeated service restarts.

## Test Case 10: Configuration Persistence After Reboot

1. Select supported parameters such as SSID or operating class and record their
   values on the Controller and all Agents.
2. Capture the baseline topology, Client associations, reachability, and
   configuration values.
3. Change the selected parameter using the approved configuration method and
   wait for propagation to all Agents.
4. Verify the changed value on the Controller and every Agent before rebooting.
5. Start Client reachability monitoring and record the reboot start time.
6. Reboot the selected device using the approved reboot procedure. This test
   uses reboot recovery only; do not substitute a factory reset.
7. After recovery, verify the device, EasyMesh service, topology, backhaul,
   fronthaul, and Client associations in that order.
8. Query the selected configuration values again and compare them with the
   values recorded before reboot. Continue monitoring and pass only when the
   values persist, topology is restored, and Clients remain reachable.

## Test Case 11: Wi-Fi Reset at Scale

1. Select the Small, Medium, or Large profile and record the affected Agent or
   Agents. Capture topology, station lists, traffic, CPU, and memory baselines.
2. Identify the Wi-Fi interface or radio to reset using:
   ```text
   ip -br link
   iw dev
   ```
   Do not select the management interface unless the test specifically has
   console or out-of-band recovery.
3. Start reachability monitoring and normal traffic. Record the reset start
   time and the exact device and interface or radio target.
4. Trigger the approved Wi-Fi interface, radio, or service reset. If the
   selected fault is an interface reset, use the approved interface-reset
   command and restore the interface before validation.
5. Monitor the Controller topology, Agent backhaul, fronthaul interfaces,
   Client station lists, traffic, CPU, and memory during recovery.
6. Record the first time each affected Agent rejoins and each Client
   reassociates. Verify:
   ```text
   iw dev <interface> link
   iw dev <interface> station dump
   ```
7. Query the final topology and compare Agent count, Client count, MAC
   membership, parent-child relationships, traffic, CPU, and memory with the
   baseline.
8. Continue monitoring for the observation period. Pass only when all expected
   Agents and Clients recover without manual reconnection, topology corruption,
   service failure, or abnormal resource usage.
