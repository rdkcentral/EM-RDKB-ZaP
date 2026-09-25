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

import time
import pytest
from rdkbmeshzap.common_utils import report_logger

def get_enabled_extenders(initialize):
    """
    Return enabled extender devices from the configured testbed.
    """
    return [
        device
        for device in initialize.get_testbed_devices()
        if (
            device.startswith("extender")
            and "_client_" not in device
            and initialize.read_from_database(device, "device_present")
        )
    ]

def get_enabled_device_al_macs(initialize):
    """
    Return AL MAC addresses for enabled controller and extender devices.
    """
    devices = [
        device
        for device in initialize.get_testbed_devices()
        if device == "controller"
        or (device.startswith("extender") and "_client_" not in device)
    ]
    devices = [
        device
        for device in devices
        if initialize.read_from_database(device, "device_present")
    ]
    return {
        device: initialize.get_al_mac_address(device, "cli").lower()
        for device in devices
    }

def create_capture_name(prefix, device=None, extension="pcapng"):
    """
    Create a timestamped capture filename, optionally including a device.
    """
    device_suffix = f"_{device}" if device else ""
    return f"{prefix}{device_suffix}_{time.time_ns()}.{extension}"

def get_backhaul_capture_interface(initialize, device):
    """
    Return the backhaul capture interface configured in platform YAML.
    """
    capture_interface = initialize.read_from_database(device, "backhaul_capture_iface")
    if not capture_interface:
        pytest.fail(
            f"{device}: backhaul_capture_iface is missing from platform YAML"
        )
    return capture_interface

def start_capture(initialize, device, capture_prefix, step, include_device=False):
    """
    Start an IEEE 1905 capture on a device backhaul interface.
    """
    capture_device = device if include_device else None
    capture_name = create_capture_name(capture_prefix, capture_device)
    capture_interface = get_backhaul_capture_interface(initialize, device)
    capture_filter = initialize.read_from_database(device, "filter_1905")
    report_logger.print_step(
        f"STEP {step}: Start packet capture on {device}"
    )
    initialize.start_frame_capture(
        device, capture_interface, capture_filter, capture_name
    )
    report_logger.print_success(
        f"PASS: Capture started in {device}; capture name: {capture_name}; "
        f"interface: {capture_interface}"
    )
    return capture_name

def stop_and_collect_capture(initialize, device, capture_name):
    """
    Stop, download, and remove a device capture.
    """
    report_logger.print_step(f"Stop and collect packet capture from {device}")
    initialize.stop_frame_capture(device)
    local_path = initialize.download_captured_pcap(device, capture_name)
    try:
        initialize.delete_captured_pcap(device, capture_name)
    except Exception as error:
        report_logger.print_info(
            f"{device}: capture already unavailable during cleanup: {error}"
        )
    report_logger.print_success(
        f"PASS: Capture stopped and collected successfully for {device}: {local_path}"
    )
    return local_path

def verify_services(initialize, device, service_names, deadline=None):
    """
    Verify required services with retries bounded by an optional deadline.
    """
    if not service_names:
        pytest.fail(f"{device}: no services were configured for validation")

    if deadline is None:
        deadline = time.monotonic() + 2
    last_error = None
    attempts = 0
    while time.monotonic() < deadline:
        attempts += 1
        try:
            for service_name in service_names:
                initialize.verify_service_status(device, service_name)
            return
        except Exception as error:
            last_error = error
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(2, remaining))
    if attempts == 0:
        pytest.fail(f"{device}: service validation deadline expired before an attempt")
    pytest.fail(f"{device}: services did not become active after {attempts} attempts: {last_error}")

def verify_controller_services(initialize, deadline=None):
    """
    Verify controller services after recovery.
    """
    verify_services(
        initialize,
        "controller",
        ("onewifi", "ieee1905_em_agent", "ieee1905_em_ctrl", "em_ctrl"),
        deadline,
    )

def verify_extender_services(initialize, extender, deadline=None):
    """
    Verify extender services after recovery.
    """
    verify_services(
        initialize,
        extender,
        ("onewifi", "ieee1905_em_agent", "em_agent"),
        deadline,
    )
