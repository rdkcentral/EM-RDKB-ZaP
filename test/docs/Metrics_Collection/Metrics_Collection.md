# Test Case 1: EM_AssociatedSTALinkMetrics

## Objective

Verify that the Multi-AP Agent reports per-STA link metrics in Associated STA Link Metrics Response messages and that the reported metrics are consistent with the corresponding STA metrics.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Associated STA Link Metrics Query, Associated STA Link Metrics Response |
| IEEE 1905 TLVs Validated | Associated STA Link Metrics TLV, Associated STA Extended Link Metrics TLV |
| Network Topology | Controller, 3 Extenders and Associated STAs |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.STA.{i}.* |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Ensure a STA is associated with the Extender BSS by checking DataElements (Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.STA.{i}.*). | Associate a STA with the Extender BSS. | STA is successfully associated with the Extender and corresponding STA DataElements parameters are populated. |
| 3 | Send an Associated STA Link Metrics Query for the associated STA. | Receive the Associated STA Link Metrics Query. | Associated STA Link Metrics Query is transmitted by the Controller and received by the Extender. |
| 4 | N/A | Send an Associated STA Link Metrics Response for the queried STA. | Extender transmits an Associated STA Link Metrics Response for the queried STA. |
| 5 | Read STA DataElements parameters using: `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.STA.{i}.*` | Verify that the STA remains associated. | Per-STA DataElements parameters are populated for the associated STA. |
| 6 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 7 | Verify the captured IEEE 1905 packets. | N/A | Associated STA Link Metrics Response contains valid Associated STA Link Metrics TLV and Associated STA Extended Link Metrics TLV for the associated STA. |
| 8 | Correlate TLV values with corresponding DataElements parameters. | N/A | `SignalStrength`, `EstMACDataRateUplink`, `EstMACDataRateDownlink`, `LastDataUplinkRate`, `LastDataDownlinkRate`, `UtilizationTransmit`, and `UtilizationReceive` reported in the TLVs are consistent with the corresponding DataElements parameter values. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 2: EM_AssociatedSTALinkMetrics_ClientMLDReporting

## Objective

