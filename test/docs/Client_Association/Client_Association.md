# EasyMesh Client Association Test Plan — Topology: 1 Controller + 3 Agents

# Test Case 1: EM_ClientAssociation_DiscoverEasyMeshSSID

## Objective
Verify that a Wi-Fi client device can discover and see the EasyMesh SSID broadcast by the mesh network (Controller and all 3 Agent devices).

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned and enabled on Controller, and propagated to all 3 Agents.
3. Client device powered on and Wi-Fi scanning operational.
4. rbuscli accessible on Controller for DataElements queries.

---

## Test Configuration
| Parameter | Value | 
|-----------|-------|
| SSID Name | EasyMesh-MESH | 
| Security Type | WPA2-Personal / WPA3-Personal | 
| Bands Enabled | 2.4 GHz, 5 GHz, 6 GHz (if supported) | 

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Retrieve and store device index into database for controller and agents | N/A | Returns index value |
| 2 | Query SSID via rbuscli: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.SSID` | N/A | Returns: `SSID = EasyMesh-MESH` |
| 3 | N/A | Wait 10 seconds for SSID propagation | Mesh nodes synchronized; beacons transmitted by Controller and all 3 Agents |
| 4 | N/A | Initiate WiFi scan: `nmcli -f SSID,FREQ dev wifi list --rescan yes | grep -i {ssid}`  and Count SSID occurrences across bands | Scan command executes successfully and Count >= 1 per band |
---

# Test Case 2: EM_ClientAssociation_DiscoverSSIDon2.4GHz

## Objective
Verify that a Wi-Fi client device can specifically discover and see the EasyMesh SSID on the 2.4 GHz band, broadcast by the Controller and all 3 Agents.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent ||
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher with 2.4 GHz support |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned and enabled on Controller, and propagated to all 3 Agents.
3. 2.4 GHz radio enabled on Controller and all 3 Agents.
4. Client device powered on and Wi-Fi scanning operational.
5. rbuscli accessible on Controller for DataElements queries.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Band | 2.4 GHz |
| Security Type | WPA2-Personal / WPA3-Personal |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|----------------- |
| 1 | N/A | Verfiy Client Generation | Wifi-4 or wifi-5 or wifi-6 |
| 2 | Retrieve and store device index ,radio indexes and BSS indexs into database for controller and agents | N/A | Returns index value |
| 3 | Verify 2.4 GHz Radio enabled on Controller and 3Agents: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.Enabled` | N/A | Returns: `Enabled = true` |
| 4 | Querry operating channel, operating class and operating bandwidth 'iw dev mld0 info`| N/A | Returns channel,bandwidth and class |
| 5 | Query SSID on 2.4 GHz Radio/BSS (Controller + 3 Agents): `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.SSID` | N/A | Returns: `SSID = EasyMesh-MESH` on all 4 devices |
| 6 | N/A | Wait 5 seconds for SSID propagation | Mesh nodes synchronized; beacons transmitted on 2.4 GHz by Controller and all 3 Agents |
| 7 | N/A | Initiate WiFi scan limited to 2.4 GHz Count SSID occurrences on 2.4 GHz : `nmcli -f SSID,FREQ dev wifi list --rescan yes  grep -i {ssid}` | Scan command executes successfully  and Count >= 1 (up to 4 APs visible: Controller + 3 Agents, if all in range)  |


---

# Test Case 3: EM_ClientAssociation_DiscoverSSIDon5GHz

## Objective
Verify that a Wi-Fi client device can specifically discover and see the EasyMesh SSID on the 5 GHz band, broadcast by the Controller and all 3 Agents.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11ac or higher with 5 GHz support |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned and enabled on Controller, and propagated to all 3 Agents.
3. 5 GHz radio enabled on Controller and all 3 Agents.
4. Client device powered on and Wi-Fi scanning operational.
5. rbuscli accessible on Controller for DataElements queries.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Band | 5 GHz |
| Security Type | WPA2-Personal / WPA3-Personal |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|----------------- |
| 1 | N/A | Verfiy Client Generation | Wifi-4 or wifi-5 or wifi-6 |
| 2 | Retrieve and store device index ,radio indexes and BSS indexs into database for controller and agents | N/A | Returns index value |
| 3 | Verify 5 GHz Radio enabled on Controller and 3Agents: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.Enabled` | N/A | Returns: `Enabled = true` |
| 4 | Querry operating channel, operating class and operating bandwidth 'iw dev mld0 info`| N/A | Returns channel,bandwidth and class |
| 5 | Query SSID on 5 GHz Radio/BSS (Controller + 3 Agents): `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.SSID` | N/A | Returns: `SSID = EasyMesh-MESH` on all 4 devices |
| 6 | N/A | Wait 5 seconds for SSID propagation | Mesh nodes synchronized; beacons transmitted on 5 GHz by Controller and all 3 Agents |
| 7 | N/A | Initiate WiFi scan limited to 5 GHz Count SSID occurrences on 5 GHz : `nmcli -f SSID,FREQ dev wifi list --rescan yes | grep -i {ssid}` | Scan command executes successfully  and Count >= 1 (up to 4 APs visible: Controller + 3 Agents, if all in range)  |

---

# Test Case 4: EM_ClientAssociation_DiscoverSSIDon6GHz

