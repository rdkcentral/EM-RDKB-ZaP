# Test Case 1: EM_FronthaulSSID_ControllerVerification
## Objective
Verify that when the Fronthaul SSID is changed via the Controller GUI, the updated SSID is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.

---

## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible, rbuscli and iw dev available) |

---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Fronthaul SSID configuration.
3. DataElements object is accessible through rbuscli on the Controller.
4. Fronthaul BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | Private_ssid |
| Fronthaul SSID (New) | EasyMesh_mld_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Login to Controller GUI and navigate to Wi-Fi / Fronthaul SSID configuration page. | GUI page loads successfully showing current Fronthaul SSID "Private_ssid". |
| 2 | Change Fronthaul SSID field to "EasyMesh_mld_ssid" and click Apply/Save. | SSID change is accepted and applied successfully via GUI, with a success confirmation message shown. |
| 3 | Verify updated SSID using `rbuscli get Device.WiFi.DataElements.Network.SSID.{i}.SSID` | rbuscli returns the updated SSID "EasyMesh_mld_ssid" for the corresponding Fronthaul BSS instance. |
| 4 | Verify updated SSID at interface level using `iw dev <interface> info` | `iw dev` output shows the Fronthaul interface (e.g., mld0) broadcasting SSID "EasyMesh_mld_ssid". |

---


# Test Case 2: EM_FronthaulSSID_ClientVerification
## Objective
Verify that after the Fronthaul SSID is changed on the Controller to "EasyMesh_mld_ssid", a Wi-Fi Client (STA) can discover the updated SSID over the air and successfully connect to it.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 1 ("EM_FronthaulSSID_ControllerVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | Private_ssid |
| Fronthaul SSID (New) | EasyMesh_mld_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan (e.g., `iw dev <client-if> scan | grep SSID`) after the SSID change is applied on the Controller. | Scan results show the updated SSID "EasyMesh_mld_ssid" being advertised, and the old SSID "Private_ssid" is no longer visible. |
| 2 | Connect the Client to the updated SSID "EasyMesh_mld_ssid" using the known passphrase, and check association using `iw dev <client-if> link`. | Client successfully authenticates and associates to SSID "EasyMesh_mld_ssid", and obtains a valid IP address via DHCP, confirming the SSID change is usable end-to-end. |
---

# Test Case 3: EM_FronthaulSSID_ControllerVerification_in_2G_interface
## Objective
Verify that when the Fronthaul SSID is changed via the Controller GUI, the updated SSID is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible, rbuscli and iw dev available) |

---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Fronthaul SSID configuration.
3. DataElements object is accessible through rbuscli on the Controller.
4. Fronthaul BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | Private_ssid |
| Fronthaul SSID (New) | EasyMesh_2g_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Login to Controller GUI and navigate to Wi-Fi / Fronthaul SSID configuration page. | GUI page loads successfully showing current Fronthaul SSID "Private_ssid". |
| 2 | Change Fronthaul SSID field to "EasyMesh_2g_ssid" and click Apply/Save. | SSID change is accepted and applied successfully via GUI, with a success confirmation message shown. |
| 3 | Verify updated SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns the updated SSID "EasyMesh_2g_ssid" for the corresponding Fronthaul BSS instance. |
| 4 | Verify updated SSID at interface level using `iw dev <interface> info` | `iw dev` output shows the Fronthaul interface broadcasting SSID "EasyMesh_2g_ssid". |

---


# Test Case 4: EM_FronthaulSSID_ClientVerification_in_2G_interface
## Objective
Verify that after the Fronthaul SSID is changed on the Controller to "EasyMesh_2g_ssid", a Wi-Fi Client (STA) can discover the updated SSID over the air and successfully connect to it.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 2 ("EM_FronthaulSSID_ControllerVerification_in_2G_interface") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | Private_ssid |
| Fronthaul SSID (New) | EasyMesh_2g_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan (e.g., `iw dev <client-if> scan | grep SSID`) after the SSID change is applied on the Controller. | Scan results show the updated SSID "EasyMesh_2g_ssid" being advertised, and the old SSID "Private_ssid" is no longer visible. |
| 2 | Connect the Client to the updated SSID "EasyMesh_2g_ssid" using the known passphrase, and check association using `iw dev <client-if> link`. | Client successfully authenticates and associates to SSID "EasyMesh_2g_ssid", and obtains a valid IP address via DHCP, confirming the SSID change is usable end-to-end. |
---

# Test Case 5: EM_FronthaulSSID_ControllerVerification_in_5G_interface
## Objective
Verify that when the Fronthaul SSID is changed via the Controller GUI, the updated SSID is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible, rbuscli and iw dev available) |

---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Fronthaul SSID configuration.
3. DataElements object is accessible through rbuscli on the Controller.
4. Fronthaul BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | Private_ssid |
| Fronthaul SSID (New) | EasyMesh_5g_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Login to Controller GUI and navigate to Wi-Fi / Fronthaul SSID configuration page. | GUI page loads successfully showing current Fronthaul SSID "Private_ssid". |
| 2 | Change Fronthaul SSID field to "EasyMesh_5g_ssid" and click Apply/Save. | SSID change is accepted and applied successfully via GUI, with a success confirmation message shown. |
| 3 | Verify updated SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns the updated SSID "EasyMesh_5g_ssid" for the corresponding Fronthaul BSS instance. |
| 4 | Verify updated SSID at interface level using `iw dev <interface> info` | `iw dev` output shows the Fronthaul interface broadcasting SSID "EasyMesh_5g_ssid". |

---


# Test Case 6: EM_FronthaulSSID_ClientVerification_in_5G_interface
## Objective
Verify that after the Fronthaul SSID is changed on the Controller to "EasyMesh_5g_ssid", a Wi-Fi Client (STA) can discover the updated SSID over the air and successfully connect to it.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 3 ("EM_FronthaulSSID_ControllerVerification_in_5G_interface") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | Private_ssid |
| Fronthaul SSID (New) | EasyMesh_5g_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan (e.g., `iw dev <client-if> scan | grep SSID`) after the SSID change is applied on the Controller. | Scan results show the updated SSID "EasyMesh_5g_ssid" being advertised, and the old SSID "Private_ssid" is no longer visible. |
| 2 | Connect the Client to the updated SSID "EasyMesh_5g_ssid" using the known passphrase, and check association using `iw dev <client-if> link`. | Client successfully authenticates and associates to SSID "EasyMesh_5g_ssid", and obtains a valid IP address via DHCP, confirming the SSID change is usable end-to-end. |
---

# Test Case 7: EM_FronthaulSSID_ControllerVerification_in_6G_interface
## Objective
Verify that when the Fronthaul SSID is changed via the Controller GUI, the updated SSID is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible, rbuscli and iw dev available) |

---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Fronthaul SSID configuration.
3. DataElements object is accessible through rbuscli on the Controller.
4. Fronthaul BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | Private_ssid |
| Fronthaul SSID (New) | EasyMesh_6g_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Login to Controller GUI and navigate to Wi-Fi / Fronthaul SSID configuration page. | GUI page loads successfully showing current Fronthaul SSID "Private_ssid". |
| 2 | Change Fronthaul SSID field to "EasyMesh_6g_ssid" and click Apply/Save. | SSID change is accepted and applied successfully via GUI, with a success confirmation message shown. |
| 3 | Verify updated SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns the updated SSID "EasyMesh_6g_ssid" for the corresponding Fronthaul BSS instance. |
| 4 | Verify updated SSID at interface level using `iw dev <interface> info` | `iw dev` output shows the Fronthaul interface broadcasting SSID "EasyMesh_6g_ssid". |

---


# Test Case 8: EM_FronthaulSSID_ClientVerification_in_6G_interface
## Objective
Verify that after the Fronthaul SSID is changed on the Controller to "EasyMesh_6g_ssid", a Wi-Fi Client (STA) can discover the updated SSID over the air and successfully connect to it.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 4 ("EM_FronthaulSSID_ControllerVerification_in_6G_interface") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Old) | Private_ssid |
| Fronthaul SSID (New) | EasyMesh_6g_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan (e.g., `iw dev <client-if> scan | grep SSID`) after the SSID change is applied on the Controller. | Scan results show the updated SSID "EasyMesh_6g_ssid" being advertised, and the old SSID "Private_ssid" is no longer visible. |
| 2 | Connect the Client to the updated SSID "EasyMesh_6g_ssid" using the known passphrase, and check association using `iw dev <client-if> link`. | Client successfully authenticates and associates to SSID "EasyMesh_6g_ssid", and obtains a valid IP address via DHCP, confirming the SSID change is usable end-to-end. |
---

# Test Case 9: EM_FronthaulPassword_Change_GUI_ControllerVerification
## Objective
Verify that when the Fronthaul Wi-Fi password (network key/passphrase) is changed via the Controller GUI, the updated password is correctly reflected in the Controller's DataElements data model (via rbuscli).
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible, rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Fronthaul password/security configuration.
3. DataElements object is accessible through rbuscli on the Controller.
4. Fronthaul BSS is operational with a known existing password prior to the change.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul Password (Old) | OldPass@123 |
| Fronthaul Password (New) | NewPass@456 |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Login to Controller GUI and navigate to Wi-Fi / Fronthaul Security configuration page. | GUI page loads successfully showing current Fronthaul SSID and password field (masked). |
| 2 | Change Fronthaul password field to "NewPass@456" and click Apply/Save. | Password change is accepted and applied successfully via GUI, with a success confirmation message shown. |
| 3 | Verify updated password using `rbuscli get Device.WiFi.DataElements.Network.PassPhrase` | rbuscli returns the updated password value "NewPass@456" for the corresponding Fronthaul BSS instance. |

---