Verify that the Multi-AP Agent reports Associated STA Link Metrics and Associated STA Extended Link Metrics for each Affiliated STA when the queried STA MAC belongs to a Client MLD and that the reported information is consistent with the corresponding STAMLD DataElements parameters.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Wi-Fi Client | 1 Client MLD associated with the selected Extender |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. Client MLD is associated with the selected Extender and visible in topology.
5. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Associated STA Link Metrics Query, Associated STA Link Metrics Response |
| IEEE 1905 TLVs Validated | Associated STA Link Metrics TLV, Associated STA Extended Link Metrics TLV |
| Network Topology | Controller, 3 Extenders and Client MLD |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMLD.{i}.STAMLD.* |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|-------|-----------------|
| 1 | Start IEEE 1905 packet capture. | Ensure Client MLD is connected to the selected Extender and verify association. | IEEE 1905 traffic capture begins successfully and Client MLD association is confirmed. |
| 2 | Send Associated STA Link Metrics Query containing the Client MLD MAC address. | Receive Associated STA Link Metrics Query. | Query referencing the Client MLD is observed. |
| 3 | N/A | Process the query and transmit an Associated STA Link Metrics Response. | Associated STA Link Metrics Response is generated for the Client MLD. |
| 4 | Read Client MLD DataElements using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMLD.{i}.STAMLD.*`. | N/A | Client MLD and Affiliated STA DataElements are populated. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Associated STA Link Metrics Response contains Associated STA Link Metrics TLVs and Associated STA Extended Link Metrics TLVs for each Affiliated STA of the Client MLD. |
| 7 | Correlate TLV values with Client MLD DataElements. | N/A | Affiliated STA MAC addresses, SignalStrength, UtilizationTransmit and UtilizationReceive reported in the TLVs are consistent with the corresponding STAMLD DataElements parameters. |
| 8 | Verify Affiliated STA reporting. | N/A | Metrics are reported separately for each Affiliated STA associated with the queried Client MLD and the number of reported affiliated STAs matches AffiliatedSTANumberOfEntries. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 3: EM_UnassociatedSTALinkMetrics_RCPIReporting

## Objective

Verify that the Multi-AP Agent reports uplink RCPI measurements for unassociated STAs through Unassociated STA Link Metrics Response messages.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Unassociated STA Link Metrics Query, 1905 Ack, Unassociated STA Link Metrics Response |
| Network Topology | Controller, 3 Extenders and Unassociated STAs |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.UnassociatedSTA.* |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
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

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 4: EM_STARCPIThresholdBasedReporting

## Objective

Verify that an unsolicited IEEE 1905 AP Metrics Response is transmitted when the associated STA RCPI crosses the configured RCPI Reporting Threshold.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| APMetricsReportingInterval | 300 |
| STA RCPI Reporting Threshold | 100 (Example) |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response, Associated STA Link Metrics TLV |
| Network Topology | Controller, 3 Extenders and Associated STAs |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval <br> Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Extender-STA | Expected Result |
|-------------|------------|----------|--------------|-----------------|
| 1 | Configure AP Metrics Reporting Interval using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval 300` | N/A | N/A | AP Metrics Reporting Interval is configured successfully. |
| 2 | Configure STA RCPI Reporting Threshold using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold 100` | N/A | N/A | STA RCPI Reporting Threshold is configured successfully. |
| 3 | Verify AP Metrics Reporting Interval using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval` | N/A | N/A | APMetricsReportingInterval returns 300. |
| 4 | Verify STA RCPI Reporting Threshold using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold` | N/A | N/A | STAReportingRCPIThreshold returns 100. |
| 5 | Start IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 traffic capture begins successfully. |
| 6 | N/A | N/A | Move the STA farther from the Extender or introduce attenuation to reduce RCPI below the configured threshold. | STA RCPI crosses the configured threshold. |
| 7 | Continue IEEE 1905 packet capture after the threshold crossing event. | Transmit unsolicited AP Metrics Response. | N/A | An unsolicited AP Metrics Response is transmitted after the RCPI threshold is crossed. |
| 8 | Stop IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 packet capture is stopped. |
| 9 | Verify the captured IEEE 1905 packets. | N/A | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response is observed after the RCPI threshold crossing and before the next scheduled reporting interval. The AP Metrics Response contains the Associated STA Link Metrics TLV with valid link metric information for the associated STA. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 5: EM_STARCPIHysteresisBehavior

## Objective

Verify that STA Metrics reporting follows the configured RCPI Hysteresis Margin and prevents excessive reporting due to small RCPI fluctuations around the threshold.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| APMetricsReportingInterval | 300 |
| STA RCPI Threshold | 100 |
| STA RCPI Hysteresis Margin Override | 10 dB |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response, Associated STA Link Metrics TLV |
| Network Topology | Controller, 3 Extenders and Associated STAs |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval <br> Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold <br> Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIHysteresisMarginOverride |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Extender-STA | Expected Result |
|-------------|------------|----------|--------------|-----------------|
| 1 | Configure AP Metrics Reporting Interval using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval 300` | N/A | N/A | AP Metrics Reporting Interval is configured successfully. |
| 2 | Configure STA RCPI Threshold using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold 100` | N/A | N/A | STA RCPI Threshold is configured successfully. |
| 3 | Configure STA RCPI Hysteresis Margin Override using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIHysteresisMarginOverride 10` | N/A | N/A | STA RCPI Hysteresis Margin Override is configured successfully. |
| 4 | Verify AP Metrics Reporting Interval using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval` | N/A | N/A | APMetricsReportingInterval returns 300 on both Controller and Extender. |
| 5 | Verify STA RCPI Threshold using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold` | N/A | N/A | STAReportingRCPIThreshold returns the configured value on both Controller and Extender. |
| 6 | Verify STA RCPI Hysteresis Margin Override using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIHysteresisMarginOverride` | N/A | N/A | STAReportingRCPIHysteresisMarginOverride returns 10 on both Controller and Extender. |
| 7 | Start IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 traffic capture begins successfully. |
| 8 | N/A | N/A | Move the STA farther from the Extender or introduce attenuation until the RCPI threshold is crossed. | RCPI crosses the configured threshold. |
| 9 | Continue IEEE 1905 packet capture after the threshold crossing event. | Transmit unsolicited AP Metrics Response. | N/A | An unsolicited AP Metrics Response is transmitted after the RCPI threshold is crossed. |
| 10 | N/A | N/A | Slightly adjust STA position around the threshold causing RCPI fluctuations within the configured hysteresis margin. | RCPI fluctuations remain within the configured hysteresis margin. |
| 11 | N/A | N/A | Further adjust STA position so that RCPI changes beyond the configured hysteresis margin. | Hysteresis condition is satisfied. |
| 12 | Continue IEEE 1905 packet capture. | Transmit unsolicited AP Metrics Response. | N/A | An additional unsolicited AP Metrics Response is transmitted after the hysteresis margin is exceeded. |
| 13 | Stop IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 packet capture is stopped. |
| 14 | Verify the captured IEEE 1905 packets. | N/A | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Responses are generated only when RCPI changes exceed the configured hysteresis margin, while fluctuations within the hysteresis margin do not trigger additional reporting. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 6: EM_STARCPIThreshold_PerSTAIsolation

## Objective

Verify that when multiple STAs are associated on the same Radio, an RCPI threshold crossing by one STA triggers an unsolicited AP Metrics Response reporting only that STA, and the other associated STAs whose RCPI did not cross the threshold are not reported.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| APMetricsReportingInterval | 300 |
| STA RCPI Reporting Threshold | 100 (Example) |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response, Associated STA Link Metrics TLV |
| Network Topology | Controller, 3 Extenders and two or more Associated STAs |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval <br> Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Extender-STA | Expected Result |
|-------------|------------|----------|--------------|-----------------|
| 1 | Configure AP Metrics Reporting Interval using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval 300` | N/A | N/A | AP Metrics Reporting Interval is configured successfully. |
| 2 | Configure STA RCPI Reporting Threshold using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold 100` | N/A | N/A | STA RCPI Reporting Threshold is configured successfully. |
| 3 | Verify STA RCPI Reporting Threshold using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold` | N/A | N/A | STAReportingRCPIThreshold returns 100. |
| 4 | Start IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 traffic capture begins successfully. |
| 5 | N/A | N/A | Move only one STA (STA1) farther from the Extender or introduce attenuation on STA1 so its RCPI crosses the threshold, while keeping the other STA(s) stationary. | STA1 RCPI crosses the configured threshold; the other STA(s) RCPI remains unchanged. |
| 6 | Continue IEEE 1905 packet capture. | Transmit unsolicited AP Metrics Response. | N/A | An unsolicited AP Metrics Response is transmitted after STA1 crosses the threshold. |
| 7 | Stop IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 packet capture is stopped. |
| 8 | Verify the captured IEEE 1905 packets. | N/A | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. The unsolicited AP Metrics Response reports only STA1 (the STA that crossed the threshold), the other associated STA(s) are not included in the threshold-triggered response. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 7: EM_BackhaulLinkMetrics_PHYRateCorrelation

