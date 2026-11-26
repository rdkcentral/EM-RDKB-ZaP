# Test Case 1: EM_Fronthaul_SSID_Change

## Objective

Verify that a Fronthaul SSID changed through the Controller GUI is applied to the wireless interface, is advertised to Clients, and can be used for Client association.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible and `iw dev` available) |
| Client | Wi-Fi test client capable of scanning and associating to the Controller-managed BSS |
| Network Topology Type | Hybrid Topology |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Fronthaul SSID configuration.
3. Fronthaul BSS/radio interface is operational and visible via `iw dev` on the Controller.
4. Controller database access is available.
5. Client is available within Wi-Fi range of the Controller.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | Fronthaul SSID change |
| SSID Selection | Randomized valid Fronthaul SSID |
| Database Validation | Compare configured SSID with the Controller database value |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Open the Fronthaul SSID configuration page and record the current SSID. | Scan for available networks and record the advertised SSID. | The configured and advertised baseline SSIDs are recorded. |
| 2 | Select a randomized valid Fronthaul SSID through the Controller GUI and apply the configuration. | Rescan for available networks after the BSS update. | The Controller accepts the change, the randomized SSID is advertised, and the old SSID is no longer advertised. |
| 3 | Compare the randomized Fronthaul SSID with the Controller database value and verify it with `iw dev <interface> info`. | N/A | The Controller GUI value, database value, and interface SSID match. |
| 4 | N/A | Associate to the randomized Fronthaul SSID and verify with `iw dev <client-if> link`. | The Client-visible SSID matches the configured value, and the Client obtains an IP address. |
| 5 | Restore the recorded original Fronthaul SSID through the Controller GUI and apply the configuration. | N/A | The original Fronthaul SSID is restored. |

---

# Test Case 2: EM_Fronthaul_Password_Change

## Objective

Verify that a Fronthaul Wi-Fi password changed through the Controller GUI is applied and that Clients reject the old password and authenticate with the new password.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible) |
| Client | Wi-Fi test client capable of scanning and associating to the Controller-managed BSS |
| Network Topology Type | Hybrid Topology |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Fronthaul password/security configuration.
3. Fronthaul BSS is operational with a known existing password prior to the change.
4. Controller database access is available.
5. Client is available within Wi-Fi range of the Controller.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | Fronthaul password change |
| Password Selection | Randomized valid Fronthaul password |
| Database Validation | Compare configured password with the Controller database value |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Open the Fronthaul security configuration page and record the current password. | Verify association to the Fronthaul BSS using the current password. | The baseline password and Client connectivity are confirmed. |
| 2 | Select a randomized valid Fronthaul password through the Controller GUI and apply the configuration. | Disconnect and attempt association using the previous Fronthaul password. | Association using the previous Fronthaul password fails. |
| 3 | Compare the randomized Fronthaul password with the Controller database value. | N/A | The Controller GUI password matches the Controller database value. |
| 4 | Verify that the Fronthaul BSS remains operational. | Associate using the randomized Fronthaul password, verify with `iw dev <client-if> link`, and confirm IP connectivity. | The Client authenticates with the randomized Fronthaul password and restores connectivity. |
| 5 | Restore the recorded original Fronthaul password through the Controller GUI and apply the configuration. | N/A | The original Fronthaul password is restored. |

---

# Test Case 3: EM_Fronthaul_SSID_Persistence

## Objective

Verify that the Fronthaul SSID configured through the Controller GUI persists across Controller reboot and the MLD interface, and that a previously connected Client reconnects to the configured SSID.

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

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Fronthaul BSS is configured on the Controller with MLO enabled, having affiliated links mapped to a single MLD.
3. Controller GUI is accessible to configure and verify the Fronthaul SSID.
4. Console/SSH CLI access is available on the Controller to issue the reboot command.
5. A known, non-default Fronthaul SSID is configured and confirmed prior to reboot.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | Fronthaul SSID persistence |
| SSID Selection | Randomized valid Fronthaul SSID |
| Reboot Method | Controller CLI reboot |
| IEEE 1905 Validation | Recovery and configuration traffic between Controller and Agents |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Start IEEE 1905 capture on the Controller and Agent backhaul interfaces. Verify the randomized Fronthaul SSID in the Controller GUI and with `iw dev <interface> info`. | Verify association with `iw dev <client-if> link` and record IP connectivity. | IEEE 1905 capture starts, the randomized Fronthaul SSID is configured, and the Client is connected. |
| 2 | Issue the approved `reboot` command through the Controller console or CLI. | Monitor reachability during the reboot. | The Controller reboots and Client connectivity is interrupted. |
| 3 | Wait for the Controller to boot and for EasyMesh services and wireless interfaces to become available. | Scan for the configured SSID and attempt reassociation. | Controller services recover and the configured SSID is advertised. |
| 4 | Verify the SSID in the Controller GUI and with `iw dev <interface> info`. Stop the IEEE 1905 capture after recovery. | Verify `iw dev <client-if> link` and IP connectivity. | The SSID is unchanged, the Client reconnects without SSID reconfiguration, and the capture is saved. |
| 5 | Validate the saved capture for IEEE 1905 recovery/configuration traffic between the Controller and Agents. | N/A | IEEE 1905 recovery/configuration traffic is present in the capture. |
| 6 | Restore the recorded original Fronthaul SSID through the Controller GUI and apply the configuration. | N/A | The original Fronthaul SSID is restored. |

