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
4. Client is available within Wi-Fi range of the Controller.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | `Existing_Fronthaul_SSID` |
| Fronthaul SSID (New) | `Fronthaul_SSID` |
| Verification Methods | Controller GUI, `iw dev`, and Client association |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Open the Fronthaul SSID configuration page and record the current SSID. | Scan for available networks and record the advertised SSID. | The configured and advertised baseline SSIDs are recorded. |
| 2 | Set the Fronthaul SSID to `Fronthaul_SSID` and apply the configuration. | Rescan for available networks after the BSS update. | The Controller accepts the change, the new SSID is advertised, and the old SSID is no longer advertised. |
| 3 | Verify the configured SSID with `iw dev <interface> info`. | Associate to `Fronthaul_SSID` and verify with `iw dev <client-if> link`. | The interface SSID and Client-visible SSID match, and the Client obtains an IP address. |

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
4. Client is available within Wi-Fi range of the Controller.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Fronthaul Password (Old) | `Existing_Fronthaul_Password` |
| Fronthaul Password (New) | `Fronthaul_Password` |
| Verification Method | Client association and connectivity |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Open the Fronthaul security configuration page and record the current password. | Verify association to the Fronthaul BSS using the current password. | The baseline password and Client connectivity are confirmed. |
| 2 | Set the Fronthaul password to `Fronthaul_Password` and apply the configuration. | Disconnect and attempt association using `Existing_Fronthaul_Password`. | Association using the old Fronthaul password fails. |
| 3 | Verify that the Fronthaul BSS remains operational. | Associate using `Fronthaul_Password`, verify with `iw dev <client-if> link`, and confirm IP connectivity. | The Client authenticates with the new Fronthaul password and restores connectivity. |

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
| Controller | EasyMesh Controller (GUI and CLI/console access, `iw dev` available) |
| Client | Wi-Fi test client capable of associating to the Controller-managed BSS |
| Network Topology Type | Hybrid Topology |

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
| Fronthaul SSID (Pre-Reboot) | `Fronthaul_SSID` |
| MLO Affiliated Links | 2.4GHz, 5GHz, 6GHz |
| Reboot Method | CLI reboot command (for example, `reboot` or vendor-specific CLI command) |
| Verification Method | Controller GUI, `iw dev`, and Client association |
| Network Topology | Controller managing Fronthaul BSS configuration with MLD |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify the Fronthaul SSID in the Controller GUI and with `iw dev <interface> info`. | Verify association with `iw dev <client-if> link` and record IP connectivity. | The configured Fronthaul SSID is `Fronthaul_SSID` and the Client is connected. |
| 2 | Issue the approved `reboot` command through the Controller console or CLI. | Monitor reachability during the reboot. | The Controller reboots and Client connectivity is interrupted. |
| 3 | Wait for the Controller to boot and for EasyMesh services and wireless interfaces to become available. | Scan for the configured SSID and attempt reassociation. | Controller services recover and the configured SSID is advertised. |
| 4 | Verify the SSID in the Controller GUI and with `iw dev <interface> info`. | Verify `iw dev <client-if> link` and IP connectivity. | The SSID is unchanged and the Client reconnects without SSID reconfiguration. |

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
| Controller | EasyMesh Controller (GUI and CLI/console access) |
| Client | Wi-Fi test client capable of associating to the Controller-managed BSS |
| Network Topology Type | Hybrid Topology |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible to configure and verify the Fronthaul password.
3. Console/SSH CLI access is available on the Controller to issue the reboot command.
4. A known, non-default Fronthaul SSID is configured and confirmed prior to reboot.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Fronthaul Password (Pre-Reboot) | `Fronthaul_Password` |
| Reboot Method | CLI reboot command (for example, `reboot` or vendor-specific CLI command) |
| Verification Method | Controller GUI and Client association |
| Network Topology | Controller managing Fronthaul BSS configuration |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify the configured password in the Controller GUI. | Verify association to the Fronthaul BSS using the configured password. | The configured password and Client association are confirmed. |
| 2 | Issue the approved `reboot` command through the Controller console or CLI. | Monitor reachability during the reboot. | The Controller reboots and Client connectivity is interrupted. |
| 3 | Wait for Controller boot completion and EasyMesh services. | Attempt reassociation using the configured password. | Controller services recover and the Client authenticates successfully. |
| 4 | Verify the configured password in the Controller GUI. | Verify `iw dev <client-if> link` and IP connectivity. | The configured password remains active and the Client reconnects successfully. |

