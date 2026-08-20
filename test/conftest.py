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
import pytest_html
from zaero.utils import zi_logger
from pathlib import Path

@pytest.fixture(scope='session', autouse=True)
def initialize():
    zi_logger.set_log_state(False)
    zaero_obj = zaero.zaero()
    current_file = Path(__file__)
    current_directory = current_file.parent / "config"
    zaero_obj.initialize_database(current_directory)
    platform = zaero_obj.read_from_database("controller", "platform")
    zaero_obj.configure_platform(platform)
    devices = zaero_obj.get_testbed_devices()
    for device in devices:
        zaero_obj.connect_with_device(device)
    # zaero_obj.connect_with_device("controller")
    # zaero_obj.connect_with_device("extender1")
    # zaero_obj.connect_with_device("extender2")
    #zaero_obj.connect_with_device("controller_wlan_client_1")
    pcap_log_dir = zaero_obj.read_from_database("controller", 'pcap_remote_dir')
    zaero_obj.set_sniffer_log_location("controller", pcap_log_dir)
    zaero_obj.ui_start_playwright("controller")
    time.sleep(1)
    zaero_obj.ui_open_browser("controller")
    time.sleep(1)
    yield zaero_obj
    zaero_obj.ui_close_browser("controller")
    zaero_obj.ui_stop_playwright("controller")
    del(zaero_obj)

@pytest.fixture(scope='function', autouse=True)
def test_setup(initialize):
    initialize.ui_open_context("controller")
    time.sleep(1)
    initialize.ui_open_page("controller")
    time.sleep(1)
    yield initialize
    initialize.ui_close_page("controller")
    initialize.ui_close_context("controller")
    try:
        initialize.stop_frame_capture("controller")
    except Exception as err:
        zi_logger.log(f"stop_frame_capture failed during teardown: {err}")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    # Start each test with a clean failure buffer.
    zi_logger.clear_error_logs()
    yield

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    errors = zi_logger.get_error_logs()
    if errors:
        report.outcome = "failed"
        report.longrepr = "Error logs found:\n" + "\n".join(errors)

    # Make the report available to fixtures/teardown that want to
    # inspect the outcome of the test they're running in.
    setattr(item, "rep_call", report)

    extra = getattr(report, "extras", None)
    if extra is None:
        extra = getattr(report, "extra", [])

    if report.failed:
        message = '<span style="color:red; font-weight:bold;">FAIL</span>'
    elif report.passed:
        message = '<span style="color:green; font-weight:bold;">PASS</span>'
    elif report.skipped:
        message = '<span style="color:orange; font-weight:bold;">SKIPPED</span>'
    else:
        message = '<span>UNKNOWN</span>'

    extra.append(pytest_html.extras.html(message))
    report.extras = extra
    


def pytest_html_results_table_html(report, data):
    if report.when != "call":
        return

    new_data = []

    # Failure traceback (includes the zi_logger error summary above).
    if report.failed and hasattr(report, "longrepr"):
        new_data.append(f"<div>{report.longrepr}</div>")

    # Colorize captured stdout lines emitted by zi_logger.
    if hasattr(report, "capstdout"):
        formatted_lines = []
        for line in report.capstdout.splitlines():
            if "PASS:" in line:
                formatted_lines.append(
                    f'<span style="color:green; font-weight:bold;">{line}</span>'
                )
            elif "FAIL:" in line:
                formatted_lines.append(
                    f'<span style="color:red; font-weight:bold;">{line}</span>'
                )
            else:
                formatted_lines.append(line)

        html = "<br>".join(formatted_lines)
        new_data.append(f"<div>{html}</div>")

    data.clear()
    data.extend(new_data)
