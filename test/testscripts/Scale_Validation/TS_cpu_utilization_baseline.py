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


def test_em_scale_cpu_utilization_baseline(initialize):
    """Validate one CPU utilization snapshot for each scale device."""
    report_logger.print_test("Entering test_em_scale_cpu_utilization_baseline")
    try:
        report_logger.print_step("STEP 1: Discover the enabled scale setup and devices")
        scale_setup = get_enabled_scale_setup(initialize)
        agents = device_utils.get_enabled_extenders(initialize)
        devices = ["controller", *agents]
        expected_agents = scale_setup["expected_agent_count"]
        report_logger.print_info(f"INFO: Scale setup={scale_setup}; devices={', '.join(devices)}; expected_extenders={expected_agents}; discovered_extenders={len(agents)}")
        if len(agents) != expected_agents:
            report_logger.print_error(f"FAIL: Scale device count mismatch: expected {expected_agents} extenders, discovered {len(agents)}")
            return
        report_logger.print_success(f"PASS: Discovered controller and {len(agents)} expected extender(s)")
        consecutive_limit = 2
        high_cpu_counts = {device: {} for device in devices}
        validated_devices = []
        report_logger.print_step("STEP 2: Capture and validate one CPU snapshot for each scale device")
        for device in devices:
            report_logger.print_step(f"STEP 2.{devices.index(device) + 1}: Collect CPU utilization from {device}")
            try:
                snapshot = device_utils.get_device_cpu_utilization(initialize, device)
                snapshot["device"] = device
                validate_cpu_utilization_limits(snapshot, high_cpu_counts[device], consecutive_limit)
                validated_devices.append(device)
                report_logger.print_success(f"PASS: Baseline observed on {device}: idle={snapshot['idle_percent']:.1f}%, utilization={snapshot['utilization_percent']:.1f}%")
            except Exception as error:
                report_logger.print_error(f"Baseline CPU collection failed on {device}: {error}")

        report_logger.print_step("STEP 3: Summarize scale-device CPU baseline results")
        if validated_devices:
            report_logger.print_success("PASS: CPU baseline validated for devices: " + ", ".join(validated_devices))
            if len(validated_devices) != len(devices):
                missing_devices = sorted(set(devices) - set(validated_devices))
                report_logger.print_error(f"FAIL: CPU baseline missing for scale devices: {', '.join(missing_devices)}")
        else:
            report_logger.print_error("ERROR: No reachable devices were available for CPU baseline validation")
    finally:
        report_logger.print_test("Exiting test_em_scale_cpu_utilization_baseline")
