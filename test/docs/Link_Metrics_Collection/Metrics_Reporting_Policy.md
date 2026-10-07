# Test Case 1: EM_APMetrics_PeriodicReporting

## Objective

Verify that the EasyMesh Agent periodically transmits IEEE 1905 AP Metrics Response messages according to the configured AP Metrics Reporting Interval, that the reporting frequency matches the configured value, and that the AP Metrics Response contains valid AP Metrics TLVs for all operational BSSs.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. EasyMesh and IEEE 1905 services are running on both devices.
3. Extender is visible in the Controller topology.
4. DataElements object is accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| AP Metrics Reporting Interval | 30 Seconds |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response |
| Network Topology | Controller and Extender |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Configure AP Metrics Reporting Interval using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval 30` | N/A | AP Metrics Reporting Interval is configured successfully. |
| 2 | Verify the configured value using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval` | N/A | APMetricsReportingInterval Parameter returns 30. |
| 3 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Wait for approximately 90 seconds (3 reporting intervals). | Transmit unsolicited AP Metrics Response messages. | Multiple unsolicited AP Metrics Response messages are transmitted periodically by the Extender. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped. |
| 6 | Verify timestamps of consecutive AP Metrics Response packets in the captured IEEE 1905 traffic. | N/A | Consecutive AP Metrics Response packets are observed at approximately 30-second intervals. |
| 7 | Verify the captured IEEE 1905 packets. | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. One AP Metrics TLV is present for each operational BSS, and each AP Metrics TLV is decodable and contains valid field values. |

---

# Test Case 2: EM_APMetrics_Disabled

## Objective

Verify that periodic AP Metrics reporting is disabled when AP Metrics Reporting Interval is configured to 0 and that the Agent does not transmit unsolicited IEEE 1905 AP Metrics Response messages.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. EasyMesh and IEEE 1905 services are running on both devices.
3. Extender is visible in the Controller topology.
4. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| AP Metrics Reporting Interval | 0 |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response |
| Network Topology | Controller and Extender |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Configure AP Metrics Reporting Interval using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval 0` | N/A | AP Metrics Reporting Interval is configured successfully. |
| 2 | Verify the configured value using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval` | N/A | APMetricsReportingInterval Parameter returns 0. |
| 3 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Monitor IEEE 1905 traffic for 5 minutes. | Continue normal operation. | No unsolicited AP Metrics Response messages are transmitted during the observation period. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response packets are not observed during the configured observation period when the reporting interval is set to 0. |

---

# Test Case 3: EasyMesh_AssociatedSTALinkMetricsInclusionPolicy_Enable

## Objective

Verify that Associated STA Link Metrics TLVs are included in IEEE 1905 AP Metrics Response messages when the Associated STA Link Metrics Inclusion Policy is enabled.

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

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. `At least one Wi-Fi client is associated with the Extender.`
3. EasyMesh and IEEE 1905 services are running on both devices.
4. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Associated STA Link Metrics Inclusion Policy | True |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response, Associated STA Link Metrics TLV |
| Network Topology | Controller, Extender and Associated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTALinkMetricsInclusionPolicy |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Enable Associated STA Link Metrics Inclusion Policy using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTALinkMetricsInclusionPolicy true` | N/A | Policy is configured successfully. |
| 2 | Verify configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTALinkMetricsInclusionPolicy` | N/A | Returned value is true. |
| 3 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Wait for an unsolicited AP Metrics Response. | Transmit unsolicited AP Metrics Response. | AP Metrics Response is transmitted by the Extender. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response contains the Associated STA Link Metrics TLV and the TLV is decodable with valid link metric information for the associated STA. |

---

> **Note:** This validation is also applicable to MLO scenarios. When a Client MLD is associated and the Associated STA Link Metrics Inclusion Policy is enabled, the AP Metrics Response shall include Associated STA Link Metrics TLVs and Associated STA Extended Link Metrics TLVs for Affiliated STAs linked to an Affiliated AP.

---

# Test Case 4: EasyMesh_AssociatedSTALinkMetricsInclusionPolicy_Disable

## Objective

