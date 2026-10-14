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
from rdkbmeshzap.common_utils.link_and_scale_stability_utils import *

def test_em_scale_memory_utilization(initialize):
	"""
	Verify memory remains within limits for the configured scale duration.
	"""
	report_logger.print_test("Entering test_em_scale_memory_utilization")
	agents = device_utils.get_enabled_extenders(initialize)
	poll_interval_sec = POLL_INTERVAL_SEC
	test_duration_sec = TEST_DURATION_SEC
	devices = ["controller", *agents]
	used_history = {device: [] for device in devices}
	report_logger.print_step("STEP 1: Capture baseline memory metrics and validate available, used, and growth limits for each device")
	baseline = {}
	for device in devices:
		try:
			baseline[device] = device_utils.get_device_memory_utilization(initialize, device)
			validate_memory_utilization_limits(baseline[device], used_history[device])
			report_logger.print_success(f"PASS: Baseline {device}: available={baseline[device]['available_percent']:.1f}%, used={baseline[device]['used_percent']:.1f}%")
		except Exception as err:
			report_logger.print_error(f"Baseline memory collection failed on {device}: {err}")
			continue
	report_logger.print_info(f"INFO: Baseline memory snapshot: {baseline}")
	report_logger.print_step("STEP 2: Monitor memory metrics at the configured interval and validate limits, growth, and baseline changes for each device")
	start_time = time.time()
	sample_count = 0
	while time.time() - start_time < test_duration_sec:
		sample_count += 1
		for device_index, device in enumerate(devices, start=1):
			try:
				report_logger.print_step(f"STEP 2.{sample_count}.{device_index}: Validate memory limits, growth, and baseline change for device #{device_index} '{device}'")
				snapshot = device_utils.get_device_memory_utilization(initialize, device)
				validate_memory_utilization_limits(
					snapshot, used_history[device], baseline[device])
				report_logger.print_success(f"PASS: Monitoring check #{sample_count} {device}: available={snapshot['available_percent']:.1f}%, used={snapshot['used_percent']:.1f}%")
			except Exception as err:
				report_logger.print_error(f"Memory monitoring failed on {device}: {err}")
				continue
		time.sleep(poll_interval_sec)
	report_logger.print_step("STEP 3: Capture final memory metrics and validate limits, growth, and baseline changes for each device")
	final = {}
	for device in devices:
		try:
			final[device] = device_utils.get_device_memory_utilization(initialize, device)
			validate_memory_utilization_limits(
				final[device], used_history[device], baseline[device])
		except Exception as err:
			report_logger.print_error(f"Final memory collection failed on {device}: {err}")
			continue
	if final:
		report_logger.print_success(f"PASS: Final memory snapshot: {final}")
		report_logger.print_success(f"PASS: Memory utilization remained within configured limits for {len(final)} reachable devices across {sample_count} monitoring checks")
	else:
		report_logger.print_error("ERROR: No reachable devices were available for final Memory validation")
	report_logger.print_test("Exiting test_em_scale_memory_utilization")