## Objective

Verify that the Backhaul PHY Rate reported through DataElements is consistent with the PHY Rate reported in the IEEE 1905 Transmitter Link Metric TLV for the active wireless backhaul link.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Link Metric Query, Link Metric Response |
| IEEE 1905 TLVs Validated | Transmitter Link Metric TLV, Receiver Link Metric TLV |
| Network Topology | Controller and 3 Extenders |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Wait for periodic IEEE 1905 Link Metric Query and Link Metric Response messages. | N/A | Periodic Link Metric Query and corresponding Link Metric Response messages are observed. |
| 3 | Read Backhaul PHY Rate using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate`. Verify backhaul STA statistics using `iw dev <backhaul_sta_interface> station dump`. | Verify backhaul connection and PHY rates using `iw dev <backhaul_interface> link`. | BackhaulPHYRate, RSSI and PHY rate information are available for the active wireless backhaul link. |
| 4 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 5 | Verify the captured IEEE 1905 packets. | N/A | Link Metric Query and corresponding Link Metric Response messages are present in the capture. Receiver Link Metric TLV contains valid RSSI information. Transmitter Link Metric TLV contains valid PHY Rate, MAC Throughput Capacity and Link Availability fields. |
| 6 | Correlate Link Metric TLV values with iw dev statistics output and `BackhaulPHYRate`. | N/A | PHY Rate and RSSI reported in the Link Metric TLVs are consistent with the observed backhaul statistics and `BackhaulPHYRate`. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 8: EM_BackhaulLinkMetrics_LinkQualityChange

## Objective

Verify that Backhaul Link Metrics and Backhaul PHY Rate are updated when wireless backhaul link quality changes.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Link Metric Query, Link Metric Response |
| IEEE 1905 TLVs Validated | Transmitter Link Metric TLV, Receiver Link Metric TLV |
| Network Topology | Controller and 3 Extenders |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Wait for periodic Link Metric Query and Link Metric Response messages. | N/A | Initial Link Metric Response is observed. |
| 3 | Read Backhaul PHY Rate using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate`. Verify backhaul STA statistics using `iw dev <backhaul_sta_interface> station dump`. | Verify backhaul connection and PHY rates using `iw dev <backhaul_interface> link`. | Initial RSSI, PHY Rate and BackhaulPHYRate values are recorded. |
| 4 | N/A | Introduce attenuation or move farther away from the Controller. | Wireless backhaul link quality decreases. |
| 5 | Continue IEEE 1905 packet capture and wait for subsequent Link Metric Response messages. | N/A | Updated Link Metric Response messages are observed. |
| 6 | Read Backhaul PHY Rate using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate`. Verify backhaul STA statistics using `iw dev <backhaul_sta_interface> station dump`. | Verify backhaul connection and PHY rates using `iw dev <backhaul_interface> link`. | Updated RSSI, PHY Rate and BackhaulPHYRate values are available. |
| 7 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 8 | Verify the captured IEEE 1905 packets, Link Metric TLVs and DataElements values. | N/A | Receiver Link Metric TLV RSSI, Transmitter Link Metric TLV PHY Rate, MAC Throughput Capacity and Link Availability reflect the changed wireless backhaul link conditions. BackhaulPHYRate is updated accordingly. |
| 9 | Correlate updated Link Metric TLV values with iw dev output statistics and `BackhaulPHYRate`. | N/A | Updated PHY Rate and RSSI values are consistent with the observed backhaul statistics and `BackhaulPHYRate`. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 9: EM_BackhaulLinkMetrics_MultiHopTopology

## Objective

Verify that Backhaul Link Metrics are reported correctly for each active backhaul hop in a multi-hop EasyMesh topology.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Daisy Chain |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Link Metric Query, Link Metric Response |
| IEEE 1905 TLVs Validated | Transmitter Link Metric TLV, Receiver Link Metric TLV |
| Network Topology | Daisy-chain topology with Controller and 3 Extenders connected in parent-child relationships. |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Wait for periodic IEEE 1905 Link Metric Query and Link Metric Response messages. | N/A | Link Metric Response messages are observed for active backhaul neighbors. |
| 3 | Read `Device.WiFi.DataElements.Network.Device.{i}.BackhaulPHYRate` using rbuscli. | N/A | BackhaulPHYRate values and active uplink information are available for all Extenders. |
| 4 | Verify backhaul statistics using `iw dev <backhaul_sta_interface> station dump`. | Verify backhaul statistics of each extender  using `iw dev <backhaul_interface> link`. | RSSI and PHY rate information are available for each active backhaul hop. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets and Link Metric TLVs. | N/A | Link Metric Responses contain valid Receiver and Transmitter Link Metrics for the active upstream backhaul neighbor. |
| 7 | Correlate Link Metric TLV values with `iw dev` statistics and `BackhaulPHYRate`. | N/A | RSSI, PHY Rate, MAC Throughput Capacity, Link Availability and BackhaulPHYRate are populated and consistent with the observed backhaul statistics for each backhaul hop. |

---

# Test Case 10: EM_BackhaulLinkMetrics_WiredBackhaul

## Objective

Verify that Backhaul Link Metrics are reported correctly for an active Ethernet backhaul link through IEEE 1905 Link Metric Response messages.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents (Wired backhaul) |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and all Extenders are onboarded with active Ethernet backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Link Metric Query, Link Metric Response |
| IEEE 1905 TLVs Validated | Transmitter Link Metric TLV, Receiver Link Metric TLV |
| Backhaul Type | Ethernet (Wired) |
| Network Topology | Controller and 3 Extenders (all active Ethernet backhaul links) |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.BackhaulMediaType |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders (3 Nos) | Expected Result |
|-------------|------------|-------------------|-----------------|
| 1 | Record baseline topology and Backhaul Media Type values from DataElements for all active backhaul links. | Start IEEE 1905 packet capture on each Extender. | Baseline topology is recorded with wired backhaul links and BackhaulMediaType values are available for all active links. |
| 2 | N/A | Verify wired backhaul interface state on each Extender. | Ethernet backhaul links are operational and used as the active backhaul connections for all Extenders. |
| 3 | Wait for two consecutive Link Metric Query and Link Metric Response exchanges for all Extenders. | N/A | Two valid Link Metric Response messages are observed for each active Ethernet backhaul neighbor. |
| 4 | N/A | Stop IEEE 1905 packet capture on each Extender. | Packet capture is stopped successfully after required exchanges are observed. |
| 5 | Verify the captured Link Metric Response (message type 0x0006) and Link Metric TLVs. | N/A | Transmitter Link Metric TLV (type 0x09) and Receiver Link Metric TLV (type 0x0A) contain valid metrics for each active Ethernet backhaul link and report the appropriate Ethernet Media Type. |
| 6 | Correlate neighbor identities and media type details from IEEE 1905 captures with topology and DataElements. | N/A | Link Metric TLVs map to all active Ethernet backhaul neighbors, report the correct Ethernet media type, and no wireless-only correlation is required. |

---

# Test Case 11: EM_APMetrics_RadioMetricsValidation

## Objective

Verify that the Multi-AP Agent includes a Radio Metrics TLV for each queried radio and that the reported values are consistent with the corresponding Radio DataElements.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | AP Metrics Query, AP Metrics Response |
| IEEE 1905 TLVs Validated | Radio Metrics TLV |
| Network Topology | Controller and 3 Extenders |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Noise <br> Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Transmit <br> Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ReceiveSelf <br> Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ReceiveOther |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | Send an AP Metrics Query identifying one or more radios. | Receive AP Metrics Query. | AP Metrics Query is received successfully. |
| 3 | N/A | Generate and transmit AP Metrics Response. | AP Metrics Response is transmitted successfully. |
| 4 | Read and record Radio DataElements using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Noise`, `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.Transmit`, `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ReceiveSelf`, and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ReceiveOther`. | N/A | Radio metric values are captured for correlation. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | One Radio Metrics TLV is present in the AP Metrics Response for each radio identified in the AP Metrics Query. |
| 7 | Correlate the reported Radio Metrics TLV values with the corresponding DataElements. | N/A | Noise, Transmit, ReceiveSelf, and ReceiveOther values reported in the Radio Metrics TLVs match the corresponding DataElements values. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 12: EM_APMetrics_QueryResponseReporting

## Objective

Verify that the Multi-AP Agent responds to an AP Metrics Query with an AP Metrics Response containing AP Metrics TLVs, AP Extended Metrics TLVs, and Affiliated AP Metrics TLVs using the same Message Identifier (MID) and containing valid reported metrics.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | AP Metrics Query, AP Metrics Response |
| IEEE 1905 TLVs Validated | AP Metrics TLV, AP Extended Metrics TLV, Affiliated AP Metrics TLV |
| Network Topology | Controller and 3 Extenders |
| DataElements (Root) | AP Metrics: Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.EstServiceParameters* <br> AP Extended Metrics: Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.*Bytes* <br> Affiliated AP Metrics: Device.WiFi.DataElements.Network.Device.{i}.APMLD.{i}.AffiliatedAP.{i}.* |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | Packet capture begins successfully. |
| 2 | Send AP Metrics Query. | Receive AP Metrics Query. | AP Metrics Query is received successfully. |
| 3 | N/A | Process AP Metrics Query and generate AP Metrics Response. | AP Metrics Response is generated successfully. |
| 4 | Read AP Metrics, AP Extended Metrics, and Affiliated AP Metrics root DataElements using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.EstServiceParameters*`, `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.*Bytes*`, and `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMLD.{i}.AffiliatedAP.{i}.*`. | N/A | Current metric values are available for comparison. |
| 5 | Stop packet capture. | N/A | Packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | AP Metrics Query and the corresponding AP Metrics Response are present in the capture. |
| 7 | Verify MID correlation. | N/A | AP Metrics Response MID matches the AP Metrics Query MID. |
| 8 | Verify AP Metrics TLVs and correlate the reported values with the corresponding DataElements. | N/A | AP Metrics TLVs are present for the queried BSSs. BSSID, Channel Utilization, Number of Associated STAs, and Estimated Service Parameters are populated with valid values and are consistent with the corresponding DataElements. |
| 9 | Verify AP Extended Metrics TLVs and correlate the reported counters with the corresponding DataElements. | N/A | AP Extended Metrics TLVs are present for the queried BSSs. Reported Unicast, Multicast, and Broadcast byte counters are consistent with the corresponding BSS DataElements values. |
| 10 | Verify Affiliated AP Metrics TLVs and correlate the reported counters with the corresponding DataElements. | N/A | Affiliated AP Metrics TLVs are present when MLO is supported and applicable. Reported Unicast, Multicast, Broadcast, Packet, and Error counters are consistent with the corresponding APMLD Affiliated AP DataElements values. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 13: EM_APMetrics_PeriodicReporting

