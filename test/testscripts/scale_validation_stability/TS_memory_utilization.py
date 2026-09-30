# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
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
"""Memory utilization stability test for the scale topology."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rdkbmeshzap.common_utils import report_logger

from utility import (
	assert_memory_limits, collect_memory, get_present_agents, get_test_parameters,

)


def test_em_scale_memory_utilization(initialize):
	"""Verify memory remains within limits for the configured scale duration."""
	report_logger.print_test("Entering test_em_scale_memory_utilization")
	agents = get_present_agents(initialize)
	test_parameters = get_test_parameters(initialize)
	poll_interval_sec = test_parameters["poll_interval_sec"]
	test_duration_sec = test_parameters["test_duration_sec"]
	devices = ["controller", *agents]
	used_history = {device: [] for device in devices}

	report_logger.print_step("Step 1: Capture baseline memory statistics")
	baseline = {}
	for device in devices:
		try:
			baseline[device] = collect_memory(initialize, device)
			assert_memory_limits(baseline[device], used_history[device])
			report_logger.print_success(
				f"Baseline {device}: "
				f"available={baseline[device]['available_percent']:.1f}%, "
				f"used={baseline[device]['used_percent']:.1f}%"
			)
		except Exception as err:
			message = f"Baseline memory collection failed on {device}: {err}"
			report_logger.print_error(message)
			pytest.fail(message)
	report_logger.print_info(f"Baseline memory snapshot: {baseline}")

	report_logger.print_step("Steps 2-4: Monitor memory during scale traffic")
	start_time = time.time()
	sample_count = 0
	while time.time() - start_time < test_duration_sec:
		sample_count += 1
		for device in devices:
			try:
				snapshot = collect_memory(initialize, device)
				assert_memory_limits(
					snapshot, used_history[device], baseline[device]
				)
				report_logger.print_success(
					f"Sample #{sample_count} {device}: "
					f"available={snapshot['available_percent']:.1f}%, "
					f"used={snapshot['used_percent']:.1f}%"
				)
			except Exception as err:
				message = f"Memory monitoring failed on {device}: {err}"
				report_logger.print_error(message)
				pytest.fail(message)
		time.sleep(poll_interval_sec)

	report_logger.print_step("Step 5: Capture final memory statistics")
	final = {}
	for device in devices:
		try:
			final[device] = collect_memory(initialize, device)
			assert_memory_limits(
				final[device], used_history[device], baseline[device]
			)
		except Exception as err:
			message = f"Final memory collection failed on {device}: {err}"
			report_logger.print_error(message)
			pytest.fail(message)
	report_logger.print_success(f"Final memory snapshot: {final}")
	report_logger.print_success("Memory utilization remained within limits")
	report_logger.print_test("Exiting test_em_scale_memory_utilization")