## Objective
Verify that a Wi-Fi client device can specifically discover and see the EasyMesh SSID on the 6 GHz band (if supported), broadcast by the Controller and all 3 Agents.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with 6 GHz support (Wi-Fi 6E capable) |
| Agent 1 | EasyMesh Agent with 6 GHz support (Wi-Fi 6E capable) |
| Agent 2 | EasyMesh Agent with 6 GHz support (Wi-Fi 6E capable) |
| Agent 3 | EasyMesh Agent with 6 GHz support (Wi-Fi 6E capable) |
| Client (DUT) | Wi-Fi STA capable of 802.11ax (Wi-Fi 6E) with 6 GHz support |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned and enabled on Controller, and propagated to all 3 Agents.
3. 6 GHz radio enabled on Controller and all 3 Agents.
4. Client device powered on and Wi-Fi 6E scanning operational.
5. rbuscli accessible on Controller for DataElements queries.
6. Regulatory domain configured to allow 6 GHz operation on Controller and all 3 Agents.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Band | 6 GHz |
| Security Type | WPA2-Personal / WPA3-Personal |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|----------------- |
| 1 | N/A | Verfiy Client Generation | Wifi-4 or wifi-5 or wifi-6 |
| 2 | Retrieve and store device index ,radio indexes and BSS indexs into database for controller and agents | N/A | Returns index value |
| 3 | Verify 6 GHz Radio enabled on Controller and 3Agents: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.Enabled` | N/A | Returns: `Enabled = true` |
| 4 | Querry operating channel, operating class and operating bandwidth 'iw dev mld0 info`| N/A | Returns channel,bandwidth and class |
| 5 | Query SSID on 6 GHz Radio/BSS (Controller + 3 Agents): `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.SSID` | N/A | Returns: `SSID = EasyMesh-MESH` on all 4 devices |
| 6 | N/A | Wait 5 seconds for SSID propagation | Mesh nodes synchronized; beacons transmitted on 6 GHz by Controller and all 3 Agents |
| 7 | N/A | Initiate WiFi scan limited to 6 GHz Count SSID occurrences on 6 GHz : `nmcli -f SSID,FREQ dev wifi list --rescan yes | grep -i {ssid}` | Scan command executes successfully  and Count >= 1 (up to 4 APs visible: Controller + 3 Agents, if all in range)  |

---


# Test Case 5: EM_ClientAssociation_AuthenticationCorrectCredentials

## Objective
Verify that  Wi-Fi client devices can successfully authenticate and associate to the EasyMesh SSID using correct WPA2/WPA3-Personal credentials, whether it associates to the Controller or to any of the 3 Agents.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. Correct passphrase configured on Controller and propagated to all 3 Agents.
4. Client device powered on and Wi-Fi scanning operational.
5. rbuscli accessible on Controller for DataElements queries.


---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal (`psk`) or WPA3-Personal (`sae`) |
| Passphrase | correctpassphrase123 |
| Authentication Method | 4-Way Handshake (WPA2) or Simultaneous Authentication of Equals (WPA3) |

---

## Test Procedure and Expected Results

| Step | Controller | Client | Expected Result |
|------|-----------|--------|------------------|
| 1 | Retrieve and store device index into database for controller and agents | N/A | Returns index value |
| 2 | Query SSID AKM configuration: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.AKMsAllowed` | N/A | Returns `AKMsAllowed = psk` (WPA2-Personal) or `sae` (WPA3-Personal) |
| 3 | Query PMF configuration: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.MFPConfig` | N/A | Returns `MFPConfig = Disabled/Optional/Required` — consistent with the security type (WPA3/SAE typically requires PMF; WPA2/psk may be Disabled or Optional) |
| 4 | Query Security Key passphrase from GUI | N/A | Returns: Passphrase |
| 5 | N/A | Wait 10 seconds for SSID propogation | SSID beacon stable on client side |
| 6 | N/A | Initiate association to EasyMesh-MESH with correct passphrase: `nmcli device wifi connect EasyMesh-MESH password correctpassphrase123 bssid {bssid}` | Association request sent to the specific AP (Controller or one of the 3 Agents) |
| 7 | N/A | Verify association status on client: `iw dev <wlan_iface> link` | Output shows: `Connected to [MAC] (on wlan iface)` `SSID: EasyMesh-MESH` `freq: [frequency]` |
| 8 |  N/A | Verify negotiated security on client: `wpa_cli -i <wlan_iface> status | grep 'key_mgmt' ` and compare with device security | Output shows security matches in client and device |
| 9 | N/A | Test connectivity (optional): `ping -c 3 8.8.8.8` | Ping successful (if gateway configured) or DHCP IP obtained |

---
# Test Case 6: EM_ClientAssociation_AuthenticationFailIncorrectCredentials

## Objective
Verify that a Wi-Fi client device fails to authenticate and associate to the EasyMesh SSID when using incorrect WPA2/WPA3-Personal credentials, against the Controller or any of the 3 Agents.