## Objective

Verify that the EasyMesh Agent periodically transmits IEEE 1905 AP Metrics Response messages according to the configured AP Metrics Reporting Interval, that the reporting frequency matches the configured value, and that the AP Metrics Response contains valid AP Metrics TLVs for all operational BSSs.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| AP Metrics Reporting Interval | 30 Seconds |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response |
| Network Topology | Controller and 3 Extenders |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Configure AP Metrics Reporting Interval using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval 30` | N/A | AP Metrics Reporting Interval is configured successfully. |
| 2 | Verify the configured value using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval` | N/A | APMetricsReportingInterval Parameter returns 30. |
| 3 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Wait for approximately 90 seconds (3 reporting intervals). | Transmit unsolicited AP Metrics Response messages. | Multiple unsolicited AP Metrics Response messages are transmitted periodically by the Extender. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped. |
| 6 | Verify timestamps of consecutive AP Metrics Response packets in the captured IEEE 1905 traffic. | N/A | Consecutive AP Metrics Response packets are observed at approximately 30-second intervals. |
| 7 | Verify the captured IEEE 1905 packets. | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. One AP Metrics TLV is present for each operational BSS, and each AP Metrics TLV is decodable and contains valid field values. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 14: EM_ChannelUtilizationThresholdBasedReporting

