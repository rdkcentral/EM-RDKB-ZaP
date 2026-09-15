import time
import os

import pytest
from packet_analyzer.ieee1905_utils import *  # noqa: F401,F403
from packet_analyzer.packet_dissector import *  # noqa: F401,F403
from rdkbmeshzap import zi_logger

import metrics_collection_utils as mc_utils


DISABLED_INTERVAL = 0
REPORTING_INTERVAL = 10
OBSERVATION_SECONDS = 100


def test_ap_metrics_response_disable(initialize):
    capture_name = mc_utils.generate_capture_name("ap_metrics_response_disable", "")
    capture_started = False
    pcap_remote_dir = initialize.read_from_database("controller", "pcap_remote_dir")
    pcap_local_dir = initialize.read_from_database("controller", "pcap_local_dir")
    capture_interface = initialize.read_from_database(
        "controller", "backhaul_capture_iface"
    )
    capture_filter = initialize.read_from_database("controller", "filter_1905")

    try:
        zi_logger.print_step(
            f"Step 1: Start 1905 frame capture on {capture_interface} "
            f"({capture_name})"
        )
        capture_filename = f"{capture_name}.pcapng"
        initialize.start_frame_capture(
            "controller", capture_interface, capture_filter, capture_filename
        )
        capture_started = True
        zi_logger.print_success("PASS: Packet capture started on the controller")

        zi_logger.print_step(
            "Step 2: Set AP Metrics Reporting Interval to 0 via GUI for all devices"
        )
        initialize.set_ap_metrics_reporting_interval(
            "controller", DISABLED_INTERVAL, apply_scope="all"
        )
        disable_time = time.time()
        zi_logger.print_success("PASS: AP Metrics reporting was disabled")

        zi_logger.print_step(
            "Step 3: Verify the configured interval in the Policy Settings page"
        )
        configured_interval = initialize.get_ap_metrics_reporting_interval("controller")
        zi_logger.print_step(f"Interval shown in GUI: {configured_interval}")
        if str(configured_interval).strip() != str(DISABLED_INTERVAL):
            pytest.fail(
                f"GUI reported interval {configured_interval!r}; "
                f"expected {DISABLED_INTERVAL}"
            )
        zi_logger.print_success("PASS: GUI read back confirms interval 0")

        zi_logger.print_step(
            f"Step 4: Allow {REPORTING_INTERVAL}s for in-flight reports to drain"
        )
        time.sleep(REPORTING_INTERVAL)

        zi_logger.print_step(
            f"Step 5: Monitor IEEE 1905 traffic for {OBSERVATION_SECONDS}s"
        )
        time.sleep(OBSERVATION_SECONDS)
        initialize.stop_frame_capture("controller")
        capture_started = False
        zi_logger.print_success("PASS: Observation completed and capture stopped")

        zi_logger.print_step("Step 6: Download and dissect the captured IEEE 1905 frames")
        local_path = initialize.download_captured_pcap(
            "controller", capture_filename
        )
        initialize.delete_captured_pcap("controller", capture_filename)
        packets = reassemble_packets(local_path)
        zi_logger.print_step(
            f"Reassembled {len(packets)} IEEE 1905 frames from {local_path}"
        )

        zi_logger.print_step(
            "Step 7: Verify the Multi-AP Policy Configuration Request and ACK"
        )
        policy_requests = check_message_presence(
            packets, MSG_TYPE_POLICY_CONFIG_REQUEST
        ) or []
        acknowledgements = check_message_presence(packets, MSG_TYPE_1905_ACK) or []
        if not policy_requests:
            pytest.fail("No Multi-AP Policy Configuration Request was captured")
        if not acknowledgements:
            pytest.fail("No IEEE 1905 ACK was captured for the policy update")
        zi_logger.print_success(
            f"PASS: Captured {len(policy_requests)} policy request(s) and "
            f"{len(acknowledgements)} ACK(s)"
        )

        zi_logger.print_step(
            "Step 8: Verify no AP Metrics Responses after the disable transition"
        )
        responses = [
            packet
            for packet in packets
            if packet.time >= disable_time + REPORTING_INTERVAL
            and check_message_presence([packet], MSG_TYPE_AP_METRICS_RESPONSE)
        ]
        zi_logger.print_step(f"AP Metrics Responses captured: {len(responses)}")
        if responses:
            pytest.fail(
                "AP Metrics Responses were captured after reporting was disabled: "
                f"{len(responses)}"
            )
        zi_logger.print_success(
            "PASS: No unsolicited AP Metrics Responses were captured while interval was 0"
        )
    finally:
        if capture_started:
            try:
                initialize.stop_frame_capture("controller")
            except Exception as error:
                zi_logger.log(f"Could not stop packet capture during teardown: {error}")
        try:
            initialize.delete_captured_pcap("controller", f"{capture_name}.pcapng")
        except Exception as error:
            zi_logger.log(f"Could not delete remote packet capture: {error}")
