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

def test_ap_metrics_periodic_reporting(initialize):
    """
    Verify AP Metrics responses arrive at the configured interval.
    """
    report_logger.print_test("Entering test_ap_metrics_periodic_reporting")
    capture_started = False
    capture_filename = None

    try:
        report_logger.print_step(
            "Step 1: Identify enabled controller and extender AL MAC addresses to validate the packet capture"
        )
        expected_device_macs = device_utils.get_enabled_device_al_macs(initialize)
        report_logger.print_success(
            f"PASS: Identified AL MAC addresses for {len(expected_device_macs)} devices"
        )

        report_logger.print_step(
            "Step 2: Configure the AP Metrics reporting interval to "
            f"{mc_utils.REPORTING_INTERVAL}s"
        )
        initialize.set_ap_metrics_reporting_interval("controller", mc_utils.REPORTING_INTERVAL, apply_scope="all")
        report_logger.print_success("PASS: Policy settings applied with interval "
            f"{mc_utils.REPORTING_INTERVAL}s")

        report_logger.print_step(
            "Step 3: Verify the configured AP Metrics reporting interval"
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
            4,
        )
        capture_started = True

        report_logger.print_step(
            "Step 5: Wait for the observation period while capturing IEEE 1905 traffic "
            f"for {mc_utils.OBSERVATION_SECONDS}s"
        )
        time.sleep(mc_utils.OBSERVATION_SECONDS)
        report_logger.print_info(
            "INFO: Observation period completed for AP Metrics response validation"
        )

        report_logger.print_step(
            "Step 6: Stop and collect capture from controller"
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

        mc_utils.validate_periodic_ap_metrics_capture(
            packets, expected_device_macs, step=7
        )
    finally:
        report_logger.print_test("Exiting test_ap_metrics_periodic_reporting")
        if capture_started:
            try:
                device_utils.stop_and_collect_capture(
                    initialize, "controller", capture_filename
                )
            except Exception as error:
                report_logger.log(f"Could not clean up packet capture: {error}")
