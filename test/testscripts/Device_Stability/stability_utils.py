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

from datetime import datetime
import subprocess
import pytest
import time
import zaero
from zaero.utils import zi_logger
from pathlib import Path
import csv
from rdkbmeshzap.common_utils import report_logger
from stability_config import AVG_CPU_BASELINE, LOG_PATHS, MAX_CPU_BASELINE, MAX_FRONTHAUL_ENABLE_RETRIES

@pytest.fixture(autouse=True)
def common_setup(initialize):
    """
    Syntax : common_setup(initialize)
    Description : Ensure that the fronthaul is enabled and sets up the common test environment by uploading the monitoring tool to the controller and providing access to testbed devices.
    Parameters : initialize - Testbed initialization object used to interact with the testbed devices.
    Return Value: A list of testbed devices obtained from the initialization object.
    """
    fronthaul_enable_retries = 0
    while True:
        report_logger.print_info(f"Inside common_setup: checking fronthaul status..")
        fronthaul_status = initialize.get_mld_status("controller")
        if fronthaul_status:
            report_logger.print_info(f"Fronthaul is already enabled.")
            break
        else:
            report_logger.print_error(f"Fronthaul is disabled, trying to enable it now.")
            initialize.set_fronthaul_network_state("controller", "Home Network", enable=True)
            fronthaul_enable_retries += 1
            time.sleep(10)
            if fronthaul_enable_retries >= MAX_FRONTHAUL_ENABLE_RETRIES:
                pytest.fail(f"common_setup: Failed to enable fronthaul after {MAX_FRONTHAUL_ENABLE_RETRIES} attempts.")

    monitoring_tool_path = Path(__file__).with_name("monitoring_tool.py")
    initialize.put_file("controller", str(monitoring_tool_path), "/nvram/")
    zaero_obj = zaero.zaero()
    devices = [device for device in zaero_obj.get_testbed_devices() if device == "controller" or (device.startswith("extender") and "_" not in device)]
    report_logger.print_info(f"Common setup completed. Testbed devices: {devices}")
    yield devices
    # Cleanup code after the test is done
    report_logger.print_info(f"Cleaning up after test.")
    initialize.execute_command("controller", "pkill -f monitoring_tool.py")
    for log_file in LOG_PATHS:
        if initialize.get_file_presence_status("controller", log_file):
            initialize.execute_command("controller", f"rm -f {log_file}")
    report_logger.print_info(f"Cleanup completed.")

def get_timestamp() -> str:
    """
    Syntax : get_timestamp()
    Description : Returns the current date and time as a formatted string.
    Parameters : None.
    Return Value: Current timestamp as a string in the format "YYYY-MM-DD HH:MM:SS".
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_core_dump_status(initialize, device, timestamp):
    """
    Syntax : get_core_dump_status(initialize, device, timestamp)
    Description : Checks whether any core dump files were created after the given timestamp on the specified device.
    Parameters :
        initialize - Testbed initialization object used to query device files and timestamps.
        device - Name of the device to inspect, such as 'controller' or 'extender1'.
        timestamp - Reference time used to identify newly created core dump files.
    Return Value: A list of core dump files found on the device that were modified after the provided timestamp.
    """
    initialize.get_file_presence_status(device, "/tmp")
    file_list = initialize.get_file_list(device,"/tmp")
    core_dump_files = []
    for item in file_list:
        if 'dmp' in item:
            modified_time = initialize.get_file_modified_time(device, f"/tmp/{item}")
            zi_logger.log(f"Modified time for {item}: {modified_time}")
            zi_logger.log(f"Timestamp to compare: {timestamp}")
            if modified_time > timestamp:
                core_dump_files.append(item)
    return core_dump_files

def analyse_device_log(csv_file):
    """
    Syntax : analyse_device_log(csv_file)
    Description : Analyzes a device monitoring CSV file and calculates memory, CPU, and PID stability metrics.
    Parameters :
        csv_file - Absolute or relative path to the CSV log file to analyze.
    Return Value: A tuple containing memory usage percentage, average CPU usage, maximum CPU usage, and PID stability status.
    """
    with open(csv_file) as f:
        rows = list(csv.DictReader(f))

    rss_values = [
        int(row["rss_kb"])
        for row in rows
        if row["rss_kb"] not in ("", "NA")
    ]
    if len(rss_values) >= 2 and rss_values[0] != 0:
        mem_percent = round(((rss_values[-1] - rss_values[0]) / rss_values[0]) * 100, 2)
    else:
        mem_percent = None

    cpu_values = [
        float(row["cpu_percent"])
        for row in rows
        if row["cpu_percent"] not in ("", "NA")
    ]
    if cpu_values:
        avg_cpu = round(sum(cpu_values) / len(cpu_values), 2)
        max_cpu = max(cpu_values)
    else:
        avg_cpu = None
        max_cpu = None

    initial_pid = rows[0]["pid"]
    pid_status = any(row["pid"] != initial_pid for row in rows[1:])
    return mem_percent,avg_cpu, max_cpu,pid_status

def log_analyzer(log_path, step_count, sub_step_count=1):
    """
    Syntax : log_analyzer(local_dir, step_count, sub_step_count)
    Description : Inspects all local log files in the specified directory, evaluates memory and CPU health, and logs any PID instability issues.
    Parameters :
        local_dir - Absolute or relative path to the local directory containing log files to analyze.
        step_count - The current step count in the test script.
        sub_step_count - The current sub-step count in the test script.
    Return Value: None. It logs pass/fail messages for each analyzed log file.
    """

    report_logger.print_step(f"Step {step_count}: Analyzing log file: {log_path}")
    mem_usage,avg_cpu, max_cpu,pid_status = analyse_device_log(log_path)
    report_logger.print_step(f"Step {step_count}.{sub_step_count}: Analyzing memory usage ")
    sub_step_count += 1
    if mem_usage is None:
        report_logger.print_error(f"controller: Memory usage unavailable")
    elif mem_usage > 20:
        report_logger.print_error(f"controller: High Memory Usage :{mem_usage}% variation detected.")
    else:
        report_logger.print_success(f"PASS: [controller] Memory usage normal : {mem_usage}% variation detected.")

    report_logger.print_step(f"Step {step_count}.{sub_step_count}: Analyzing Average CPU usage ")
    sub_step_count += 1
    if avg_cpu is None:
        report_logger.print_error(f"controller: Average CPU usage unavailable.")
    elif avg_cpu > AVG_CPU_BASELINE:
        report_logger.print_error(f"controller: High Average CPU Detected : {avg_cpu}% .")
    else:
        report_logger.print_success(f"PASS: [controller] Average CPU usage normal : {avg_cpu}%.")

    report_logger.print_step(f"Step {step_count}.{sub_step_count}: Analyzing Max CPU usage ")
    sub_step_count += 1
    if max_cpu is None:
        report_logger.print_error(f"controller: Max CPU usage unavailable.")
    elif max_cpu > MAX_CPU_BASELINE:
        report_logger.print_error(f"controller: High Max CPU Detected : {max_cpu}% .")
    else:
        report_logger.print_success(f"PASS: [controller] Max CPU usage normal : {max_cpu}%.")

    report_logger.print_step(f"Step {step_count}.{sub_step_count}: Analyzing PID stability ")
    sub_step_count += 1
    if pid_status:
        report_logger.print_error(f"controller: PID Change Detected.")
    else:
        report_logger.print_success(f"PASS: [controller] PID is stable.")  