## Test Type
**Negative**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. Correct passphrase configured on Controller and propagated to all 3 Agents.
4. Client device powered on and Wi-Fi scanning operational.
5. rbuscli accessible on Controller for DataElements queries.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal (`psk`) or WPA3-Personal (`sae`)  |
| Correct Passphrase | correctpassphrase123 |
| Incorrect Passphrase | wrongpassphrase999 |
| Authentication Method | 4-Way Handshake (WPA2) or Simultaneous Authentication of Equals (WPA3) |
| Cipher Suite | CCMP (AES) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Query SSID AKM configuration: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.AKMsAllowed` | N/A | Returns `AKMsAllowed = psk` (WPA2-Personal) or `sae` (WPA3-Personal) |
| 1b | Query PMF configuration: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.MFPConfig` | N/A | Returns `MFPConfig = Disabled/Optional/Required` — consistent with the security type (WPA3/SAE typically requires PMF; WPA2/psk may be Disabled or Optional) |
| 2 | N/A | Wait 2 seconds for network stability | SSID beacon stable on client side |
| 3 | N/A | Initiate association to EasyMesh-MESH with incorrect passphrase: `nmcli device wifi connect EasyMesh-MESH password wrongpassphrase999` | Association request sent to nearest/strongest AP (Controller or one of the 3 Agents) |
| 4 | N/A | Verify association fails on client: `iw dev <wlan_iface> link` | Output shows: `Not connected` or connection error message |
| 5 | N/A | Verify connection info shows failure: `nmcli device show <wlan_iface>` | grep -E `"SSID|STATE|CONNECTION"`  Output contains: `STATE: disconnected` or `Connection refused` |
| 6 | N/A | Check system logs for authentication failure: `journalctl -u wpa_supplicant -n 5` | grep -i `"authentication|handshake|failed"`  Logs show authentication failure message (e.g., `WPA: 4-Way Handshake failed`)` |
| 7 | Query associated client count before attempt for Controller and each of the 3 Agents: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Records initial counts for all 4 devices |
| 8 | Query associated client count after failed attempt for Controller and each of the 3 Agents: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Counts remain unchanged on all 4 devices (client not added anywhere) |
| 9 | N/A | Query client MAC address: `ip link show <wlan_iface>` | grep `"link/ether"` | Returns client MAC (e.g., `aa:bb:cc:dd:ee:ff`) |
| 10 | Query Controller and each of the 3 Agents for connected client MAC: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STA.{l}.MACAddress` | N/A | None of the 5 lists contain the client MAC address |
| 11 | N/A | Verify no connectivity to network: `ping -c 1 8.8.8.8` | Ping fails with no route or timeout (no network access) |
| 12 | N/A | Attempt WiFi scan after failed authentication: `iw dev <wlan_iface> scan` | grep `"SSID: EasyMesh-MESH"`  SSID still visible in scan results (from Controller and/or any of the 3 Agents) |
| 13 | Confirm client authentication was rejected by whichever Controller/Agent it attempted | Confirm EasyMesh-MESH disconnected state maintained | Controller/Agents and Client operations successful (failure verified) |

---

# Test Case 7: EM_ClientAssociation_4WayHandshakeSuccess

## Objective
Verify that a Wi-Fi client device successfully completes the 4-Way Handshake with the EasyMesh AP (Controller or any of the 3 Agents) when authenticating with correct WPA2-Personal credentials.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher with WPA2 support |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal security, consistent across Controller and all 3 Agents.
3. Correct passphrase configured on Controller and propagated to all 3 Agents.
4. Client device powered on and Wi-Fi scanning operational.
5. rbuscli accessible on Controller for DataElements queries.
6. wpa_supplicant or similar WPA2 client available on DUT.
7. Note: `Device.N` below refers to whichever Controller/Agent (Device.1-Device.4) the client actually associates to.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal |
| Passphrase | correctpassphrase123 |
| Handshake Type | 4-Way Handshake (M1, M2, M3, M4) |
| Cipher Suite | CCMP (AES) |
| Group Cipher | CCMP |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Query SSID AKM configuration: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.AKMsAllowed` | N/A | Returns `AKMsAllowed = psk` (WPA2-Personal) or `sae` (WPA3-Personal) |
| 1b | Query PMF configuration: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.MFPConfig` | N/A | Returns `MFPConfig = Disabled/Optional/Required` — consistent with the security type (WPA3/SAE typically requires PMF; WPA2/psk may be Disabled or Optional) |
| 2 | N/A | Enable WPA supplicant logging (optional): `wpa_cli -i <wlan_iface> log_level DEBUG` | Logging enabled for detailed handshake info |
| 3 | N/A | Initiate association to EasyMesh-MESH with correct passphrase: `nmcli device wifi connect EasyMesh-MESH password correctpassphrase123` | Association request sent to nearest/strongest AP (Controller or one of the 3 Agents) |
| 4 | N/A | Monitor for handshake completion: `wpa_cli -i <wlan_iface> status` | Output shows: `wpa_state=COMPLETED` |
| 5 | N/A | Verify 4-Way Handshake M1 received: `journalctl -u wpa_supplicant -n 10` | grep -i `"eapol.*key"`  Logs show EAPOL Key frame M1 message received |
| 6 | N/A | Verify M2 sent from client: `journalctl -u wpa_supplicant -n 10` | grep -i `"sending.*eapol"`  Logs show EAPOL Key frame M2 message sent |
| 7 | N/A | Verify M3 received: `journalctl -u wpa_supplicant -n 10` | grep -i `"installing.*keys"`  Logs show M3 received and key installation initiated |
| 8 | N/A | Verify M4 sent (final handshake frame): `wpa_cli -i <wlan_iface> status` | grep -i `"key_mgmt"`  Output shows: `key_mgmt=WPA2-PSK` |
| 9 | N/A | Verify pairwise key installed: `wpa_cli -i <wlan_iface> get_capability pairwise` | Output shows: `CCMP` (or supported cipher) |
| 10 | N/A | Verify group key installed: `wpa_cli -i <wlan_iface> get_capability group` | Output shows: `CCMP` (or supported cipher) |
| 11 | N/A | Verify final connection state: `iw dev <wlan_iface> link` | Output shows: `Connected to [MAC] (on <wlan_iface>)` `SSID: EasyMesh-MESH` |
| 12 | Query the associated Controller/Agent (Device.N) for associated client: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Count includes this client (count >= 1) on the Controller or Agent it attached to |
| 13 | N/A | Query client authentication info: `iw dev <wlan_iface> link` | grep -i `"auth|security"`  Output shows authentication type: `WPA2-PSK` and key management active |
| 14 | N/A | Test data connectivity: `ping -c 3 8.8.8.8` | Ping successful or responds (if gateway available) |
| 15 | Confirm handshake logs on the associated Controller/Agent (Device.N, if available): `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STA.{l}.MACAddress` | N/A | Client MAC present in associated devices list |
| 16 | Confirm 4-Way Handshake completed successfully | Confirm connection stable with keys installed | Controller/Agent and Client operations successful |

---
# Test Case 8: EM_ClientAssociation_DHCPIPAssignment