## Objective

Verify that an unsolicited IEEE 1905 AP Metrics Response is transmitted when the configured Channel Utilization Reporting Threshold is crossed.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| APMetricsReportingInterval | 300 |
| Channel Utilization Reporting Threshold | 30 |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response |
| Network Topology | Controller, 3 Extenders and Associated STAs |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval, Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelUtilizationReportingThreshold |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Extender-STA | Expected Result |
|-------------|------------|----------|--------------|-----------------|
| 1 | Configure AP Metrics Reporting Interval using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval 300` | N/A | N/A | AP Metrics Reporting Interval is configured successfully. |
| 2 | Configure Channel Utilization Reporting Threshold using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelUtilizationReportingThreshold 30` | N/A | N/A | Channel Utilization Reporting Threshold is configured successfully. |
| 3 | Verify AP Metrics Reporting Interval using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval` | N/A | N/A | APMetricsReportingInterval returns 300. |
| 4 | Verify Channel Utilization Reporting Threshold using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelUtilizationReportingThreshold` | N/A | N/A | ChannelUtilizationReportingThreshold returns 30. |
| 5 | Start IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 traffic capture begins successfully. |
| 6 | Start an iperf3 server using `iperf3 -s` | N/A | Generate heavy traffic to the Controller using `iperf3 -c <controller-ip> -t 120 -P 10` | Channel Utilization increases and exceeds the configured threshold. |
| 7 | Continue IEEE 1905 packet capture during traffic generation. | Transmit unsolicited AP Metrics Response. | N/A | AP Metrics Response is transmitted after the Channel Utilization threshold is crossed. |
| 8 | Stop IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 packet capture is stopped. |
| 9 | Verify the captured IEEE 1905 packets. | N/A | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response is observed after the Channel Utilization threshold is crossed and before the next scheduled reporting interval, containing an updated Channel Utilization value. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 15: EM_LinkMetricQuery_AllNeighbors

