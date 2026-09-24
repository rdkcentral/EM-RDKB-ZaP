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
import zaero
from zaero.utils import zi_logger
from zaero.utils.database import Database
from packet_analyzer.protocol_validation import common_protocol_validation
from rdkbmeshzap.common_utils import report_logger
import time
from html import escape
from pathlib import Path

_setup_output = ""

@pytest.fixture(scope="session", autouse=True)
def initialize():
	zaero_obj = zaero.zaero()
	current_directory = Path(__file__).parent / "config"
	zaero_obj.initialize_database(current_directory)
	platform = zaero_obj.read_from_database("controller", "platform")
	zaero_obj.configure_platform(platform)
	for device_name, device_data in Database._Database__database.items():
		device_data.setdefault(
			"device_present", device_name not in {"protocol", "test_parameters"}
		)
	pcap_log_dir = zaero_obj.read_from_database("controller", "pcap_remote_dir")
	pcap_local_dir = zaero_obj.read_from_database("controller", "pcap_local_dir")
	Path(pcap_local_dir).mkdir(parents=True, exist_ok=True)
	zaero_obj.pcap_log_dir = pcap_log_dir
	yield zaero_obj


@pytest.fixture(scope="function", autouse=True)
def test_setup(request, initialize):
	if request.node.get_closest_marker("connectivity_check"):
		yield initialize
		return
	if not getattr(initialize, "accessibility_validated", False):
		pytest.skip("Setup accessibility validation did not pass")

	initialize.set_sniffer_log_location("controller", initialize.pcap_log_dir)
	playwright_started = browser_started = False
	try:
		initialize.ui_start_playwright("controller")
		playwright_started = True
		time.sleep(1)
		initialize.ui_open_browser("controller")
		browser_started = True
		time.sleep(1)
		initialize.ui_open_context("controller")
		time.sleep(1)
		initialize.ui_open_page("controller")
		time.sleep(1)
		yield initialize
	finally:
		try:
			initialize.ui_close_page("controller")
		except Exception:
			pass
		try:
			initialize.ui_close_context("controller")
		except Exception:
			pass
		if browser_started:
			try:
				initialize.ui_close_browser("controller")
			except Exception:
				pass
		if playwright_started:
			try:
				initialize.ui_stop_playwright("controller")
			except Exception:
				pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
	report_logger.clear_error_logs()
	zi_logger.clear_error_logs()
	yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
	global _setup_output
	outcome = yield
	report = outcome.get_result()
	if report.when != "call":
		return
	if item.get_closest_marker("connectivity_check"):
		_setup_output = "\n".join(
			content
			for section_name, content in getattr(report, "sections", [])
			if section_name in ("Captured stdout call", "Captured log call")
		)
		report.connectivity_check = True
		return
	errors = report_logger.get_error_logs() + zi_logger.get_error_logs()
	if errors:
		report.outcome = "failed"
		report.longrepr = "Error logs found:\n" + "\n".join(errors)


def pytest_html_results_table_html(report, data):
	if report.when != "call" or getattr(report, "connectivity_check", False):
		data.clear()
		return
	new_data = []
	if report.failed and hasattr(report, "longrepr"):
		new_data.append(f"<div>{escape(str(report.longrepr))}</div>")
	call_output = "\n".join(
		content
		for section_name, content in getattr(report, "sections", [])
		if section_name in ("Captured stdout call", "Captured log call")
	)
	if call_output:
		html = "<br>".join(
			report_logger.format_report_line(line)
			for line in call_output.splitlines()
		)
		new_data.append(f"<div>{html}</div>")
	data.clear()
	data.extend(new_data)


def pytest_html_results_table_row(report, cells):
	if report.when != "call" or getattr(report, "connectivity_check", False):
		cells.clear()


def pytest_html_results_summary(prefix, summary, postfix):
	prefix.append(report_logger.get_report_style())
	if _setup_output:
		setup_html = "<br>".join(
			report_logger.format_report_line(line)
			for line in _setup_output.splitlines()
		)
		postfix.append(
			"<details class=\"setup-accessibility\">"
			"<summary>Setup Accessibility Validation</summary>"
			f"<div>{setup_html}</div>"
			"</details>"
		)


@pytest.fixture
def protocol_validation(request, initialize):
	capture_name = f"{request.node.name}.pcap"
	report_logger.print_step("========== Start Frame Capture ==========")
	backhaul_iface = initialize.read_from_database("controller", "backhaul_capture_iface")
	frame_filter = initialize.read_from_database("controller", "filter_1905")
	initialize.start_frame_capture("controller", backhaul_iface, frame_filter, capture_name)
	yield True
	report_logger.print_step("========== Stop Frame Capture ==========")
	initialize.stop_frame_capture("controller")
	report_logger.print_step(f"Frame Capture saved as {capture_name}")
	initialize.download_captured_pcap("controller", capture_name)
	initialize.delete_captured_pcap("controller", capture_name)
	if initialize.read_from_database("protocol", "common_protocol_validation"):
		report_logger.print_step("========== Start Common Protocol Validation ==========")
		try:
			common_protocol_validation(capture_name)
		except Exception as error:
			report_logger.print_error(f"Protocol Validation Failed: {error}")
			pytest.fail(f"Protocol Validation Failed: {error}")
		report_logger.print_step("========== Stop Common Protocol Validation ==========")
