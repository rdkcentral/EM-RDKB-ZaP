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
import pytest
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
	failures = []

	report_logger.print_step(
		"STEP 1: Capture baseline memory statistics for each device and" 
		 "verify available and used memory are within expected limits"
	)
	baseline = {}
	for device in devices:
		try:
			baseline[device] = collect_device_memory_utilization(initialize, device)
			validate_memory_utilization_limits(baseline[device], used_history[device])
			report_logger.print_success(
				f"PASS: Baseline {device}: "
				f"available={baseline[device]['available_percent']:.1f}%, "
				f"used={baseline[device]['used_percent']:.1f}%"
			)
		except Exception as err:
			message = f"Baseline memory collection failed on {device}: {err}"
			report_logger.print_error(message)
			continue
	report_logger.print_info(f"INFO: Baseline memory snapshot: {baseline}")

	report_logger.print_step(
		"STEP 2: Monitor each device at the configured interval and compare memory "
		"usage with its baseline"
	)
	start_time = time.time()
	sample_count = 0
	while time.time() - start_time < test_duration_sec:
		sample_count += 1
		for device in devices:
			try:
				report_logger.print_step(
					f"STEP 2.{sample_count}: Monitor memory usage on {device}"
				)
				snapshot = collect_device_memory_utilization(initialize, device)
				validate_memory_utilization_limits(
					snapshot, used_history[device], baseline[device]
				)
				report_logger.print_success(
					f"PASS: Monitoring check #{sample_count} {device}: "
					f"available={snapshot['available_percent']:.1f}%, "
					f"used={snapshot['used_percent']:.1f}%"
				)
			except Exception as err:
				message = f"Memory monitoring failed on {device}: {err}"
				report_logger.print_error(message)
				continue
		time.sleep(poll_interval_sec)

	report_logger.print_step(
		"STEP 3: Capture final memory statistics and ensure memory usage remains within expected limits"
	)
	final = {}
	for device in devices:
		try:
			final[device] = collect_device_memory_utilization(initialize, device)
			validate_memory_utilization_limits(
				final[device], used_history[device], baseline[device]
			)
		except Exception as err:
			message = f"Final memory collection failed on {device}: {err}"
			report_logger.print_error(message)
			continue

	if final:
		report_logger.print_success(
			f"PASS: Final CPU snapshot: {final}"
	    )
		report_logger.print_success(
			f"PASS: CPU utilization remained within configured limits for "
			f"{len(final)} reachable devices across {sample_count} monitoring samples"
    	)
	else:
		report_logger.print_error(
        "ERROR: No reachable devices were available for final CPU validation"
    	)
	report_logger.print_test("Exiting test_em_scale_cpu_utilization")