## Objective

Verify that the EasyMesh Agent correctly responds to an IEEE 1905 Link Metric Query for all neighbors and reports link metrics for all active Ethernet and Wi-Fi backhaul links.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Link Metric Query, Link Metric Response |
| Network Topology | Controller and 3 Extenders |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 2 | IEEE 1905 Link Metric Query for all neighbors is transmitted by the Controller. | Receive Link Metric Query. | Link Metric Query is received successfully by the Extender. |
| 3 | N/A | Process Link Metric Query and transmit Link Metric Response. | Link Metric Response is transmitted successfully. |
| 4 | Verify active neighbor information from the topology. | Verify active backhaul links. | Active neighbors are identified successfully. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Link Metric Query and corresponding Link Metric Response are present in the capture. |
| 7 | Verify Receiver Link Metric TLVs, Transmitter Link Metric TLVs, and correlate the reported metrics with active neighbor links. | Verify active Ethernet and Wi-Fi backhaul links. | Receiver and Transmitter Link Metric TLVs are reported for all active neighbors, and the reported metrics correspond to all active Ethernet and Wi-Fi backhaul neighbor links. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---

# Test Case 16: EM_LinkMetricQuery_SpecificNeighbor

## Objective

Verify that the EasyMesh Agent correctly responds to an IEEE 1905 Link Metric Query for a specific neighbor and reports link metrics only for the requested neighbor.