Verify that Associated STA Link Metrics TLVs are not included in IEEE 1905 AP Metrics Response messages when the Associated STA Link Metrics Inclusion Policy is disabled.

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

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. `At least one Wi-Fi client is associated with the Extender.`
3. EasyMesh and IEEE 1905 services are running on both devices.
4. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Associated STA Link Metrics Inclusion Policy | False |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response |
| Network Topology | Controller, Extender and Associated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTALinkMetricsInclusionPolicy |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Disable Associated STA Link Metrics Inclusion Policy using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTALinkMetricsInclusionPolicy false` | N/A | Policy is configured successfully. |
| 2 | Verify configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTALinkMetricsInclusionPolicy` | N/A | Returned value is false. |
| 3 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Wait for an unsolicited AP Metrics Response. | Transmit unsolicited AP Metrics Response. | AP Metrics Response is transmitted by the Extender. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response does not contain the Associated STA Link Metrics TLV. |

---

> **Note:** This validation is also applicable to MLO scenarios. When a Client MLD is associated and the Associated STA Link Metrics Inclusion Policy is disabled, the AP Metrics Response shall not include Associated STA Link Metrics TLVs or Associated STA Extended Link Metrics TLVs for Affiliated STAs linked to an Affiliated AP.

---

# Test Case 5: EasyMesh_AssociatedSTATrafficStatsInclusionPolicy_Enable

## Objective

Verify that Associated STA Traffic Statistics TLVs are included in IEEE 1905 AP Metrics Response messages when the Associated STA Traffic Statistics Inclusion Policy is enabled.

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

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. `At least one Wi-Fi client is associated with the Extender.`
3. EasyMesh and IEEE 1905 services are running on both devices.
4. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Associated STA Traffic Statistics Inclusion Policy | True |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response, Associated STA Traffic Statistics TLV |
| Network Topology | Controller, Extender and Associated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTATrafficStatsInclusionPolicy, Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.STA.{i}.BytesReceived, BytesSent, PacketsReceived, PacketsSent, ErrorsReceived, ErrorsSent and RetransCount

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Extender-STA | Expected Result |
|-------------|------------|----------|--------------|-----------------|
| 1 | Enable Associated STA Traffic Statistics Inclusion Policy using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTATrafficStatsInclusionPolicy true` | N/A | N/A | Policy is configured successfully. |
| 2 | Verify configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTATrafficStatsInclusionPolicy` | N/A | N/A | Returned value is true. |
| 3 | Start IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Start an iperf3 server using `iperf3 -s` | N/A | Generate traffic to the Controller using `iperf3 -c <controller-ip> -t 60 -P 5` | STA traffic statistics are updated. |
| 5 | Read STA Traffic Statistics DataElements using rbuscli. | N/A | N/A | Current STA traffic statistics values are available for comparison. |
| 6 | Wait for an unsolicited AP Metrics Response. | Transmit unsolicited AP Metrics Response. | N/A | AP Metrics Response is transmitted by the Extender. |
| 7 | Stop IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 packet capture is stopped. |
| 8 | Verify the captured IEEE 1905 packets. | N/A | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response contains the Associated STA Traffic Statistics TLV and the TLV is decodable with valid traffic statistics information for the associated STA. |
| 9 | Correlate Associated STA Traffic Statistics TLV values with DataElements. | N/A | N/A | BytesReceived, BytesSent, PacketsReceived, PacketsSent, ErrorsReceived, ErrorsSent and RetransCount reported in the Associated STA Traffic Statistics TLV are consistent with the corresponding STA DataElements values. |

---

> **Note:** This validation is also applicable to MLO scenarios. When a Client MLD is associated and the Associated STA Traffic Statistics Inclusion Policy is enabled, the AP Metrics Response shall include Associated STA Traffic Stats TLVs for Client MLDs and Affiliated STA Metrics TLVs for Affiliated STAs linked to an Affiliated AP.

---

# Test Case 6: EasyMesh_AssociatedSTATrafficStatsInclusionPolicy_Disable

## Objective

