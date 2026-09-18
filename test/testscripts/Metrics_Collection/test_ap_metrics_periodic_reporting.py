"""Validate periodic AP Metrics reporting from enabled extenders."""

import time

import pytest
from packet_analyzer.packet_dissector import reassemble_packets

import device_utils
import metrics_collection_utils as mc_utils
import test_report_utils as zi_logger

def test_ap_metrics_periodic_reporting(initialize):
    """Verify AP Metrics responses arrive at the configured interval."""
    capture_started = False
    expected_device_macs = device_utils.get_enabled_testbed_device_macs(initialize)
    capture_filename = None

    try:
        zi_logger.print_step(
            "Step 1: Configure AP Metrics Reporting Interval to "
            f"{mc_utils.REPORTING_INTERVAL}s"
        )
        initialize.set_ap_metrics_reporting_interval(
            "controller", mc_utils.REPORTING_INTERVAL, apply_scope="all"
        )
        zi_logger.print_success(
            "PASS: Policy settings applied with interval "
            f"{mc_utils.REPORTING_INTERVAL}s"
        )

        configured_interval = initialize.get_ap_metrics_reporting_interval("controller")
        if str(configured_interval).strip() != str(mc_utils.REPORTING_INTERVAL):
            pytest.fail(
                f"Configured interval {configured_interval!r}; "
                f"expected {mc_utils.REPORTING_INTERVAL}"
            )
        zi_logger.print_success("PASS: Configured interval matches the expected value")

        capture_filename = device_utils.start_capture(
            initialize, "controller", "ap_metrics_periodic", 2
        )
        capture_started = True
        zi_logger.print_success("PASS: Packet capture started")

        zi_logger.print_step(
            "Step 3: Observe AP Metrics reporting for "
            f"{mc_utils.OBSERVATION_SECONDS}s"
        )
        time.sleep(mc_utils.OBSERVATION_SECONDS)

        zi_logger.print_step("Step 4: Download and analyze the captured frames")
        local_path = device_utils.stop_and_collect_capture(
            initialize, "controller", capture_filename
        )
        capture_started = False
        packets = reassemble_packets(local_path)

        responses = mc_utils.validate_periodic_ap_metrics_capture(
            packets, expected_device_macs
        )
        zi_logger.print_success(
            f"PASS: {len(responses)} AP Metrics Response(s) with valid TLVs were captured"
        )
    finally:
        if capture_started:
            try:
                initialize.stop_frame_capture("controller")
            except Exception as error:
                zi_logger.log(f"Could not stop packet capture during teardown: {error}")
        if capture_started and capture_filename:
            try:
                device_utils.stop_and_collect_capture(
                    initialize, "controller", capture_filename
                )
            except Exception as error:
                zi_logger.log(f"Could not collect remote packet capture: {error}")
