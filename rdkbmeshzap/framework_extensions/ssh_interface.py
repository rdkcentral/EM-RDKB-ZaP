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

import shlex
import time
from pathlib import Path
from typing import Optional, Tuple
from zaero.utils.ssh_interface import SshInterface

class SshInterface_Extension(SshInterface):
    """
    Extended SshInterface with SSH capabilities.
    
    Provides methods for command execution and file transfer with timeout
    enforcement and proper error handling.
    
    """

    def get_ssh_client(self, device: str):
        """
        Extract the underlying SSH client from SshInterface's registry.
        
        Args:
            device: Device alias/name.
            
        Returns:
            Paramiko SSHClient instance.
            
        Raises:
            RuntimeError: If SSH client cannot be accessed.
        """
        try:
            connection_registry = getattr(type(self), "_SshInterface__objects")
            if device not in connection_registry:
                raise RuntimeError(f"Device '{device}' not found in SSH connection registry")
            return connection_registry[device]["client"]
        except (AttributeError, KeyError, TypeError) as e:
            raise RuntimeError(f"Cannot access SSH client for {device}: {e}")

    def get_ssh_transport(self, device: str):
        """
        Extract the SSH transport from the client.
        
        Args:
            device: Device alias/name.
            
        Returns:
            Paramiko Transport instance.
            
        Raises:
            RuntimeError: If transport is not available or not active.
        """
        ssh_client = self.get_ssh_client(device)
        transport = ssh_client.get_transport()
        if transport is None or not transport.is_active():
            raise RuntimeError(f"SSH transport for {device} is not active")
        return transport

    def open_ssh_channel(self, device: str, timeout: Optional[float] = None):
        """
        Open a new SSH channel for a device.
        
        Args:
            device: Device alias/name.
            timeout: Socket timeout in seconds.
            
        Returns:
            Paramiko Channel object.
            
        Raises:
            RuntimeError: If channel cannot be opened.
        """
        transport = self.get_ssh_transport(device)
        try:
            return transport.open_session(timeout=timeout)
        except Exception as e:
            raise RuntimeError(f"Cannot open SSH channel for {device}: {e}") from e

    def execute_command_with_result(
        self,
        device: str,
        command: str,
        timeout: Optional[float] = None,
        encoding: str = "utf-8",
        errors: str = "replace"
    ) -> Tuple[str, str, int]:
        """
        Execute a command and return decoded stdout/stderr plus exit status.
        
        Args:
            device: Device alias/name.
            command: Command to execute on the remote device.
            timeout: Channel-open and output inactivity timeout in seconds.
            encoding: Text encoding for output (default: utf-8).
            errors: Error handling mode ('replace', 'ignore', 'strict').
            
        Returns:
            Tuple of (stdout_text, stderr_text, exit_status).
            
        Example:
            stdout, stderr, status = initialize.execute_command_with_result(device, "uname -a")

        Raises:
            RuntimeError: If transport or command execution fails.
        """
        channel = None
        try:
            channel = self.open_ssh_channel(device, timeout=timeout)
            channel.exec_command(command)

            stdout_data = bytearray()
            stderr_data = bytearray()
            buffer_size = 65536
            last_activity = time.monotonic()

            while not channel.exit_status_ready():
                received_data = False
                if channel.recv_ready():
                    data = channel.recv(buffer_size)
                    if data:
                        stdout_data.extend(data)
                        received_data = True
                if channel.recv_stderr_ready():
                    error_data = channel.recv_stderr(buffer_size)
                    if error_data:
                        stderr_data.extend(error_data)
                        received_data = True
                if received_data:
                    last_activity = time.monotonic()
                elif timeout is not None and time.monotonic() - last_activity >= timeout:
                    raise TimeoutError(f"Command on {device} was inactive for {timeout} seconds")
                time.sleep(0.01)

            while channel.recv_ready():
                data = channel.recv(buffer_size)
                if data:
                    stdout_data.extend(data)
            while channel.recv_stderr_ready():
                error_data = channel.recv_stderr(buffer_size)
                if error_data:
                    stderr_data.extend(error_data)

            exit_status = channel.recv_exit_status()
            return (
                bytes(stdout_data).decode(encoding, errors=errors),
                bytes(stderr_data).decode(encoding, errors=errors),
                exit_status
            )

        except (RuntimeError, TimeoutError):
            raise
        except Exception as e:
            raise RuntimeError(f"Command execution failed on {device}: {e}") from e
        finally:
            if channel is not None:
                try:
                    channel.close()
                except Exception:
                    pass

    def stream_command_output_to_file(
        self,
        device: str,
        remote_command: str,
        local_path: Path,
        socket_timeout: float = 30,
        total_timeout: float = 600,
        buffer_size: int = 65536
    ) -> None:
        """
        Stream command output to a local file with timeout enforcement.
        
        Args:
            device: Device alias/name.
            remote_command: Command to execute that produces output via stdout.
            local_path: Local file path to write output to.
            socket_timeout: Maximum inactivity time per socket operation (seconds).
            total_timeout: Maximum total transfer duration (seconds).
            buffer_size: Size of read buffer for each recv call.
            
        Example:
            initialize.stream_command_output_to_file(device, "dmesg", Path("dmesg.log"))

        Raises:
            RuntimeError: If transport or command execution fails.
            TimeoutError: If operation exceeds timeout limits.
            IOError: If file write fails.
        """
        channel = None
        partial_path = local_path.with_name(local_path.name + ".part")
        error_output = bytearray()
        deadline = time.monotonic() + total_timeout

        try:
            remaining_timeout = deadline - time.monotonic()
            if remaining_timeout <= 0:
                raise TimeoutError(f"Stream transfer exceeded {total_timeout} seconds")
            channel = self.open_ssh_channel(device, timeout=min(socket_timeout, remaining_timeout))
            remaining_timeout = deadline - time.monotonic()
            if remaining_timeout <= 0:
                raise TimeoutError(f"Stream transfer exceeded {total_timeout} seconds")
            channel.settimeout(min(socket_timeout, remaining_timeout))
            channel.exec_command(remote_command)
            last_activity = time.monotonic()

            with partial_path.open("wb") as output:
                while not channel.exit_status_ready() or channel.recv_ready() or channel.recv_stderr_ready():
                    now = time.monotonic()

                    if now >= deadline:
                        raise TimeoutError(f"Stream transfer exceeded {total_timeout} seconds")
                    if now - last_activity > socket_timeout:
                        raise TimeoutError(f"Stream transfer was inactive for {socket_timeout} seconds")

                    received_data = False
                    if channel.recv_ready():
                        data = channel.recv(buffer_size)
                        if data:
                            output.write(data)
                            received_data = True
                    if channel.recv_stderr_ready():
                        error_data = channel.recv_stderr(buffer_size)
                        if error_data:
                            error_output.extend(error_data)
                            received_data = True

                    if received_data:
                        last_activity = time.monotonic()
                    else:
                        time.sleep(0.05)

                exit_status = channel.recv_exit_status()

            if time.monotonic() >= deadline:
                raise TimeoutError(f"Stream transfer exceeded {total_timeout} seconds")

            if exit_status != 0:
                error_message = error_output.decode("utf-8", errors="replace").strip()
                raise RuntimeError(
                    f"Remote command failed with exit status {exit_status}"
                    f"{': ' + error_message if error_message else ''}"
                )

            partial_path.replace(local_path)

        except (RuntimeError, TimeoutError):
            raise
        except Exception as e:
            raise RuntimeError(f"Stream transfer failed for {device}: {e}") from e
        finally:
            partial_path.unlink(missing_ok=True)
            if channel is not None:
                try:
                    channel.close()
                except Exception:
                    pass

    def stream_remote_file(
        self,
        device: str,
        remote_path: str,
        local_path: Path,
        compress: bool = False,
        socket_timeout: float = 30,
        total_timeout: float = 600
    ) -> None:
        """
        Download a remote file (optionally compressed) to a local path.
        
        Args:
            device: Device alias/name.
            remote_path: Absolute path to remote file.
            local_path: Local destination path.
            compress: Compress the file on the remote device before transfer (gzip).
            socket_timeout: Maximum inactivity time per socket operation (seconds).
            total_timeout: Maximum total transfer duration (seconds).
            
        Example:
            initialize.stream_remote_file(device, "/tmp/em_agent.log", Path("em_agent.log"), compress=True)

        Raises:
            RuntimeError: If transport or command execution fails.
            TimeoutError: If operation exceeds timeout limits.
            IOError: If file write fails.
        """
        command = "gzip -c" if compress else "cat"
        remote_command = f"{command} -- {shlex.quote(remote_path)}"
        self.stream_command_output_to_file(
            device,
            remote_command,
            local_path,
            socket_timeout=socket_timeout,
            total_timeout=total_timeout
        )