# Test Case 10: EM_FronthaulPassword_Change_GUI_ClientVerification
## Objective
Verify that after the Fronthaul password is changed on the Controller to "NewPass@456", a Wi-Fi Client (STA) is rejected using the old password and can successfully authenticate and connect using the new password.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 5 ("EM_FronthaulPassword_Change_GUI_ControllerVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul Password (Old) | OldPass@123 |
| Fronthaul Password (New) | NewPass@456 |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller GUI managing Fronthaul BSS configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Attempt to connect the Client to the Fronthaul SSID using the old password "OldPass@123". | Client authentication fails / association is rejected, confirming the old password is no longer valid. |
| 2 | Connect the Client to the Fronthaul SSID using the updated password "NewPass@456" and check association using `iw dev <client-if> link`. | Client successfully authenticates and associates using the new password "NewPass@456", and obtains a valid IP address via DHCP. |
---

# Test Case 11: EM_FronthaulSSID_Persistence_Reboot_MLDVerification
## Objective
Verify that after giving a reboot via CLI, the previously configured Fronthaul SSID persists across reboot and is correctly reflected in the Controller's DataElements data model, including on the corresponding MLD (Multi-Link Device) interface, via rbuscli.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (CLI/console access, rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Fronthaul BSS is configured on the Controller with MLO enabled, having affiliated links mapped to a single MLD.
3. DataElements object is accessible through rbuscli on the Controller.
4. Console/SSH CLI access is available on the Controller to issue the reboot command.
5. A known, non-default Fronthaul SSID is configured and confirmed prior to reboot.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Pre-Reboot) | EasyMesh_mld_ssid |
| MLO Affiliated Links | 2.4GHz, 5GHz, 6GHz |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration with MLD |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify MLD interface SSID using `rbuscli get Device.WiFi.DataElements.Network.SSID.{i}.SSID` | rbuscli returns "EasyMesh_mld_ssid" on the MLD interface, confirming pre-reboot baseline state. |
| 2 | Issue reboot via CLI (e.g., `reboot` command over SSH/console). | Reboot command is accepted, and Controller begins reboot sequence. |
| 3 | Wait for Controller to complete boot-up and for EasyMesh/IEEE 1905 services and rbuscli to become available again. | Controller comes back online successfully, with all EasyMesh services and rbus operational. |
| 4 | Verify MLD interface SSID persistence using `rbuscli get Device.WiFi.DataElements.Network.SSID.{i}.SSID` | rbuscli returns "EasyMesh_mld_ssid" on the MLD interface post-reboot, confirming no discrepancy between BSS-level and MLD-level SSID after reboot. |
| 5 | Cross-check pre-reboot and post-reboot MLD SSID values. | Values match exactly, confirming SSID configuration was retained in persistent storage and correctly restored to the MLD interface after reboot with no reset to default. |
---


# Test Case 12: EM_FronthaulSSID_Persistence_Reboot_MLDClientVerification
## Objective
Verify that after a Controller reboot, a previously connected Wi-Fi Client (STA) can re-associate to the persisted Fronthaul SSID "EasyMesh_mld_ssid" and regain connectivity without any manual reconfiguration of the SSID.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 6 ("EM_FronthaulSSID_Persistence_Reboot_MLDVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Pre-Reboot) | EasyMesh_mld_ssid |
| MLO Affiliated Links | 2.4GHz, 5GHz, 6GHz |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration with MLD |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Before the Controller reboot, confirm the Client is associated to the Fronthaul SSID using `iw dev <client-if> link`. | Client shows an active association to SSID "EasyMesh_mld_ssid" prior to reboot, establishing the pre-reboot baseline. |
| 2 | After the Controller completes its reboot sequence, verify the Client reconnects (automatically or manually) to the same SSID and check `iw dev <client-if> link`. | Client re-associates successfully to the persisted SSID "EasyMesh_mld_ssid" and regains IP connectivity, confirming the reboot did not disrupt client-facing service or reset the SSID to default. |
---

# Test Case 13: EM_FronthaulSSID_Persistence_Reboot_2G_Verification
## Objective
Verify that after giving a reboot via CLI, the previously configured Fronthaul SSID persists across reboot and is correctly reflected in the Controller's DataElements data model, including on the corresponding 2G interface, via rbuscli.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (CLI/console access, rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. Console/SSH CLI access is available on the Controller to issue the reboot command.
4. A known, non-default Fronthaul SSID is configured and confirmed prior to reboot.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Pre-Reboot) | EasyMesh_2G_ssid |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration with 2G |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify 2G interface SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns "EasyMesh_2G_ssid" on the 2G interface, confirming pre-reboot baseline state. |
| 2 | Issue reboot via CLI (e.g., `reboot` command over SSH/console). | Reboot command is accepted, and Controller begins reboot sequence. |
| 3 | Wait for Controller to complete boot-up and for EasyMesh/IEEE 1905 services and rbuscli to become available again. | Controller comes back online successfully, with all EasyMesh services and rbus operational. |
| 4 | Verify 2G interface SSID persistence using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns "EasyMesh_2G_ssid" on the 2G interface post-reboot, confirming no discrepancy between BSS-level and 2G-level SSID after reboot. |
| 5 | Cross-check pre-reboot and post-reboot 2G SSID values. | Values match exactly, confirming SSID configuration was retained in persistent storage and correctly restored to the 2G interface after reboot with no reset to default. |
---


# Test Case 14: EM_FronthaulSSID_Persistence_Reboot_2G_ClientVerification
## Objective
Verify that after a Controller reboot, a previously connected Wi-Fi Client (STA) can re-associate to the persisted Fronthaul SSID "EasyMesh_2G_ssid" and regain connectivity without any manual reconfiguration of the SSID.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 7 ("EM_FronthaulSSID_Persistence_Reboot_2G_Verification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Pre-Reboot) | EasyMesh_2G_ssid |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration with 2G |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Before the Controller reboot, confirm the Client is associated to the Fronthaul SSID using `iw dev <client-if> link`. | Client shows an active association to SSID "EasyMesh_2G_ssid" prior to reboot, establishing the pre-reboot baseline. |
| 2 | After the Controller completes its reboot sequence, verify the Client reconnects (automatically or manually) to the same SSID and check `iw dev <client-if> link`. | Client re-associates successfully to the persisted SSID "EasyMesh_2G_ssid" and regains IP connectivity, confirming the reboot did not disrupt client-facing service or reset the SSID to default. |
---

# Test Case 15: EM_FronthaulSSID_Persistence_Reboot_5G_Verification
## Objective
Verify that after giving a reboot via CLI, the previously configured Fronthaul SSID persists across reboot and is correctly reflected in the Controller's DataElements data model, including on the corresponding 5G interface, via rbuscli.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (CLI/console access, rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. Console/SSH CLI access is available on the Controller to issue the reboot command.
4. A known, non-default Fronthaul SSID is configured and confirmed prior to reboot.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Pre-Reboot) | EasyMesh_5G_ssid |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration with 5G |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify 5G interface SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns "EasyMesh_5G_ssid" on the 5G interface, confirming pre-reboot baseline state. |
| 2 | Issue reboot via CLI (e.g., `reboot` command over SSH/console). | Reboot command is accepted, and Controller begins reboot sequence. |
| 3 | Wait for Controller to complete boot-up and for EasyMesh/IEEE 1905 services and rbuscli to become available again. | Controller comes back online successfully, with all EasyMesh services and rbus operational. |
| 4 | Verify 5G interface SSID persistence using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns "EasyMesh_5G_ssid" on the 5G interface post-reboot, confirming no discrepancy between BSS-level and 5G-level SSID after reboot. |
| 5 | Cross-check pre-reboot and post-reboot 5G SSID values. | Values match exactly, confirming SSID configuration was retained in persistent storage and correctly restored to the 5G interface after reboot with no reset to default. |
---


