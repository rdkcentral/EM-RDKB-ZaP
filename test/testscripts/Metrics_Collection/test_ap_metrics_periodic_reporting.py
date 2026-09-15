import time
import importlib.util
import os
from pathlib import Path

import pytest
from packet_analyzer.ieee1905_utils import *  # noqa: F401,F403
from packet_analyzer.packet_dissector import *  # noqa: F401,F403
from rdkbmeshzap import zi_logger

import metrics_collection_utils as mc_utils


DEVICE_UTILS_PATH = Path(__file__).resolve().parents[3] / "common-utils" / "device_utils.py"
device_utils_spec = importlib.util.spec_from_file_location(
    "device_utils", DEVICE_UTILS_PATH
)
device_utils = importlib.util.module_from_spec(device_utils_spec)
device_utils_spec.loader.exec_module(device_utils)


REPORTING_INTERVAL = 10
INTERVAL_TOLERANCE = 1
OBSERVATION_SECONDS = 120


def test_ap_metrics_periodic_reporting(initialize):
    capture_name = mc_utils.generate_capture_name("ap_metrics_periodic", "")
    capture_started = False
    pcap_remote_dir = initialize.read_from_database("controller", "pcap_remote_dir")
    pcap_local_dir = initialize.read_from_database("controller", "pcap_local_dir")
    enabled_extender_macs = device_utils.get_enabled_extender_macs(initialize)
    expected_extender_macs = set(enabled_extender_macs.values())
    capture_interface = initialize.read_from_database(
        "controller", "backhaul_capture_iface"
    )
    capture_filter = initialize.read_from_database("controller", "filter_1905")

    try:
        zi_logger.print_step(
            "Step 1: Configure AP Metrics Reporting Interval "
            f"to {REPORTING_INTERVAL}s via GUI for all devices"
        )
        initialize.set_ap_metrics_reporting_interval(
            "controller", REPORTING_INTERVAL, apply_scope="all"
        )
        zi_logger.print_success(
            f"PASS: Policy Settings applied with interval {REPORTING_INTERVAL}s"
        )

        zi_logger.print_step(
            "Step 2: Read back the configured interval from the Policy Settings page"
        )
        configured_interval = initialize.get_ap_metrics_reporting_interval("controller")
        zi_logger.print_step(f"Interval shown in GUI: {configured_interval}")
        if str(configured_interval).strip() != str(REPORTING_INTERVAL):
            pytest.fail(
                f"GUI reported interval {configured_interval!r}; "
                f"expected {REPORTING_INTERVAL}"
            )
        zi_logger.print_success(
            f"PASS: GUI read back matches the expected interval {REPORTING_INTERVAL}s"
        )

        zi_logger.print_step(
            f"Step 3: Start 1905 frame capture on {capture_interface} "
            f"({capture_name})"
        )
        zi_logger.print_step(
            f"Enabled extenders and expected AL MACs: "
            f"{sorted(expected_extender_macs)}"
        )
        capture_filename = f"{capture_name}.pcapng"
        initialize.start_frame_capture(
            "controller", capture_interface, capture_filter, capture_filename
        )
        capture_started = True
        zi_logger.print_success("PASS: Packet capture started on the controller")

        zi_logger.print_step(
            f"Step 4: Observe AP Metrics reporting for {OBSERVATION_SECONDS}s"
        )
        time.sleep(OBSERVATION_SECONDS)
        initialize.stop_frame_capture("controller")
        capture_started = False
        zi_logger.print_success("PASS: Observation window completed, capture stopped")

        zi_logger.print_step("Step 5: Download and dissect the captured 1905 frames")
        local_path = initialize.download_captured_pcap(
            "controller", capture_filename
        )
        initialize.delete_captured_pcap("controller", capture_filename)
        packets = reassemble_packets(local_path)
        zi_logger.print_step(
            f"Reassembled {len(packets)} 1905 frames from {local_path}"
        )

        zi_logger.print_step(
            "Step 6: Verify every AP Metrics Response carries the AP Metrics TLV"
        )
        responses = check_message_presence(
            packets, MSG_TYPE_AP_METRICS_RESPONSE
        ) or []
        zi_logger.print_step(f"AP Metrics Responses captured: {len(responses)}")
        for response in responses:
            if not check_tlv_presence(response, TLV_TYPE_AP_METRICS):
                pytest.fail("AP Metrics Response is missing its AP Metrics TLV")
        zi_logger.print_success(
            f"PASS: All {len(responses)} AP Metrics Responses carry the AP Metrics TLV"
        )

        zi_logger.print_step(
            "Step 7: Validate the reporting interval of every reporting agent"
        )
        response_times_by_agent = mc_utils.extract_message_times_by_source(
            packets, MSG_TYPE_AP_METRICS_RESPONSE
        )
        if not response_times_by_agent:
            pytest.fail("No AP Metrics Responses were captured")
        zi_logger.print_step(
            f"Reporting agents detected: {sorted(response_times_by_agent)}"
        )
        observed_extender_macs = set(response_times_by_agent)
        missing_extenders = expected_extender_macs - observed_extender_macs
        unexpected_sources = observed_extender_macs - expected_extender_macs
        if missing_extenders or unexpected_sources:
            pytest.fail(
                "AP Metrics Response sources do not match enabled extenders; "
                f"missing={sorted(missing_extenders)}, "
                f"unexpected={sorted(unexpected_sources)}"
            )
        zi_logger.print_success(
            "PASS: AP Metrics Response sources match all enabled extenders"
        )

        failures = []
        for agent, response_times in sorted(response_times_by_agent.items()):
            intervals = [
                round(later - earlier)
                for earlier, later in zip(response_times, response_times[1:])
            ]
            if any(
                abs(interval - REPORTING_INTERVAL) > INTERVAL_TOLERANCE
                for interval in intervals
            ):
                failures.append(f"{agent}: observed intervals {intervals}")
            else:
                zi_logger.print_step(
                    f"{agent}: {len(response_times)} reports, intervals {intervals}"
                )

        if failures:
            pytest.fail(
                f"AP Metrics intervals must be within "
                f"{REPORTING_INTERVAL}+/-{INTERVAL_TOLERANCE}s; "
                + "; ".join(failures)
            )

        zi_logger.print_success(
            f"PASS: {len(response_times_by_agent)} agent(s) reported AP Metrics "
            f"within {REPORTING_INTERVAL}+/-{INTERVAL_TOLERANCE}s"
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