---

# Test Case 4: EM_Fronthaul_Password_Persistence

## Objective

Verify that the Fronthaul password configured through the Controller GUI persists across Controller reboot and that a Client can re-authenticate using the configured password.

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

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible to configure and verify the Fronthaul password.
3. Console/SSH CLI access is available on the Controller to issue the reboot command.
4. A known, non-default Fronthaul password is configured and confirmed prior to reboot.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | Fronthaul password persistence |
| Password Selection | Randomized valid Fronthaul password |
| Reboot Method | Controller CLI reboot |
| IEEE 1905 Validation | Recovery and configuration traffic between Controller and Agents |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Start IEEE 1905 capture on the Controller and Agent backhaul interfaces. Verify the randomized Fronthaul password in the Controller GUI. | Verify association to the Fronthaul BSS using the randomized Fronthaul password. | IEEE 1905 capture starts, and the randomized Fronthaul password and Client association are confirmed. |
| 2 | Issue the approved `reboot` command through the Controller console or CLI. | Monitor reachability during the reboot. | The Controller reboots and Client connectivity is interrupted. |
| 3 | Wait for Controller boot completion and EasyMesh services. | Attempt reassociation using the randomized Fronthaul password. | Controller services recover and the Client authenticates successfully. |
| 4 | Verify the randomized Fronthaul password in the Controller GUI. Stop the IEEE 1905 capture after recovery. | Verify `iw dev <client-if> link` and IP connectivity. | The randomized Fronthaul password remains active, the Client reconnects successfully, and the capture is saved. |
| 5 | Validate the saved capture for IEEE 1905 recovery/configuration traffic between the Controller and Agents. | N/A | IEEE 1905 recovery/configuration traffic is present in the capture. |
| 6 | Restore the recorded original Fronthaul password through the Controller GUI and apply the configuration. | N/A | The original Fronthaul password is restored. |

---

# Test Case 5: EM_2G_Radio_Channel_Change

## Objective

Verify that the 2.4 GHz radio channel can be changed through the Controller GUI and observed by the Client.

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

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows 2.4 GHz channel configuration.
3. The 2.4 GHz radio interface is operational with a known current channel.
4. Regulatory domain/Country Code permits the selected channel.
5. The randomized 2.4 GHz channel selected for the test differs from the recorded baseline channel.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | 2.4 GHz channel change |
| Channel Selection | Randomized valid 2.4 GHz channel different from baseline |
| IEEE 1905 Validation | Channel configuration traffic between Controller and Agents |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Start IEEE 1905 capture on the Controller and Agent backhaul interfaces. Record the current channel in the Controller GUI and verify it with `iw dev <interface> info`. | Verify association to the 2.4 GHz BSS and record the link information. | IEEE 1905 capture starts, and the baseline channel and Client connectivity are confirmed. |
| 2 | Select a randomized valid 2.4 GHz channel in the Controller GUI and apply the configuration. | Wait for channel transition and reassociation, if required. | The radio transitions to the selected channel. |
| 3 | Verify the selected channel with `iw dev <interface> info`. Stop the IEEE 1905 capture after reassociation. | Verify `iw dev <client-if> link` after reassociation. | The radio and Client report the selected channel, connectivity is restored, and the capture is saved. |
| 4 | Validate the saved capture for IEEE 1905 configuration traffic between the Controller and Agents. | N/A | IEEE 1905 configuration traffic is present in the capture. |
| 5 | Restore the recorded original 2.4 GHz channel through the Controller GUI and apply the configuration. | N/A | The original 2.4 GHz channel is restored. |

---

# Test Case 6: EM_5G_Radio_Channel_Change

## Objective

