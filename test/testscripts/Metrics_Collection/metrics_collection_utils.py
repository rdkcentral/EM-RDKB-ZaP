"""Shared helpers for the Metrics Collection test scripts."""

from datetime import datetime

from scapy.layers.l2 import Ether

__all__ = ["generate_capture_name", "extract_message_times_by_source"]


def generate_capture_name(prefix, extension="pcapng"):
    """Return a timestamped capture file name that is unique per test run."""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.{extension}"


def extract_message_times_by_source(packets, message_type):
    """Group the capture timestamps of a 1905 message type per sender MAC."""
    times_by_source = {}
    for packet in packets:
        if not packet.haslayer(Ether):
            continue
        payload = bytes(packet[Ether].payload)
        if len(payload) >= 4 and (payload[2] << 8 | payload[3]) == message_type:
            source = packet[Ether].src.lower()
            times_by_source.setdefault(source, []).append(float(packet.time))
    return {source: sorted(times) for source, times in times_by_source.items()}
