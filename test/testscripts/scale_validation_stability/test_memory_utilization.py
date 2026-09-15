"""Memory utilization stability test for the scale topology."""

import sys
import time
from pathlib import Path

import pytest

from zaero.utils import zi_logger

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import POLL_INTERVAL_SEC, SCALE_AGENTS, TEST_DURATION_SEC
from utility import assert_memory_limits, collect_memory, device_present


def test_em_scale_memory_utilization(initialize):
	"""Verify memory remains within limits for the configured scale duration."""
	agents = [
		agent for agent in SCALE_AGENTS
		if device_present(initialize, agent)
	]
	poll_interval_sec = POLL_INTERVAL_SEC
	test_duration_sec = TEST_DURATION_SEC
	devices = ["controller", *agents]
	used_history = {device: [] for device in devices}

	zi_logger.log("STEP: Step 1: Capture baseline memory statistics")
	baseline = {}
	for device in devices:
		try:
			baseline[device] = collect_memory(initialize, device)
			assert_memory_limits(baseline[device], used_history[device])
			zi_logger.log(
				f"SUCCESS: Baseline {device}: "
				f"available={baseline[device]['available_percent']:.1f}%, "
				f"used={baseline[device]['used_percent']:.1f}%"
			)
		except Exception as err:
			pytest.fail(f"Baseline memory collection failed on {device}: {err}")
	print(f"BASELINE MEMORY: {baseline}")

	zi_logger.log("STEP: Steps 2-4: Monitor memory during scale traffic")
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
				zi_logger.log(
					f"SUCCESS: Sample #{sample_count} {device}: "
					f"available={snapshot['available_percent']:.1f}%, "
					f"used={snapshot['used_percent']:.1f}%"
				)
			except Exception as err:
				pytest.fail(f"Memory monitoring failed on {device}: {err}")
		time.sleep(poll_interval_sec)

	zi_logger.log("STEP: Step 5: Capture final memory statistics")
	final = {}
	for device in devices:
		try:
			final[device] = collect_memory(initialize, device)
			assert_memory_limits(
				final[device], used_history[device], baseline[device]
			)
		except Exception as err:
			pytest.fail(f"Final memory collection failed on {device}: {err}")
	print(f"FINAL MEMORY: {final}")
	zi_logger.log("SUCCESS: Memory utilization remained within limits — PASS")