Verify that the 5 GHz radio channel can be changed through the Controller GUI and observed by the Client.

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

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows 5 GHz channel configuration.
3. The 5 GHz radio interface is operational with a known current channel.
4. Regulatory domain/Country Code permits the selected channel.
5. The randomized 5 GHz channel selected for the test differs from the recorded baseline channel.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | 5 GHz channel change |
| Channel Selection | Randomized valid 5 GHz channel different from baseline |
| IEEE 1905 Validation | Channel configuration traffic between Controller and Agents |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Start IEEE 1905 capture on the Controller and Agent backhaul interfaces. Record the current channel in the Controller GUI and verify it with `iw dev <interface> info`. | Verify association to the 5 GHz BSS and record the link information. | IEEE 1905 capture starts, and the baseline channel and Client connectivity are confirmed. |
| 2 | Select a randomized valid 5 GHz channel in the Controller GUI and apply the configuration. | Wait for channel transition and reassociation, if required. | The radio transitions to the selected channel. |
| 3 | Verify the selected channel with `iw dev <interface> info`. Stop the IEEE 1905 capture after reassociation. | Verify `iw dev <client-if> link` after reassociation. | The radio and Client report the selected channel, connectivity is restored, and the capture is saved. |
| 4 | Validate the saved capture for IEEE 1905 configuration traffic between the Controller and Agents. | N/A | IEEE 1905 configuration traffic is present in the capture. |
| 5 | Restore the recorded original 5 GHz channel through the Controller GUI and apply the configuration. | N/A | The original 5 GHz channel is restored. |

---

# Test Case 7: EM_6G_Radio_Channel_Change

## Objective

Verify that the 6 GHz radio channel can be changed through the Controller GUI and observed by the Client.

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

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows 6 GHz channel configuration.
3. The 6 GHz radio interface is operational with a known current channel.
4. Regulatory domain/Country Code permits the selected channel.
5. The randomized 6 GHz channel selected for the test differs from the recorded baseline channel.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | 6 GHz channel change |
| Channel Selection | Randomized valid 6 GHz channel different from baseline |
| IEEE 1905 Validation | Channel configuration traffic between Controller and Agents |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Start IEEE 1905 capture on the Controller and Agent backhaul interfaces. Record the current channel in the Controller GUI and verify it with `iw dev <interface> info`. | Verify association to the 6 GHz BSS and record the link information. | IEEE 1905 capture starts, and the baseline channel and Client connectivity are confirmed. |
| 2 | Select a randomized valid 6 GHz channel in the Controller GUI and apply the configuration. | Wait for channel transition and reassociation, if required. | The radio transitions to the selected channel. |
| 3 | Verify the selected channel with `iw dev <interface> info`. Stop the IEEE 1905 capture after reassociation. | Verify `iw dev <client-if> link` after reassociation. | The radio and Client report the selected channel, connectivity is restored, and the capture is saved. |
| 4 | Validate the saved capture for IEEE 1905 configuration traffic between the Controller and Agents. | N/A | IEEE 1905 configuration traffic is present in the capture. |
| 5 | Restore the recorded original 6 GHz channel through the Controller GUI and apply the configuration. | N/A | The original 6 GHz channel is restored. |

---

# Test Case 8: EM_Fronthaul_SSID_Broadcast_Configuration

## Objective

Verify that Fronthaul SSID broadcast can be disabled and enabled through the Controller GUI, and that Client visibility and association reflect the configured broadcast state.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI and `iw dev` available) |
| Client | Wi-Fi test client capable of scanning and associating to the Controller-managed BSS |
| Network Topology Type | Hybrid Topology |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Fronthaul SSID broadcast configuration.
3. Fronthaul BSS/radio interface is operational and visible through `iw dev`.
4. Client is available within Wi-Fi range of the Controller.
5. The Client is configured to forget the Fronthaul network before the broadcast-disabled validation.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | Fronthaul SSID broadcast |
| Initial State | Enabled |
| Updated State | Disabled, then enabled |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify that Fronthaul SSID broadcast is enabled in the Controller GUI and confirm the BSS with `iw dev <interface> info`. | Scan for available networks and record `Fronthaul_SSID`. | The Fronthaul BSS is operational and the SSID is visible to the Client. |
| 2 | Disable Fronthaul SSID broadcast through the Controller GUI and apply the configuration. | Forget the saved network, then scan for available networks. | The BSS remains operational, but `Fronthaul_SSID` is not advertised in the Client scan. |
| 3 | Re-enable Fronthaul SSID broadcast through the Controller GUI and apply the configuration. | Scan for available networks and associate to `Fronthaul_SSID`. | The SSID is advertised again, the Client associates successfully, and `iw dev <client-if> link` shows an active connection. |
| 4 | Restore the original Fronthaul SSID broadcast state through the Controller GUI. | N/A | The original Fronthaul SSID broadcast configuration is restored. |

---

# Test Case 9: EM_2G_Radio_Enable_Disable

## Objective

