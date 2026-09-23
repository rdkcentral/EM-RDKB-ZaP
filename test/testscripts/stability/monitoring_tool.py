#!/usr/bin/env python3

import os
import csv
import time
import subprocess
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 5
LOG_DIR = "/nvram"


PROCESSES = [
    "onewifi_em_agent",
    "onewifi_em_ctrl",
    "OneWifi"
]

WARNING_LOG = os.path.join(LOG_DIR, "process_monitor_warnings.log")
STABILITY_ISSUE_FILE = os.path.join(LOG_DIR, "stability_issue")

# run_cmd
# Syntax : run_cmd(cmd)
# Description : Executes a shell command and returns its trimmed output.
# Parameters :
#     cmd - Shell command to execute.
# Return Value: Command output as a string, or an empty string if execution fails.
def run_cmd(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""

# get_uptime_s()
# Syntax : get_uptime_s()
# Description : Retrieves the system uptime in the format returned by the uptime command.
# Parameters : None.
# Return Value: Uptime string from the system, or an empty string if unavailable.
def get_uptime_s():
    return run_cmd("uptime -s")

# get_pid
# Syntax : get_pid(proc_name)
# Description : Fetches the PID of the requested process name using pidof.
# Parameters :
#     proc_name - Name of the process whose PID should be retrieved.
# Return Value: First PID of the process if found, otherwise None.
def get_pid(proc_name):
    pid = run_cmd(f"pidof {proc_name}")
    if not pid:
        return None
    # If multiple PIDs exist, use first one.
    return pid.split()[0]

# get_memory_stats
# Syntax : get_memory_stats(pid)
# Description : Reads the RSS memory usage for a given PID from /proc/<pid>/status.
# Parameters :
#     pid - Process ID whose memory usage is to be read.
# Return Value: RSS memory size in KB as a string, or 'NA' if unavailable.
def get_memory_stats(pid):
    rss = "NA"
    line = run_cmd(f"grep VmRSS /proc/{pid}/status")
    if line:
        rss = line.split()[1]
    return rss

# get_cpu_usage
# Syntax : get_cpu_usage(pid)
# Description : Retrieves the current CPU usage percentage for the specified process.
# Parameters :
#     pid - Process ID whose CPU usage should be measured.
# Return Value: CPU usage percentage as a string, or 'NA' if not available.
def get_cpu_usage(pid):
    cmd = (
        f"top -bn2 -d 1 -p {pid} "
        f"| tail -1 "
        f"| awk '{{print $9}}'"
    )

    cpu = run_cmd(cmd)
    if not cpu:
        cpu = "NA"
    return cpu

# write_warning
# Syntax : write_warning(msg)
# Description : Writes a warning log entry to the monitoring warnings file and prints it to the console.
# Parameters :
#     msg - Warning message to log.
# Return Value: None.
def write_warning(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] WARNING: {msg}"

    print(log_msg)

    with open(WARNING_LOG, "a") as f:
        f.write(log_msg + "\n")

# touch_stability_issue
# Syntax : touch_stability_issue(data)
# Description : Appends a stability issue message to the stability issue log and refreshes the file timestamp.
# Parameters :
#     data - Message describing the detected stability issue.
# Return Value: True if the issue log is updated successfully, otherwise False.
def touch_stability_issue(data: str) -> bool:
    try:
        with open(STABILITY_ISSUE_FILE, "a", encoding="utf-8") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{timestamp} - {data}\n")

        os.utime(STABILITY_ISSUE_FILE, None)
        return True

    except FileNotFoundError as exc:
        logger.error(
            f"Stability issue file not found: {STABILITY_ISSUE_FILE}. Error: {exc}"
        )

    except PermissionError as exc:
        logger.error(
            f"Permission denied while writing to {STABILITY_ISSUE_FILE}. Error: {exc}"
        )

    except OSError as exc:
        logger.error(
            f"OS error while updating {STABILITY_ISSUE_FILE}. Error: {exc}"
        )

    except Exception as exc:
        logger.exception(
            f"Unexpected error while updating stability issue file: {exc}"
        )

    return False

#init_csv
# Syntax : init_csv(log_file)
# Description : Initializes a CSV log file with headers if it does not already exist.
# Parameters :
#     log_file - Path to the CSV log file to initialize.
# Return Value: None.
def init_csv(log_file):
    if not os.path.exists(log_file):
        with open(log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "uptime_s",
                "pid",
                "rss_kb",
                "cpu_percent"
            ])

#log_process
# Syntax : log_process(proc_name, data)
# Description : Logs process monitoring data to a CSV file, initializing the file if necessary.
# Parameters :
#     proc_name - Name of the process being monitored.
#     data - List of data values to log (e.g., timestamp, uptime, pid, rss, cpu).
# Return Value: None.
def log_process(proc_name, data):
    log_file = os.path.join(
        LOG_DIR,
        f"{proc_name}_monitor.csv"
    )

    init_csv(log_file)

    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)

# main
# Syntax : main()
# Description : Main monitoring loop that checks system uptime, core dumps, and process statuses, logging any stability issues.
# Parameters : None.
# Return Value: None.
def main():

    previous_pid = {}
    previous_uptime_s = get_uptime_s()

    while True:

        current_uptime_s = get_uptime_s()

        if current_uptime_s != previous_uptime_s:
            write_warning(
                f"System boot time changed: "
                f"{previous_uptime_s} -> {current_uptime_s}"
            )
            touch_stability_issue("Device reboot detected")

        previous_uptime_s = current_uptime_s

        # add line to check core dump presence inside /tmp directory using ls /tmp | grep dmp
        core_dumps = subprocess.getoutput("ls /tmp | grep dmp").strip()
        if core_dumps:
            write_warning(
                f"Core dumps detected: {core_dumps}"
            )
            touch_stability_issue(f"Core dumps detected: {core_dumps}")

        for proc in PROCESSES:

            pid = get_pid(proc)

            if pid is None:
                write_warning(
                    f"{proc} is not running"
                )
                continue

            old_pid = previous_pid.get(proc)

            if old_pid and old_pid != pid:
                write_warning(
                    f"{proc} PID changed: "
                    f"{old_pid} -> {pid}"
                )
                touch_stability_issue(f"{proc} PID changed: {old_pid} -> {pid}")

            previous_pid[proc] = pid

            rss = get_memory_stats(pid)
            cpu = get_cpu_usage(pid)

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            row = [
                timestamp,
                current_uptime_s,
                pid,
                rss,
                cpu
            ]
            log_process(proc, row)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()