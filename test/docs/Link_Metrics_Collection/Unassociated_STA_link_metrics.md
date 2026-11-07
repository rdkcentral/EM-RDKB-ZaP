# Test Case 1: EasyMesh_UnassociatedSTALinkMetrics_RCPIReporting

## Objective

Verify that the Multi-AP Agent reports uplink RCPI measurements for unassociated STAs through Unassociated STA Link Metrics Response messages.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Unassociated STA | Wi-Fi Client not associated with any BSS operated by the Agent |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. An unassociated STA is present and detectable by the Agent.
4. DataElements objects are accessible through rbuscli.
5. Controller or test tool supports generation of Unassociated STA Link Metrics Query messages.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Unassociated STA Link Metrics Query, 1905 Ack, Unassociated STA Link Metrics Response |
| Network Topology | Controller, Extender and Unassociated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.UnassociatedSTA.* |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|-------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Send an Unassociated STA Link Metrics Query containing one or more unassociated STA MAC addresses. | Receive Unassociated STA Link Metrics Query. | Query is received successfully by the Extender. |
| 3 | N/A | Send 1905 Ack and perform RCPI measurements for the specified STA(s). | 1905 Ack is transmitted and measurement process is initiated. |
| 4 | Read Unassociated STA DataElements using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.UnassociatedSTA.*`. | N/A | MAC address and SignalStrength DataElements are populated for the detected STA(s). |
| 5 | N/A | Send Unassociated STA Link Metrics Response. | Unassociated STA Link Metrics Response is transmitted successfully. |
| 6 | Send 1905 Ack for the response. | N/A | Response acknowledgement is transmitted successfully. |
| 7 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 8 | Verify the captured IEEE 1905 packets and response contents. | N/A | Unassociated STA Link Metrics Query, 1905 Ack, Response and final 1905 Ack are present in the capture. |
| 9 | Correlate response values with DataElements parameters. | N/A | MAC Address, Signal Strength (RCPI), Operating Class and Channel information reported in the Unassociated STA Link Metrics Response are consistent with the corresponding Unassociated STA DataElements values.|

---

# Test Case 2: EasyMesh_UnassociatedSTALinkMetrics_AssociatedSTAErrorHandling

## Objective

Verify that the Multi-AP Agent reports the appropriate error information when an Unassociated STA Link Metrics Query contains a STA that is already associated with a BSS operated by the Agent.

## Test Type

**Negative**

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

1. Controller and Agent are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. At least one STA is associated with a BSS operated by the Extender.
4. Controller or test tool supports generation of Unassociated STA Link Metrics Query messages.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Unassociated STA Link Metrics Query, 1905 Ack |
| IEEE 1905 TLVs Validated | Error Code TLV |
| Error Condition | Queried STA is associated with a BSS operated by the Agent |
| Network Topology | Controller, Extender and Associated STA |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Send an Unassociated STA Link Metrics Query containing the MAC address of a STA currently associated with the Extender. | Receive Unassociated STA Link Metrics Query. | Query is received successfully by the Extender. |
| 3 | N/A | Process the query and transmit a 1905 Ack. | 1905 Ack is transmitted successfully and includes an Error Code TLV with Reason Code set to `0x01` for the associated STA. |
| 4 | N/A | Send an Unassociated STA Link Metrics Response, if applicable. | Unassociated STA Link Metrics Response is transmitted only if valid measurements are available for other unassociated STAs included in the query. |
| 5 | Send a 1905 Ack for the response, if received. | N/A | Response acknowledgement is transmitted successfully. |
| 6 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 7 | Verify the captured IEEE 1905 packets. | N/A | Unassociated STA Link Metrics Query and corresponding 1905 Ack containing the Error Code TLV are observed. Unassociated STA Link Metrics Response and final 1905 Ack may be present if measurements were performed for other valid unassociated STAs. |
| 8 | Verify the Error Code TLV in the 1905 Ack message. | N/A | Error Code TLV is present in the 1905 Ack message with Reason Code set to `0x01` and includes the MAC address of the associated STA specified in the query. |

---

# Test Case 3: EasyMesh_UnassociatedSTALinkMetrics_NoMeasurementAvailable

## Objective

Verify that the Multi-AP Agent reports an Unassociated STA Link Metrics Response with zero STA entries when RCPI measurements cannot be obtained for any of the requested unassociated STAs.

## Test Type

**Negative**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Unassociated STA | STA not detectable by the Extender |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. DataElements objects are accessible through rbuscli.
4. Controller or test tool supports generation of Unassociated STA Link Metrics Query messages.
5. The queried STA MAC address is not detectable by the Agent.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Unassociated STA Link Metrics Query, 1905 Ack, Unassociated STA Link Metrics Response |
| Network Topology | Controller and Extender |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Send an Unassociated STA Link Metrics Query containing one or more undetectable STA MAC addresses. | Receive Unassociated STA Link Metrics Query. | Query is received successfully by the Extender. |
| 3 | N/A | Send 1905 Ack and attempt RCPI measurements. | 1905 Ack is transmitted successfully. |
| 4 | N/A | Complete the measurement attempt. | No RCPI measurements are obtained for the requested STA(s). |
| 5 | N/A | Send an Unassociated STA Link Metrics Response. | Response is transmitted successfully. |
| 6 | Send 1905 Ack for the response. | N/A | Response acknowledgement is transmitted successfully. |
| 7 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 8 | Verify the captured IEEE 1905 packets. | N/A | Query, 1905 Ack, Response and final 1905 Ack are present in the capture. |
| 9 | Verify the values in the Unassociated STA Link Metrics Response. | N/A | Number of STAs Included is set to `0` and no matching Unassociated STA entry is present for the queried STA(s). |

---

# Test Case 4: EasyMesh_UnassociatedSTALinkMetrics_OffChannelMeasurement

## Objective

Verify that the Multi-AP Agent performs RCPI measurements on the channels and operating classes specified in the query when Off-Channel Unassociated STA Link Metrics capability is supported.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Wi-Fi Client | Unassociated STA operating on a different channel |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. Agent advertises support for Off-Channel Unassociated STA Link Metrics capability in the AP Capability TLV.
4. An unassociated STA is operating on the requested channel.
5. DataElements objects are accessible through rbuscli.
6. Controller or test tool supports generation of Unassociated STA Link Metrics Query messages.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Unassociated STA Link Metrics Query, 1905 Ack, Unassociated STA Link Metrics Response |
| Network Topology | Controller, Agent and Unassociated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.UnassociatedSTA.* |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | Read the current radio operating channel. | Extender radio operating channel is identified and IEEE 1905 traffic capture begins successfully. |
| 2 | Send an Unassociated STA Link Metrics Query containing the STA MAC address, operating class and channel information corresponding to a channel different from the Extender's current operating channel. | Receive Unassociated STA Link Metrics Query. | Query is received successfully by the Extender. |
| 3 | N/A | Send 1905 Ack and perform RCPI measurements on the requested channel. | 1905 Ack is transmitted successfully and off-channel measurement is initiated. |
| 4 | N/A | Collect RCPI measurements and send an Unassociated STA Link Metrics Response. | Response is transmitted successfully. |
| 5 | Send 1905 Ack for the response. | N/A | Response acknowledgement is transmitted successfully. |
| 6 | Read Unassociated STA DataElements using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.UnassociatedSTA.*`. | Verify off-channel STA information. | Unassociated STA DataElements contain MACAddress, OperatingClass, Channel and SignalStrength information for the detected STA. |
| 7 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 8 | Verify the captured IEEE 1905 packets. | N/A | Unassociated STA Link Metrics Query, 1905 Ack, Unassociated STA Link Metrics Response and final 1905 Ack are present in the capture. |
| 9 | Verify off-channel measurement behavior. | N/A | The Operating Class and Channel specified in the query differ from the Extender radio operating channel, confirming off-channel measurement operation. |
| 10 | Verify the Unassociated STA Link Metrics Response values. | N/A | The queried STA is present in the UnassociatedSTA DataElements table. OperatingClass and Channel reflect where the STA was last detected, and the SignalStrength (RCPI) reported in the response is consistent with the corresponding DataElements value. |