## Objective
Verify that  Wi-Fi client devices receives a valid IP address via DHCP after successful authentication and association to the EasyMesh SSID, regardless of whether it associates to the Controller or one of the 3 Agents.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with DHCP server enabled |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state with DHCP enabled |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. DHCP server running and operational on Controller (or backhaul network), reachable via all 3 Agents.
4. Client device powered on and Wi-Fi scanning operational.
5. rbuscli accessible on Controller for DataElements queries.
6. DHCP client (dhclient) available on client device.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Passphrase | correctpassphrase123 |
| DHCP Pool | <-DHCP_MIN_Addr-> - <-DHCP_MAX_Addr-> |
| Gateway IP | <-Gateway-IP-> |
| DNS Server | 8.8.8.8 (or Controller IP) |
| Lease Time | 3600 seconds (default) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Retrieve and store device index into database for controller and agents | N/A | Returns index value |
| 2 | Verify DHCP server is enabled: `rbuscli getv Device.DHCPv4.Server.Enable` | N/A | Returns: `Enable = true` |
| 3 | Query DHCP server pool configuration: `rbuscli getv Device.DHCPv4.Server.Pool.{i}.MinAddress` | N/A | Returns: `MinAddress = <DHCP_MIN_Addr>` |
| 4 | Query DHCP pool end: `rbuscli getv Device.DHCPv4.Server.Pool.{i}.MaxAddress` | N/A | Returns: `MaxAddress = <DHCP_MIN_Addr>` |
| 5 | Retrieve SSID from Data Elements `rbuscli getv Device.WiFi.DataElements.SSID.{i}.SSID` | N/A | Returns SSID | 
| 6 |  N/A | Associate to EasyMesh-MESH with correct passphrase: `nmcli device wifi connect EasyMesh-MESH password correctpassphrase123 bssid {bssid}` | Association successful, to Controller or one of the 3 Agents |
| 7 |  N/A | Wait 10 seconds for association completion | Client authenticated and associated to AP |
| 8 | N/A | Verify association status: `iw dev <wlan_iface> link` | Output shows: `Connected to [MAC] (on <wlan_iface>)` `SSID: EasyMesh-MESH` |
| 9 | N/A | Trigger DHCP request (if not automatic): `dhclient -v <wlan_iface>` | DHCP discovery, offer, request, acknowledge sequence initiated (through the associated Agent's backhaul to the Controller's DHCP server, if applicable) |
| 10 | N/A | Verify IP address assigned: `/sbin/ifconfig {interface}` | grep `"inet "` Output shows: `inet <IP-Addr> brd <DHCP_MAX_Addr> scope global <wlan_iface>` (IP in DHCP pool range) |
| 11 | N/A | Verify IP is within DHCP pool range | Output shows IP between <DHCP_MIN_Addr> and <DHCP_MAX_Addr> (valid pool allocation) |

---

# Test Case 9: EM_ClientAssociation_GatewayReachability

## Objective
Verify that  Wi-Fi client devices can successfully ping and reach the gateway after receiving a valid IP address via DHCP and associating to the EasyMesh SSID, whether attached to the Controller or one of the 3 Agents.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with DHCP server and gateway functionality enabled |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Agent 4 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state with DHCP and routing enabled |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. Client successfully associated (to Controller or any of the 3 Agents) and received valid DHCP IP address (from TC-008).
4. Gateway IP is reachable and configured on Controller, and routed through the backhaul to all 3 Agents.
5. rbuscli accessible on Controller for DataElements queries.
6. ping utility available on client device.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Client IP Range | `<DHCP_MIN_Addr> - <DHCP_MAX_Addr>` |
| Gateway IP | `<Gateway-IP>` |
| Ping Packet Count | 5 |
| Ping Timeout | 5 seconds per packet |


---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Retrieve and store device index into database for controller and agents | N/A | Returns index value |
| 2 | Verify gateway interface is up: `rbuscli getv Device.IP.Interface.{i}.Enable` | N/A | Returns: `Enable = true` |
| 3 | Query gateway IP address: `rbuscli getv Device.IP.Interface.{i}.IPv4Address.{j}.IPAddress` and compare with controller gateway IP address | N/A | Returns: `IPAddress = <Gateway-IP>` (or configured gateway IP) |
| 4 | N/A | Verify client IP address assigned: `/sbin/ifconfig {interface}` | grep `"inet "` Output shows: `inet <IP-Addr> ` |
| 5 | N/A | Verify default route configured: `ip route show` | grep `"default"` Output shows: `default via <Gateway-IP> dev <wlan_iface>` |
| 6 | N/A | Ping gateway (3 packets): `ping -c 3 <Gateway-IP>` and verify connectivity | All 3 packets transmitted and received successfully (regardless of whether traffic backhauls through an Agent) |
| 7 | Query gateway for connected clients: `rbuscli getv Device.DHCPv4.Server.Pool.1.ClientNumberOfEntries` | N/A | Count >= 1 (client counted in active pool regardless of which Agent it is attached to) |

---

# Test Case 10: EM_ClientAssociation_TrafficFlow_TCP_Upstream

