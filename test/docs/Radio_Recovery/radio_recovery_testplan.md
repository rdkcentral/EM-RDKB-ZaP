# Test Case 1: EasyMesh_Fronthaul_Disable_Enable

## Objective

Verify that disabling the fronthaul from the Controller removes all fronthaul BSSs across the Controller and EM Agents (making them unavailable to clients), that re-enabling the fronthaul restores the BSSs and reassociates clients, and that backhaul connectivity and internet reachability are retained throughout.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | 3 EasyMesh Agent |
| Wi-Fi Client | At least Each client per EM devices, make sure that there should be 2.4ghz and 5ghz clients |
| Network Topology | Hybrid topology with 1 Controller and 3 Extenders |

---

## Pre-Requisites

1. Controller and Extenders are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. RDKBCLI is available and accessible

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| BSS Verification | `iw dev`; client side `sudo nmcli device wifi rescan` + `nmcli device wifi list` |
| Client Association Verification | `iw dev <multi link interface> station dump` |
| Backhaul Verification | `iw dev <backhaul interface> link` or `Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType` |
| Connectivity Verification | ping |

---

## Test Procedure and Expected Results

| Step Number | Controller | EM Agent (all) | Clients (all) | Expected Result |
|-------------|------------|----------------|---------------|-----------------|
| 1 | Disable fronthaul from `rdkbcli`. | N/A | N/A | Fronthaul is disabled from the Controller. |
| 2 | Verify that no fronthaul BSS is listed: `iw dev`. | Verify that no fronthaul BSS is listed: `iw dev`. | Verify that no fronthaul BSS is listed: `sudo nmcli device wifi rescan` + `nmcli device wifi list`. | No fronthaul BSS available. |
| 3 | N/A | Verify backhaul status: `iw dev <backhaul interface> link` or `Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`. | N/A | Backhaul remains connected. |
| 4 | N/A | Verify internet connectivity using ping. | N/A | Internet connectivity is retained over the backhaul. |
| 5 | Enable the fronthaul from `rdkbcli`. | N/A | N/A | Fronthaul is enabled from the Controller. |
| 6 | Verify that fronthaul BSS is listed: `iw dev`. | Verify that fronthaul BSS is listed: `iw dev`. | N/A | Fronthaul BSS is available again on Controller and Agents. |
| 7 | Verify that clients are reassociated using `iw dev <multi link interface> station dump`. | Verify that clients are reassociated using `iw dev <multi link interface> station dump`. | N/A | Clients are reassociated to the fronthaul BSS. |
| 8 | N/A | Verify backhaul status: `iw dev <backhaul interface> link` or `Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`. | N/A | Backhaul remains connected. |
| 9 | N/A | Verify internet connectivity using ping. | N/A | Internet connectivity is retained. |

---

# Test Case 2: EasyMesh_Radio_Disable_Enable

## Objective

Verify that disabling a specific radio (2.4GHz, then repeated for 5GHz) from the Controller removes only that radio's BSS and disconnects only its associated clients while clients on other radios remain connected, that re-enabling the radio restores the BSS and reconnects the affected clients after the reconnection delay, and that backhaul connectivity and internet reachability are retained throughout.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | 3 EasyMesh Agent |
| Wi-Fi Client | At least Each client per EM devices, make sure that there should be 2.4ghz and 5ghz clients |
| Network Topology | Hybrid topology with 1 Controller and 3 Extenders |

---

## Pre-Requisites

1. Controller and Extenders are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. RDKBCLI is available and accessible

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Radios Exercised | 2.4GHz, then repeat for 5GHz |
| BSS Verification | `iw dev` |
| Client Association Verification | `iw dev <multi link interface> station dump` |
| Backhaul Verification | `iw dev <backhaul interface> link` or `Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType` |
| Connectivity Verification | ping 8.8.8.8 |

---

## Test Procedure and Expected Results

