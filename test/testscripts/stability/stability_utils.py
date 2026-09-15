import subprocess
from zaero.utils import zi_logger
from pathlib import Path
import csv


AVG_CPU_BASELINE = 5
MAX_CPU_BASELINE = 20

#copy_file_to_remote
# Syntax : copy_file_to_remote(local_file, remote_host, remote_path, remote_user="root")
# Description : Copies a local file to a remote host using SCP.
# Parameters :
#     local_file - Path of the source file to copy.
#     remote_host - IP address or hostname of the destination machine.
#     remote_path - Destination directory path on the remote host.
#     remote_user - SSH username used for the remote connection. Default is 'root'.
# Return Value: True if the file is copied successfully, otherwise False.
def copy_file_to_remote(local_file, remote_host, remote_path, remote_user="root"):
    cmd = [
        "scp",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        local_file,
        f"{remote_user}@{remote_host}:{remote_path}"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully copied '{local_file}' to '{remote_host}:{remote_path}'")
        return True
    print(f"SCP failed: {result.stderr}")
    return False

#get_core_dump_status
# Syntax : get_core_dump_status(initialize, device, timestamp)
# Description : Checks whether any core dump files were created after the given timestamp on the specified device.
# Parameters :
#     initialize - Testbed initialization object used to query device files and timestamps.
#     device - Name of the device to inspect, such as 'controller' or 'extender1'.
#     timestamp - Reference time used to identify newly created core dump files.
# Return Value: A list of core dump files found on the device that were modified after the provided timestamp.
def get_core_dump_status(initialize, device, timestamp):
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

# analyse_device_log
# Syntax : analyse_device_log(csv_file)
# Description : Analyzes a device monitoring CSV file and calculates memory, CPU, and PID stability metrics.
# Parameters :
#     csv_file - Absolute or relative path to the CSV log file to analyze.
# Return Value: A tuple containing memory usage percentage, average CPU usage, maximum CPU usage, and PID stability status.
def analyse_device_log(csv_file):
    with open(csv_file) as f:
        rows = list(csv.DictReader(f))
    initial_rss = int(rows[0]["rss_kb"])
    final_rss = int(rows[-1]["rss_kb"])
    initial_cpu = float(rows[0]["cpu_percent"])
    final_cpu = float(rows[-1]["cpu_percent"])
    mem_percent =  round(((final_rss - initial_rss) / initial_rss) * 100, 2)
    cpu_values = [float(row["cpu_percent"]) for row in rows]
    avg_cpu = round(sum(cpu_values) / len(cpu_values), 2)
    max_cpu = max(cpu_values)
    initial_pid = rows[0]["pid"]
    pid_status = any(row["pid"] != initial_pid for row in rows[1:])
    return mem_percent,avg_cpu, max_cpu,pid_status

# log_analyzer
# Syntax : log_analyzer(initialize)
# Description : Inspects all local log files for the controller and extender, evaluates memory and CPU health, and logs any PID instability issues.
# Parameters :
#     initialize - Testbed initialization object used to locate the local log directory for each device.
# Return Value: None. It logs pass/fail messages for each analyzed log file.
def log_analyzer(initialize):
    for device in ["controller", "extender1"]:
        local_dir = initialize.read_from_database(device, "pcap_local_dir")
        files = [f.name for f in Path(local_dir).iterdir() if f.is_file()]
        for file in files:
            zi_logger.log(f"Analyzing log file: {local_dir}/{file}")
            mem_usage,avg_cpu, max_cpu,pid_status = analyse_device_log(f"{local_dir}/{file}")
            if mem_usage > 20:
                zi_logger.print_error(f"{device}: High Memory Usage Detected :{mem_usage}% check log file: {local_dir}/{file}")
            else:
                zi_logger.print_success(f"{device}: Memory usage normal in log file: {local_dir}/{file}")
            if avg_cpu > AVG_CPU_BASELINE:
                zi_logger.print_error(f"{device}: High Average CPU Detected : {avg_cpu}% check log file: {local_dir}/{file}")
            else:
                zi_logger.print_success(f"{device}: Average CPU usage normal in log file: {local_dir}/{file}")
            if max_cpu > MAX_CPU_BASELINE:
                zi_logger.print_error(f"{device}: High Max CPU Detected : {max_cpu}% check log file: {local_dir}/{file}")
            else:
                zi_logger.print_success(f"{device}: Max CPU usage normal in log file: {local_dir}/{file}")
            if pid_status:
                zi_logger.print_error(f"{device}: PID Change Detected. check log file: {local_dir}/{file}")
            else:
                zi_logger.print_success(f"{device}: PID is stable in log file: {local_dir}/{file}")  

