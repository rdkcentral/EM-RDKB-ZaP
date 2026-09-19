"""Validate that AP Metrics responses stop when reporting is disabled."""

import time

from packet_analyzer.packet_dissector import reassemble_packets

import metrics_collection_utils as mc_utils
from rdkbmeshzap.common_utils import device_utils, report_logger

def test_ap_metrics_response_disable(initialize):
    """
    Verify no unsolicited AP Metrics responses follow interval zero.
    """
    report_logger.print_test("Entering test_ap_metrics_response_disable")
    capture_filename = None
    capture_started = False
    expected_device_macs = device_utils.get_enabled_testbed_device_macs(initialize)

    try:
        capture_filename = device_utils.start_capture(
            initialize,
            "controller",
            "test_ap_metrics_response_disable",
            1,
        )
        capture_started = True
        report_logger.print_success("PASS: Packet capture started")

        report_logger.print_step("Step 2: Set AP Metrics Reporting Interval to 0")
        initialize.set_ap_metrics_reporting_interval(
            "controller", mc_utils.DISABLED_INTERVAL, apply_scope="all"
        )
        disable_time = time.time()
        configured_interval = initialize.get_ap_metrics_reporting_interval("controller")
        if str(configured_interval).strip() != str(mc_utils.DISABLED_INTERVAL):
            pytest.fail(
                f"Configured interval {configured_interval!r}; "
                f"expected {mc_utils.DISABLED_INTERVAL}"
            )
        report_logger.print_success("PASS: AP Metrics reporting was disabled")

        report_logger.print_step(
            "Step 3: Allow "
            f"{mc_utils.DRAIN_SECONDS}s for in-flight reports to drain"
        )
        time.sleep(mc_utils.DRAIN_SECONDS)
        report_logger.print_step(
            "Step 4: Monitor IEEE 1905 traffic for "
            f"{mc_utils.OBSERVATION_SECONDS}s"
        )
        time.sleep(mc_utils.OBSERVATION_SECONDS)

        report_logger.print_step("Step 5: Download and analyze the captured frames")
        local_path = device_utils.stop_and_collect_capture(
            initialize, "controller", capture_filename
        )
        capture_started = False
        packets = reassemble_packets(local_path)

        mc_utils.validate_disabled_ap_metrics_capture(
            packets,
            disable_time,
            mc_utils.DRAIN_SECONDS,
            expected_device_macs,
        )
        if not report_logger.get_error_logs():
            report_logger.print_success(
                "PASS: No AP Metrics Responses were captured after disabling"
            )
    finally:
        report_logger.print_test("Exiting test_ap_metrics_response_disable")
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
