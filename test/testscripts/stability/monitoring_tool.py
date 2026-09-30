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

#!/usr/bin/env python3

import os
import csv
import time
import subprocess
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 60
LOG_DIR = "/tmp/"


PROCESSES = [
    "onewifi_em_agent",
    "onewifi_em_ctrl",
    "OneWifi"
]

def run_cmd(cmd):
    """
    Syntax : run_cmd(cmd)
    Description : Executes a shell command and returns its trimmed output.
    Parameters :
        cmd - Shell command to execute.
    Return Value: Command output as a string, or an empty string if execution fails.
    """
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""

def get_pid(proc_name):
    """
    Syntax : get_pid(proc_name)
    Description : Fetches the PID of the requested process name using pidof.
    Parameters :
        proc_name - Name of the process whose PID should be retrieved.
    Return Value: First PID of the process if found, otherwise None.
    """
    pid = run_cmd(f"pidof {proc_name}")
    if not pid:
        return None
    # If multiple PIDs exist, use first one.
    return pid.split()[0]

def get_memory_stats(pid):
    """
    Syntax : get_memory_stats(pid)
    Description : Reads the RSS memory usage for a given PID from /proc/<pid>/status.
    Parameters :
        pid - Process ID whose memory usage is to be read.
    Return Value: RSS memory size in KB as a string, or 'NA' if unavailable.
    """
    rss = "NA"
    line = run_cmd(f"grep VmRSS /proc/{pid}/status")
    if line:
        rss = line.split()[1]
    return rss


def get_cpu_usage(pid):
    """
    Syntax : get_cpu_usage(pid)
    Description : Retrieves the current CPU usage percentage for the specified process.
    Parameters :
        pid - Process ID whose CPU usage should be measured.
    Return Value: CPU usage percentage as a string, or 'NA' if not available.
    """
    cmd = (
        f"top -bn2 -d 1 -p {pid} "
        f"| tail -1 "
        f"| awk '{{print $9}}'"
    )
    cpu = run_cmd(cmd)
    if not cpu:
        cpu = "NA"
    return cpu

def init_csv(log_file):
    """
    Syntax : init_csv(log_file)
    Description : Initializes a CSV log file with headers if it does not already exist.
    Parameters :
        log_file - Path to the CSV log file to initialize.
    Return Value: None.
    """
    if not os.path.exists(log_file):
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "pid",
                "rss_kb",
                "cpu_percent"
            ])

def log_process(proc_name, data):
    """
    Syntax : log_process(proc_name, data)
    Description : Logs process monitoring data to a CSV file, initializing the file if necessary.
    Parameters :
        proc_name - Name of the process being monitored.
        data - List of data values to log (e.g., timestamp, uptime, pid, rss, cpu).
    Return Value: None.
    """
    log_file = os.path.join(
        LOG_DIR,
        f"{proc_name}_monitor.csv"
    )
    init_csv(log_file)
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)


def main():
    """
    Syntax : main()
    Description : Main monitoring loop that checks system uptime, core dumps, and process statuses, logging any stability issues.
    Parameters : None.
    Return Value: None.
    """
    while True:
        for proc in PROCESSES:
            pid = get_pid(proc)
            if pid is None:
                pid = 0
            rss = get_memory_stats(pid)
            cpu = get_cpu_usage(pid)
            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            row = [
                timestamp,
                pid,
                rss,
                cpu
            ]
            log_process(proc, row)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()