## Objective
Verify that selected Wi-Fi client devices can successfully transmit data traffic (upstream) over the EasyMesh network after authentication, association, and IP address assignment, whether attached to the Controller or one of the 3 Agents.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with DHCP and routing enabled |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state with internet connectivity |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. rbuscli accessible on Controller for DataElements queries.
4. iperf3 (or equivalent traffic tool) available on client and Controller.
5. External server (8.8.8.8 or similar) reachable for connectivity tests.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Client IP | `<IP_Addr>` (from DHCP pool) |
| Gateway IP | `<Gateway-IP>` |
| Test Duration | 10 seconds per traffic test |
| Packet Size | 1024 bytes (default for iperf3) |
| Traffic Type | TCP |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Get enabled clients and randomly select one controller client and one extender client| N/A | Count >= 1 (client associated to Controller or one of the 3 Agents) |
| 2 | N/A | Connect selected clients to `Easymesh SSID` and verify association status| Client gets connected to `Easymesh SSID` |
| 3 | N/A | Verify client IP assigned: `ip addr show <wlan_iface>` | grep `"inet "` Output shows valid IP in `<IP_Addr>` range |
| 4 | N/A | Test upstream TCP traffic (10 second test): `iperf3 -c <Gateway-IP> -t 10 -J` | TCP connection established, data transmitted successfully (traffic backhauled through the Agent if not directly attached to Controller) |
| 6 | N/A | check for Sender Bitrate, Receiver bitrate and retransmission rate| Output shows: the required data |

---

# Test Case 11: EM_ClientAssociation_TrafficFlow_TCP_Downstream

## Objective
Verify that the Controller can successfully transmit TCP data traffic (downstream) to selected Wi-Fi client devices over the EasyMesh network after authentication, association, and IP address assignment, whether the clients are attached directly to the Controller or through an Agent.

## Test Type
**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with DHCP and routing enabled |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state with network connectivity |

---

## Pre-Requisites

