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

import pytest
import time
from packet_analyzer.packet_dissector import reassemble_packets
import metrics_collection_utils as mc_utils
from rdkbmeshzap.common_utils import device_utils, report_logger

def test_ap_metrics_response_disable(initialize):
    """
    Verify that no AP Metrics responses are reported after the interval is set to zero.
    """
    report_logger.print_test("Entering test_ap_metrics_response_disable")
    capture_filename = None
    capture_started = False

    try:
        report_logger.print_step(
            "Step 1: Identify enabled controller and extender AL MAC addresses "
            "to validate the packet capture"
        )
        expected_device_macs = device_utils.get_enabled_device_al_macs(initialize)
        report_logger.print_success(
            f"PASS: Identified AL MAC addresses for {len(expected_device_macs)} devices"
        )

        report_logger.print_step(
            "Step 2: Disable AP Metrics reporting by setting the "
            f"interval to {mc_utils.DISABLED_INTERVAL}s"
        )
        initialize.set_ap_metrics_reporting_interval(
            "controller", mc_utils.DISABLED_INTERVAL, apply_scope="all"
        )
        disable_time = time.time()
        report_logger.print_success("PASS: AP Metrics reporting disable setting applied")

        report_logger.print_step(
            "Step 3: Verify the configured AP Metrics reporting interval is 0s"
        )
        configured_interval = initialize.get_ap_metrics_reporting_interval("controller")
        if str(configured_interval).strip() != str(mc_utils.DISABLED_INTERVAL):
            pytest.fail(
                f"Configured interval {configured_interval!r}; "
                f"expected {mc_utils.DISABLED_INTERVAL}"
            )
        report_logger.print_success("PASS: Configured interval confirms AP Metrics reporting is disabled")

        report_logger.print_step(
            "Step 4: Wait "
            f"{mc_utils.DRAIN_SECONDS}s for in-flight AP Metrics responses to drain"
        )
        report_logger.print_info(
            "INFO: Waiting for in-flight AP Metrics responses to drain"
        )
        time.sleep(mc_utils.DRAIN_SECONDS)

        capture_filename = device_utils.start_capture(
            initialize,
            "controller",
            "test_ap_metrics_response_disable",
            5,
        )
        capture_started = True

        report_logger.print_step(
            "Step 6: Monitor IEEE 1905 traffic for "
            f"{mc_utils.OBSERVATION_SECONDS}s"
        )
        report_logger.print_info(
            "INFO: Monitoring IEEE 1905 traffic while AP Metrics reporting is disabled"
        )
        time.sleep(mc_utils.OBSERVATION_SECONDS)

        report_logger.print_step(
            "Step 7: Stop the capture and download from Controller"
        )
        try:
            local_path = device_utils.stop_and_collect_capture(
                initialize, "controller", capture_filename
            )
            capture_started = False
        except Exception as error:
            report_logger.print_error(
                f"FAIL: Could not stop and collect capture for controller: {error}"
            )
            raise
        packets = reassemble_packets(local_path)

        mc_utils.validate_disabled_ap_metrics_capture(
            packets,
            disable_time,
            mc_utils.DRAIN_SECONDS,
            expected_device_macs,
            step=8,
        )
    finally:
        report_logger.print_test("Exiting test_ap_metrics_response_disable")
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(
                    initialize, "controller", capture_filename
                )
            except Exception as error:
                report_logger.log(f"Could not collect remote packet capture: {error}")