---

> **Notes:** This test case is applicable only when the Agent advertises support for the Off-Channel Unassociated STA Link Metrics capability. If the capability is not advertised in the AP Capability TLV, the test case should be marked **Not Applicable (N/A)**.

---

# Test Case 5: EasyMesh_UnassociatedSTALinkMetrics_AckTiming

## Objective

Verify that the Multi-AP Agent and Controller acknowledge Unassociated STA Link Metrics messages within one second.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Unassociated STA | Wi-Fi Client not associated with any BSS operated by the Agent |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded successfully.
2. EasyMesh and IEEE 1905 services are running.
3. Agent advertises support for Unassociated STA Link Metrics in the AP Capability TLV.
4. At least one unassociated STA is present and detectable by the Agent.
5. Controller or test tool supports generation of Unassociated STA Link Metrics Query messages.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Unassociated STA Link Metrics Query, 1905 Ack, Unassociated STA Link Metrics Response |
| Timing Requirement | Acknowledgement within 1 second |
| Network Topology | Controller, Extender and Unassociated STA |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Send an Unassociated STA Link Metrics Query. | Receive the Unassociated STA Link Metrics Query. | Query is received successfully by the Extender. |
| 3 | Receive the 1905 Ack. | Send a 1905 Ack for the Unassociated STA Link Metrics Query. | 1905 Ack is transmitted successfully. |
| 4 | Receive the Unassociated STA Link Metrics Response. | Perform RCPI measurements and transmit an Unassociated STA Link Metrics Response. | Unassociated STA Link Metrics Response is transmitted successfully. |
| 5 | Send a 1905 Ack for the Unassociated STA Link Metrics Response. | Receive the 1905 Ack. | Response acknowledgement is transmitted successfully. |
| 6 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 7 | Verify the captured IEEE 1905 packets. | N/A | Unassociated STA Link Metrics Query, corresponding 1905 Ack, Unassociated STA Link Metrics Response, and corresponding 1905 Ack are observed in the capture. |
| 8 | Verify message exchange timing. | N/A | The time interval between the Unassociated STA Link Metrics Query and the corresponding 1905 Ack is less than 1 second, and the time interval between the Unassociated STA Link Metrics Response and the corresponding 1905 Ack is less than 1 second. |

---