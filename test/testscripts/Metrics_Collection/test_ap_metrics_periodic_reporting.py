"""Validate periodic AP Metrics reporting from enabled extenders."""

import time

from packet_analyzer.packet_dissector import reassemble_packets

import metrics_collection_utils as mc_utils
from rdkbmeshzap.common_utils import device_utils, report_logger

def test_ap_metrics_periodic_reporting(initialize):
    """
    Verify AP Metrics responses arrive at the configured interval.
    """
    report_logger.print_test("Entering test_ap_metrics_periodic_reporting")
    capture_started = False
    expected_device_macs = device_utils.get_enabled_testbed_device_macs(initialize)
    capture_filename = None

    try:
        report_logger.print_step(
            "Step 1: Configure AP Metrics Reporting Interval to "
            f"{mc_utils.REPORTING_INTERVAL}s"
        )
        initialize.set_ap_metrics_reporting_interval(
            "controller", mc_utils.REPORTING_INTERVAL, apply_scope="all"
        )
        report_logger.print_success(
            "PASS: Policy settings applied with interval "
            f"{mc_utils.REPORTING_INTERVAL}s"
        )

        configured_interval = initialize.get_ap_metrics_reporting_interval("controller")
        if str(configured_interval).strip() != str(mc_utils.REPORTING_INTERVAL):
            pytest.fail(
                f"Configured interval {configured_interval!r}; "
                f"expected {mc_utils.REPORTING_INTERVAL}"
            )
        report_logger.print_success("PASS: Configured interval matches the expected value")

        capture_filename = device_utils.start_capture(
            initialize,
            "controller",
            "test_ap_metrics_periodic_reporting",
            2,
        )
        capture_started = True
        report_logger.print_success("PASS: Packet capture started")

        report_logger.print_step(
            "Step 3: Observe AP Metrics reporting for "
            f"{mc_utils.OBSERVATION_SECONDS}s"
        )
        time.sleep(mc_utils.OBSERVATION_SECONDS)

        report_logger.print_step("Step 4: Download and analyze the captured frames")
        local_path = device_utils.stop_and_collect_capture(
            initialize, "controller", capture_filename
        )
        capture_started = False
        packets = reassemble_packets(local_path)

        responses = mc_utils.validate_periodic_ap_metrics_capture(
            packets, expected_device_macs
        )
        if responses and not report_logger.get_error_logs():
            report_logger.print_success(
                f"PASS: {len(responses)} AP Metrics Response(s) with valid TLVs were captured"
            )
    finally:
        report_logger.print_test("Exiting test_ap_metrics_periodic_reporting")
        if capture_started:
            try:
                initialize.stop_frame_capture("controller")
            except Exception as error:
                report_logger.log(f"Could not stop packet capture during teardown: {error}")
        if capture_started and capture_filename:
            try:
                device_utils.stop_and_collect_capture(
                    initialize, "controller", capture_filename
                )
            except Exception as error:
                report_logger.log(f"Could not collect remote packet capture: {error}")
