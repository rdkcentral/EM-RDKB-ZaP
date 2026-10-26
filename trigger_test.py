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

from pathlib import Path
import subprocess
import sys
import yaml
import questionary
from filelock import FileLock, Timeout

def get_test_files(base_dir):
    """
    Return all discoverable test files under the test directory.
    """
    return sorted(
        path
        for path in (base_dir / "test").rglob("*.py")
        if path.name.startswith(("test_", "TS_"))
    )

def get_execution_mode(base_dir):
    """
    Read and validate the test selection mode from platform.yaml.
    """
    platform_path = base_dir / "test" / "config" / "platform.yaml"
    with platform_path.open(encoding="utf-8") as platform_file:
        platform = yaml.safe_load(platform_file) or {}
    mode = platform.get("test_parameters", {}).get("execution_mode", "browser")
    if mode not in {"terminal", "browser"}:
        raise ValueError(
            "test_parameters.execution_mode must be either "
            "'terminal' or 'browser'"
        )
    return mode

def get_test_suites(base_dir, test_files):
    """
    Group test files by suite and ignore root-level helper files.
    """
    suites = {}
    for path in test_files:
        relative_path = path.relative_to(base_dir / "test")
        if len(relative_path.parts) < 2:
            continue
        suite_name = (
            "ref_test"
            if relative_path.parts[0] == "ref_test"
            else relative_path.parts[1]
        )
        suites.setdefault(suite_name, []).append(path)
    return suites

def select_test_suite(base_dir, test_files):
    """
    Interactively select test cases grouped by suite.
    """
    selected_files = []
    remaining_cases = {
        suite_name: list(paths)
        for suite_name, paths in get_test_suites(base_dir, test_files).items()
    }
    while True:
        suite_names = sorted(remaining_cases)
        suite_name = questionary.select(
            f"TESTBED TEST CONSOLE | Select a test suite ({len(selected_files)} selected)",
            choices=[
                questionary.Choice(
                    f"{name.replace('_', ' ')} ({len(remaining_cases[name])} test cases)",
                    value=name,
                )
                for name in suite_names
            ] + [
                questionary.Choice("[RUN] Run Validation", value="__run__"),
                questionary.Choice("[EXIT] Exit", value="__exit__"),
            ],
        ).ask()
        if suite_name in {None, "__exit__"}:
            return []
        if suite_name == "__run__":
            if not selected_files:
                print("No test case selected. Please select at least one case.")
                continue
            return selected_files
        case_choices = [
            questionary.Choice(
                path.relative_to(base_dir / "test").as_posix(),
                value=path,
                checked=path in selected_files,
            )
            for path in remaining_cases[suite_name]
        ]
        cases = questionary.checkbox(
            f"Select test cases in {suite_name}",
            choices=case_choices,
            instruction="Space = select/unselect | Enter = continue",
        ).ask()
        if cases is None:
            return []
        previous_suite_files = [
            path for path in selected_files if path in remaining_cases[suite_name]
        ]
        selected_case_names = [path.name for path in cases]
        print(
            "Selected test cases: "
            + (", ".join(selected_case_names) if selected_case_names else "None")
        )
        deselected_case_names = [
            path.name for path in previous_suite_files if path not in cases
        ]
        if deselected_case_names:
            print(f"Deselected test cases: {', '.join(deselected_case_names)}")
        selected_files = [
            path for path in selected_files if path not in remaining_cases[suite_name]
        ]
        selected_files.extend(cases or [])

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    dashboard = base_dir / "test_dashboard" / "test_dashboard.py"
    execution_mode = get_execution_mode(base_dir)
    if execution_mode == "terminal":
        test_files = get_test_files(base_dir)
        selected_files = select_test_suite(base_dir, test_files)
        if not selected_files:
            raise SystemExit(0)
        try:
            with FileLock(str(base_dir / ".pytest_dashboard_session.lock"), timeout=0):
                from main import run_tests
                result, _ = run_tests(base_dir, selected_files)
                raise SystemExit(result)
        except Timeout:
            raise SystemExit("Another test run is already in progress.")
    try:
        import streamlit  # noqa: F401
    except ImportError:
        raise SystemExit("Streamlit is required when execution_mode is 'browser'.")
    raise SystemExit(subprocess.call([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dashboard),
        "--browser.gatherUsageStats=false",
    ]))