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

import time
from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.link_stability_utils import *

def test_em_backhaul_phy_rate_stability(initialize):
    """
    Verify backhaul PHY rates remain stable relative to their baseline.
    """
    report_logger.print_test("Entering test_em_backhaul_phy_rate_stability")
    try:
        extenders = device_utils.get_enabled_extenders(initialize)
        if not extenders:
            report_logger.print_error("No backhaul extenders are marked present in the database")
            return
        interval = POLL_INTERVAL_SEC
        duration = TEST_DURATION_SEC
        baseline = {}
        report_logger.print_step("STEP 1: Capture baseline PHY rates for each backhaul link")
        for extender_index, extender in enumerate(extenders, start=1):
            try:
                stored_interface = initialize.read_from_database(extender,"backhaul_interface",)
                if not stored_interface:
                    report_logger.print_error(
                        f"FAIL: {extender}: required backhaul configuration is missing from platform.yaml")
                    continue
                interfaces = [stored_interface]
            except Exception as err:
                report_logger.print_error(f"Unable to discover required backhaul configuration for '{extender}': {err}")
                continue
            for interface in interfaces:
                try:
                    state = initialize.get_backhaul_interface_details(extender,interface,)
                except Exception as err:
                    report_logger.print_error(f"Unable to capture baseline PHY rates for '{extender}': {err}")
                    continue
                report_logger.print_info(f"INFO: Baseline extender #{extender_index} {extender}: {state}")
                if not state["connected"]:
                    report_logger.print_error(f"Backhaul link is not connected for '{extender}'")
                    continue
                current_rates = {"tx_mbps": rate_to_mbps(*state["tx_rate"]) if state["tx_rate"] else None, "rx_mbps": rate_to_mbps(*state["rx_rate"]) if state["rx_rate"] else None}
                error = validate_phy_rates(current_rates)
                if error:
                    report_logger.print_error(f"{extender}: {error}")
                    continue
                baseline[(extender, interface)] = current_rates
                report_logger.print_success(f"PASS: Captured baseline PHY rates for {extender} (TX={current_rates['tx_mbps']} Mbps, RX={current_rates['rx_mbps']} Mbps)")
        report_logger.print_info(f"INFO: Baseline PHY rates captured for {len(baseline)} backhaul link(s)")
        report_logger.print_step("STEP 2: Monitor backhaul PHY rates")
        start = time.time()
        poll = 0
        while time.time() - start < duration:
            poll += 1
            for link_index, ((extender, interface),baseline_rates,) in enumerate(baseline.items(), start=1):
                try:
                    report_logger.print_step(f"STEP 2.{poll}.{link_index}: Validate PHY rates for {extender}")
                    state = initialize.get_backhaul_interface_details(extender,interface,)
                except Exception as err:
                    report_logger.print_error(f"{extender}: state collection failed: {err}")
                    continue
                report_logger.print_info(
                    f"INFO: Poll #{poll}, link #{link_index} {extender}: {state}")
                if not state["connected"]:
                    report_logger.print_error(f"{extender}: backhaul link disconnected")
                    continue
                current_rates = {"tx_mbps": rate_to_mbps(*state["tx_rate"]) if state["tx_rate"] else None, "rx_mbps": rate_to_mbps(*state["rx_rate"]) if state["rx_rate"] else None}
                error = validate_phy_rates(current_rates=current_rates,baseline_rates=baseline_rates,)
                if error:
                    report_logger.print_error(f"{extender}: {error}")
                else:
                    report_logger.print_success(f"PASS: {extender} TX={current_rates['tx_mbps']} Mbps RX={current_rates['rx_mbps']} Mbps")
            time.sleep(interval)
        report_logger.print_step("STEP 3: Validate final PHY rates against baseline")
        for link_index, ((extender, interface),baseline_rates,) in enumerate(baseline.items(), start=1):
            try:
                report_logger.print_info(f"INFO: Final state collection for link #{link_index} {extender}")
                state = initialize.get_backhaul_interface_details(extender,interface,)
            except Exception as err:
                report_logger.print_error(f"{extender}:final state collection failed: {err}")
                continue
            if not state["connected"]:
                report_logger.print_error(f"{extender}: backhaul link disconnected")
                continue
            current_rates = {"tx_mbps": rate_to_mbps(*state["tx_rate"]) if state["tx_rate"] else None, "rx_mbps": rate_to_mbps(*state["rx_rate"]) if state["rx_rate"] else None}
            error = validate_phy_rates(current_rates=current_rates,baseline_rates=baseline_rates,)
            if error:
                report_logger.print_error(f"{extender}: {error}")
            else:
                report_logger.print_success(f"PASS: Final PHY-rate validation passed for extender '{extender}' (TX={current_rates['tx_mbps']} Mbps, RX={current_rates['rx_mbps']} Mbps; baseline TX={baseline_rates['tx_mbps']} Mbps, RX={baseline_rates['rx_mbps']} Mbps)")
    finally:
        report_logger.print_test("Exiting test_em_backhaul_phy_rate_stability")