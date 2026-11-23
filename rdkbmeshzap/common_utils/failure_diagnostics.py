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

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from rdkbmeshzap.common_utils import device_utils, report_logger

# Limit SSH channel setup and stream inactivity.
LOG_TRANSFER_SOCKET_TIMEOUT = 30
# Limit the total duration of a log transfer.
LOG_TRANSFER_DEADLINE_SECONDS = 600
DIAGNOSTIC_COMMAND_TIMEOUT = 30
# Each entry pairs a remote log path with whether to compress it.
CONTROLLER_LOG_PATHS_WITH_COMPRESSION = (
    ("/tmp/em_ctrl.log", True),
    ("/tmp/em_agent.log", True),
    ("/tmp/em_cli.log", False),
)
EXTENDER_LOG_PATHS_WITH_COMPRESSION = (("/tmp/em_agent.log", True),)
# Service names checked for each device.
CONTROLLER_SERVICES = ("em_ctrl", "ieee1905_em_ctrl", "ieee1905_em_agent", "em_agent", "onewifi")
EXTENDER_SERVICES = ("em_agent", "ieee1905_em_agent", "onewifi")

def stream_log(initialize, device, remote_path, local_path, compress=False, remote_command=None):
    """
    Syntax : stream_log(initialize, device, remote_path, local_path, compress=False)
    Description : Streams a complete remote log to a local file, optionally compressed.
    Parameters :
        initialize - Framework_Extension instance with streaming capabilities.
        device - Name of the device containing the log.
        remote_path - Absolute path to the remote log file.
        local_path - Destination path for the log.
        compress - Compress the log on the remote device before transferring it.
        remote_command - Optional command that writes the log data to stdout.
    Return Value: None. Raises an exception when the transfer fails or times out.
    """
    try:
        if remote_command:
            initialize.stream_command_output_to_file(
                device,
                remote_command,
                local_path,
                socket_timeout=LOG_TRANSFER_SOCKET_TIMEOUT,
                total_timeout=LOG_TRANSFER_DEADLINE_SECONDS
            )
        else:
            initialize.stream_remote_file(
                device,
                remote_path,
                local_path,
                compress=compress,
                socket_timeout=LOG_TRANSFER_SOCKET_TIMEOUT,
                total_timeout=LOG_TRANSFER_DEADLINE_SECONDS
            )
    except Exception as e:
        raise RuntimeError(str(e)) from e

def record_command_output(debug_sections, name, collect):
    """
    Syntax : record_command_output(debug_sections, name, collect)
    Description : Adds command output or a collection error to diagnostic sections.
    Parameters :
        debug_sections - List receiving formatted diagnostic text.
        name - Label identifying the command or data source.
        collect - Callable that retrieves the command output.
    Return Value: None. Collection errors are recorded instead of being raised.
    """
    try:
        result = collect()
        if isinstance(result, tuple):
            output = result[0] if result else ""
            error = result[1] if len(result) > 1 else ""
            if len(result) > 2 and result[2] != 0:
                error = f"{error}\nExit status: {result[2]}".strip()
        else:
            output, error = result, ""
        debug_sections.append(f"\n--- {name} ---\n{output or ''}\n{error or ''}\n")
    except Exception as error:
        debug_sections.append(f"\n--- {name} collection failed ---\n{error}\n")