Verify that Associated STA Traffic Statistics TLVs are not included in IEEE 1905 AP Metrics Response messages when the Associated STA Traffic Statistics Inclusion Policy is disabled.

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

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. `At least one Wi-Fi client is associated with the Extender.`
3. EasyMesh and IEEE 1905 services are running on both devices.
4. DataElements objects are accessible through rbuscli.
---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Associated STA Traffic Statistics Inclusion Policy | False |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response |
| Network Topology | Controller, Extender and Associated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTATrafficStatsInclusionPolicy |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Extender-STA | Expected Result |
|-------------|------------|----------|--------------|-----------------|
| 1 | Disable Associated STA Traffic Statistics Inclusion Policy using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTATrafficStatsInclusionPolicy false` | N/A | N/A | Policy is configured successfully. |
| 2 | Verify configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.AssociatedSTATrafficStatsInclusionPolicy` | N/A | N/A | Returned value is false. |
| 3 | Start IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Start an iperf3 server using `iperf3 -s` | N/A | Generate traffic to the Controller using `iperf3 -c <controller-ip> -t 60 -P 5` | STA traffic statistics are updated. |
| 5 | Wait for an unsolicited AP Metrics Response. | Transmit unsolicited AP Metrics Response. | Maintain normal STA association. | AP Metrics Response is transmitted by the Extender. |
| 6 | Stop IEEE 1905 packet capture. | N/A | N/A | IEEE 1905 packet capture is stopped. |
| 7 | Verify the captured IEEE 1905 packets. | N/A | N/A | Multi-AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response does not contain the Associated STA Traffic Statistics TLV. |

---

> **Note:** This validation is also applicable to MLO scenarios. When a Client MLD is associated and the Associated STA Traffic Statistics Inclusion Policy is disabled, the AP Metrics Response shall not include Associated STA Traffic Stats TLVs for Client MLDs or Affiliated STA Metrics TLVs for Affiliated STAs linked to an Affiliated AP.

---

# Test Case 7: EasyMesh_APMetricsWiFi6STAStatus_Enable

## Objective

Verify that the Associated Wi-Fi 6 STA Status TLV is included in IEEE 1905 AP Metrics Response messages when the Wi-Fi 6 STA Status Inclusion Policy is enabled.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Wi-Fi Client | Wi-Fi 6 Associated STA |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. EasyMesh and IEEE 1905 services are running on both devices.
3. `At least one Wi-Fi 6 STA is associated with the Extender.`
4. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Associated Wi-Fi 6 STA Status Inclusion Policy | True |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response, Associated Wi-Fi 6 STA Status TLV |
| Network Topology | Controller, Extender and Wi‑Fi 6 STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.APMetricsWiFi6, Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.BSS.{i}.STA.{i}.TIDQueueSizes.{i}.TID, Size |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Enable Wi‑Fi 6 STA Status Inclusion Policy using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.APMetricsWiFi6 true` | N/A | Policy is configured successfully. |
| 2 | Verify configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.APMetricsWiFi6` | N/A | Returned value is true. |
| 3 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Wait for an unsolicited AP Metrics Response. | Transmit unsolicited AP Metrics Response. | AP Metrics Response is transmitted by the Agent. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Multi‑AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response contains the Associated Wi‑Fi 6 STA Status TLV with valid information for the associated Wi‑Fi 6 STA. |
| 7 | Correlate Associated Wi-Fi 6 STA Status TLV values with DataElements. | N/A | TID and Queue Size values reported in the Associated Wi-Fi 6 STA Status TLV are consistent with the corresponding TIDQueueSizes DataElements values. |

---

> **Note:** This validation is also applicable to MLO scenarios. When a Client MLD is associated and the Associated Wi‑Fi 6 STA Status Inclusion Policy is enabled, the AP Metrics Response shall include an Associated Wi‑Fi 6 STA Status Report TLV for the Client MLD. The TLV shall not be reported for individual Affiliated STAs.

---

# Test Case 8: EasyMesh_APMetricsWiFi6STAStatus_Disable

## Objective

Verify that the Associated Wi‑Fi 6 STA Status TLV is not included in IEEE 1905 AP Metrics Response messages when the Wi‑Fi 6 STA Status Inclusion Policy is disabled.

## Test Type

**Positive**

---

## Test Environment

| Component | Description |
|-----------|-------------|
| Controller | EasyMesh Controller |
| Extender | EasyMesh Agent |
| Wi‑Fi Client | Wi‑Fi 6 Associated STA |
| Packet Analyzer | IEEE 1905 packet analysis tool |

---