1. Controller and all 3 Agents (Agent 1–Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across the Controller and all 3 Agents.
3. `rbuscli` accessible on the Controller for DataElements queries.
4. `iperf3` available on the Controller and selected Wi-Fi clients.
5. Selected Wi-Fi clients are capable of establishing TCP connections with the Controller.
6. Controller bridge IP address is configured and reachable from the connected clients.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Client IP | `<IP_Addr>` (from DHCP pool) |
| Controller Server IP | `<Controller-Bridge-IP>` |
| Test Duration | 10 seconds per traffic test |
| Packet Size | 1024 bytes (iperf3 default) |
| Traffic Type | TCP |
| Traffic Direction | Downstream (Controller → Client) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Get enabled clients and randomly select one Controller client and one Extender client. | N/A | At least one Controller client and one Extender client are available for testing. |
| 2 | Retrieve the EasyMesh SSID and fronthaul password from the Controller. | Connect selected clients to the EasyMesh SSID and verify association status. | Selected clients successfully connect and associate with the EasyMesh SSID. |
| 3 | N/A | Verify client IP address using `ip addr show <wlan_iface>`. | Each selected client receives a valid IP address from the DHCP pool. |
| 4 | Retrieve the Controller bridge IP address and start the TCP iperf3 server on the Controller using `iperf3 -s -B <Controller-Bridge-IP>`. | N/A | TCP iperf3 server starts successfully and listens on the Controller bridge IP address. |
| 5 | Keep the TCP iperf3 server running. | Initiate TCP downstream traffic using `iperf3 -c <Controller-Bridge-IP> -t 10 -R -J`. | TCP connection is established and data is successfully received by the client from the Controller. Traffic is backhauled through the Agent when the client is connected to an Agent. |
| 6 | Stop the iperf3 server after traffic generation completes. | Retrieve and inspect the iperf3 client log. | Log contains `iperf Done` and indicates successful completion of the downstream traffic test. |
| 7 | N/A | Verify TCP sender bitrate, receiver bitrate, and retransmission count from the iperf3 output. | Sender bitrate and receiver bitrate are reported, and TCP retransmission information is available in the iperf3 output. |
| 8 | N/A | Verify the overall TCP downstream traffic result for each selected client. | TCP downstream traffic is successfully verified for all selected clients. |

---

# Test Case 12: EM_ClientAssociation_TrafficFlow_UDP_Upstream

## Objective
Verify that selected Wi-Fi client devices can successfully transmit UDP data traffic (upstream) to the Controller over the EasyMesh network after authentication, association, and IP address assignment, whether attached directly to the Controller or through Agent 1.

## Test Type
**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with DHCP and routing enabled |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state with network connectivity |

---

## Pre-Requisites

1. Controller and all 3 Agents (Agent 1–Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across the Controller and all 3 Agents.
3. `rbuscli` accessible on the Controller for DataElements queries.
4. `iperf3` available on the Controller and selected Wi-Fi clients.
5. Selected Wi-Fi clients are capable of establishing UDP traffic with the Controller.
6. Controller bridge IP address is configured and reachable from the connected clients.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Client IP | `<IP_Addr>` (from DHCP pool) |
| Controller Server IP | `<Controller-Bridge-IP>` |
| Test Duration | 10 seconds per traffic test |
| Packet Size | Default iperf3 UDP packet size |
| Traffic Type | UDP |
| Traffic Direction | Upstream (Client → Controller) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Get enabled clients and randomly select one Controller client and one Extender client. | N/A | At least one Controller client and one Extender client are available for testing. |
| 2 | Retrieve the EasyMesh SSID and fronthaul password from the Controller. | Connect selected clients to the EasyMesh SSID and verify association status. | Selected clients successfully connect and associate with the EasyMesh SSID. |
| 3 | N/A | Verify client IP address using `ip addr show <wlan_iface>`. | Each selected client receives a valid IP address from the DHCP pool. |
| 4 | Retrieve the Controller bridge IP address and start the UDP iperf3 server using `iperf3 -s -B <Controller-Bridge-IP>`. | N/A | UDP iperf3 server starts successfully on the Controller. |
| 5 | Keep the UDP iperf3 server running. | Initiate UDP upstream traffic using `iperf3 -c <Controller-Bridge-IP> -u -t 10`. | UDP traffic is successfully transmitted from the client to the Controller. Traffic is backhauled through the Agent when the client is connected to an Agent. |
| 6 | Stop the iperf3 server after traffic generation completes. | Retrieve and inspect the iperf3 client log. | Log contains `iperf Done.` indicating successful completion of the UDP traffic test. |
| 7 | N/A | Verify UDP sender bitrate from the iperf3 output. | UDP sender bitrate is successfully reported. |
| 8 | N/A | Verify UDP receiver bitrate, jitter, lost datagrams, total datagrams, and packet loss percentage. | UDP receiver statistics are successfully reported, including bitrate, jitter, and packet loss information. |
| 9 | N/A | Verify the overall UDP upstream traffic result for each selected client. | UDP upstream traffic flow is successfully verified for all selected clients. |

---
# Test Case 13: EM_ClientAssociation_TrafficFlow_UDP_Downstream

## Objective
Verify that the Controller can successfully transmit UDP data traffic (downstream) to selected Wi-Fi client devices over the EasyMesh network after authentication, association, and IP address assignment, whether attached directly to the Controller or through Agent 1.

## Test Type
**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with DHCP and routing enabled |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state with network connectivity |

---

## Pre-Requisites

1. Controller and all 3 Agents (Agent 1–Agent 3) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across the Controller and all 3 Agents.
3. `rbuscli` accessible on the Controller for DataElements queries.
4. `iperf3` available on the Controller and selected Wi-Fi clients.
5. Selected Wi-Fi clients are capable of receiving UDP traffic from the Controller.
6. Controller bridge IP address is configured and reachable from the connected clients.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Client IP | `<IP_Addr>` (from DHCP pool) |
| Controller Server IP | `<Controller-Bridge-IP>` |
| Test Duration | 10 seconds per traffic test |
| Packet Size | Default iperf3 UDP packet size |
| Traffic Type | UDP |
| Traffic Direction | Downstream (Controller → Client) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Get enabled clients and randomly select one Controller client and one Extender client. | N/A | At least one Controller client and one Extender client are available for testing. |
| 2 | Retrieve the EasyMesh SSID and fronthaul password from the Controller. | Connect selected clients to the EasyMesh SSID and verify association status. | Selected clients successfully connect and associate with the EasyMesh SSID. |
| 3 | N/A | Verify client IP address using `ip addr show <wlan_iface>`. | Each selected client receives a valid IP address from the DHCP pool. |
| 4 | Retrieve the Controller bridge IP address and start the UDP iperf3 server using `iperf3 -s -B <Controller-Bridge-IP>`. | N/A | UDP iperf3 server starts successfully on the Controller. |
| 5 | Keep the UDP iperf3 server running. | Initiate UDP downstream traffic using `iperf3 -c <Controller-Bridge-IP> -u -t 10 -R`. | UDP traffic is successfully transmitted from the Controller to the client. Traffic is backhauled through the Agent when the client is connected to an Agent. |
| 6 | Stop the iperf3 server after traffic generation completes. | Retrieve and inspect the iperf3 client log. | Log contains `iperf Done` indicating successful completion of the UDP downstream traffic test. |
| 7 | N/A | Verify UDP sender bitrate and sender packet loss from the iperf3 output. | UDP sender bitrate and packet loss statistics are successfully reported. |
| 8 | N/A | Verify UDP receiver bitrate, jitter, lost datagrams, total datagrams, and packet loss percentage. | UDP receiver statistics are successfully reported, including bitrate, jitter, and packet loss information. |
| 9 | N/A | Verify the overall UDP downstream traffic result for each selected client. | UDP downstream traffic flow is successfully verified for all selected clients. |

---

# Test Case 14: EM_ClientAssociation_SuccessRateRepeatedCycles

## Objective
Verify that a Wi-Fi client device maintains a high association success rate (> 99%) when undergoing repeated connect/disconnect cycles to the EasyMesh SSID over an extended period, across a mesh of 1 Controller and 3 Agents.

## Test Type
**Positive / Stress / Reliability**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller with DHCP and routing enabled |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Agent 4 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 4) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. Client device powered on and Wi-Fi scanning operational.
4. rbuscli accessible on Controller for DataElements queries.
5. Automated connection/disconnection script available on client.
6. Test duration: minimum 100 cycles.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Passphrase | correctpassphrase123 |
| Total Cycles | 100 minimum |
| Cycle Time | Connect (30 sec) + Disconnect (5 sec) = 35 sec per cycle |
| Expected Success Rate | > 99% (maximum 1 failure per 100 cycles) |
| Test Duration | ~58 minutes |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Verify SSID is enabled: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.SSID` | N/A | Returns: `SSID = EasyMesh-MESH` |
| 2 | N/A | Initialize cycle counter (cycles=0, failures=0) | Test tracking initialized |
| 3 | N/A | Execute automated script: `for i in {1..100}; do nmcli device wifi connect EasyMesh-MESH password correctpassphrase123; sleep 30; nmcli device disconnect <wlan_iface>; sleep 5; done` | 100 connect/disconnect cycles execute (client may roam to any of the Controller or 3 Agents based on signal strength) |
| 4 | N/A | Monitor connection status during each cycle: `iw dev <wlan_iface> link` | Each cycle: Connected -> Disconnected -> Connected |
| 5 | N/A | Log connection failures and the associated AP (Controller/Agent 1-4) for each cycle: timestamp, error message, retry status | Failures tracked and logged per AP |
| 6 | N/A | Calculate success rate: `(100 - failures) / 100 x 100` | Success Rate = (100 - failures) / 100 x 100 |
| 7 | N/A | Verify success rate meets requirement: `if Success_Rate >= 99.0; then PASS; else FAIL; fi` | Success Rate >= 99.0% |
| 8 | Verify Controller and all 3 Agents remained operational: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.Status` | N/A | Status = Operational on all 5 devices (no errors/degradation) |
| 9 | N/A | Verify no system crashes: `dmesg` | grep -i `"error crash segfault"`  Kernel logs show no critical errors |
| 10 | Confirm association success rate > 99% across the Controller and 3 Agents | Confirm no unexpected disconnections | Test PASSED if success rate >= 99% |

---
# Test Case 15: EM_ClientAssociation_AssociationTimeThreshold

## Objective
Verify that a Wi-Fi client device associates to the EasyMesh SSID within an acceptable time threshold after initiating connection request, regardless of whether it associates to the Controller or one of the 3 Agents.

## Test Type
**Positive / Performance**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Agent 4 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 4) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. Client device powered on and Wi-Fi scanning operational.
4. rbuscli accessible on Controller for DataElements queries.
5. Timer utility available on client device.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Passphrase | correctpassphrase123 |
| Max Association Time | 10 seconds (scan to fully associated with IP) |
| Auth Handshake Time | 2-3 seconds |
| DHCP Assignment Time | 3-5 seconds |
| Test Iterations | 10 association attempts |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Verify SSID is enabled: `rbuscli getv Device.WiFi.DataElements.Network.SSID.{i}.SSID` | N/A | Returns: `SSID = EasyMesh-MESH` |
| 2 | N/A | Start timer and initiate connection: `time nmcli device wifi connect EasyMesh-MESH password correctpassphrase123` | Connection attempt begins with timestamp recorded |
| 3 | N/A | Monitor association status: `iw dev <wlan_iface> link` | Output shows transition from disconnected -> connected, and which BSSID (Controller or Agent 1-4) it connected to |
| 4 | N/A | Wait for DHCP IP assignment: `ip addr show <wlan_iface>` | Client receives IP address within acceptable time |
| 5 | N/A | Stop timer and record total association time and the AP associated to | Association time and associated AP (Controller/Agent 1-4) logged |
| 6 | N/A | Verify association time <= 10 seconds: `if association_time <= 10; then PASS; else FAIL; fi` | Association time <= 10 seconds, on whichever AP was selected |
| 7 | N/A | Disconnect and repeat steps 2-6 for 10 total iterations | All 10 association attempts complete (may associate to different Agents/Controller across iterations) |
| 8 | N/A | Calculate average association time: `sum(all_times) / 10` | Average time recorded |
| 9 | N/A | Calculate max association time: `max(all_times)` | Maximum time recorded |
| 10 | N/A | Verify all 10 attempts met threshold: `if all_times <= 10; then PASS; else FAIL; fi` | All 10 iterations <= 10 seconds |
| 11 | Query Controller and each of the 3 Agents for association count: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Counts reflect successful associations on whichever device(s) the client attached to |
| 12 | Confirm average time acceptable | Confirm max time < 10 seconds on all iterations | Test PASSED if all iterations <= 10 seconds |