# Test Case 16: EM_FronthaulSSID_Persistence_Reboot_5G_ClientVerification
## Objective
Verify that after a Controller reboot, a previously connected Wi-Fi Client (STA) can re-associate to the persisted Fronthaul SSID "EasyMesh_5G_ssid" and regain connectivity without any manual reconfiguration of the SSID.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 8 ("EM_FronthaulSSID_Persistence_Reboot_5G_Verification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Pre-Reboot) | EasyMesh_5G_ssid |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration with 5G |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Before the Controller reboot, confirm the Client is associated to the Fronthaul SSID using `iw dev <client-if> link`. | Client shows an active association to SSID "EasyMesh_5G_ssid" prior to reboot, establishing the pre-reboot baseline. |
| 2 | After the Controller completes its reboot sequence, verify the Client reconnects (automatically or manually) to the same SSID and check `iw dev <client-if> link`. | Client re-associates successfully to the persisted SSID "EasyMesh_5G_ssid" and regains IP connectivity, confirming the reboot did not disrupt client-facing service or reset the SSID to default. |
---

# Test Case 17: EM_FronthaulSSID_Persistence_Reboot_6G_Verification
## Objective
Verify that after giving a reboot via CLI, the previously configured Fronthaul SSID persists across reboot and is correctly reflected in the Controller's DataElements data model, including on the corresponding 6G interface, via rbuscli.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (CLI/console access, rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. Console/SSH CLI access is available on the Controller to issue the reboot command.
4. A known, non-default Fronthaul SSID is configured and confirmed prior to reboot.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Pre-Reboot) | EasyMesh_6G_ssid |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration with 6G |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify 6G interface SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns "EasyMesh_6G_ssid" on the 6G interface, confirming pre-reboot baseline state. |
| 2 | Issue reboot via CLI (e.g., `reboot` command over SSH/console). | Reboot command is accepted, and Controller begins reboot sequence. |
| 3 | Wait for Controller to complete boot-up and for EasyMesh/IEEE 1905 services and rbuscli to become available again. | Controller comes back online successfully, with all EasyMesh services and rbus operational. |
| 4 | Verify 6G interface SSID persistence using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.SSID` | rbuscli returns "EasyMesh_6G_ssid" on the 6G interface post-reboot, confirming no discrepancy between BSS-level and 6G-level SSID after reboot. |
| 5 | Cross-check pre-reboot and post-reboot 6G SSID values. | Values match exactly, confirming SSID configuration was retained in persistent storage and correctly restored to the 6G interface after reboot with no reset to default. |
---


# Test Case 18: EM_FronthaulSSID_Persistence_Reboot_6G_ClientVerification
## Objective
Verify that after a Controller reboot, a previously connected Wi-Fi Client (STA) can re-associate to the persisted Fronthaul SSID "EasyMesh_6G_ssid" and regain connectivity without any manual reconfiguration of the SSID.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 9 ("EM_FronthaulSSID_Persistence_Reboot_6G_Verification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul SSID (Pre-Reboot) | EasyMesh_6G_ssid |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration with 6G |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Before the Controller reboot, confirm the Client is associated to the Fronthaul SSID using `iw dev <client-if> link`. | Client shows an active association to SSID "EasyMesh_6G_ssid" prior to reboot, establishing the pre-reboot baseline. |
| 2 | After the Controller completes its reboot sequence, verify the Client reconnects (automatically or manually) to the same SSID and check `iw dev <client-if> link`. | Client re-associates successfully to the persisted SSID "EasyMesh_6G_ssid" and regains IP connectivity, confirming the reboot did not disrupt client-facing service or reset the SSID to default. |
---

# Test Case 19: EM_Password_Persistence_Reboot_Verification
## Objective
Verify that after giving a reboot via CLI, the previously configured Fronthaul Password persists across reboot and is correctly reflected in the Controller's DataElements data model, including on the corresponding fronthaul interface, via rbuscli.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (CLI/console access, rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. Console/SSH CLI access is available on the Controller to issue the reboot command.
4. A known, non-default Fronthaul SSID is configured and confirmed prior to reboot.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul Password (Pre-Reboot) | EasyMesh_test_fronthaul |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify fronthaul interface Password using `rbuscli get Device.WiFi.DataElements.Network.PassPhrase` | rbuscli returns "EasyMesh_test_fronthaul" on the fronthaul interface, confirming pre-reboot baseline state. |
| 2 | Issue reboot via CLI (e.g., `reboot` command over SSH/console). | Reboot command is accepted, and Controller begins reboot sequence. |
| 3 | Wait for Controller to complete boot-up and for EasyMesh/IEEE 1905 services and rbuscli to become available again. | Controller comes back online successfully, with all EasyMesh services and rbus operational. |
| 4 | Verify fronthaul interface Password persistence using `rbuscli get Device.WiFi.DataElements.Network.PassPhrase` | rbuscli returns "EasyMesh_test_fronthaul" on the fronthaul interface post-reboot, confirming no discrepancy between BSS-level and fronthaul-level SSID after reboot. |
| 5 | Cross-check pre-reboot and post-reboot fronthaul password values. | Values match exactly, confirming SSID configuration was retained in persistent storage and correctly restored to the fronthaul interface after reboot with no reset to default. |
---


# Test Case 20: EM_Password_Persistence_Reboot_ClientVerification
## Objective
Verify that after a Controller reboot, a Wi-Fi Client (STA) can re-authenticate and reconnect to the Fronthaul BSS using the same, persisted password, confirming the password was retained across reboot.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 10 ("EM_Password_Persistence_Reboot_Verification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Fronthaul Password (Pre-Reboot) | EasyMesh_test_fronthaul |
| Reboot Method | CLI reboot command (e.g., `reboot` or vendor-specific CLI command) |
| Verification Method | rbuscli DataElements get (post-reboot) |
| Network Topology | Controller managing Fronthaul BSS configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Before the Controller reboot, confirm the Client is associated to the Fronthaul BSS using the configured password, via `iw dev <client-if> link`. | Client shows an active, authenticated association prior to reboot, establishing the pre-reboot baseline. |
| 2 | After the Controller completes its reboot sequence, attempt to reconnect the Client using the same previously configured password. | Client successfully re-authenticates and re-associates using the persisted password, and regains IP connectivity, confirming the password was retained across reboot. |
---

# Test Case 21: EM_CountryCode_Set_Verify_RBUSCLI
## Objective
Verify that the Regulatory Domain / Country Code can be successfully configured on the Controller via rbuscli, and that the updated value is correctly reflected in the DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. Radio interface(s) are operational prior to Country Code configuration.
4. Current/default Country Code value is known prior to the change.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Country Code (Old/Default) | US |
| Country Code (New) | IN |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current Country Code using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.CountryCode` | rbuscli returns the current/default value "US", confirming baseline state prior to change. |
| 2 | Configure Country Code using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.CountryCode "IN"` | Country Code configuration request is accepted and applied successfully. |
| 3 | Verify updated Country Code using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.CountryCode` | rbuscli returns the updated value "IN", confirming the Country Code change was applied. |
---


