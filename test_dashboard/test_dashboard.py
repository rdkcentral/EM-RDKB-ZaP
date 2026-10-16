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

import os
import re
import threading
import time
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from filelock import FileLock, Timeout
import streamlit as st
import yaml
from trigger_test import get_test_files, get_test_suites

# Dashboard configuration and shared runtime paths.
BASE_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = Path(__file__).resolve().parent / "test_dashboard.css"
REPORT_HOST = os.environ.get("REPORT_HOST", "127.0.0.1")
RUN_LOCK_PATH = BASE_DIR / ".pytest_dashboard.lock"
SUITE_DETAILS = {
    "Client_Association": "Client discovery, authentication, DHCP, and gateway reachability",
    "Controller_Recovery": "Controller reboot and extender reconnection validation",
    "Device_Stability": "Channel, SSID, fronthaul, and endurance stress tests",
    "Metrics_Collection": "Periodic reporting and response-disable validation",
    "Multi_Agent_Onboarding": "Topology count and duplicate-entry validation",
    "ref_test": "Reference and protocol validation tests",
}

# Configure the Streamlit page before rendering any dashboard content.
st.set_page_config(page_title="EM-RDKB Automation Dashboard", page_icon="🧪", layout="wide")

# Serve generated reports from a cached local HTTP server.
@st.cache_resource(show_spinner=False)
def get_report_server(report_root):
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(
        *args, directory=str(report_root), **kwargs
    )
    server = ThreadingHTTPServer((REPORT_HOST, 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server

def get_report_url(report_path):
    server = get_report_server(report_path.parent)
    return f"http://{REPORT_HOST}:{server.server_port}/{report_path.name}"

# Prevent concurrent validation runs from sharing the testbed.
@contextmanager
def acquire_run_lock():
    try:
        lock = FileLock(str(RUN_LOCK_PATH), timeout=0)
        lock.acquire()
    except Timeout:
        yield False
        return
    try:
        yield True
    finally:
        lock.release()

# Build the active-device summary shown in the dashboard.
def get_testbed_summary():
    infra_path = BASE_DIR / "test" / "config" / "infra.yaml"
    with infra_path.open(encoding="utf-8") as infra_file:
        infra = yaml.safe_load(infra_file) or {}
    devices = [
        device
        for device, details in infra.items()
        if isinstance(details, dict) and details.get("device_present", False)
    ]
    return {
        "Controllers": sum(device == "controller" for device in devices),
        "Extenders": sum(
            device.startswith("extender") and "_client_" not in device
            for device in devices
        ),
        "Wi-Fi Clients": sum("wlan" in device or "wifi" in device for device in devices),
        "LAN Clients": sum("_lan_client_" in device for device in devices),
    }

def get_testbed_summary_with_timeout(timeout_seconds=5):
    summary = {}
    def load_summary():
        try:
            summary.update(get_testbed_summary())
        except Exception:
            pass
    loader = threading.Thread(target=load_summary, daemon=True)
    loader.start()
    loader.join(timeout_seconds)
    return summary or {
        "Controllers": "Loading",
        "Extenders": "Loading",
        "Wi-Fi Clients": "Loading",
        "LAN Clients": "Loading",
    }

# Read execution totals from the current pytest HTML report.
def get_execution_counts(report_path, fallback_count, result):
    counts = {"Passed": 0, "Failed": 0, "Skipped": 0}
    if report_path and report_path.exists():
        report_html = report_path.read_text(encoding="utf-8", errors="ignore")
        for label in counts:
            match = re.search(rf"(\d+) {label}", report_html, re.IGNORECASE)
            if match:
                counts[label] = int(match.group(1))
        if sum(counts.values()) > 0:
            return counts
    counts["Passed" if result == 0 else "Failed"] = fallback_count
    return counts

# Apply pending session-state changes before rendering the dashboard.
if st.session_state.pop("reset_test_selection", False):
    for state_key in list(st.session_state):
        if isinstance(state_key, str) and state_key.startswith(("suite_", "case_")):
            st.session_state[state_key] = False

if st.session_state.get("test_session_closed"):
    st.markdown(
        """
        <div style="position: fixed; inset: 0; z-index: 99999; background: #FFFFFF; display: flex; align-items: center; justify-content: center;">
            <div style="text-align: center; background: #F3F8FF; border: 1px solid #B9D2F5; border-radius: 12px; padding: 2.2rem 3rem;">
                <div style="font-size: 2rem; margin-bottom: 0.6rem;">&#10003;</div>
                <div style="color: #174A86; font-size: 1.25rem; font-weight: 800;">Test session closed</div>
                <div style="color: #60758A; margin-top: 0.45rem;">Please close this browser tab manually.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(5)
    os._exit(0)

# Load the external dashboard stylesheet.
st.markdown(
    f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

loading_placeholder = st.empty()
loading_placeholder.markdown(
    """
    <div style="min-height: 58vh; display: flex; align-items: center; justify-content: center;">
        <div style="text-align: center; color: #243B6B;">
            <div style="font-size: 2rem; margin-bottom: 0.7rem;">&#8987;</div>
            <div style="font-size: 1.15rem; font-weight: 800;">Loading dashboard configuration...</div>
            <div style="color: #425466; margin-top: 0.35rem;">Preparing available test suites</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load available tests and testbed data before rendering selectors.
test_files = get_test_files(BASE_DIR)
suites = get_test_suites(BASE_DIR, test_files)

loading_placeholder.markdown(
    """
    <div style="min-height: 58vh; display: flex; align-items: center; justify-content: center;">
        <div style="text-align: center; color: #243B6B;">
            <div style="font-size: 2rem; margin-bottom: 0.7rem;">&#8987;</div>
            <div style="font-size: 1.15rem; font-weight: 800;">Reading testbed configuration...</div>
            <div style="color: #425466; margin-top: 0.35rem;">Loading devices and environment details</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
testbed_summary = get_testbed_summary_with_timeout()
loading_placeholder.empty()

# Render sidebar navigation and execution history.
st.sidebar.markdown(
    '<div class="sidebar-brand">Easy Mesh Test Hub</div>'
    '<div class="sidebar-subtitle">Explore suites, cases, and previous runs</div>',
    unsafe_allow_html=True,
)
with st.sidebar.expander("Test Suite Explorer", expanded=False):
    st.markdown(
        f'<div class="sidebar-count">{len(suites)} suites &nbsp;|&nbsp; {len(test_files)} test cases</div>',
        unsafe_allow_html=True,
    )
    for suite_name in sorted(suites):
        with st.expander(f"{suite_name.replace('_', ' ')} ({len(suites[suite_name])} cases)", expanded=False):
            for path in suites[suite_name]:
                st.markdown(f'<div class="sidebar-case">{path.stem}</div>', unsafe_allow_html=True)

with st.sidebar.expander("Execution History", expanded=False):
    history_runs = sorted(
        (path for path in (BASE_DIR / "Reports").glob("TestRun_*") if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not history_runs:
        st.caption("No previous test executions found.")
    else:
        for run_dir in history_runs:
            report_path = run_dir / "report.html"
            if report_path.exists():
                st.markdown(
                    f'<div class="sidebar-history-link"><div>{run_dir.name}</div>'
                    f'<a href="{get_report_url(report_path)}" target="_blank">Open report &rarr;</a></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption(f"{run_dir.name} | Report missing")

# Render the dashboard header and testbed summary.
st.markdown(
    """
    <div class="hero">
            <h1>EM-RDKB Automation Dashboard</h1>
        <p>Choose test suites and test cases for execution.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
        f"""
        <div class="summary-panel">
            <div class="summary-title">Test Environment Overview</div>
            <div class="summary-subtitle">Testbed Configuration</div>
            <div class="summary-grid">
                <div class="summary-card"><strong>{testbed_summary['Controllers']}</strong><span>Controllers</span></div>
                <div class="summary-card"><strong>{testbed_summary['Extenders']}</strong><span>Extenders</span></div>
                <div class="summary-card"><strong>{testbed_summary['Wi-Fi Clients']}</strong><span>Wi-Fi Clients</span></div>
                <div class="summary-card"><strong>{testbed_summary['LAN Clients']}</strong><span>LAN Clients</span></div>
            </div>
            <div class="summary-subtitle">Test Inventory</div>
            <div class="inventory-grid">
                <div class="inventory-card"><span>Available Test Suites</span><strong>{len(suites)}</strong></div>
                <div class="inventory-card"><span>Available Test Cases</span><strong>{len(test_files)}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
)

# Render suite and case selection controls.
st.markdown('<div class="step-heading">Select Test Suites</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">Choose one or more test suites.</div>', unsafe_allow_html=True)
selected_names = []
execution_in_progress = st.session_state.get("execution_in_progress", False)
columns = st.columns(2)
for index, suite_name in enumerate(sorted(suites)):
    with columns[index % 2]:
        if st.checkbox(
            f"{suite_name.replace('_', ' ')}  |  {len(suites[suite_name])} test cases",
            key=f"suite_{suite_name}",
            help=SUITE_DETAILS.get(suite_name, "Test suite"),
            disabled=execution_in_progress,
        ):
            selected_names.append(suite_name)

st.markdown(
    f'<div class="count-card suite-count"><span class="count-label">Selected test suites</span>'
    f'<span class="count-value">{len(selected_names)}</span></div>',
    unsafe_allow_html=True,
)

selected_cases_by_suite = {}
st.markdown('<div class="step-heading">Select Test Cases</div>', unsafe_allow_html=True)
if selected_names:
    st.markdown('<div class="section-note">Choose the test cases you want to run.</div>', unsafe_allow_html=True)
    for suite_name in selected_names:
        selected_cases = []
        with st.container(border=True):
            st.markdown(
                f'<div class="case-panel-title">{suite_name.replace("_", " ")} test cases</div>',
                unsafe_allow_html=True,
            )
            for path in suites[suite_name]:
                case_name = path.stem.removeprefix("TS_").replace('_', ' ')
                case_key = f"case_{path.as_posix()}"
                if case_key not in st.session_state:
                    st.session_state[case_key] = True
                if st.checkbox(
                    case_name,
                    key=case_key,
                    disabled=execution_in_progress,
                ):
                    selected_cases.append(path)
        selected_cases_by_suite[suite_name] = selected_cases
else:
    st.markdown(
        '<div class="empty-state"><strong>No test suite selected</strong>'
        '<span>Select a suite above to view its individual test cases here.</span></div>',
        unsafe_allow_html=True,
    )

case_files = [
    path
    for suite_cases in selected_cases_by_suite.values()
    for path in suite_cases
]

st.markdown(
    f'<div class="count-card case-count"><span class="count-label">Selected test cases</span>'
    f'<span class="count-value">{len(case_files)}</span></div>',
    unsafe_allow_html=True,
)

# Execute the selected cases while controls are locked.
with st.container(border=True):
    st.markdown('<div class="step-heading">STEP 3 &nbsp;|&nbsp; Execute selected tests</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Prerequisite checks run automatically before the selected cases begin.</div>', unsafe_allow_html=True)
    if st.button(
        "Run Validation",
        type="primary",
        disabled=not case_files or execution_in_progress,
        use_container_width=True,
    ):
        st.session_state["pending_case_files"] = case_files
        st.session_state["execution_in_progress"] = True
        st.rerun()

    if execution_in_progress:
        from main import run_tests

        case_files = st.session_state.pop("pending_case_files", case_files)
        with acquire_run_lock() as lock_acquired:
            if not lock_acquired:
                st.markdown(
                    '<div class="run-busy"><span class="run-busy-icon">&#9208;</span>'
                    '<div><strong>Execution in progress</strong>'
                    '<span>Another validation run is using the testbed. Please try again shortly.</span></div></div>',
                    unsafe_allow_html=True,
                )
                st.stop()

            started_at = time.perf_counter()
            try:
                with st.spinner("Running selected test suites..."):
                    result, report_path = run_tests(BASE_DIR, case_files)
            finally:
                st.session_state["execution_in_progress"] = False
        elapsed_seconds = time.perf_counter() - started_at
        current_report = report_path if report_path.exists() else None
        execution_counts = get_execution_counts(current_report, len(case_files), result)
        report_location = (
            f'Report Generated: <a href="{get_report_url(current_report)}" target="_blank">'
            f'{current_report}</a>'
            if current_report else "Current execution report is not available"
        )
        st.session_state["last_execution_report"] = {
            "status": "Completed",
            "selected_cases": len(case_files),
            "duration": elapsed_seconds,
            "counts": execution_counts,
            "location": report_location,
        }
        st.session_state["reset_test_selection"] = True
        st.rerun()

# Show the most recent execution result.
last_execution_report = st.session_state.get("last_execution_report")
if last_execution_report:
    counts = last_execution_report["counts"]
    st.markdown(
        f'<div class="report-card"><strong>Validation report</strong>'
        f'<div class="report-stats">'
        f'<div class="report-stat status"><span>Status</span><b>{last_execution_report["status"]}</b></div>'
        f'<div class="report-stat"><span>Selected cases</span><b>{last_execution_report["selected_cases"]}</b></div>'
        f'<div class="report-stat"><span>Duration</span><b>{last_execution_report["duration"]:.1f}s</b></div>'
        f'<div class="report-stat passed"><span>Passed</span><b>{counts["Passed"]}</b></div>'
        f'<div class="report-stat failed"><span>Failed</span><b>{counts["Failed"]}</b></div>'
        f'<div class="report-stat skipped"><span>Skipped</span><b>{counts["Skipped"]}</b></div></div>'
        f'<div class="report-link">{last_execution_report["location"]}</div></div>',
        unsafe_allow_html=True,
    )
if st.button("Close Test Session", use_container_width=True):
    st.session_state["test_session_closed"] = True
    st.rerun()