---

# Test Case 16: EM_ClientAssociation_ControllerDataElementsVisibility

## Objective
Verify that a Wi-Fi client device appears in the Controller's Data Elements connected-client list after successful authentication and association to the EasyMesh SSID, whether it is physically attached to the Controller or to one of the 3 Agents.

## Test Type
**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Agent 4 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 4) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. Client device powered on and Wi-Fi scanning operational.
4. rbuscli accessible on Controller for DataElements queries.
5. Note: `Device.N` below refers to whichever Controller/Agent (Device.1-Device.5) the client actually associates to.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Passphrase | correctpassphrase123 |
| Radio | Radio.1 (2.4 GHz) or Radio.2 (5 GHz) |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Query associated client count before association, for Controller and all 3 Agents: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Returns initial counts (typically 0 on all 5 devices if no clients connected) |
| 2 | N/A | Associate to EasyMesh-MESH: `nmcli device wifi connect EasyMesh-MESH password correctpassphrase123` | Association successful, to Controller or one of the 3 Agents |
| 3 | N/A | Verify client is connected and identify the BSSID: `iw dev <wlan_iface> link` | grep `"Connected"`  Output shows: `Connected to [MAC]` — map the BSSID to Controller/Agent 1-4 |
| 4 | N/A | Query client MAC address: `ip link show <wlan_iface>` | grep `"link/ether"`  Returns client MAC (e.g., aa:bb:cc:dd:ee:ff) |
| 5 | Query associated client count after association on the identified Device.N: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Count on Device.N increased by 1 (client now listed); other 4 devices remain unchanged |
| 6 | Query connected clients list on Device.N: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.AssociatedDevicesList` | N/A | Returns list containing client MAC address |
| 7 | Verify client MAC in list: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STA.{l}.MACAddress | grep "aa:bb:cc:dd:ee:ff"` | N/A | Client MAC found in associated devices list |
| 8 | Verify client IP in DHCP pool (served centrally by Controller): `rbuscli getv Device.DHCPv4.Server.Pool.{i}.Client.{j}.IPAddress` | N/A | Returns IP address matching client's assigned IP |
| 9 | Verify client MAC in DHCP client list: `rbuscli getv Device.DHCPv4.Server.Pool.{i}.Client.{j}.Chaddr` | N/A | Returns client MAC address |
| 10 | Confirm client visible in all relevant Data Elements on the associated Controller/Agent | Confirm client MAC, IP visible | Test PASSED if client appears in all queries |

---

# Test Case 17: EM_ClientAssociation_ReassociationAfterDisconnection

## Objective
Verify that a Wi-Fi client device automatically re-associates to the EasyMesh SSID after disconnection (power off/WiFi toggle) without requiring manual reconfiguration of credentials, potentially reassociating to a different Agent or the Controller than before.

