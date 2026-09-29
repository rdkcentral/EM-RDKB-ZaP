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
"""CPU utilization stability test for the scale topology."""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import POLL_INTERVAL_SEC, SCALE_AGENTS, TEST_DURATION_SEC
from rdkbmeshzap.common_utils import report_logger

from utility import (
	assert_cpu_limits, collect_cpu, device_present,
)


def test_em_scale_cpu_utilization(initialize):
	"""Verify CPU remains within limits for the configured scale test duration."""
	report_logger.print_test("Entering test_em_scale_cpu_utilization")
	agents = [
		agent for agent in SCALE_AGENTS
		if device_present(initialize, agent)
	]
	poll_interval_sec = POLL_INTERVAL_SEC
	test_duration_sec = TEST_DURATION_SEC
	devices = ["controller", *agents]
	consecutive_limit = 2
	high_cpu_counts = {device: {} for device in devices}

	report_logger.print_step("Step 1: Capture baseline CPU statistics")
	report_logger.print_step(
		"Expected Result: Each device must have more than 20% idle CPU, "
		"less than 80% utilization, and no sustained high-CPU process"
	)
	baseline = {}
	for device in devices:
		try:
			baseline[device] = collect_cpu(initialize, device)
			assert_cpu_limits(
				baseline[device], high_cpu_counts[device], consecutive_limit
			)
			report_logger.print_success(
				f"Baseline observed on {device}: "
				f"idle={baseline[device]['idle_percent']:.1f}%, "
				f"utilization={baseline[device]['utilization_percent']:.1f}%"
			)
		except Exception as err:
			message = f"Baseline CPU collection failed on {device}: {err}"
			report_logger.print_error(message)
			pytest.fail(message)

	report_logger.print_step("Steps 2-4: Monitor CPU during scale traffic")
	report_logger.print_step(
		f"Expected Result: CPU remains within limits for approximately "
		f"{test_duration_sec} seconds, sampled every {poll_interval_sec} seconds"
	)
	start_time = time.time()
	sample_count = 0
	while time.time() - start_time < test_duration_sec:
		sample_count += 1
		for device in devices:
			try:
				snapshot = collect_cpu(initialize, device)
				assert_cpu_limits(
					snapshot, high_cpu_counts[device], consecutive_limit,
					baseline[device]
				)
				report_logger.print_success(
					f"Sample #{sample_count} observed on {device}: "
					f"idle={snapshot['idle_percent']:.1f}%, "
					f"utilization={snapshot['utilization_percent']:.1f}%"
				)
			except Exception as err:
				message = f"CPU monitoring failed on {device}: {err}"
				report_logger.print_error(message)
				pytest.fail(message)
		time.sleep(poll_interval_sec)

	report_logger.print_step("Step 5: Capture final CPU statistics")
	final = {}
	for device in devices:
		try:
			final[device] = collect_cpu(initialize, device)
			assert_cpu_limits(
				final[device], high_cpu_counts[device], consecutive_limit,
				baseline[device]
			)
			report_logger.print_success(
				f"Final observed result for {device}: "
				f"idle={final[device]['idle_percent']:.1f}%, "
				f"utilization={final[device]['utilization_percent']:.1f}%"
			)
		except Exception as err:
			message = f"Final CPU collection failed on {device}: {err}"
			report_logger.print_error(message)
			pytest.fail(message)

	report_logger.print_success(
		f"CPU utilization remained within configured limits for all "
		f"{len(devices)} devices across {sample_count} monitoring samples"
	)
	report_logger.print_test("Exiting test_em_scale_cpu_utilization")
