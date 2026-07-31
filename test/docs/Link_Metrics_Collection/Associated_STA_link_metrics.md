# Test Case 1: EasyMesh_AssociatedSTALinkMetrics

## Objective

Verify that the Multi-AP Agent reports per-STA link metrics in Associated STA Link Metrics Response messages and that the reported metrics are consistent with the corresponding STA metrics.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Wi-Fi Client | Associated STA |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. At least one STA is associated with the Extender.
4. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Associated STA Link Metrics Query, Associated STA Link Metrics Response |
| IEEE 1905 TLVs Validated | Associated STA Link Metrics TLV, Associated STA Extended Link Metrics TLV |
| Network Topology | Controller, Extender and Associated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.STA.{i}.* |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Ensure a STA is associated with the Extender BSS. | Associate a STA with the Extender BSS. | STA is successfully associated with the Extender and corresponding STA DataElements parameters are populated. |
| 3 | Send an Associated STA Link Metrics Query for the associated STA. | Respond to the Associated STA Link Metrics Query. | Controller sends an Associated STA Link Metrics Query and the Extender responds with an Associated STA Link Metrics Response. |
| 4 | Read STA DataElements parameters using: `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.STA.{i}.*` | Verify that the STA remains associated. | Per-STA DataElements parameters are populated for the associated STA. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Associated STA Link Metrics Response contains valid Associated STA Link Metrics TLV and Associated STA Extended Link Metrics TLV for the associated STA. |
| 7 | Correlate TLV values with corresponding DataElements parameters. | N/A | `SignalStrength`, `EstMACDataRateUplink`, `EstMACDataRateDownlink`, `LastDataUplinkRate`, `LastDataDownlinkRate`, `UtilizationTransmit`, and `UtilizationReceive` reported in the TLVs are consistent with the corresponding DataElements parameter values. |

---

# Test Case 2: EasyMesh_AssociatedSTALinkMetrics_UnassociatedSTA

## Objective

Verify that the Multi-AP Agent reports the appropriate error information when an Associated STA Link Metrics Query is received for a STA that is not associated with any BSS operated by the Agent.

## Test Type

**Negative**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. A non-associated STA MAC address is available for testing.
4. Controller or test tool supports generation of an Associated STA Link Metrics Query for a specified STA MAC address.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Associated STA Link Metrics Query, Associated STA Link Metrics Response |
| IEEE 1905 TLVs Validated | Associated STA Link Metrics TLV, Error Code TLV |
| Network Topology | Controller and Extender |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|-------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Send an Associated STA Link Metrics Query containing a non-associated STA MAC address. | Receive Associated STA Link Metrics Query. | Query is received successfully by the Agent. |
| 3 | N/A | Process the query and transmit an Associated STA Link Metrics Response. | Associated STA Link Metrics Response is generated for the queried STA MAC. |
| 4 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 5 | Verify the captured IEEE 1905 packets and response message. | N/A | Associated STA Link Metrics Response corresponding to the queried STA MAC address is present in the capture. |
| 6 | Verify the response contents and Error Code TLV. | N/A | Number of BSSIDs Reported is set to `0`. Error Code TLV is present with Reason Code set to `0x02` and contains the queried STA MAC address. |

> **Note:** This test case requires the ability to generate an Associated STA Link Metrics Query for a specific STA MAC address. Execution may require a test controller or protocol injection tool if the production controller does not support this functionality.

---

# Test Case 3: EasyMesh_AssociatedSTALinkMetrics_ClientMLDReporting

## Objective

Verify that the Multi-AP Agent reports Associated STA Link Metrics and Associated STA Extended Link Metrics for each Affiliated STA when the queried STA MAC belongs to a Client MLD and that the reported information is consistent with the corresponding STAMLD DataElements parameters.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Client MLD | Wi-Fi 7 Multi-Link Device |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. Wi-Fi 7 MLO functionality is enabled.
4. A Client MLD is associated with the Extender.
5. At least two Affiliated STAs belonging to the Client MLD are active.
6. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Associated STA Link Metrics Query, Associated STA Link Metrics Response |
| IEEE 1905 TLVs Validated | Associated STA Link Metrics TLV, Associated STA Extended Link Metrics TLV |
| Network Topology | Controller, Extender and Client MLD |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMLD.{i}.STAMLD.* |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|-------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Send Associated STA Link Metrics Query containing the Client MLD MAC address. | Receive Associated STA Link Metrics Query. | Query referencing the Client MLD is observed. |
| 3 | N/A | Process the query and transmit an Associated STA Link Metrics Response. | Associated STA Link Metrics Response is generated for the Client MLD. |
| 4 | Read Client MLD DataElements using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMLD.{i}.STAMLD.*`. | N/A | Client MLD and Affiliated STA DataElements are populated. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Associated STA Link Metrics Response contains Associated STA Link Metrics TLVs and Associated STA Extended Link Metrics TLVs for each Affiliated STA of the Client MLD. |
| 7 | Correlate TLV values with Client MLD DataElements. | N/A | Affiliated STA MAC addresses, SignalStrength, UtilizationTransmit and UtilizationReceive reported in the TLVs are consistent with the corresponding STAMLD DataElements parameters. |
| 8 | Verify Affiliated STA reporting. | N/A | Metrics are reported separately for each Affiliated STA associated with the queried Client MLD and the number of reported affiliated STAs matches AffiliatedSTANumberOfEntries. |

---