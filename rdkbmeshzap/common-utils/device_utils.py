"""Shared testbed and capture helpers."""

import re
import time

import test_report_utils as zi_logger

def get_enabled_extenders(initialize):
    """Return enabled extender devices from the configured testbed."""
    return [
        device
        for device in initialize.get_testbed_devices()
        if (
            device.startswith("extender")
            and "_client_" not in device
            and initialize.read_from_database(device, "device_present")
        )
    ]

def get_enabled_extender_macs(initialize):
    """Return normalized AL MAC addresses for enabled extenders."""
    return {
        device: initialize.get_al_mac_address(device, "cli").lower()
        for device in get_enabled_extenders(initialize)
    }

def get_enabled_testbed_device_macs(initialize):
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

def create_capture_name(prefix, extender, extension="pcapng"):
    """Create a timestamped capture filename for an extender."""
    return f"{prefix}_{extender}_{int(time.time())}.{extension}"

def get_extenders_by_topology_role(initialize, role):
    """Return enabled extenders matching the requested topology role."""
    extenders = []
    for device in initialize.get_testbed_devices():
        if not device.startswith("extender") or "_client_" in device:
            continue
        if not initialize.read_from_database(device, "device_present"):
            continue
        configured_role = initialize.read_from_database(device, "topology_role")
        if configured_role == role:
            extenders.append(device)
        elif configured_role is None and role == "star":
            tunnel_device = initialize.read_from_database(device, "tunnel_device")
            if tunnel_device == "controller":
                extenders.append(device)
    return extenders

def get_backhaul_capture_interface(initialize, device):
    """Determine the interface used to capture a device backhaul."""
    try:
        capture_interface = initialize.read_from_database(
            device, "backhaul_capture_iface"
        )
        if capture_interface:
            return capture_interface
    except Exception:
        pass
    ssh = initialize.get_connection_module_object("ssh")
    ssh.switch_connection(device)
    candidates = re.findall(
        r"\b([A-Za-z0-9_.]+_virt_peer)\b",
        str(ssh.execute_command("ifconfig")),
    )
    for preferred in ("eth1_virt_peer", "eth0_virt_peer"):
        if preferred in candidates:
            return preferred
    if candidates:
        return candidates[0]
    raise RuntimeError(f"{device}: could not determine backhaul capture interface")

def start_capture(initialize, device, capture_prefix, step):
    """
    Start an IEEE 1905 capture on a device backhaul interface.
    """
    capture_name = create_capture_name(capture_prefix, device)
    capture_interface = get_backhaul_capture_interface(initialize, device)
    capture_filter = initialize.read_from_database(device, "filter_1905")
    initialize.start_frame_capture(
        device, capture_interface, capture_filter, capture_name
    )
    zi_logger.print_step(
        f"STEP {step}: {device}: capture started on "
        f"{capture_interface}; file {capture_name}"
    )
    return capture_name

def stop_and_collect_capture(initialize, device, capture_name):
    """
    Stop, download, and remove a device capture.
    """
    initialize.stop_frame_capture(device)
    local_path = initialize.download_captured_pcap(device, capture_name)
    try:
        initialize.delete_captured_pcap(device, capture_name)
    except Exception as error:
        zi_logger.print_step(
            f"{device}: capture already unavailable during cleanup: {error}"
        )
    return local_path

def verify_services(initialize, device, service_names, deadline=None):
    """Verify required services with retries bounded by an optional deadline."""
    last_error = None
    for attempt in range(1, 6):
        if deadline is not None and time.monotonic() >= deadline:
            break
        try:
            for service_name in service_names:
                initialize.verify_service_status(device, service_name)
            return
        except Exception as error:
            last_error = error
            if attempt == 5:
                break
            remaining = deadline - time.monotonic() if deadline else 2
            if remaining <= 0:
                break
            time.sleep(min(2, remaining))
    raise RuntimeError(
        f"{device}: services did not become active after 5 attempts: {last_error}"
    )

def verify_controller_services(initialize, step, deadline=None):
    """Verify controller services after recovery."""
    verify_services(
        initialize,
        "controller",
        ("onewifi", "ieee1905_em_agent", "ieee1905_em_ctrl", "em_ctrl"),
        deadline,
    )

def verify_extender_services(initialize, extender, step, deadline=None):
    """Verify extender services after recovery."""
    verify_services(
        initialize,
        extender,
        ("onewifi", "ieee1905_em_agent", "em_agent"),
        deadline,
    )