## Pre-Requisites

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. EasyMesh and IEEE 1905 services are running on both devices.
3. `At least one Wi‑Fi 6 STA is associated with the Extender.`
4. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Associated Wi‑Fi 6 STA Status Inclusion Policy | False |
| IEEE 1905 Messages Validated | Multi‑AP Policy Configuration Request, ACK, AP Metrics Response |
| Network Topology | Controller, Extender and Wi‑Fi 6 STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.APMetricsWiFi6 |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Expected Result |
|-------------|------------|----------|-----------------|
| 1 | Disable Wi‑Fi 6 STA Status Inclusion Policy using `rbuscli set Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.APMetricsWiFi6 false` | N/A | Policy is configured successfully. |
| 2 | Verify configuration using `rbuscli get Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.APMetricsWiFi6` | N/A | Returned value is false. |
| 3 | Start IEEE 1905 packet capture. | N/A | IEEE 1905 traffic capture begins successfully. |
| 4 | Wait for an unsolicited AP Metrics Response. | Transmit unsolicited AP Metrics Response. | AP Metrics Response is transmitted by the Agent. |
| 5 | Stop IEEE 1905 packet capture. | N/A | IEEE 1905 packet capture is stopped successfully. |
| 6 | Verify the captured IEEE 1905 packets. | N/A | Multi‑AP Policy Configuration Request and corresponding ACK message are observed successfully for the configuration applied via rbuscli. AP Metrics Response does not contain the Associated Wi‑Fi 6 STA Status TLV. |

---

> **Note:** This validation is also applicable to MLO scenarios. When a Client MLD is associated and the Associated Wi-Fi 6 STA Status Inclusion Policy is disabled, the AP Metrics Response shall not include an Associated Wi-Fi 6 STA Status Report TLV for the Client MLD. Associated Wi-Fi 6 STA Status Report TLVs shall not be reported for individual Affiliated STAs.

---

# Test Case 9: EasyMesh_ChannelUtilizationThresholdBasedReporting

## Objective

Verify that an unsolicited IEEE 1905 AP Metrics Response is transmitted when the configured Channel Utilization Reporting Threshold is crossed.

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

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. EasyMesh and IEEE 1905 services are running on both devices.
3. `At least one STA is associated with the Extender.`
4. DataElements objects are accessible through rbuscli.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| APMetricsReportingInterval | 300 |
| Channel Utilization Reporting Threshold | 30 |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response |
| Network Topology | Controller, Extender and Associated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval, Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.ChannelUtilizationReportingThreshold |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Extender-STA | Expected Result |
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

# Test Case 10: EasyMesh_STARCPIThresholdBasedReporting

## Objective

Verify that an unsolicited IEEE 1905 AP Metrics Response is transmitted when the associated STA RCPI crosses the configured RCPI Reporting Threshold.

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

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. `At least One STA is associated with the Extender.`
3. EasyMesh and IEEE 1905 services are running on both devices.
4. DataElements objects are accessible through rbuscli.
5. STA position can be adjusted to vary signal strength.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| APMetricsReportingInterval | 300 |
| STA RCPI Reporting Threshold | 100 (Example) |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response, Associated STA Link Metrics TLV |
| Network Topology | Controller, Extender and Associated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval, Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Extender-STA | Expected Result |
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

# Test Case 11: EasyMesh_STARCPIHysteresisBehavior

## Objective

Verify that STA Metrics reporting follows the configured RCPI Hysteresis Margin and prevents excessive reporting due to small RCPI fluctuations around the threshold.

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

1. Controller and Extender are onboarded with an active EasyMesh backhaul connection.
2. `At least one STA is associated with the Extender.`
3. EasyMesh and IEEE 1905 services are running on both devices.
4. DataElements objects are accessible through rbuscli.
5. Signal attenuation setup is available.

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| APMetricsReportingInterval | 300 |
| STA RCPI Threshold | 100 |
| STA RCPI Hysteresis Margin Override | 10 dB |
| IEEE 1905 Messages Validated | Multi-AP Policy Configuration Request, ACK, AP Metrics Response, Associated STA Link Metrics TLV |
| Network Topology | Controller, Extender and Associated STA |
| DataElements | Device.WiFi.DataElements.Network.Device.{i}.APMetricsReportingInterval, Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIThreshold, Device.WiFi.DataElements.Network.Device.{i}.Radio.{i}.STAReportingRCPIHysteresisMarginOverride |

---

## Test Procedure and Expected Results

| Step Number | Controller | Extender | Extender-STA | Expected Result |
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