Verify that the 2.4 GHz radio can be disabled and re-enabled through the Controller GUI, and that Client availability follows the configured radio state.

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

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows 2.4 GHz radio enable/disable configuration.
3. The 2.4 GHz radio is operational and visible through `iw dev`.
4. The 2.4 GHz radio is hosted on an EasyMesh Agent.
5. Client is available within Wi-Fi range of the Controller.
6. Client association and connectivity are confirmed on the selected radio before the change.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | 2.4 GHz radio enable/disable |
| Radio State | Enabled, disabled, then enabled |
| IEEE 1905 Validation | Radio configuration traffic between Controller and Agent |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Start IEEE 1905 capture on the Controller and Agent backhaul interfaces. Verify that the 2.4 GHz radio is enabled in the Controller GUI and confirm its interface with `iw dev`. | Associate to the 2.4 GHz BSS and verify with `iw dev <client-if> link`. | IEEE 1905 capture starts, the 2.4 GHz radio is operational, and the Client is connected. |
| 2 | Disable the 2.4 GHz radio through the Controller GUI and apply the configuration. | Disconnect from the 2.4 GHz BSS and scan for available networks. | The 2.4 GHz BSS is unavailable for Client association. |
| 3 | Re-enable the 2.4 GHz radio through the Controller GUI and apply the configuration. | Scan for the BSS, associate again, and verify with `iw dev <client-if> link`. | The 2.4 GHz radio and BSS become operational, and Client connectivity is restored. |
| 4 | Stop the IEEE 1905 capture and validate the saved capture for radio configuration traffic between the Controller and Agent. | N/A | IEEE 1905 configuration traffic is present in the capture. |

---

# Test Case 10: EM_5G_Radio_Enable_Disable

## Objective

Verify that the 5 GHz radio can be disabled and re-enabled through the Controller GUI, and that Client availability follows the configured radio state.

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

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows 5 GHz radio enable/disable configuration.
3. The 5 GHz radio is operational and visible through `iw dev`.
4. The 5 GHz radio is hosted on an EasyMesh Agent.
5. Client is available within Wi-Fi range of the Controller.
6. Client association and connectivity are confirmed on the 5 GHz radio before the change.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | 5 GHz radio enable/disable |
| Radio State | Enabled, disabled, then enabled |
| IEEE 1905 Validation | Radio configuration traffic between Controller and Agent |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Start IEEE 1905 capture on the Controller and Agent backhaul interfaces. Verify that the 5 GHz radio is enabled in the Controller GUI and confirm its interface with `iw dev`. | Associate to the 5 GHz BSS and verify with `iw dev <client-if> link`. | IEEE 1905 capture starts, the 5 GHz radio is operational, and the Client is connected. |
| 2 | Disable the 5 GHz radio through the Controller GUI and apply the configuration. | Disconnect from the 5 GHz BSS and scan for available networks. | The 5 GHz BSS is unavailable for Client association. |
| 3 | Re-enable the 5 GHz radio through the Controller GUI and apply the configuration. | Scan for the BSS, associate again, and verify with `iw dev <client-if> link`. | The 5 GHz radio and BSS become operational, and Client connectivity is restored. |
| 4 | Stop the IEEE 1905 capture and validate the saved capture for radio configuration traffic between the Controller and Agent. | N/A | IEEE 1905 configuration traffic is present in the capture. |

---

# Test Case 11: EM_6G_Radio_Enable_Disable

## Objective

Verify that the 6 GHz radio can be disabled and re-enabled through the Controller GUI, and that Client availability follows the configured radio state.

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

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows 6 GHz radio enable/disable configuration.
3. The 6 GHz radio is operational and visible through `iw dev`.
4. The 6 GHz radio is hosted on an EasyMesh Agent.
5. Client is available within Wi-Fi range of the Controller.
6. Client association and connectivity are confirmed on the 6 GHz radio before the change.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Configuration | 6 GHz radio enable/disable |
| Radio State | Enabled, disabled, then enabled |
| IEEE 1905 Validation | Radio configuration traffic between Controller and Agent |
| Network Topology | Controller and 3 Extenders in an active EasyMesh Hybrid topology |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Start IEEE 1905 capture on the Controller and Agent backhaul interfaces. Verify that the 6 GHz radio is enabled in the Controller GUI and confirm its interface with `iw dev`. | Associate to the 6 GHz BSS and verify with `iw dev <client-if> link`. | IEEE 1905 capture starts, the 6 GHz radio is operational, and the Client is connected. |
| 2 | Disable the 6 GHz radio through the Controller GUI and apply the configuration. | Disconnect from the 6 GHz BSS and scan for available networks. | The 6 GHz BSS is unavailable for Client association. |
| 3 | Re-enable the 6 GHz radio through the Controller GUI and apply the configuration. | Scan for the BSS, associate again, and verify with `iw dev <client-if> link`. | The 6 GHz radio and BSS become operational, and Client connectivity is restored. |
| 4 | Stop the IEEE 1905 capture and validate the saved capture for radio configuration traffic between the Controller and Agent. | N/A | IEEE 1905 configuration traffic is present in the capture. |

