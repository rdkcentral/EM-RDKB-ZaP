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
import zaero
import pytest
import time
from zaero.utils.database import Database
from pathlib import Path
from packet_analyzer.protocol_validation import common_protocol_validation
from rdkbmeshzap.common_utils import report_logger

_setup_output = ""

@pytest.fixture(scope='session', autouse=True)
def initialize():
    zaero_obj = zaero.zaero()
    current_file = Path(__file__)
    current_directory = current_file.parent / "config"
    zaero_obj.initialize_database(current_directory)
    platform = zaero_obj.read_from_database("controller", "platform")
    zaero_obj.configure_platform(platform)
    for device_name, device_data in Database._Database__database.items():
        device_data.setdefault("device_present", device_name != "protocol")
    pcap_log_dir = zaero_obj.read_from_database("controller", 'pcap_remote_dir')
    pcap_local_dir = zaero_obj.read_from_database("controller", 'pcap_local_dir')
    Path(pcap_local_dir).mkdir(parents=True, exist_ok=True)
    zaero_obj.pcap_log_dir = pcap_log_dir
    yield zaero_obj

@pytest.fixture(scope='function', autouse=True)
def test_setup(request, initialize):
    if request.node.get_closest_marker("connectivity_check"):
        yield initialize
        return
    if not getattr(initialize, "accessibility_validated", False):
        pytest.skip("Setup accessibility validation did not pass")
    initialize.set_sniffer_log_location("controller", initialize.pcap_log_dir)
    initialize.ui_start_playwright("controller")
    initialize.playwright_started = True
    time.sleep(1)
    initialize.ui_open_browser("controller")
    initialize.browser_started = True
    time.sleep(1)
    initialize.ui_open_context("controller")
    time.sleep(1)
    initialize.ui_open_page("controller")
    time.sleep(1)
    try:
        yield initialize
    finally:
        initialize.ui_close_page("controller")
        initialize.ui_close_context("controller")
        if getattr(initialize, "browser_started", False):
            try:
                initialize.ui_close_browser("controller")
            finally:
                initialize.browser_started = False
        if getattr(initialize, "playwright_started", False):
            try:
                initialize.ui_stop_playwright("controller")
            finally:
                initialize.playwright_started = False

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    # Start each test with a clean failure buffer.
    report_logger.clear_error_logs()
    yield

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if item.get_closest_marker("connectivity_check") is not None:
        global _setup_output
        _setup_output = ""
        _setup_output = "\n".join(
            content
            for section_name, content in getattr(report, "sections", [])
            if section_name in ("Captured stdout call", "Captured log call")
        )
        report.connectivity_check = True
        return

    errors = report_logger.get_error_logs()
    if errors:
        report.outcome = "failed"
        report.longrepr = "Error logs found:\n" + "\n".join(errors)

def pytest_html_results_table_html(report, data):
    if report.when != "call":
        data.clear()
        return

    if getattr(report, "connectivity_check", False):
        data.clear()
        return

    new_data = []

    if report.failed and hasattr(report, "longrepr"):
        new_data.append(f"<div>{report.longrepr}</div>")

    call_output = "\n".join(
        content
        for section_name, content in getattr(report, "sections", [])
        if section_name in ("Captured stdout call", "Captured log call")
    )
    if call_output:
        report_lines = call_output.splitlines()
        html = "<br>".join(
            report_logger.format_report_line(line)
            for line in report_lines
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
    report_logger.print_step("========== Start Frame Capture ==========")
    backhaul_iface = initialize.read_from_database("controller", "backhaul_capture_iface")
    frame_filter = initialize.read_from_database("controller", "filter_1905")
    initialize.start_frame_capture("controller" ,backhaul_iface, frame_filter, f"{request.node.name}.pcap")
    yield True
    report_logger.print_step("========== Stop Frame Capture ==========")
    initialize.stop_frame_capture("controller")
    report_logger.print_step(f"Frame Capture saved as {request.node.name}.pcap")
    report_logger.print_step("Download Captured pcap file from DUT to local machine")
    initialize.download_captured_pcap("controller", f"{request.node.name}.pcap")
    initialize.delete_captured_pcap("controller", f"{request.node.name}.pcap")
    CPV = initialize.read_from_database("protocol", "common_protocol_validation")
    if CPV:
        report_logger.print_step("========== Start Common Protocol Validation ==========")
        try:
            common_protocol_validation(f"{request.node.name}.pcap")
        except Exception as err:
            report_logger.print_error(f"Protocol Validation Failed : {err}")
            pytest.fail(f"Protocol Validation Failed : {err}")
        report_logger.print_step("========== Stop Common Protocol Validation ==========")

    if hasattr(request.node, 'protocol_specific_function'):
        try:
            request.node.protocol_specific_function(f"{request.node.name}.pcap")
        except Exception as ERR:
            raise RuntimeError(f"{ERR}")
