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

from rdkbmeshzap.common_utils import device_utils, report_logger
from rdkbmeshzap.common_utils.scale_validation_utils import *

def test_em_scale_configuration_propagation_baseline(initialize):
    """Set and validate one propagation cycle for each configuration parameter."""
    report_logger.print_test("Entering test_em_scale_configuration_propagation_baseline")
    agents = []
    originals = {}
    try:
        report_logger.print_step("STEP 1: Validate the enabled scale setup and discover scale extenders")
        scale_setup = get_enabled_scale_setup(initialize)
        agents = device_utils.get_enabled_extenders(initialize)
        expected_agents = scale_setup["expected_agent_count"]
        report_logger.print_info(f"INFO: Scale setup={scale_setup}; discovered {len(agents)} scale extenders; expected={expected_agents}")
        if not agents:
            report_logger.print_error("No enabled extenders are available for propagation baseline validation")
            return
        if len(agents) != expected_agents:
            report_logger.print_error(f"FAIL: Scale device count mismatch: expected {expected_agents} extenders, discovered {len(agents)}")
            report_logger.print_info(f"INFO: Continuing validation with the {len(agents)} available scale extender(s)")
        else:
            report_logger.print_success(f"PASS: Discovered {len(agents)} expected scale extender(s)")
        report_logger.print_step("STEP 2: Capture controller configuration and validate the initial propagation")
        baseline_failures = []
        for parameter in CONFIGURATION_PARAMETERS:
            try:
                report_logger.print_step(f"STEP 2.1: Getting {parameter} from controller")
                controller_value = get_scale_configuration_parameter(initialize, "controller", parameter)
                originals[parameter] = controller_value
                report_logger.print_step(f"STEP 2.2: Checking {parameter} on extenders {sorted(agents)}")
                mismatches, observed = get_scale_configuration_mismatches(initialize, agents, parameter, controller_value)
                if mismatches:
                    baseline_failures.extend(f"Baseline {parameter}: {mismatch}" for mismatch in mismatches)
                else:
                    report_logger.print_success(f"PASS: Baseline {parameter}={controller_value} matches all extenders")
                report_logger.print_info(f"INFO: Baseline {parameter} values: controller={controller_value}, extenders={observed}")
            except Exception as error:
                baseline_failures.append(f"Unable to capture {parameter} baseline: {error}")
        if baseline_failures:
            for failure in baseline_failures:
                report_logger.print_error(failure)
            report_logger.print_info("INFO: Baseline mismatches found; continuing with propagation validation")
        else:
            report_logger.print_success("PASS: Extender configuration baseline captured")
        report_logger.print_step("STEP 3: Set and validate one propagation cycle for each parameter")
        for parameter, original_value in originals.items():
            try:
                report_logger.print_step(f"STEP 3.1: Setting controller {parameter} from {original_value}")
                target_value = set_controller_scale_configuration_parameter(initialize, parameter, original_value)
                report_logger.print_step(f"STEP 3.2: Checking controller {parameter} update")
                controller_updated, controller_value = wait_for_controller_scale_configuration_update(initialize, parameter, target_value)
                if not controller_updated:
                    report_logger.print_error(f"Controller {parameter} update failed: expected={target_value}, observed={controller_value}")
                    continue
                report_logger.print_success(f"PASS: Controller {parameter} updated to {controller_value}")
                report_logger.print_step(f"STEP 3.3: Checking {parameter} propagation on extenders {sorted(agents)}")
                propagated, observed = wait_for_scale_configuration_propagation(initialize, agents, parameter, target_value)
                if propagated:
                    report_logger.print_success(f"PASS: {parameter} propagated to controller and {len(agents)} extenders")
                else:
                    report_logger.print_error(f"{parameter} did not propagate to all extenders: {observed}")
            except Exception as error:
                report_logger.print_error(f"{parameter} propagation validation failed: {error}")
    finally:
        report_logger.print_step("STEP 4: Restore the original configuration")
        for parameter, original_value in reversed(list(originals.items())):
            try:
                report_logger.print_step(f"STEP 4.1: Restoring controller {parameter} to {original_value}")
                restore_controller_scale_configuration_parameter(initialize, parameter, original_value)
                report_logger.print_step(f"STEP 4.2: Checking restored {parameter} on controller")
                restored_controller_value = get_scale_configuration_parameter(initialize, "controller", parameter)
                if str(restored_controller_value) == str(original_value):
                    report_logger.print_success(f"PASS: Controller {parameter} restored to {restored_controller_value}")
                else:
                    report_logger.print_error(f"Controller {parameter} restoration mismatch: expected={original_value}, observed={restored_controller_value}")
                report_logger.print_step(f"STEP 4.3: Checking restored {parameter} propagation on extenders {sorted(agents)}")
                restored, observed = wait_for_scale_configuration_propagation(initialize, agents, parameter, original_value)
                if restored:
                    report_logger.print_success(f"PASS: Restored {parameter} across all extenders")
                else:
                    report_logger.print_error(f"Unable to restore {parameter}: {observed}")
            except Exception as error:
                report_logger.print_error(f"Failed to restore {parameter}: {error}")
        report_logger.print_test("Exiting test_em_scale_configuration_propagation_baseline")