## Test Type
**Positive / Reliability**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Agent 4 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 4) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. Client device already associated and connected to EasyMesh-MESH (from previous test case), on the Controller or one of the 3 Agents.
4. rbuscli accessible on Controller for DataElements queries.
5. The client was attached to before and after the reassociation, respectively — these may differ.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Passphrase | correctpassphrase123 (stored on client from previous connection) |
| Disconnection Method | WiFi toggle or power cycle |
| Re-association Wait Time | 30 seconds |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Query associated client count before disconnection on Device.N(old): `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Count >= 1 (client currently associated) |
| 2 | N/A | Verify client is currently connected: `iw dev <wlan_iface> link` | grep `"Connected"`  Output shows: `Connected to [MAC]` |
| 3 | N/A | Disconnect from network: `nmcli device disconnect <wlan_iface>` or disable WiFi radio | Disconnection initiated |
| 4 | N/A | Verify disconnection: `iw dev <wlan_iface> link` | grep `"Not connected"`  Output shows: `Not connected` |
| 5 | Query associated client count after disconnection on Device.N(old): `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Count decreased by 1 (client removed from list) |
| 6 | N/A | Re-enable WiFi or power on device: `nmcli radio wifi on` | WiFi re-enabled |
| 7 | N/A | Wait 5 seconds for WiFi to stabilize | WiFi radio initialized |
| 8 | N/A | Trigger automatic re-association (client should auto-connect): `nmcli device wifi connect EasyMesh-MESH` (without password if stored) or auto-connect enabled | Client initiates re-association automatically |
| 9 | N/A | Verify re-association successful and identify Device.N(new): `iw dev <wlan_iface> link` | grep `"Connected"`  Output shows: `Connected to [MAC]` (may be a different Controller/Agent BSSID than before, i.e. Device.N(new) != Device.N(old), in a multi-AP mesh) |
| 10 | N/A | Wait for DHCP IP assignment: `ip addr show <wlan_iface>` | grep `"inet "`  Client receives new IP address |
| 11 | Query associated client count after re-association on Device.N(new): `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Count increased back to original on Device.N(new) (client re-joined, possibly via a different Agent) |
| 12 | Query connected clients list on Device.N(new): `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STA.{l}.MACAddress` | N/A | Client MAC present in list again |
| 13 | N/A | Verify connectivity after re-association: `ping -c 3 <gateway-IP>` | Ping successful to gateway |
| 14 | Confirm client re-associated (to Controller or any of the 3 Agents) without manual credential entry | Confirm automatic association and IP assignment | Test PASSED if client re-associated without manual configuration |

---

# Test Case 18: EM_ClientAssociation_DisassociationHandling

## Objective
Verify that client disassociation is handled cleanly - client is properly removed from the topology and connected-client list on the Controller and on whichever of the 3 Agents it was attached to, after disconnection.

## Test Type
**Positive / Reliability**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Agent 1 | EasyMesh Agent |
| Agent 2 | EasyMesh Agent |
| Agent 3 | EasyMesh Agent |
| Agent 4 | EasyMesh Agent |
| Client (DUT) | Wi-Fi STA capable of 802.11n/802.11ac or higher |
| Network Setup | Mesh topology with 1 Controller + 3 Agents in operational state |

---

## Pre-Requisites
1. Controller and all 3 Agents (Agent 1-Agent 4) initialized and synchronized via IEEE 1905.1 topology.
2. EasyMesh SSID provisioned with WPA2-Personal or WPA3-Personal security, consistent across Controller and all 3 Agents.
3. Client device already associated to EasyMesh-MESH SSID, on the Controller or one of the 3 Agents.
4. rbuscli accessible on Controller for DataElements queries.
5. Note: `Device.N` below refers to whichever Controller/Agent (Device.1-Device.5) the client is attached to.

---

## Test Configuration
| Parameter | Value |
|-----------|-------|
| SSID Name | EasyMesh-MESH |
| Security Type | WPA2-Personal or WPA3-Personal |
| Disassociation Method | WiFi toggle, power off, or explicit disconnect |

---

## Test Procedure and Expected Results

| Step Number | Controller | Client | Expected Result |
|-------------|-----------|--------|-----------------|
| 1 | Query associated client count before disassociation on Device.N: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Returns count including client (count >= 1) |
| 2 | Query connected clients list before disassociation on Device.N: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STA.{l}.MACAddress` | N/A | Client MAC present in list |
| 3 | N/A | Query client MAC: `ip link show <wlan_iface>` | grep `"link/ether"` Returns client MAC (e.g., aa:bb:cc:dd:ee:ff) |
| 4 | N/A | Initiate disassociation: `nmcli device disconnect <wlan_iface>` or toggle WiFi off | Disconnection initiated |
| 5 | N/A | Verify client disconnected: `iw dev <wlan_iface> link` | grep `"Not connected"`  Output shows: `Not connected` |
| 6 | Query associated client count after disassociation on Device.N: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STANumberOfEntries` | N/A | Count decreased by 1 on Device.N (client removed) |
| 7 | Query connected clients list after disassociation on Device.N: `rbuscli getv Device.WiFi.DataElements.Network.Device.{i}.Radio.{j}.BSS.{k}.STA.{l}.MACAddress` | N/A | Client MAC NOT in list (removed cleanly) |
| 8 | Query DHCP client list on Controller: `rbuscli getv Device.DHCPv4.Server.Pool.{i}.ClientNumberOfEntries` | N/A | Client count decreased (DHCP lease released) |
| 9 | Verify client MAC not in DHCP clients: `rbuscli getv Device.DHCPv4.Server.Pool.{i}.Client.{j}.Chaddr` | N/A | Client MAC not found in active DHCP clients |
| 10 | Verify no lingering errors in Controller and Agent 1-4 logs: `dmesg | grep -i "error|deauth" | tail -5` | N/A | Disassociation logged cleanly on Device.N, no anomalies on the Controller or the other 3 Agents |
| 11 | Confirm client removed from all relevant Data Elements on the Controller and the associated Agent | Confirm no stale entries in connected-client list | Test PASSED if client cleanly removed from topology |

---