## Test Type

**Positive**

---

## Test Environment
| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extenders | 3 EasyMesh Agents |
| Network Topology Type | Hybrid |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites
1. Controller and all Extenders are onboarded with active EasyMesh backhaul connections.
2. EasyMesh and IEEE 1905 services are running on Controller and all Extenders.
3. All Extenders are visible in the Controller topology.
4. DataElements is accessible via rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| IEEE 1905 Messages Validated | Link Metric Query, Link Metric Response |
| Network Topology | Controller and 3 Extenders |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extenders | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Identify the target neighbor from the topology. | Verify connectivity to the target neighbor. | Target neighbor is identified successfully. |
| 2 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 3 | IEEE 1905 Link Metric Query for the specific neighbor is transmitted by the Controller. | Receive Link Metric Query. | Neighbor-specific Link Metric Query is received successfully by the Extender. |
| 4 | N/A | Process Link Metric Query and transmit Link Metric Response. | Neighbor-specific Link Metric Response is transmitted successfully. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Neighbor-specific Link Metric Query and corresponding Link Metric Response are present in the capture. |
| 7 | Verify the Receiver Link Metric TLVs, Transmitter Link Metric TLVs, and correlate the reported metrics with the requested neighbor. | Verify active link information for the requested neighbor. | Receiver and Transmitter Link Metric TLVs are present for the requested neighbor, and the reported metrics correspond only to the specified neighbor link. |

---

> Note: If required, follow the same procedure for the remaining Extenders (Extender-2 and Extender-3).

---
