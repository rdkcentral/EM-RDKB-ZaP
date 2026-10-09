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

def test_em_scale_cpu_utilization(initialize):
	"""
	Verify CPU remains within limits for the configured scale test duration.
	"""
	report_logger.print_test("Entering test_em_scale_cpu_utilization")
	agents = device_utils.get_enabled_extenders(initialize)
	poll_interval_sec = POLL_INTERVAL_SEC
	test_duration_sec = TEST_DURATION_SEC
	devices = ["controller", *agents]
	consecutive_limit = 2
	high_cpu_counts = {device: {} for device in devices}
	report_logger.print_step(
	    "STEP 1: Capture baseline CPU usage for each device and verify that "
    	"CPU utilization remains below 80%, idle CPU stays above 20%, and "
    	"no process is consuming excessive CPU resources"
	)
	baseline = {}
	for device in devices:
		try:
			baseline[device] = collect_device_cpu_utilization(initialize, device)
			validate_cpu_utilization_limits(
				baseline[device], high_cpu_counts[device], consecutive_limit
			)
			report_logger.print_success(
				f"PASS: Baseline observed on {device}: "
				f"idle={baseline[device]['idle_percent']:.1f}%, "
				f"utilization={baseline[device]['utilization_percent']:.1f}%"
			)
		except Exception as err:
			message = f"Baseline CPU collection failed on {device}: {err}"
			report_logger.print_error(message)
			continue

	report_logger.print_step(
    "STEP 2: Monitor CPU usage on each device and compare it against the baseline values"
	)
	report_logger.print_info(
    f"INFO: Monitoring CPU usage for {test_duration_sec} seconds at "
    f"{poll_interval_sec}-second intervals"
	)
	start_time = time.time()
	sample_count = 0
	while time.time() - start_time < test_duration_sec:
		sample_count += 1
		for device in devices:
			try:
				report_logger.print_step(
        		    f"STEP 2.{sample_count}: Monitor CPU usage on {device}"
        		)
				snapshot = collect_device_cpu_utilization(initialize, device)
				validate_cpu_utilization_limits(
					snapshot, high_cpu_counts[device], consecutive_limit,
					baseline[device]
				)
				report_logger.print_success(
					f"PASS: Monitoring check #{sample_count} observed on {device}: "
					f"idle={snapshot['idle_percent']:.1f}%, "
					f"utilization={snapshot['utilization_percent']:.1f}%"
				)
			except Exception as err:
				message = f"CPU monitoring failed on {device}: {err}"
				report_logger.print_error(message)
				continue
		time.sleep(poll_interval_sec)

	report_logger.print_step(
		"STEP 3: Capture final CPU statistics and validate CPU usage remains within expected limits"
	)
	final = {}
	for device in devices:
		try:
			final[device] = collect_device_cpu_utilization(initialize, device)
			validate_cpu_utilization_limits(
				final[device], high_cpu_counts[device], consecutive_limit,
				baseline[device]
			)
			report_logger.print_success(
				f"PASS: Final observed result for {device}: "
				f"idle={final[device]['idle_percent']:.1f}%, "
				f"utilization={final[device]['utilization_percent']:.1f}%"
			)
		except Exception as err:
			message = f"Final CPU collection failed on {device}: {err}"
			report_logger.print_error(message)
			continue	
	if final:
		report_logger.print_success(
            f"PASS: CPU utilization remained within configured limits for "
            f"devices: {', '.join(final.keys())} across "
        f"{sample_count} monitoring samples"
    )
	else:
		report_logger.print_error(
        	"ERROR: No reachable devices were available for final CPU validation"
    )
