"""Shared helpers for Metrics Collection tests."""

from scapy.layers.l2 import Ether
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
from rdkbmeshzap.common_utils import report_logger

REPORTING_INTERVAL = 10
INTERVAL_TOLERANCE = 1
OBSERVATION_SECONDS = 120
DISABLED_INTERVAL = 0
DRAIN_SECONDS = 10

def extract_message_times_by_source(packets, message_type):
    """
    Group timestamps for a 1905 message type by source MAC.
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

def validate_periodic_ap_metrics_capture(packets, expected_device_macs):
    """
    Validate AP Metrics Responses and their AP Metrics TLVs.
    """
    all_responses = check_message_presence(packets, MSG_TYPE_AP_METRICS_RESPONSE) or []
    expected_sources = set(expected_device_macs.values())
    responses = [
        response
        for response in all_responses
        if response.haslayer(Ether)
        and response[Ether].src.lower() in expected_sources
    ]
    if not responses:
        report_logger.print_error(
            "No AP Metrics Responses from enabled testbed devices were captured"
        )
        return []
    if any(
        not check_tlv_presence(response, TLV_TYPE_AP_METRICS)
        for response in responses
    ):
        report_logger.print_error("An AP Metrics Response is missing its AP Metrics TLV")
    response_times_by_source = extract_message_times_by_source(
        packets, MSG_TYPE_AP_METRICS_RESPONSE
    )
    interval_failures = []
    for source, response_times in response_times_by_source.items():
        intervals = [
            later - earlier
            for earlier, later in zip(response_times, response_times[1:])
        ]
        invalid_intervals = [
            round(interval, 2)
            for interval in intervals
            if abs(interval - REPORTING_INTERVAL) > INTERVAL_TOLERANCE
        ]
        if invalid_intervals:
            interval_failures.append(f"{source}: {invalid_intervals}")
    if interval_failures:
        report_logger.print_error(
            (
                f"AP Metrics Response intervals exceeded the allowed range of "
                f"{REPORTING_INTERVAL}+/-{INTERVAL_TOLERANCE}s. "
                f"Observed intervals: {'; '.join(interval_failures)}"
            )
        )
    return responses

def validate_disabled_ap_metrics_capture(
    packets, disabled_at, drain_seconds, expected_device_macs
):
    """
    Validate that no AP Metrics Responses occur after reporting is disabled.
    """
    expected_sources = set(expected_device_macs.values())
    responses = [
        packet
        for packet in packets
        if packet.time >= disabled_at + drain_seconds
        and check_message_presence([packet], MSG_TYPE_AP_METRICS_RESPONSE)
        and packet.haslayer(Ether)
        and packet[Ether].src.lower() in expected_sources
    ]
    if responses:
        report_logger.print_error(
            "AP Metrics Responses were captured after reporting was disabled."
        )