---

# Test Case 5: EM_Radio_Channel_Change

## Objective

Verify that the 2.4 GHz, 5 GHz, and 6 GHz radios can be configured to valid operating channels through the Controller GUI and that connected Clients observe and use the updated channels.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI and `iw dev` available) |
| Clients | Wi-Fi test clients associated with the Controller-managed 2.4 GHz, 5 GHz, and 6 GHz BSSs |
| Network Topology Type | Hybrid Topology |

---

## Pre-Requisites

1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows radio-channel configuration.
3. 2.4 GHz, 5 GHz, and 6 GHz radio interfaces are operational with known current channels.
4. Regulatory domain/Country Code configured on the Controller permits the selected operating channels for each radio band.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Radio Bands | 2.4GHz, 5GHz, 6GHz |
| Operating Channel (Old) | Record the current channel for each radio band |
| Operating Channel (New) | Select a valid channel for each radio band |
| Verification Method | Controller GUI, `iw dev`, and Client link status |
| Network Topology | Controller managing 2.4GHz, 5GHz, and 6GHz radio configuration |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Open the radio configuration page and record the current channel for each radio band. Verify the baseline with `iw dev <interface> info`. | Verify association to the 2.4 GHz, 5 GHz, and 6 GHz BSSs and record the current link information. | The baseline channel and Client connectivity are confirmed for each radio band. |
| 2 | Set a valid channel for each radio band in the Controller GUI and apply the configuration. | Wait for each channel transition and reassociation, if required. | The Controller accepts the changes and each radio transitions to its selected channel. |
| 3 | Verify the selected channel for each radio with `iw dev <interface> info`. | Verify `iw dev <client-if> link` for each BSS after reassociation. | The radio interfaces and Clients report the selected channels, and Client connectivity is restored on all radio bands. |

---

# Test Case 6: EM_Fronthaul_SSID_Broadcast_Configuration

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
| Fronthaul SSID | `Fronthaul_SSID` |
| Initial Broadcast State | Enabled |
| Updated Broadcast State | Disabled, then enabled |
| Verification Method | Controller GUI, `iw dev`, and Client scan/association |
| Network Topology | Controller-managed Fronthaul BSS configuration |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify that Fronthaul SSID broadcast is enabled in the Controller GUI and confirm the BSS with `iw dev <interface> info`. | Scan for available networks and record `Fronthaul_SSID`. | The Fronthaul BSS is operational and the SSID is visible to the Client. |
| 2 | Disable Fronthaul SSID broadcast through the Controller GUI and apply the configuration. | Forget the saved network, then scan for available networks. | The BSS remains operational, but `Fronthaul_SSID` is not advertised in the Client scan. |
| 3 | Re-enable Fronthaul SSID broadcast through the Controller GUI and apply the configuration. | Scan for available networks and associate to `Fronthaul_SSID`. | The SSID is advertised again, the Client associates successfully, and `iw dev <client-if> link` shows an active connection. |

---

# Test Case 7: EM_Radio_Enable_Disable

## Objective

Verify that a 2.4 GHz, 5 GHz, or 6 GHz radio can be disabled and re-enabled through the Controller GUI, and that Client availability follows the configured radio state.

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
2. Controller GUI is accessible and allows radio enable/disable configuration.
3. The selected 2.4 GHz, 5 GHz, or 6 GHz radio is operational and visible through `iw dev`.
4. Client is available within Wi-Fi range of the Controller.
5. Client association and connectivity are confirmed on the selected radio before the change.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4 GHz, 5 GHz, or 6 GHz |
| Initial Radio State | Enabled |
| Updated Radio State | Disabled, then enabled |
| Verification Method | Controller GUI, `iw dev`, and Client scan/association |
| Network Topology | Controller-managed multi-band radio configuration |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|------------|--------|-----------------|
| 1 | Verify that the selected radio is enabled in the Controller GUI and confirm its interface with `iw dev`. | Associate to the selected radio BSS and verify with `iw dev <client-if> link`. | The selected radio is operational and the Client is connected. |
| 2 | Disable the selected radio through the Controller GUI and apply the configuration. | Disconnect from the selected BSS and scan for available networks. | The selected radio is no longer available for Client association, while other enabled radio bands remain operational. |
| 3 | Re-enable the selected radio through the Controller GUI and apply the configuration. | Scan for the BSS, associate again, and verify with `iw dev <client-if> link`. | The radio interface becomes operational, the BSS is available, and Client connectivity is restored. |