def collect_device_failure_diagnostics(initialize, scenario_dir, device):
    """
    Syntax : collect_device_failure_diagnostics(initialize, scenario_dir, device)
    Description : Collects command output and complete compressed logs for one device.
    Parameters :
        initialize - Framework_Extension object with SSH capabilities.
        scenario_dir - Directory containing diagnostics for the failed test.
        device - Name of the device to collect diagnostics from.
    Return Value: List of local paths created for the device diagnostics.
    """
    device_dir = scenario_dir / device.capitalize()
    debug_info_path = device_dir / "device_debug_info.log"
    debug_sections = [f"Device: {device}\n"]
    diagnostic_paths = []
    try:
        if not initialize.is_device_alive(device):
            return diagnostic_paths
    except Exception:
        return diagnostic_paths
    device_dir.mkdir(parents=True, exist_ok=True)
    log_paths_with_compression = (
        CONTROLLER_LOG_PATHS_WITH_COMPRESSION
        if device == "controller"
        else EXTENDER_LOG_PATHS_WITH_COMPRESSION
    )
    # Snapshot all configured logs in parallel before collecting live command state.
    with ThreadPoolExecutor(max_workers=len(log_paths_with_compression) + 1) as executor:
        transfers = {}
        for remote_path, compress in log_paths_with_compression:
            suffix = ".gz" if compress else ""
            local_path = device_dir / f"{Path(remote_path).name}{suffix}"
            transfers[executor.submit(stream_log, initialize, device, remote_path, local_path, compress=compress)] = (remote_path, local_path)
        onewifi_local_path = device_dir / "onewifi_logs.tar.gz"
        transfers[
            executor.submit(
                stream_log,
                initialize,
                device,
                "/rdklogs/logs",
                onewifi_local_path,
                remote_command=(
                    "cd /rdklogs/logs && "
                    "find . -type f -iname 'wifi*' -print | tar -czf - -T -"
                ),
            )
        ] = ("OneWifi logs in /rdklogs/logs", onewifi_local_path)
        # A failed log is recorded, but does not prevent other diagnostics from being collected.
        for future in as_completed(transfers):
            remote_path, local_path = transfers[future]
            try:
                future.result()
                if local_path.is_file():
                    diagnostic_paths.append(local_path)
            except Exception as error:
                message = f"FAIL: {device}: log collection failed for {remote_path} ({type(error).__name__}): {error!r}"
                report_logger.print_error(message)
                debug_sections.append(f"{message}\n")
    # Capture service and interface state after the log snapshot.
    try:
        services = CONTROLLER_SERVICES if device == "controller" else EXTENDER_SERVICES
        debug_sections.append("\n--- Services checked ---\n" + "\n".join(services) + "\n")
        service_command = " ".join(services)
        record_command_output(debug_sections, "systemctl status", lambda: initialize.execute_command_with_result(device, f"systemctl status {service_command} --no-pager 2>&1", timeout=DIAGNOSTIC_COMMAND_TIMEOUT))
        record_command_output(debug_sections, "iw dev", lambda: initialize.execute_command_with_result(device, "iw dev", timeout=DIAGNOSTIC_COMMAND_TIMEOUT))
        record_command_output(debug_sections, "ifconfig", lambda: initialize.execute_command_with_result(device, "ifconfig 2>&1", timeout=DIAGNOSTIC_COMMAND_TIMEOUT))
        record_command_output(debug_sections, "version.txt", lambda: initialize.execute_command_with_result(device, "cat /version.txt 2>&1", timeout=DIAGNOSTIC_COMMAND_TIMEOUT))
    except Exception as error:
        message = f"FAIL: {device}: command diagnostics failed: {error!r}"
        report_logger.print_error(message)
        debug_sections.append(f"{message}\n")
    try:
        debug_info_path.write_text("".join(debug_sections), encoding="utf-8")
        diagnostic_paths.append(debug_info_path)
    except Exception:
        pass
    return diagnostic_paths

@device_utils.suppress_zaero_logs
def collect_failure_diagnostics(initialize, run_dir, test_case_name):
    """
    Syntax : collect_failure_diagnostics(initialize, run_dir, test_case_name)
    Description : Collects failure diagnostics for the controller and enabled extenders.
    Parameters :
        initialize - Testbed initialization object used to access device APIs.
        run_dir - Directory where the test report and diagnostics are stored.
        test_case_name - Name used to create the failed-test diagnostics directory.
    Return Value: A tuple of the scenario directory and created file paths, or None if its directory cannot be created.
    """
    try:
        scenario_dir = Path(run_dir) / "device_logs" / test_case_name
        scenario_dir.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        report_logger.print_error(f"FAIL: failure diagnostics directory creation failed: {error}")
        return None
    diagnostic_paths = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(collect_device_failure_diagnostics, initialize, scenario_dir, "controller"): "controller"}
        try:
            extenders = device_utils.get_enabled_extenders(initialize)
        except Exception as error:
            report_logger.print_error(f"FAIL: failure diagnostics extender discovery failed: {error}")
            extenders = []
        # Start each extender's log snapshot without waiting for earlier devices.
        futures.update(
            {
                executor.submit(collect_device_failure_diagnostics, initialize, scenario_dir, extender): extender
                for extender in extenders
            }
        )
        for future in as_completed(futures):
            device = futures[future]
            try:
                diagnostic_paths.extend(future.result())
            except Exception as error:
                report_logger.print_error(f"FAIL: {device}: failure diagnostics collection failed: {error}")
    return scenario_dir, diagnostic_paths