| Step Number | Controller | EM Agent (all) | Clients (all) | Expected Result |
|-------------|------------|----------------|---------------|-----------------|
| 1 | Disable 2.4GHz radio using `rdkbcli`. | N/A | N/A | 2.4GHz radio is disabled from the Controller. |
| 2 | Verify that no BSS is available for the 2.4GHz radio: `iw dev`. | N/A | N/A | No BSS available for the 2.4GHz radio. |
| 3 | Verify that clients using the 2.4GHz radio were disconnected and others remain connected: `iw dev <multi link interface> station dump`. | N/A | N/A | Only 2.4GHz clients are disconnected; 5GHz and 6GHz clients remain connected. |
| 4 | N/A | Verify backhaul status: `iw dev <backhaul interface> link` or `Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`. | N/A | Backhaul remains connected. |
| 5 | N/A | Verify internet connectivity using ping. | N/A | Internet connectivity is retained. |
| 6 | N/A | Verify that no BSS is available for the 2.4GHz radio: `iw dev`. | N/A | No BSS available for the 2.4GHz radio on the Agents. |
| 7 | N/A | Verify that clients using the 2.4GHz radio were disconnected and others remain connected: `iw dev <multi link interface> station dump`. | N/A | Only 2.4GHz clients are disconnected; 5GHz and 6GHz clients remain connected. |
| 8 | N/A | N/A | Verify that clients connected to 5GHz and 6GHz BSS are able to ping google. | 5GHz and 6GHz clients retain internet connectivity. |
| 9 | Enable 2.4GHz radio using `rdkbcli`. | N/A | N/A | 2.4GHz radio is enabled from the Controller. |
| 10 | Verify that link is available for the 2.4GHz radio: `iw dev`. | N/A | N/A | BSS/link available for the 2.4GHz radio. |
| 11 | Wait for client reconnect delay. | N/A | N/A | Reconnection delay elapses. |
| 12 | Verify that clients using the 2.4GHz radio were reconnected and others remain connected: `iw dev <multi link interface> station dump`. | N/A | N/A | 2.4GHz clients are reconnected and other clients remain connected. |
| 13 | N/A | Verify backhaul status: `iw dev <backhaul interface> link` or `Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType`. | N/A | Backhaul remains connected. |
| 14 | N/A | Verify internet connectivity using ping. | N/A | Internet connectivity is retained. |
| 15 | N/A | Verify that link is available for the 2.4GHz radio: `iw dev`. | N/A | BSS/link available for the 2.4GHz radio on the Agents. |
| 16 | N/A | Verify that clients using the 2.4GHz radio were reconnected and others remain connected: `iw dev <multi link interface> station dump`. | N/A | 2.4GHz clients are reconnected and other clients remain connected. |
| 17 | N/A | N/A | Verify that clients connected to 2.4GHz, 5GHz and 6GHz BSS are able to ping google. | All clients retain internet connectivity. |
| 18 | Repeat all the steps with 5GHz. | Repeat all the steps with 5GHz. | Repeat all the steps with 5GHz. | 5GHz radio disable/enable behaves the same, with only 5GHz clients affected. |

---

# Test Case 3: EasyMesh_Operating_Class_Channel_Change

## Objective

Verify that setting a radio's operating class and channel from the Controller is correctly applied and reflected on the Controller, EM Agents and clients, and that the configured operating class and channel persist across a radio disable/enable cycle.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | 3 EasyMesh Agent |
| Wi-Fi Client | At least Each client per EM devices, make sure that there should be 2.4ghz and 5ghz clients |
| Network Topology | Hybrid topology with 1 Controller and 3 Extenders |

---

## Pre-Requisites

1. Controller and Extenders are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. RDKBCLI is available and accessible

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Example Setting | 2.4GHz radio, operating class 81, channel 6 |
| Channel/Operating Class Verification | `iw dev` (operating class derived from channel, width, band) |
| Client-side Verification | `sudo nmcli device wifi rescan` + `nmcli device wifi list` |
| Radio Toggle | Disable/Enable radio using `rdkbcli` |

---

## Test Procedure and Expected Results

| Step Number | Controller | EM Agent (all) | Clients (all) | Expected Result |
|-------------|------------|----------------|---------------|-----------------|
| 1 | Set operating class and channel for a radio using `rdkbcli` (example: 2.4GHz radio, operating class 81, channel 6). | N/A | N/A | Operating class and channel are set on the Controller. |
| 2 | Verify the channel and operating class using `iw dev` (operating class can be checked based on channel, width, band). | Verify the channel and operating class using `iw dev` (operating class can be checked based on channel, width, band). | N/A | Configured channel and operating class are reflected on Controller and Agents. |
| 3 | N/A | N/A | Verify the channel using `sudo nmcli device wifi rescan` + `nmcli device wifi list`. | Configured channel is observed by clients. |
| 4 | Disable 2.4GHz radio using `rdkbcli`. | N/A | N/A | 2.4GHz radio is disabled from the Controller. |
| 5 | Verify that no BSS is available for the 2.4GHz radio: `iw dev`. | N/A | N/A | No BSS available for the 2.4GHz radio. |
| 6 | Enable 2.4GHz radio. | N/A | N/A | 2.4GHz radio is enabled from the Controller. |
| 7 | Verify that BSS is available for the 2.4GHz radio: `iw dev`. | N/A | N/A | BSS available for the 2.4GHz radio. |
| 8 | Verify the channel and operating class using `iw dev` (operating class can be checked based on channel, width, band). | Verify the channel and operating class using `iw dev` (operating class can be checked based on channel, width, band). | N/A | Configured channel and operating class persist after the radio toggle on Controller and Agents. |
| 9 | N/A | N/A | Verify the channel using `sudo nmcli device wifi rescan` + `nmcli device wifi list`. | Configured channel persists and is observed by clients. |
| 10 | Repeat all the steps with 5GHz, operating class = 115 and channel = 36 | Repeat all the steps with 5GHz, operating class = 115 and channel = 36 | Repeat all the steps with 5GHz, operating class = 115 and channel = 36 | Operating class and channel are applied and persist after the radio toggle for 5GHz. |

---
