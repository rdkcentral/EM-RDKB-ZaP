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
from zaero.utils.database import Database
import sys
from pathlib import Path
from packet_analyzer.packet_dissector import *
from packet_analyzer.message_verify import *
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.protocol_validation import *

COMMON_UTILS_PATH = Path(__file__).resolve().parents[1] / "common-utils"
if str(COMMON_UTILS_PATH) not in sys.path:
    sys.path.insert(0, str(COMMON_UTILS_PATH))

@pytest.fixture(scope='session', autouse=True)
def initialize():
    zi_logger.set_log_state(False)
    zaero_obj = zaero.zaero()
    current_file = Path(__file__)
    current_directory = current_file.parent / "config"
    zaero_obj.initialize_database(current_directory)
    platform = zaero_obj.read_from_database("controller", "platform")
    zaero_obj.configure_platform(platform)
    for device_name, device_data in Database._Database__database.items():
        device_data.setdefault("device_present", device_name != "protocol")
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

    if report.failed:
        result_html = '<span style="color:red; font-weight:bold;">FAIL</span>'
    elif report.passed:
        result_html = '<span style="color:green; font-weight:bold;">PASS</span>'
    elif report.skipped:
        result_html = '<span style="color:orange; font-weight:bold;">SKIPPED</span>'
    else:
        result_html = '<span>UNKNOWN</span>'

    new_data.append(f"<div>Result: {result_html}</div>")

    if report.failed and hasattr(report, "longrepr"):
        new_data.append(f"<div>{report.longrepr}</div>")

    if hasattr(report, "capstdout"):
        formatted_lines = []
        for line in report.capstdout.splitlines():
            if "STEP" in line:
                formatted_lines.append(
                    f'<span style="color:blue; font-weight:bold;">{line}</span>'
                )
            elif "PASS:" in line:
                formatted_lines.append(
                    f'<span style="color:green; font-weight:bold;">{line}</span>'
                )
            elif "FAIL:" in line:
                formatted_lines.append(
                    f'<span style="color:red; font-weight:bold;">{line}</span>'
                )
            elif "ERROR :" in line or "ERROR:" in line:
                formatted_lines.append(
                    f'<span style="color:red; font-weight:bold;">{line}</span>'
                )
            else:
                formatted_lines.append(line)

        html = "<br>".join(formatted_lines)
        new_data.append(f"<div>{html}</div>")

    data.clear()
    data.extend(new_data)

@pytest.fixture
def protocol_validation(request,initialize):
    zi_logger.print_step("========== Start Frame Capture ==========")
    backhaul_iface = initialize.read_from_database("controller", "backhaul_capture_iface")
    frame_filter = initialize.read_from_database("controller", "filter_1905")
    initialize.start_frame_capture("controller" ,backhaul_iface, frame_filter, f"{request.node.name}.pcap")
    yield True
    zi_logger.print_step("========== Stop Frame Capture ==========")
    initialize.stop_frame_capture("controller")
    zi_logger.print_step(f"Frame Capture saved as {request.node.name}.pcap")
    zi_logger.print_step("Download Captured pcap file from DUT to local machine")
    initialize.download_captured_pcap("controller", f"{request.node.name}.pcap")
    initialize.delete_captured_pcap("controller", f"{request.node.name}.pcap")
    CPV = initialize.read_from_database("protocol", "common_protocol_validation")
    if CPV:
        zi_logger.print_step("========== Start Common Protocol Validation ==========")
        try:
            common_protocol_validation(f"{request.node.name}.pcap")
        except Exception as err:
            zi_logger.print_error(f"Protocol Validation Failed : {err}")
            pytest.fail(f"Protocol Validation Failed : {err}")
        zi_logger.print_step("========== Stop Common Protocol Validation ==========")

    if hasattr(request.node, 'protocol_specific_function'):
        try:
            request.node.protocol_specific_function(f"{request.node.name}.pcap")
        except Exception as ERR:
            raise RuntimeError(f"{ERR}")