# Test Case 22: EM_CountryCode_Set_Verify_ClientVerification
## Objective
Verify that after the Regulatory Domain / Country Code is changed on the Controller to "IN", a Wi-Fi Client (STA) observes a channel/regulatory environment consistent with the newly configured Country Code.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 11 ("EM_CountryCode_Set_Verify_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Country Code (Old/Default) | US |
| Country Code (New) | IN |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan and inspect the set of channels/regulatory information advertised (e.g., `iw dev <client-if> scan`, or `iw reg get` on a client-side radio, where supported). | Channels and regulatory information observed by the Client are consistent with the "IN" regulatory domain (differing from the previous "US" domain where channel availability diverges). |
---

# Test Case 23: EM_2GRadio_Bandwidth_Change_20to40MHz_RBUSCLI
## Objective
Verify that the 2.4GHz Radio operating bandwidth can be successfully changed from 20 MHz to 40 MHz via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 2.4GHz Radio interface is operational with current bandwidth set to 20 MHz.
4. Regulatory domain/Country Code configured on the Controller supports 40 MHz operation on 2.4GHz.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Bandwidth (Old) | 20 MHz |
| Operating Bandwidth (New) | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (2.4GHz Radio instance) | rbuscli returns the current value "20", confirming baseline bandwidth state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "40"` (2.4GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 2.4GHz Radio. |
| 3 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the updated value "40", confirming the bandwidth change was applied on the 2.4GHz Radio. |
| 4 | Verify updated Operating Class reflects the 40 MHz channel configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 40 MHz operating class for the 2.4GHz band, consistent with the regulatory domain configured. |
| 5 | Verify Radio Enabled/operational status post-change using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Enabled` | Radio remains "true" (enabled/operational), confirming the bandwidth change did not disrupt Radio functionality. |
| 6 | Verify BSS(s) under the 2.4GHz Radio remain operational post-change using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.Enabled` | All associated BSS instances under the 2.4GHz Radio return "true", confirming Fronthaul/Backhaul BSSs remain active after the bandwidth change. |
---


# Test Case 24: EM_2GRadio_Bandwidth_Change_20to40MHz_ClientVerification
## Objective
Verify that after the 2.4GHz Radio operating bandwidth is changed on the Controller to 40 MHz, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated channel width at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 12 ("EM_2GRadio_Bandwidth_Change_20to40MHz_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Bandwidth (Old) | 20 MHz |
| Operating Bandwidth (New) | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to a BSS on the affected 2.4GHz radio and check the negotiated channel width using `iw dev <client-if> link` or `iw dev <client-if> station dump`. | Client link reports a channel width consistent with "40 MHz", confirming the bandwidth change on the 2.4GHz radio is reflected at the client-visible link level. |
---

# Test Case 25: EM_2GRadio_Bandwidth_Change_40to20MHz_RBUSCLI
## Objective
Verify that the 2.4GHz Radio operating bandwidth can be successfully changed from 40 MHz to 20 MHz via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Packet Analyzer | IEEE 1905 packet analysis tool (optional, for reference) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 2.4GHz Radio interface is operational with current bandwidth set to 40 MHz.
4. Regulatory domain/Country Code configured on the Controller supports both 20 MHz and 40 MHz operation on 2.4GHz.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Bandwidth (Old) | 40 MHz |
| Operating Bandwidth (New) | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (2.4GHz Radio instance) | rbuscli returns the current value "40", confirming baseline bandwidth state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "20"` (2.4GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 2.4GHz Radio. |
| 3 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the updated value "20", confirming the bandwidth change was applied on the 2.4GHz Radio. |
| 4 | Verify updated Operating Class reflects the 20 MHz channel configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 20 MHz operating class for the 2.4GHz band, consistent with the regulatory domain configured. |
| 5 | Verify Radio Enabled/operational status post-change using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Enabled` | Radio remains "true" (enabled/operational), confirming the bandwidth change did not disrupt Radio functionality. |
| 6 | Verify BSS(s) under the 2.4GHz Radio remain operational post-change using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.Enabled` | All associated BSS instances under the 2.4GHz Radio return "true", confirming Fronthaul/Backhaul BSSs remain active after the bandwidth change. |
---


# Test Case 26: EM_2GRadio_Bandwidth_Change_40to20MHz_ClientVerification
## Objective
Verify that after the 2.4GHz Radio operating bandwidth is changed on the Controller to 20 MHz, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated channel width at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 13 ("EM_2GRadio_Bandwidth_Change_40to20MHz_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Bandwidth (Old) | 40 MHz |
| Operating Bandwidth (New) | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to a BSS on the affected 2.4GHz radio and check the negotiated channel width using `iw dev <client-if> link` or `iw dev <client-if> station dump`. | Client link reports a channel width consistent with "20 MHz", confirming the bandwidth change on the 2.4GHz radio is reflected at the client-visible link level. |
---

# Test Case 27: EM_2GRadio_Bandwidth_80MHz_InvalidConfig_RBUSCLI
## Objective
Verify that an attempt to configure an unsupported 80 MHz bandwidth on the 2.4GHz Radio via rbuscli is correctly rejected by the Controller, and that the Radio retains its last valid operating bandwidth without disruption.
## Test Type
**Negative**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
| Packet Analyzer | IEEE 1905 packet analysis tool (optional, for reference) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 2.4GHz Radio interface is operational with a known valid bandwidth (20 MHz or 40 MHz).
4. 80 MHz bandwidth is understood to be unsupported on the 2.4GHz band per 802.11 standards (5GHz/6GHz only).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Bandwidth (Existing/Valid) | 40 MHz |
| Operating Bandwidth (Invalid, Attempted) | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (2.4GHz Radio instance) | rbuscli returns the current valid value "40", confirming baseline bandwidth state prior to the invalid configuration attempt. |
| 2 | Attempt to configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "80"` (2.4GHz Radio instance) | Set request is rejected by the Controller/rbus with an appropriate error (e.g., invalid value/out-of-range), and no change is applied. |
| 3 | Verify bandwidth remains unchanged using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns "40", confirming the Radio retained its last valid bandwidth and the invalid 80 MHz value was not applied. |
| 4 | Verify Radio Enabled/operational status post-attempt using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Enabled` | Radio remains "true" (enabled/operational), confirming the rejected configuration attempt did not disrupt Radio functionality. |
| 5 | Verify BSS(s) under the 2.4GHz Radio remain operational using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.Enabled` | All associated BSS instances under the 2.4GHz Radio return "true", confirming Fronthaul/Backhaul BSSs remain active and unaffected. |
---


# Test Case 28: EM_2GRadio_Bandwidth_80MHz_InvalidConfig_ClientVerification
## Objective
Verify that when an unsupported operating bandwidth is rejected by the Controller on the 2.4GHz Radio, an already-connected Wi-Fi Client (STA) remains unaffected and continues operating at the last valid bandwidth.
## Test Type
**Negative**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 14 ("EM_2GRadio_Bandwidth_80MHz_InvalidConfig_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Bandwidth (Existing/Valid) | 40 MHz |
| Operating Bandwidth (Invalid, Attempted) | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Verify the Client remains connected to the 2.4GHz radio and check the link bandwidth using `iw dev <client-if> link`. | Client link continues to report a channel width consistent with the last valid value ("40 MHz"), confirming the rejected/unsupported bandwidth request had no effect on the active client connection. |
---

# Test Case 29: EM_2GRadio_ChannelChange_Channel_1_RBUSCLI
## Objective
Verify that the 2.4GHz Radio operating channel can be successfully changed to Channel 1 via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 2.4GHz Radio interface is operational with a known current channel (other than Channel 1).
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 1.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Channel (Old) | 6 |
| Operating Channel (New) | 1 |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` (2.4GHz Radio instance) | rbuscli returns the current value "6", confirming baseline channel state prior to change. |
| 2 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "1"` (2.4GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 2.4GHz Radio. |
| 3 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "1", confirming the channel change was applied on the 2.4GHz Radio. |
---


# Test Case 30: EM_2GRadio_ChannelChange_Channel_1_ClientVerification
## Objective
Verify that after the 2.4GHz Radio operating channel is changed on the Controller to Channel 1, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 15 ("EM_2GRadio_ChannelChange_Channel_1_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Channel (Old) | 6 |
| Operating Channel (New) | 1 |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 2.4GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "1", confirming the channel change propagated to a client-visible connection on the 2.4GHz radio. |
---

# Test Case 31: EM_2GRadio_ChannelChange_Channel_6_RBUSCLI
## Objective
Verify that the 2.4GHz Radio operating channel can be successfully changed to Channel 6 via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 2.4GHz Radio interface is operational with a known current channel (other than Channel 6).
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 6.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Channel (Old) | 1 |
| Operating Channel (New) | 6 |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` (2.4GHz Radio instance) | rbuscli returns the current value "6", confirming baseline channel state prior to change. |
| 2 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "6"` (2.4GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 2.4GHz Radio. |
| 3 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "6", confirming the channel change was applied on the 2.4GHz Radio. |
---


# Test Case 32: EM_2GRadio_ChannelChange_Channel_6_ClientVerification
## Objective
Verify that after the 2.4GHz Radio operating channel is changed on the Controller to Channel 6, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 16 ("EM_2GRadio_ChannelChange_Channel_6_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Channel (Old) | 1 |
| Operating Channel (New) | 6 |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 2.4GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "6", confirming the channel change propagated to a client-visible connection on the 2.4GHz radio. |
---

# Test Case 33: EM_2GRadio_ChannelChange_Channel_11_RBUSCLI
## Objective
Verify that the 2.4GHz Radio operating channel can be successfully changed to Channel 11 via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 2.4GHz Radio interface is operational with a known current channel (other than Channel 11).
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 11.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Channel (Old) | 6 |
| Operating Channel (New) | 11 |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` (2.4GHz Radio instance) | rbuscli returns the current value "11", confirming baseline channel state prior to change. |
| 2 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "11"` (2.4GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 2.4GHz Radio. |
| 3 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "11", confirming the channel change was applied on the 2.4GHz Radio. |
---


# Test Case 34: EM_2GRadio_ChannelChange_Channel_11_ClientVerification
## Objective
Verify that after the 2.4GHz Radio operating channel is changed on the Controller to Channel 11, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 17 ("EM_2GRadio_ChannelChange_Channel_11_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4GHz |
| Operating Channel (Old) | 6 |
| Operating Channel (New) | 11 |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 2.4GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 2.4GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "11", confirming the channel change propagated to a client-visible connection on the 2.4GHz radio. |
---

# Test Case 35: EM_5GRadio_Bandwidth_Change_20MHz_RBUSCLI
## Objective
Verify that the 5GHz Radio operating bandwidth can be successfully changed to 20 MHz via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current bandwidth (e.g., 80 MHz).
4. Regulatory domain/Country Code configured on the Controller permits 20 MHz operation on 5GHz.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Old) | 80 MHz |
| Operating Bandwidth (New) | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current value "80", confirming baseline bandwidth state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "20"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the updated value "20", confirming the bandwidth change was applied on the 5GHz Radio. |
| 4 | Verify updated Operating Class reflects the 20 MHz channel configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 20 MHz operating class for the 5GHz band, consistent with the regulatory domain configured. |

---


# Test Case 36: EM_5GRadio_Bandwidth_Change_20MHz_ClientVerification
## Objective
Verify that after the 5GHz Radio operating bandwidth is changed on the Controller to 20 MHz, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated channel width at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 18 ("EM_5GRadio_Bandwidth_Change_20MHz_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Old) | 80 MHz |
| Operating Bandwidth (New) | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to a BSS on the affected 5GHz radio and check the negotiated channel width using `iw dev <client-if> link` or `iw dev <client-if> station dump`. | Client link reports a channel width consistent with "20 MHz", confirming the bandwidth change on the 5GHz radio is reflected at the client-visible link level. |
---

# Test Case 37: EM_5GRadio_Bandwidth_Change_40MHz_RBUSCLI
## Objective
Verify that the 5GHz Radio operating bandwidth can be successfully changed to 40 MHz via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current bandwidth (e.g., 20 MHz).
4. Regulatory domain/Country Code configured on the Controller permits 40 MHz operation on 5GHz.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Old) | 20 MHz |
| Operating Bandwidth (New) | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current value "20", confirming baseline bandwidth state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "40"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the updated value "40", confirming the bandwidth change was applied on the 5GHz Radio. |
| 4 | Verify updated Operating Class reflects the 40 MHz channel configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 40 MHz operating class for the 5GHz band, consistent with the regulatory domain configured. |

---


# Test Case 38: EM_5GRadio_Bandwidth_Change_40MHz_ClientVerification
## Objective
Verify that after the 5GHz Radio operating bandwidth is changed on the Controller to 40 MHz, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated channel width at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 19 ("EM_5GRadio_Bandwidth_Change_40MHz_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Old) | 20 MHz |
| Operating Bandwidth (New) | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to a BSS on the affected 5GHz radio and check the negotiated channel width using `iw dev <client-if> link` or `iw dev <client-if> station dump`. | Client link reports a channel width consistent with "40 MHz", confirming the bandwidth change on the 5GHz radio is reflected at the client-visible link level. |
---

# Test Case 39: EM_5GRadio_Bandwidth_Change_80MHz_RBUSCLI
## Objective
Verify that the 5GHz Radio operating bandwidth can be successfully changed to 80 MHz via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current bandwidth (e.g., 40 MHz).
4. Regulatory domain/Country Code configured on the Controller permits 80 MHz operation on 5GHz.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Old) | 40 MHz |
| Operating Bandwidth (New) | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current value "40", confirming baseline bandwidth state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "80"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the updated value "80", confirming the bandwidth change was applied on the 5GHz Radio. |
| 4 | Verify updated Operating Class reflects the 80 MHz channel configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 80 MHz operating class for the 5GHz band, consistent with the regulatory domain configured. |

---


# Test Case 40: EM_5GRadio_Bandwidth_Change_80MHz_ClientVerification
## Objective
Verify that after the 5GHz Radio operating bandwidth is changed on the Controller to 80 MHz, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated channel width at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 20 ("EM_5GRadio_Bandwidth_Change_80MHz_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Old) | 40 MHz |
| Operating Bandwidth (New) | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to a BSS on the affected 5GHz radio and check the negotiated channel width using `iw dev <client-if> link` or `iw dev <client-if> station dump`. | Client link reports a channel width consistent with "80 MHz", confirming the bandwidth change on the 5GHz radio is reflected at the client-visible link level. |
---

# Test Case 41: EM_5GRadio_Bandwidth_Change_160MHz_RBUSCLI
## Objective
Verify that the 5GHz Radio operating bandwidth can be successfully changed to 160 MHz via rbuscli, and that the updated value is correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current bandwidth (e.g., 80 MHz).
4. Regulatory domain/Country Code configured on the Controller permits 160 MHz operation on 5GHz.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Old) | 80 MHz |
| Operating Bandwidth (New) | 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current value "80", confirming baseline bandwidth state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "160"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the updated value "160", confirming the bandwidth change was applied on the 5GHz Radio. |
| 4 | Verify updated Operating Class reflects the 160 MHz channel configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 160 MHz operating class for the 5GHz band, consistent with the regulatory domain configured. |

---


# Test Case 42: EM_5GRadio_Bandwidth_Change_160MHz_ClientVerification
## Objective
Verify that after the 5GHz Radio operating bandwidth is changed on the Controller to 160 MHz, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated channel width at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 21 ("EM_5GRadio_Bandwidth_Change_160MHz_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Old) | 80 MHz |
| Operating Bandwidth (New) | 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to a BSS on the affected 5GHz radio and check the negotiated channel width using `iw dev <client-if> link` or `iw dev <client-if> station dump`. | Client link reports a channel width consistent with "160 MHz", confirming the bandwidth change on the 5GHz radio is reflected at the client-visible link level. |
---

# Test Case 43: EM_5GRadio_Bandwidth_320MHz_RBUSCLI
## Objective
Verify that an attempt to configure an unsupported 320 MHz bandwidth on the 5GHz Radio via rbuscli is correctly rejected by the Controller, and that the Radio retains its last valid operating bandwidth without disruption.
## Test Type
**Negative**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known valid bandwidth (e.g., 80 MHz).
4. 320 MHz bandwidth is understood to be unsupported on the 5GHz band per 802.11 standards (6GHz/802.11be only).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Existing/Valid) | 80 MHz |
| Operating Bandwidth (Invalid, Attempted) | 320 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current valid value "80", confirming baseline bandwidth state prior to the invalid configuration attempt. |
| 2 | Attempt to configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "320"` (5GHz Radio instance) | Set request is rejected by the Controller/rbus with an appropriate error (e.g., invalid value/out-of-range), and no change is applied. |
| 3 | Verify bandwidth remains unchanged using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns "80", confirming the Radio retained its last valid bandwidth and the invalid 320 MHz value was not applied. |

---


# Test Case 44: EM_5GRadio_Bandwidth_320MHz_ClientVerification
## Objective
Verify that when an unsupported operating bandwidth is rejected by the Controller on the 5GHz Radio, an already-connected Wi-Fi Client (STA) remains unaffected and continues operating at the last valid bandwidth.
## Test Type
**Negative**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 22 ("EM_5GRadio_Bandwidth_320MHz_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Bandwidth (Existing/Valid) | 80 MHz |
| Operating Bandwidth (Invalid, Attempted) | 320 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Verify the Client remains connected to the 5GHz radio and check the link bandwidth using `iw dev <client-if> link`. | Client link continues to report a channel width consistent with the last valid value ("80 MHz"), confirming the rejected/unsupported bandwidth request had no effect on the active client connection. |
---

# Test Case 45: EM_5GRadio_20MHz_Channel_36_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 36 with 20 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 36 with 20 MHz bandwidth (UNII-1 band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 149 |
| Operating Channel (New) | 36 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "149" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "20"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "36"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "36", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "20", confirming 20 MHz bandwidth is applied along with Channel 36. |
| 6 | Verify updated Operating Class corresponds to Channel 36 at 20 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 20 MHz operating class for Channel 36 (UNII-1, e.g., Class 115), consistent with the regulatory domain configured. |
---


# Test Case 46: EM_5GRadio_20MHz_Channel_36_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 36, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 23 ("EM_5GRadio_20MHz_Channel_36_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 149 |
| Operating Channel (New) | 36 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "36", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 47: EM_5GRadio_20MHz_Channel_52_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 52 with 20 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 52 with 20 MHz bandwidth (UNII-2A band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 149 |
| Operating Channel (New) | 52 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "149" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "20"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "52"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "52", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "20", confirming 20 MHz bandwidth is applied along with Channel 52. |
| 6 | Verify updated Operating Class corresponds to Channel 52 at 20 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 20 MHz operating class for Channel 52 (UNII-2A, e.g., Class 115), consistent with the regulatory domain configured. |
---


# Test Case 48: EM_5GRadio_20MHz_Channel_52_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 52, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 24 ("EM_5GRadio_20MHz_Channel_52_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 149 |
| Operating Channel (New) | 52 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "52", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 49: EM_5GRadio_20MHz_Channel_100_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 100 with 20 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 100 with 20 MHz bandwidth (UNII-2C band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 149 |
| Operating Channel (New) | 100 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "149" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "20"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "100"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "100", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "20", confirming 20 MHz bandwidth is applied along with Channel 100. |
| 6 | Verify updated Operating Class corresponds to Channel 100 at 20 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 20 MHz operating class for Channel 100 (UNII-2C, e.g., Class 115), consistent with the regulatory domain configured. |
---


# Test Case 50: EM_5GRadio_20MHz_Channel_100_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 100, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 25 ("EM_5GRadio_20MHz_Channel_100_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 149 |
| Operating Channel (New) | 100 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "100", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 51: EM_5GRadio_20MHz_Channel_149_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 149 with 20 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 149 with 20 MHz bandwidth (UNII-3 band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 149 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "100" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "20"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "149"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "149", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "20", confirming 20 MHz bandwidth is applied along with Channel 149. |
| 6 | Verify updated Operating Class corresponds to Channel 149 at 20 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 20 MHz operating class for Channel 149 (UNII-3, e.g., Class 115), consistent with the regulatory domain configured. |
---


# Test Case 52: EM_5GRadio_20MHz_Channel_149_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 149, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 26 ("EM_5GRadio_20MHz_Channel_149_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 149 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "149", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 53: EM_5GRadio_40MHz_Channel_36_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 36 with 40 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 36 with 40 MHz bandwidth (UNII-1 band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 149 |
| Operating Channel (New) | 36 |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "149" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "40"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "36"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "36", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "40", confirming 40 MHz bandwidth is applied along with Channel 36. |
| 6 | Verify updated Operating Class corresponds to Channel 36 at 40 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 40 MHz operating class for Channel 36 (UNII-1, e.g., Class 116), consistent with the regulatory domain configured. |
---
 

# Test Case 54: EM_5GRadio_40MHz_Channel_36_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 36, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 27 ("EM_5GRadio_40MHz_Channel_36_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 149 |
| Operating Channel (New) | 36 |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "36", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 55: EM_5GRadio_40MHz_Channel_52_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 52 with 40 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 52 with 40 MHz bandwidth (UNII-3 band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 52  |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "100" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "40"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "52"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "52", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "40", confirming 40 MHz bandwidth is applied along with Channel 52. |
| 6 | Verify updated Operating Class corresponds to Channel 52 at 40 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 40 MHz operating class for Channel 52 , consistent with the regulatory domain configured. |
---


# Test Case 56: EM_5GRadio_40MHz_Channel_52_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 52, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 28 ("EM_5GRadio_40MHz_Channel_52_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 52 |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "52", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 57: EM_5GRadio_40MHz_Channel_100_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 100 with 40 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 100 with 40 MHz bandwidth.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 80 |
| Operating Channel (New) | 100 |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "80" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "40"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "100"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "100", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "40", confirming 40 MHz bandwidth is applied along with Channel 100. |
| 6 | Verify updated Operating Class corresponds to Channel 100 at 40 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 40 MHz operating class for Channel 100, consistent with the regulatory domain configured. |
---


# Test Case 58: EM_5GRadio_40MHz_Channel_100_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 100, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 29 ("EM_5GRadio_40MHz_Channel_100_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 80 |
| Operating Channel (New) | 100 |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "100", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 59: EM_5GRadio_40MHz_Channel_149_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 149 with 40 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 149 with 40 MHz bandwidth.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 149 |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "100" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "40"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "149"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "149", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "40", confirming 40 MHz bandwidth is applied along with Channel 149. |
| 6 | Verify updated Operating Class corresponds to Channel 149 at 40 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 40 MHz operating class for Channel 149, consistent with the regulatory domain configured. |
---


# Test Case 60: EM_5GRadio_40MHz_Channel_149_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 149, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 30 ("EM_5GRadio_40MHz_Channel_149_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 149 |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "149", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 61: EM_5GRadio_80MHz_Channel_36_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 36 with 80 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 36 with 80 MHz bandwidth.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 36 |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "100" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "80"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "36"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "36", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "80", confirming 80 MHz bandwidth is applied along with Channel 36. |
| 6 | Verify updated Operating Class corresponds to Channel 36 at 80 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 80 MHz operating class for Channel 36, consistent with the regulatory domain configured. |
---


# Test Case 62: EM_5GRadio_80MHz_Channel_36_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 36, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 31 ("EM_5GRadio_80MHz_Channel_36_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 36 |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "36", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 63: EM_5GRadio_80MHz_Channel_52_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 52 with 80 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 52 with 80 MHz bandwidth (UNII-3 band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 52  |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "100" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "80"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "52"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "52", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "80", confirming 80 MHz bandwidth is applied along with Channel 52. |
| 6 | Verify updated Operating Class corresponds to Channel 52 at 80 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 80 MHz operating class for Channel 52 , consistent with the regulatory domain configured. |
---



# Test Case 64: EM_5GRadio_80MHz_Channel_52_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 52, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 32 ("EM_5GRadio_80MHz_Channel_52_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 52 |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "52", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 65: EM_5GRadio_80MHz_Channel_100_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 100 with 80 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 100 with 80 MHz bandwidth (UNII-3 band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 36 |
| Operating Channel (New) | 100  |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "36" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "80"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "100"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "100", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "80", confirming 80 MHz bandwidth is applied along with Channel 100. |
| 6 | Verify updated Operating Class corresponds to Channel 100 at 80 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 80 MHz operating class for Channel 100 , consistent with the regulatory domain configured. |
---


# Test Case 66: EM_5GRadio_80MHz_Channel_100_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 100, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 33 ("EM_5GRadio_80MHz_Channel_100_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 36 |
| Operating Channel (New) | 100 |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "100", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 67: EM_5GRadio_80MHz_Channel_149_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 149 with 80 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 149 with 80 MHz bandwidth.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 149 |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "100" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "80"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "149"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "149", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "80", confirming 80 MHz bandwidth is applied along with Channel 149. |
| 6 | Verify updated Operating Class corresponds to Channel 149 at 80 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 80 MHz operating class for Channel 149, consistent with the regulatory domain configured. |
---


# Test Case 68: EM_5GRadio_80MHz_Channel_149_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 149, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 34 ("EM_5GRadio_80MHz_Channel_149_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 149 |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "149", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 69: EM_5GRadio_160MHz_Channel_36_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 36 with 160 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 36 with 160 MHz bandwidth.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 36 |
| Operating Bandwidth | 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "100" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "160"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "36"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "36", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "160", confirming 160 MHz bandwidth is applied along with Channel 36. |
| 6 | Verify updated Operating Class corresponds to Channel 36 at 160 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 160 MHz operating class for Channel 36, consistent with the regulatory domain configured. |
---


# Test Case 70: EM_5GRadio_160MHz_Channel_36_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 36, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 35 ("EM_5GRadio_160MHz_Channel_36_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 100 |
| Operating Channel (New) | 36 |
| Operating Bandwidth | 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "36", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 71: EM_5GRadio_160MHz_Channel_100_ChannelChange_RBUSCLI
## Objective
Verify that the 5GHz Radio can be successfully configured to operate on Channel 100 with 160 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 100 with 160 MHz bandwidth (UNII-3 band).
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 36 |
| Operating Channel (New) | 100  |
| Operating Bandwidth | 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (5GHz Radio instance) | rbuscli returns the current channel "36" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "160"` (5GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 5GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "100"` (5GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 5GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "100", confirming the channel change was applied on the 5GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "160", confirming 160 MHz bandwidth is applied along with Channel 100. |
| 6 | Verify updated Operating Class corresponds to Channel 100 at 160 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 160 MHz operating class for Channel 100 , consistent with the regulatory domain configured. |
---


# Test Case 72: EM_5GRadio_160MHz_Channel_100_ChannelChange_ClientVerification
## Objective
Verify that after the 5GHz Radio operating channel is changed on the Controller to Channel 100, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 36 ("EM_5GRadio_160MHz_Channel_100_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel (Old) | 36 |
| Operating Channel (New) | 100 |
| Operating Bandwidth | 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 5GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "100", confirming the channel change propagated to a client-visible connection on the 5GHz radio. |
---

# Test Case 73: EM_5GRadio_160MHz_Channel_132_InvalidConfig_RBUSCLI
## Objective
Verify that an attempt to configure Channel 132 with 160 MHz bandwidth on the 5GHz Radio via rbuscli is correctly rejected by the Controller, and that the Radio retains its last valid channel/bandwidth without disruption.
## Test Type
**Negative**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5GHz Radio interface is operational with a known valid channel and bandwidth (e.g., Channel 100 at 160 MHz).
4. Channel 132 is understood to be unable to support 160 MHz bandwidth on the 5GHz band, since it falls outside the two valid 160 MHz blocks (36–64 and 100–128) defined by the regulatory channel plan.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel/Bandwidth (Existing/Valid) | Channel 100, 160 MHz |
| Operating Channel/Bandwidth (Invalid, Attempted) | Channel 132, 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `...Bandwidth` (5GHz Radio instance) | rbuscli returns the current valid channel "100" and bandwidth "160", confirming baseline state prior to the invalid configuration attempt. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "160"` (5GHz Radio instance) | Bandwidth remains set to 160 MHz (already valid at baseline). |
| 3 | Attempt to configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "132"` (5GHz Radio instance) | Set request is rejected by the Controller/rbus with an appropriate error (e.g., invalid value/unsupported channel-bandwidth combination), and no change is applied. |
| 4 | Verify channel remains unchanged using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns "100", confirming the Radio retained its last valid channel and the invalid Channel 132/160 MHz combination was not applied. |
| 5 | Verify Radio Enabled/operational status post-attempt using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Enabled` | Radio remains "true" (enabled/operational), confirming the rejected configuration attempt did not disrupt Radio functionality. |
---


# Test Case 74: EM_5GRadio_160MHz_Channel_132_InvalidConfig_ClientVerification
## Objective
Verify that when an unsupported/invalid channel (or channel-bandwidth combination) is rejected by the Controller on the 5GHz Radio, an already-connected Wi-Fi Client (STA) remains unaffected and continues operating on the last valid channel.
## Test Type
**Negative**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 37 ("EM_5GRadio_160MHz_Channel_132_InvalidConfig_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5GHz |
| Operating Channel/Bandwidth (Existing/Valid) | Channel 100, 160 MHz |
| Operating Channel/Bandwidth (Invalid, Attempted) | Channel 132, 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 5GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Verify the Client remains connected to the 5GHz radio and check the operating channel using `iw dev <client-if> link`. | Client link continues to report the last valid operating channel ("Channel 100, 160 MHz"), confirming the rejected/unsupported channel request had no effect on the active client connection. |
---

# Test Case 75: EM_6GRadio_20MHz_Channel_33_ChannelChange_RBUSCLI
## Objective
Verify that the 6GHz Radio can be successfully configured to operate on Channel 33 with 20 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 6GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 33 with 20 MHz bandwidth.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 65 |
| Operating Channel (New) | 33 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (6GHz Radio instance) | rbuscli returns the current channel "65" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "20"` (6GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 6GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "33"` (6GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 6GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "33", confirming the channel change was applied on the 6GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "20", confirming 20 MHz bandwidth is applied along with Channel 33. |
| 6 | Verify updated Operating Class corresponds to Channel 33 at 20 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 20 MHz operating class for Channel 33, consistent with the regulatory domain configured. |
---


# Test Case 76: EM_6GRadio_20MHz_Channel_33_ChannelChange_ClientVerification
## Objective
Verify that after the 6GHz Radio operating channel is changed on the Controller to Channel 33, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 38 ("EM_6GRadio_20MHz_Channel_33_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 65 |
| Operating Channel (New) | 33 |
| Operating Bandwidth | 20 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 6GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "33", confirming the channel change propagated to a client-visible connection on the 6GHz radio. |
---

# Test Case 77: EM_6GRadio_40MHz_Channel_65_ChannelChange_RBUSCLI
## Objective
Verify that the 6GHz Radio can be successfully configured to operate on Channel 65 with 40 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 6GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 65 with 40 MHz.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 97 |
| Operating Channel (New) | 65  |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (6GHz Radio instance) | rbuscli returns the current channel "97" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "40"` (6GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 6GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "65"` (6GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 6GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "65", confirming the channel change was applied on the 6GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "40", confirming 40 MHz bandwidth is applied along with Channel 65. |
| 6 | Verify updated Operating Class corresponds to Channel 65 at 40 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 40 MHz operating class for Channel 65 , consistent with the regulatory domain configured. |
---


# Test Case 78: EM_6GRadio_40MHz_Channel_65_ChannelChange_ClientVerification
## Objective
Verify that after the 6GHz Radio operating channel is changed on the Controller to Channel 65, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 39 ("EM_6GRadio_40MHz_Channel_65_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 97 |
| Operating Channel (New) | 65 |
| Operating Bandwidth | 40 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 6GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "65", confirming the channel change propagated to a client-visible connection on the 6GHz radio. |
---

# Test Case 79: EM_6GRadio_80MHz_Channel_97_ChannelChange_RBUSCLI
## Objective
Verify that the 6GHz Radio can be successfully configured to operate on Channel 97 with 80 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 6GHz Radio interface is operational with a known current channel and bandwidth.	
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 97 with 80 MHz bandwidth.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 65 |
| Operating Channel (New) | 97 |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (6GHz Radio instance) | rbuscli returns the current channel "65" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "80"` (6GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 6GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "97"` (6GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 6GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "97", confirming the channel change was applied on the 6GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "80", confirming 80 MHz bandwidth is applied along with Channel 97. |
| 6 | Verify updated Operating Class corresponds to Channel 97 at 80 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 80 MHz operating class for Channel 97, consistent with the regulatory domain configured. |
---


# Test Case 80: EM_6GRadio_80MHz_Channel_97_ChannelChange_ClientVerification
## Objective
Verify that after the 6GHz Radio operating channel is changed on the Controller to Channel 97, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 40 ("EM_6GRadio_80MHz_Channel_97_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 65 |
| Operating Channel (New) | 97 |
| Operating Bandwidth | 80 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 6GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "97", confirming the channel change propagated to a client-visible connection on the 6GHz radio. |
---

# Test Case 81: EM_6GRadio_160MHz_Channel_129_ChannelChange_RBUSCLI
## Objective
Verify that the 6GHz Radio can be successfully configured to operate on Channel 129 with 160 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 6GHz Radio interface is operational with a known current channel and bandwidth.	
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 129 with 160 MHz bandwidth.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 65 |
| Operating Channel (New) | 129 |
| Operating Bandwidth | 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (6GHz Radio instance) | rbuscli returns the current channel "65" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "160"` (6GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 6GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "129"` (6GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 6GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "129", confirming the channel change was applied on the 6GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "160", confirming 160 MHz bandwidth is applied along with Channel 129. |
| 6 | Verify updated Operating Class corresponds to Channel 129 at 160 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 160 MHz operating class for Channel 129, consistent with the regulatory domain configured. |
---


# Test Case 82: EM_6GRadio_160MHz_Channel_129_ChannelChange_ClientVerification
## Objective
Verify that after the 6GHz Radio operating channel is changed on the Controller to Channel 129, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 41 ("EM_6GRadio_160MHz_Channel_129_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 65 |
| Operating Channel (New) | 129 |
| Operating Bandwidth | 160 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 6GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "129", confirming the channel change propagated to a client-visible connection on the 6GHz radio. |
---

# Test Case 83: EM_6GRadio_320MHz_Channel_129_ChannelChange_RBUSCLI
## Objective
Verify that the 6GHz Radio can be successfully configured to operate on Channel 129 with 320 MHz bandwidth via rbuscli, and that the updated channel and bandwidth values are correctly reflected in the Controller's DataElements data model.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 6GHz Radio interface is operational with a known current channel and bandwidth.
4. Regulatory domain/Country Code configured on the Controller permits operation on Channel 129 with 320 MHz.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 97 |
| Operating Channel (New) | 129  |
| Operating Bandwidth | 320 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Verify current channel and bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` (6GHz Radio instance) | rbuscli returns the current channel "97" and bandwidth, confirming baseline state prior to change. |
| 2 | Configure bandwidth using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelBandwidth "320"` (6GHz Radio instance) | Bandwidth configuration request is accepted and applied successfully on the 6GHz Radio. |
| 3 | Configure channel using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Channel "129"` (6GHz Radio instance) | Channel configuration request is accepted and applied successfully on the 6GHz Radio. |
| 4 | Verify updated channel using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Channel` | rbuscli returns the updated value "129", confirming the channel change was applied on the 6GHz Radio. |
| 5 | Verify updated bandwidth using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Bandwidth` | rbuscli returns the value "320", confirming 320 MHz bandwidth is applied along with Channel 129. |
| 6 | Verify updated Operating Class corresponds to Channel 129 at 320 MHz using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.CurrentOperatingClasses.{i}.Class` | Operating Class value returned corresponds to a valid 320	 MHz operating class for Channel 129 , consistent with the regulatory domain configured. |
---


# Test Case 84: EM_6GRadio_320MHz_Channel_129_ChannelChange_ClientVerification
## Objective
Verify that after the 6GHz Radio operating channel is changed on the Controller to Channel 129, a Wi-Fi Client (STA) connected to the corresponding BSS reflects the updated operating channel at the link level.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 42 ("EM_6GRadio_320MHz_Channel_129_ChannelChange_RBUSCLI") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6GHz |
| Operating Channel (Old) | 97 |
| Operating Channel (New) | 129 |
| Operating Bandwidth | 320 MHz |
| Verification Method | rbuscli DataElements get |
| Network Topology | Controller managing 6GHz Radio configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | Reconnect the Client to the 6GHz BSS after the channel change and verify the operating channel using `iw dev <client-if> link`. | Client link reports association on channel "129", confirming the channel change propagated to a client-visible connection on the 6GHz radio. |
---

# Test Case 85: EM_Primary2GSSID_EnabledOnCreation_ControllerVerification
## Objective
Verify that when a primary SSID (SSID-1) is created on the 2G radio on the Controller, it is enabled correctly, and this is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli and iw dev available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 2G radio BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4 GHz |
| Primary SSID (SSID-1, New) | EasyMesh_2G_Primary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 2G radio primary SSID (SSID-1) configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Configure the primary SSID (SSID-1) name on the 2G radio using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.1.SSID string EasyMesh_2G_Primary` | rbuscli command executes successfully and returns a success/OK status, applying the new SSID-1 value on the Controller. |
| 2 | Enable the primary SSID (SSID-1) using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.1.Enabled bool true` | rbuscli command executes successfully and returns a success/OK status, enabling SSID-1 on the 2G radio. |
| 3 | Verify the created SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.1.SSID` | rbuscli returns the newly created SSID "EasyMesh_2G_Primary" for the 2G radio's BSS.1 (SSID-1) instance. |
| 4 | Verify the Enable status using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.1.Enabled` | rbuscli returns the Enabled parameter as "true", confirming SSID-1 on the 2G radio is enabled. |
| 5 | Verify the interface status using `iw dev` on the Controller (checking the 2G radio's primary interface, e.g., wifi0). | `iw dev` output shows the 2G radio's primary interface up and broadcasting SSID "EasyMesh_2G_Primary". |
---



# Test Case 86: EM_Primary2GSSID_EnabledOnCreation_ClientVerification
## Objective
Verify that immediately after the SSID "EasyMesh_2G_Primary" is created and enabled on the 2.4 GHz radio on the Controller, a Wi-Fi Client (STA) can discover it via scan and successfully connect without delay.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 43 ("EM_Primary2GSSID_EnabledOnCreation_ControllerVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4 GHz |
| Primary SSID (SSID-1, New) | EasyMesh_2G_Primary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 2G radio primary SSID (SSID-1) configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan immediately after the SSID is created on the Controller. | The newly created SSID "EasyMesh_2G_Primary" is visible in Client scan results without delay, confirming it is broadcasting immediately upon creation. |
| 2 | Connect the Client to the newly created SSID "EasyMesh_2G_Primary" and verify connectivity using `iw dev <client-if> link` and a DHCP/ping check. | Client associates successfully to SSID "EasyMesh_2G_Primary" and obtains IP connectivity, confirming the SSID is enabled and fully operational immediately upon creation. |
---

# Test Case 87: EM_Secondary2GSSID_EnabledOnCreation_ControllerVerification
## Objective
Verify that when a secondary SSID (SSID-2) is created on the same 2G radio on the Controller, it is enabled correctly, and this is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli and iw dev available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 2G radio BSS/radio interface is operational and visible via `iw dev` on the Controller.
4. Primary SSID (SSID-1) already exists on the same 2G radio.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4 GHz |
| Secondary SSID (SSID-2, New) | EasyMesh_2G_Secondary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 2G radio secondary SSID (SSID-2) configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Configure the secondary SSID (SSID-2) name on the same 2G radio using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.2.SSID string EasyMesh_2G_Secondary` | rbuscli command executes successfully and returns a success/OK status, applying the new SSID-2 value on the Controller. |
| 2 | Enable the secondary SSID (SSID-2) using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.2.Enabled bool true` | rbuscli command executes successfully and returns a success/OK status, enabling SSID-2 on the 2G radio without affecting the existing primary SSID (SSID-1). |
| 3 | Verify the created SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.2.SSID` | rbuscli returns the newly created SSID "EasyMesh_2G_Secondary" for the 2G radio's BSS.2 (SSID-2) instance. |
| 4 | Verify the Enable status using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.1.BSS.2.Enabled` | rbuscli returns the Enabled parameter as "true", confirming SSID-2 on the 2G radio is enabled. |
| 5 | Verify the interface status using `iw dev` on the Controller (checking the 2G radio's secondary interface, e.g., wifi0.1). | `iw dev` output shows the 2G radio's secondary interface up and broadcasting SSID "EasyMesh_2G_Secondary". |

---


# Test Case 88: EM_Secondary2GSSID_EnabledOnCreation_ClientVerification
## Objective
Verify that immediately after the SSID "EasyMesh_2G_Secondary" is created and enabled on the 2.4 GHz radio on the Controller, a Wi-Fi Client (STA) can discover it via scan and successfully connect without delay.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 44 ("EM_Secondary2GSSID_EnabledOnCreation_ControllerVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 2.4 GHz |
| Secondary SSID (SSID-2, New) | EasyMesh_2G_Secondary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 2G radio secondary SSID (SSID-2) configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan immediately after the SSID is created on the Controller. | The newly created SSID "EasyMesh_2G_Secondary" is visible in Client scan results without delay, confirming it is broadcasting immediately upon creation. |
| 2 | Connect the Client to the newly created SSID "EasyMesh_2G_Secondary" and verify connectivity using `iw dev <client-if> link` and a DHCP/ping check. | Client associates successfully to SSID "EasyMesh_2G_Secondary" and obtains IP connectivity, confirming the SSID is enabled and fully operational immediately upon creation. |
---

# Test Case 89: EM_Primary5GSSID_EnabledOnCreation_ControllerVerification
## Objective
Verify that when a primary SSID (SSID-A) is created on the 5G radio on the Controller, it is enabled correctly, and this is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli and iw dev available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5G radio BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5 GHz |
| Primary SSID (SSID-A, New) | EasyMesh_5G_Primary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 5G radio primary SSID (SSID-A) configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Configure the primary SSID (SSID-A) name on the 5G radio using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.2.BSS.1.SSID string EasyMesh_5G_Primary` | rbuscli command executes successfully and returns a success/OK status, applying the new SSID-A value on the Controller. |
| 2 | Enable the primary SSID (SSID-A) using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.2.BSS.1.Enabled bool true` | rbuscli command executes successfully and returns a success/OK status, enabling SSID-A on the 5G radio. |
| 3 | Verify the created SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.2.BSS.1.SSID` | rbuscli returns the newly created SSID "EasyMesh_5G_Primary" for the 5G radio's BSS.1 (SSID-A) instance. |
| 4 | Verify the Enable status using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.2.BSS.1.Enabled` | rbuscli returns the Enabled parameter as "true", confirming SSID-A on the 5G radio is enabled. |
| 5 | Verify the interface status using `iw dev` on the Controller (checking the 5G radio's primary interface, e.g., wifi1). | `iw dev` output shows the 5G radio's primary interface up and broadcasting SSID "EasyMesh_5G_Primary". |

---


# Test Case 90: EM_Primary5GSSID_EnabledOnCreation_ClientVerification
## Objective
Verify that immediately after the SSID "EasyMesh_5G_Primary" is created and enabled on the 5 GHz radio on the Controller, a Wi-Fi Client (STA) can discover it via scan and successfully connect without delay.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 45 ("EM_Primary5GSSID_EnabledOnCreation_ControllerVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5 GHz |
| Primary SSID (SSID-A, New) | EasyMesh_5G_Primary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 5G radio primary SSID (SSID-A) configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan immediately after the SSID is created on the Controller. | The newly created SSID "EasyMesh_5G_Primary" is visible in Client scan results without delay, confirming it is broadcasting immediately upon creation. |
| 2 | Connect the Client to the newly created SSID "EasyMesh_5G_Primary" and verify connectivity using `iw dev <client-if> link` and a DHCP/ping check. | Client associates successfully to SSID "EasyMesh_5G_Primary" and obtains IP connectivity, confirming the SSID is enabled and fully operational immediately upon creation. |
---

# Test Case 91: EM_Secondary5GSSID_EnabledOnCreation_ControllerVerification
## Objective
Verify that when a secondary SSID (SSID-B) is created on the same 5G radio on the Controller, it is enabled correctly, and this is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli and iw dev available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 5G radio BSS/radio interface is operational and visible via `iw dev` on the Controller.
4. Primary SSID (SSID-A) already exists on the same 5G radio.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5 GHz |
| Secondary SSID (SSID-B, New) | EasyMesh_5G_Secondary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 5G radio secondary SSID (SSID-B) configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Configure the secondary SSID (SSID-B) name on the same 5G radio using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.2.BSS.2.SSID string EasyMesh_5G_Secondary` | rbuscli command executes successfully and returns a success/OK status, applying the new SSID-B value on the Controller. |
| 2 | Enable the secondary SSID (SSID-B) using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.2.BSS.2.Enabled bool true` | rbuscli command executes successfully and returns a success/OK status, enabling SSID-B on the 5G radio without affecting the existing primary SSID (SSID-A). |
| 3 | Verify the created SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.2.BSS.2.SSID` | rbuscli returns the newly created SSID "EasyMesh_5G_Secondary" for the 5G radio's BSS.2 (SSID-B) instance. |
| 4 | Verify the Enable status using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.2.BSS.2.Enabled` | rbuscli returns the Enabled parameter as "true", confirming SSID-B on the 5G radio is enabled. |
| 5 | Verify the interface status using `iw dev` on the Controller (checking the 5G radio's secondary interface, e.g., wifi1.1). | `iw dev` output shows the 5G radio's secondary interface up and broadcasting SSID "EasyMesh_5G_Secondary". |

---


# Test Case 92: EM_Secondary5GSSID_EnabledOnCreation_ClientVerification
## Objective
Verify that immediately after the SSID "EasyMesh_5G_Secondary" is created and enabled on the 5 GHz radio on the Controller, a Wi-Fi Client (STA) can discover it via scan and successfully connect without delay.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 46 ("EM_Secondary5GSSID_EnabledOnCreation_ControllerVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 5 GHz |
| Secondary SSID (SSID-B, New) | EasyMesh_5G_Secondary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 5G radio secondary SSID (SSID-B) configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan immediately after the SSID is created on the Controller. | The newly created SSID "EasyMesh_5G_Secondary" is visible in Client scan results without delay, confirming it is broadcasting immediately upon creation. |
| 2 | Connect the Client to the newly created SSID "EasyMesh_5G_Secondary" and verify connectivity using `iw dev <client-if> link` and a DHCP/ping check. | Client associates successfully to SSID "EasyMesh_5G_Secondary" and obtains IP connectivity, confirming the SSID is enabled and fully operational immediately upon creation. |
---

# Test Case 93: EM_Primary6GSSID_EnabledOnCreation_ControllerVerification
## Objective
Verify that when a primary SSID (SSID-A) is created on the 6G radio on the Controller, it is enabled correctly, and this is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli and iw dev available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 6G radio BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6 GHz |
| Primary SSID (SSID-A, New) | EasyMesh_6G_Primary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 6G radio primary SSID (SSID-A) configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Configure the primary SSID (SSID-A) name on the 6G radio using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.3.BSS.1.SSID string EasyMesh_6G_Primary` | rbuscli command executes successfully and returns a success/OK status, applying the new SSID-A value on the Controller. |
| 2 | Enable the primary SSID (SSID-A) using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.3.BSS.1.Enabled bool true` | rbuscli command executes successfully and returns a success/OK status, enabling SSID-A on the 6G radio. |
| 3 | Verify the created SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.3.BSS.1.SSID` | rbuscli returns the newly created SSID "EasyMesh_6G_Primary" for the 6G radio's BSS.1 (SSID-A) instance. |
| 4 | Verify the Enable status using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.3.BSS.1.Enabled` | rbuscli returns the Enabled parameter as "true", confirming SSID-A on the 6G radio is enabled. |
| 5 | Verify the interface status using `iw dev` on the Controller (checking the 6G radio's primary interface, e.g., wifi2). | `iw dev` output shows the 6G radio's primary interface up and broadcasting SSID "EasyMesh_6G_Primary". |

---


# Test Case 94: EM_Primary6GSSID_EnabledOnCreation_ClientVerification
## Objective
Verify that immediately after the SSID "EasyMesh_6G_Primary" is created and enabled on the 6 GHz radio on the Controller, a Wi-Fi Client (STA) can discover it via scan and successfully connect without delay.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 47 ("EM_Primary6GSSID_EnabledOnCreation_ControllerVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6 GHz |
| Primary SSID (SSID-A, New) | EasyMesh_6G_Primary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 6G radio primary SSID (SSID-A) configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan immediately after the SSID is created on the Controller. | The newly created SSID "EasyMesh_6G_Primary" is visible in Client scan results without delay, confirming it is broadcasting immediately upon creation. |
| 2 | Connect the Client to the newly created SSID "EasyMesh_6G_Primary" and verify connectivity using `iw dev <client-if> link` and a DHCP/ping check. | Client associates successfully to SSID "EasyMesh_6G_Primary" and obtains IP connectivity, confirming the SSID is enabled and fully operational immediately upon creation. |
---

# Test Case 95: EM_Secondary6GSSID_EnabledOnCreation_ControllerVerification
## Objective
Verify that when a secondary SSID (SSID-B) is created on the same 6G radio on the Controller, it is enabled correctly, and this is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (rbuscli and iw dev available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. DataElements object is accessible through rbuscli on the Controller.
3. 6G radio BSS/radio interface is operational and visible via `iw dev` on the Controller.
4. Primary SSID (SSID-A) already exists on the same 6G radio.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6 GHz |
| Secondary SSID (SSID-B, New) | EasyMesh_6G_Secondary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 6G radio secondary SSID (SSID-B) configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Configure the secondary SSID (SSID-B) name on the same 6G radio using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.3.BSS.2.SSID string EasyMesh_6G_Secondary` | rbuscli command executes successfully and returns a success/OK status, applying the new SSID-B value on the Controller. |
| 2 | Enable the secondary SSID (SSID-B) using `rbuscli set Device.WiFi.DataElements.Network.Device.1.Radio.3.BSS.2.Enabled bool true` | rbuscli command executes successfully and returns a success/OK status, enabling SSID-B on the 6G radio without affecting the existing primary SSID (SSID-A). |
| 3 | Verify the created SSID using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.3.BSS.2.SSID` | rbuscli returns the newly created SSID "EasyMesh_6G_Secondary" for the 6G radio's BSS.2 (SSID-B) instance. |
| 4 | Verify the Enable status using `rbuscli get Device.WiFi.DataElements.Network.Device.1.Radio.3.BSS.2.Enabled` | rbuscli returns the Enabled parameter as "true", confirming SSID-B on the 6G radio is enabled. |
| 5 | Verify the interface status using `iw dev` on the Controller (checking the 6G radio's secondary interface, e.g., wifi2.1). | `iw dev` output shows the 6G radio's secondary interface up and broadcasting SSID "EasyMesh_6G_Secondary". |

---


# Test Case 96: EM_Secondary6GSSID_EnabledOnCreation_ClientVerification
## Objective
Verify that immediately after the SSID "EasyMesh_6G_Secondary" is created and enabled on the 6 GHz radio on the Controller, a Wi-Fi Client (STA) can discover it via scan and successfully connect without delay.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (managing the relevant Wi-Fi configuration referenced in the corresponding Controller-side test case) |
| Client (STA) | Wi-Fi client/station capable of scanning and associating to the Controller-managed BSS (e.g., `iw`, `wpa_cli`, or OS Wi-Fi utility available) |
---
## Pre-Requisites
1. The Controller-side configuration change described in Test Case 48 ("EM_Secondary6GSSID_EnabledOnCreation_ControllerVerification") has already been applied and verified via rbuscli.
2. Client (STA) device is available, within Wi-Fi range of the Controller, and capable of scanning/connecting to the relevant BSS.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Radio Band | 6 GHz |
| Secondary SSID (SSID-B, New) | EasyMesh_6G_Secondary |
| Verification Methods | rbuscli set/get, iw dev |
| Network Topology | Controller managing 6G radio secondary SSID (SSID-B) configuration |
| Client Device | Wi-Fi test client/STA (e.g., laptop, mobile device, or Wi-Fi test tool) |
---
## Test Procedure and Expected Results
| Step Number | Client | Expected Result |
|-------------|--------|-----------------|
| 1 | On the Client (STA), perform a Wi-Fi scan immediately after the SSID is created on the Controller. | The newly created SSID "EasyMesh_6G_Secondary" is visible in Client scan results without delay, confirming it is broadcasting immediately upon creation. |
| 2 | Connect the Client to the newly created SSID "EasyMesh_6G_Secondary" and verify connectivity using `iw dev <client-if> link` and a DHCP/ping check. | Client associates successfully to SSID "EasyMesh_6G_Secondary" and obtains IP connectivity, confirming the SSID is enabled and fully operational immediately upon creation. |
---

# Test Case 97: EM_BackhaulSSID_Change_ControllerVerification
## Objective
Verify that when the Backhaul (BH) SSID is changed via the Controller GUI to "BH-2G-Mesh", the updated SSID is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible, rbuscli and iw dev available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Backhaul SSID configuration.
3. DataElements object is accessible through rbuscli on the Controller.
4. Backhaul BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul SSID (Old) | EasyMesh_BH_ssid |
| Backhaul SSID (New) | BH-2G-Mesh |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Backhaul BSS configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Login to Controller GUI and navigate to Wi-Fi / Backhaul SSID configuration page. | GUI page loads successfully showing current Backhaul SSID "EasyMesh_BH_ssid". |
| 2 | Change Backhaul SSID field to "BH-2G-Mesh" and click Apply/Save. | SSID change is accepted and applied successfully via GUI, with a success confirmation message shown. |
| 3 | Verify updated SSID using `rbuscli get Device.WiFi.DataElements.Network.SSID.{i}.SSID` | rbuscli returns the updated SSID "BH-2G-Mesh" for the corresponding Backhaul BSS instance. |
| 4 | Verify updated SSID at interface level using `iw dev <interface> info` | `iw dev` output shows the Backhaul interface (e.g., wl1/ath1) broadcasting SSID "BH-2G-Mesh". |

---


# Test Case 98: EM_BackhaulSSID_UniqueBSSID_ControllerVerification
  ## Objective
  Verify that when a new Backhaul (BH) SSID is created on the Controller via the GUI, a unique BSSID is assigned to it, and this is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
  ## Test Type
  **Positive**
  ---
  ## Test Environment
  | Component | Description |
  |-----------|-------------|
  | Controller | EasyMesh Controller (GUI accessible, rbuscli and iw dev available) |
  ---
  ## Pre-Requisites
  1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
  2. Controller GUI is accessible and allows Backhaul SSID configuration.
  3. DataElements object is accessible through rbuscli on the Controller.
  4. Backhaul BSS/radio interface is operational and visible via `iw dev` on the Controller.
  5. Existing Fronthaul and other BSS BSSIDs on the Controller are noted beforehand for uniqueness comparison.
  ---
  ## Test Configuration
  | Parameter | Value |
  |-----------|-------|
  | Backhaul SSID (New) | EasyMesh_BH_ssid |
  | Verification Methods | rbuscli DataElements get, iw dev |
  | Network Topology | Controller GUI managing Backhaul BSS configuration |
  ---
  ## Test Procedure and Expected Results
  | Step Number | Controller | Expected Result |
  |-------------|------------|-----------------|
  | 1 | Login to Controller GUI and navigate to Wi-Fi / Backhaul SSID configuration page. | GUI page loads successfully showing the Backhaul SSID configuration section. |
  | 2 | Enter "EasyMesh_BH_ssid" in the Backhaul SSID field and click Apply/Save to create the BH SSID. | BH SSID creation is accepted and applied successfully via GUI, with a success confirmation message shown, and a BSSID is auto-assigned to the new BH BSS. |
  | 3 | Verify the assigned BSSID using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.BSSID`  | rbuscli returns the newly created SSID "EasyMesh_BH_ssid" along with a valid, non-null BSSID value that is distinct from the BSSIDs of other existing BSS instances . |
  | 4 | Verify the assigned BSSID at interface level using `iw dev <interface> info` on the Controller. | `iw dev` output shows the Backhaul interface broadcasting SSID "EasyMesh_BH_ssid" with an "addr" (BSSID) field matching the BSSID retrieved via rbuscli, and different from the BSSID of other interfaces . |

---


# Test Case 99: EM_BackhaulSSID_EnabledOnCreation_ControllerVerification
## Objective
Verify that when a new Backhaul (BH) SSID is created on the Controller via the GUI, it is enabled immediately after creation, and this is correctly reflected in the Controller's DataElements data model (via rbuscli) and confirmed at the wireless interface level (via iw dev) on the Controller.
## Test Type
**Positive**
---
## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller (GUI accessible, rbuscli and iw dev available) |
---
## Pre-Requisites
1. Controller is onboarded and EasyMesh/IEEE 1905 services are running.
2. Controller GUI is accessible and allows Backhaul SSID configuration.
3. DataElements object is accessible through rbuscli on the Controller.
4. Backhaul BSS/radio interface is operational and visible via `iw dev` on the Controller.
---
## Test Configuration
| Parameter | Value |
|-----------|-------|
| Backhaul SSID (New) | EasyMesh_BH_ssid |
| Verification Methods | rbuscli DataElements get, iw dev |
| Network Topology | Controller GUI managing Backhaul BSS configuration |
---
## Test Procedure and Expected Results
| Step Number | Controller | Expected Result |
|-------------|------------|-----------------|
| 1 | Login to Controller GUI and navigate to Wi-Fi / Backhaul SSID configuration page. | GUI page loads successfully showing the Backhaul SSID configuration section. |
| 2 | Enter "EasyMesh_BH_ssid" in the Backhaul SSID field and click Apply/Save to create the BH SSID. | BH SSID creation is accepted and applied successfully via GUI, with a success confirmation message shown. |
| 3 | Immediately verify the SSID using `rbuscli get Device.WiFi.DataElements.Network.SSID.{i}.SSID` | rbuscli returns the newly created SSID "EasyMesh_BH_ssid" . |
| 4 | Immediately verify the interface status using `iw dev <interface> info` on the Controller. | `iw dev` output shows the Backhaul interface up and broadcasting SSID "EasyMesh_BH_ssid" without delay. |

---

