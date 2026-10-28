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
import shlex
from threading import Lock
import time
from rdkbmeshzap.common_utils import device_utils, report_logger

# Limit SSH channel setup and stream inactivity.
LOG_TRANSFER_SOCKET_TIMEOUT = 30
# Limit the total duration of a log transfer.
LOG_TRANSFER_DEADLINE_SECONDS = 600
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
DEVICE_CONNECTION_LOCK = Lock()

def stream_log(connection_obj, device, remote_path, local_path, compress=False, remote_command=None):
    """
    Syntax : stream_log(connection_obj, device, remote_path, local_path, compress=False)
    Description : Streams a complete remote log to a local file, optionally compressed.
    Parameters :
        connection_obj - Selected Zaero connection object for the device.
        device - Name of the device containing the log.
        remote_path - Absolute path to the remote log file.
        local_path - Destination path for the log.
        compress - Compress the log on the remote device before transferring it.
        remote_command - Optional command that writes the log data to stdout.
    Return Value: None. Raises an exception when the transfer fails or times out.
    """
    # Use the device-specific client so parallel transfers avoid shared alias switching.
    connection_registry = getattr(type(connection_obj), "_SshInterface__objects")
    ssh_client = connection_registry[device]["client"]
    transport = ssh_client.get_transport()
    if transport is None or not transport.is_active():
        raise RuntimeError(f"SSH transport for {device} is not active")
    deadline = time.monotonic() + LOG_TRANSFER_DEADLINE_SECONDS
    last_activity = time.monotonic()
    partial_path = local_path.with_name(local_path.name + ".part")
    # Preserve remote command errors for the transfer failure message.
    error_output = bytearray()
    channel = transport.open_session(timeout=LOG_TRANSFER_SOCKET_TIMEOUT)
    try:
        if remote_command is None:
            command = "gzip -c" if compress else "cat"
            remote_command = f"{command} -- {shlex.quote(remote_path)}"
        channel.exec_command(remote_command)
        with partial_path.open("wb") as output:
            # Drain both streams while enforcing inactivity and total-time limits.
            while not channel.exit_status_ready() or channel.recv_ready() or channel.recv_stderr_ready():
                now = time.monotonic()
                if now > deadline:
                    raise TimeoutError(f"Full log transfer exceeded {LOG_TRANSFER_DEADLINE_SECONDS} seconds")
                if now - last_activity > LOG_TRANSFER_SOCKET_TIMEOUT:
                    raise TimeoutError(f"Full log transfer was inactive for {LOG_TRANSFER_SOCKET_TIMEOUT} seconds")
                received_data = False
                if channel.recv_ready():
                    data = channel.recv(65536)
                    if data:
                        output.write(data)
                        received_data = True
                if channel.recv_stderr_ready():
                    error_data = channel.recv_stderr(65536)
                    if error_data:
                        error_output.extend(error_data)
                        received_data = True
                if received_data:
                    last_activity = time.monotonic()
                else:
                    time.sleep(0.05)
            exit_status = channel.recv_exit_status()
        if exit_status != 0:
            error_message = error_output.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"Remote log command failed with exit status {exit_status}{': ' + error_message if error_message else ''}")
        # Publish the file only after the remote command succeeds.
        partial_path.replace(local_path)
    except Exception:
        partial_path.unlink(missing_ok=True)
        raise
    finally:
        channel.close()

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
        output, error = result if isinstance(result, tuple) else (result, "")
        debug_sections.append(f"\n--- {name} ---\n{output or ''}\n{error or ''}\n")
    except Exception as error:
        debug_sections.append(f"\n--- {name} collection failed ---\n{error}\n")

def collect_device_failure_diagnostics(initialize, scenario_dir, device):
    """
    Syntax : collect_device_failure_diagnostics(initialize, scenario_dir, device)
    Description : Collects command output and complete compressed logs for one device.
    Parameters :
        initialize - Testbed initialization object used to access device APIs.
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
    try:
        connection = initialize.read_from_database(device, "connection")
        connection_obj = initialize.get_connection_module_object(connection)
    except Exception as error:
        debug_sections.append(f"Connection failed: {error}\n")
        report_logger.print_error(f"FAIL: {device}: failure diagnostics connection failed: {error}")
        try:
            device_dir.mkdir(parents=True, exist_ok=True)
            debug_info_path.write_text("".join(debug_sections), encoding="utf-8")
            diagnostic_paths.append(debug_info_path)
        except Exception:
            pass
        return diagnostic_paths
    device_dir.mkdir(parents=True, exist_ok=True)
    # Snapshot the live logs before running other diagnostic commands.
    log_paths_with_compression = (
        CONTROLLER_LOG_PATHS_WITH_COMPRESSION
        if device == "controller"
        else EXTENDER_LOG_PATHS_WITH_COMPRESSION
    )
    # Transfer this device's full logs concurrently to reduce collection time.
    with ThreadPoolExecutor(max_workers=len(log_paths_with_compression) + 1) as executor:
        transfers = {}
        for remote_path, compress in log_paths_with_compression:
            suffix = ".gz" if compress else ""
            local_path = device_dir / f"{Path(remote_path).name}{suffix}"
            transfers[executor.submit(stream_log, connection_obj, device, remote_path, local_path, compress=compress)] = (remote_path, local_path)
        onewifi_local_path = device_dir / "onewifi_logs.tar.gz"
        transfers[
            executor.submit(
                stream_log,
                connection_obj,
                device,
                "/rdklogs/logs",
                onewifi_local_path,
                remote_command=(
                    "cd /rdklogs/logs && "
                    "find . -type f -iname 'wifi*' -print | tar -czf - -T -"
                ),
            )
        ] = ("OneWifi logs in /rdklogs/logs", onewifi_local_path)
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
        with DEVICE_CONNECTION_LOCK:
            connection_obj.switch_connection(device)
            services = CONTROLLER_SERVICES if device == "controller" else EXTENDER_SERVICES
            debug_sections.append("\n--- Services checked ---\n" + "\n".join(services) + "\n")
            service_command = " ".join(services)
            record_command_output(debug_sections, "systemctl status", lambda: connection_obj.execute_command(f"systemctl status {service_command} --no-pager 2>&1", return_stderr=True))
            record_command_output(debug_sections, "iw dev", lambda: initialize.get_iw_dev_info(device, method="cli"))
            record_command_output(debug_sections, "ifconfig", lambda: connection_obj.execute_command("ifconfig 2>&1", return_stderr=True))
            record_command_output(debug_sections, "version.txt", lambda: connection_obj.execute_command("cat /version.txt 2>&1", return_stderr=True))
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