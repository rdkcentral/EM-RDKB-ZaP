# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 RDK Management
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from scapy.layers.l2 import Ether
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import report_logger

# Interval in seconds between periodic AP Metrics reports.
REPORTING_INTERVAL = 10

# Allowed tolerance in seconds for validating the reporting interval.
INTERVAL_TOLERANCE = 1

# Total duration in seconds to monitor periodic AP Metrics reporting.
OBSERVATION_SECONDS = 120

# Interval value used to disable periodic AP Metrics reporting.
DISABLED_INTERVAL = 0

# Wait time in seconds to clear previously generated AP Metrics reports before validation.
DRAIN_SECONDS = 10

def extract_message_times_by_source(packets, message_type):
    """
    Syntax: extract_message_times_by_source(packets, message_type)
    Description: Group timestamps for a 1905 message type by source MAC.
    Parameters: packets - Decoded packets; message_type - IEEE 1905 message type.
    Return Value: A source-MAC-to-sorted-timestamps dictionary.
    Example: extract_message_times_by_source(packets, MSG_TYPE_AP_METRICS_RESPONSE)
    """
    times_by_source = {}
    for packet in packets:
        if not packet.haslayer(Ether):
            continue
        payload = bytes(packet[Ether].payload)
        if len(payload) >= 4 and (payload[2] << 8 | payload[3]) == message_type:
            source = packet[Ether].src.lower()
            times_by_source.setdefault(source, []).append(float(packet.time))
    return {
        source: sorted(times)
        for source, times in times_by_source.items()
    }

def validate_periodic_ap_metrics_capture(packets, expected_device_macs, step):
    """
    Syntax: validate_periodic_ap_metrics_capture(packets, expected_device_macs, step)
    Description: Validate AP Metrics Responses and their AP Metrics TLVs and intervals.
    Parameters: packets - Decoded packets; expected_device_macs - Expected device MACs; step - Report step.
    Return Value: None; reports validation results.
    Example: validate_periodic_ap_metrics_capture(packets, device_macs, 1)
    """
    report_logger.print_step(f"STEP {step}: Validate AP Metrics Response presence and AP Metrics TLVs")
    expected_device_macs = {
        device: mac
        for device, mac in expected_device_macs.items()
        if device.startswith("extender")
    }
    expected_sources = set(expected_device_macs.values())
    responses = [
        packet
        for packet in packets
        if packet.haslayer(Ether)
        and packet[Ether].src.lower() in expected_sources
        and check_message_presence([packet], MSG_TYPE_AP_METRICS_RESPONSE)
    ]
    if not responses:
        report_logger.print_error("FAIL: No AP Metrics Responses from enabled testbed devices were captured")
        return
    missing_tlv = any(
        not check_tlv_presence(bytes(response[Ether].payload), TLV_TYPE_AP_METRICS)
        for response in responses
    )
    if missing_tlv:
        report_logger.print_error("FAIL: An AP Metrics Response is missing its AP Metrics TLV")
    else:
        report_logger.print_success("PASS: AP Metrics Responses were captured with the AP Metrics TLV")

    report_logger.print_step(f"STEP {step+1}: Validate that AP Metrics responses were reported periodically at the configured {REPORTING_INTERVAL}-second interval")
    response_times_by_source = {
        source: times
        for source, times in extract_message_times_by_source(
            packets, MSG_TYPE_AP_METRICS_RESPONSE
        ).items()
        if source in expected_sources
    }

    for device, source in expected_device_macs.items():
        response_times = response_times_by_source.get(source)
        if response_times is None:
            report_logger.print_error(f"FAIL: No AP Metrics Responses were captured for {device}")
            continue
        intervals = [
            later - earlier
            for earlier, later in zip(response_times, response_times[1:])
        ]
        if len(response_times) < 2:
            report_logger.print_error(f"FAIL: Fewer than two AP Metrics Responses were captured for {device}")
            continue
        invalid_intervals = [
            round(interval, 2)
            for interval in intervals
            if abs(interval - REPORTING_INTERVAL) > INTERVAL_TOLERANCE
        ]
        if invalid_intervals:
            report_logger.print_error(f"FAIL: AP Metrics Response intervals for {device} exceeded the allowed range of {REPORTING_INTERVAL}+/-{INTERVAL_TOLERANCE}s. Observed intervals: {invalid_intervals}")
        else:
            report_logger.print_success(f"PASS: AP Metrics Response intervals for {device} are within the allowed range of {REPORTING_INTERVAL}+/-{INTERVAL_TOLERANCE}s")

def validate_disabled_ap_metrics_capture(
    packets, disabled_at, drain_seconds, expected_device_macs, step
):
    """
    Syntax: validate_disabled_ap_metrics_capture(packets, disabled_at, drain_seconds, expected_device_macs, step)
    Description: Validate that no AP Metrics Responses occur after reporting is disabled.
    Parameters: packets - Decoded packets; disabled_at - Disable timestamp; drain_seconds - Grace period; expected_device_macs - Expected MACs; step - Report step.
    Return Value: None; reports validation results.
    Example: validate_disabled_ap_metrics_capture(packets, disabled_at, 10, device_macs, 1)
    """
    report_logger.print_step(f"STEP {step}: Validate that no AP Metrics responses were reported after reporting was disabled")
    expected_device_macs = {
        device: mac
        for device, mac in expected_device_macs.items()
        if device.startswith("extender")
    }
    responses_by_source = {}
    for packet in packets:
        if (
            packet.time < disabled_at + drain_seconds
            or not check_message_presence([packet], MSG_TYPE_AP_METRICS_RESPONSE)
            or not packet.haslayer(Ether)
        ):
            continue
        source = packet[Ether].src.lower()
        responses_by_source.setdefault(source, []).append(packet)

    for device, source in expected_device_macs.items():
        if responses_by_source.get(source):
            report_logger.print_error(f"FAIL: AP Metrics Responses from {device} were captured after reporting was disabled")
        else:
            report_logger.print_success(f"PASS: No AP Metrics Responses from {device} were captured after reporting was disabled")
