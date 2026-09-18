"""Controller recovery orchestration helpers."""

import time
import re
import pytest
from packet_analyzer.ieee1905_utils import *
from packet_analyzer.packet_dissector import *
import test_report_utils as zi_logger

import client_utils
import device_utils

RECOVERY_KPI_SECONDS = 300
RETRY_INTERVAL_SECONDS = 5
MAX_RETRIES = RECOVERY_KPI_SECONDS // RETRY_INTERVAL_SECONDS
def reconnect_device(initialize, device, logger=zi_logger, step=None, started_at=None):
    """Reconnect a device within the configured recovery KPI window."""
    message = f"{device}: waiting for SSH recovery"
    logger.print_step(message if step is None else f"STEP {step}: {message}")
    deadline = time.monotonic() + RECOVERY_KPI_SECONDS
    if started_at is not None:
        deadline = started_at + RECOVERY_KPI_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        if time.monotonic() >= deadline:
            break
        initialize.close_connection(device)
        try:
            initialize.connect_with_device(device)
        except Exception as error:
            logger.print_step(f"{device} connect attempt {attempt} failed: {error}")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(RETRY_INTERVAL_SECONDS, remaining))
            continue
        if time.monotonic() > deadline:
            break
        logger.print_success(f"PASS: {device} connection restored on attempt {attempt}")
        return
    pytest.fail(
        f"Could not reconnect {device} within {RECOVERY_KPI_SECONDS} seconds"
    )

def recover_device(initialize, device, started_at, results, step, logger=zi_logger):
    """Reconnect a device, verify services, and record recovery time."""
    try:
        reconnect_device(
            initialize, device, logger, step=step, started_at=started_at
        )
        recovery_time = time.monotonic() - started_at
        if recovery_time >= RECOVERY_KPI_SECONDS:
            pytest.fail(
                f"{device}: recovery exceeded {RECOVERY_KPI_SECONDS} seconds"
            )
        deadline = started_at + RECOVERY_KPI_SECONDS
        if device == "controller":
            device_utils.verify_controller_services(initialize, step, deadline)
        else:
            device_utils.verify_extender_services(initialize, device, deadline)
        results[device] = recovery_time
        logger.print_success(f"PASS: {device} connection restored in {recovery_time:.1f}s")
        return recovery_time
    except Exception as error:
        results[device] = error
        return error

def stop_collect_reassemble_and_validate_topology_capture(
    initialize, extender, capture_name, step, extender_al_mac=None
):
    """Collect a capture, reassemble packets, and validate topology traffic."""
    local_path = device_utils.stop_and_collect_capture(
        initialize, extender, capture_name
    )
    packets = reassemble_packets(local_path)
    validate_topology_capture(packets, extender, step, extender_al_mac)
    return local_path

def validate_topology_capture(packets, extender, step, extender_al_mac=None):
    """Require topology query and response messages in a recovery capture."""
    for message_type, message_name in (
        (MSG_TYPE_AP_TOPOLOGY_QUERY, "Topology Query"),
        (MSG_TYPE_AP_TOPOLOGY_RESPONSE, "Topology Response"),
    ):
        if extender_al_mac:
            present = check_message_presence(
                packets, message_type, src_mac=extender_al_mac
            ) or check_message_presence(packets, message_type, dst_mac=extender_al_mac)
        else:
            present = check_message_presence(packets, message_type) or []
        if not present:
            pytest.fail(f"{extender}: expected {message_name} after recovery")

def get_bssid_device(initialize, devices, bssid):
    """Return the device exposing the requested Wi-Fi BSSID."""
    normalized_bssid = (bssid or "").lower()
    ssh = initialize.get_connection_module_object("ssh")
    for device in devices:
        try:
            ssh.switch_connection(device)
            output = ssh.execute_command("iw dev")
        except Exception:
            continue
        if re.search(
            rf"^\s*addr\s+{re.escape(normalized_bssid)}\b",
            str(output),
            re.IGNORECASE | re.MULTILINE,
        ):
            return device
    return None

def map_clients_to_extenders(client_devices, extenders):
    """Map the first configured WLAN client to each extender."""
    client_groups = {
        extender: next(
            ([client] for client in client_devices if client.startswith(f"{extender}_")),
            [],
        )
        for extender in extenders
    }
    missing = [extender for extender in extenders if not client_groups[extender]]
    if missing:
        pytest.fail(
            "No enabled WLAN client is configured for extender(s): "
            f"{', '.join(missing)}"
        )
    return client_groups

def recover_extender_and_client(initialize, interface_cli, extender, clients, capture_name,
                     started_at, allowed_bssids, results, step=None):
    """Recover an extender, collect its capture, and validate client access."""
    try:
        recovery_result = recover_device(
            initialize, extender, started_at, results, step, zi_logger
        )
        if isinstance(recovery_result, Exception):
            raise recovery_result
        results[extender] = {
            "recovery_time": recovery_result,
            "clients": clients,
        }
        time.sleep(20)
        local_path = device_utils.stop_and_collect_capture(
            initialize, extender, capture_name
        )
        results[extender]["capture_path"] = local_path
        for client in clients:
            reconnect_device(initialize, client, zi_logger, step=9)
        results[extender]["client_accessible"] = all(
            initialize.is_device_alive(client) for client in clients
        )
        ssh = initialize.get_connection_module_object("ssh")
        results[extender]["client_bssids"] = {
            client: client_utils.get_connected_client_bssid(initialize, client, ssh)
            for client in clients
        }
        results[extender]["bssid_matches"] = {
            client: bssid in allowed_bssids
            for client, bssid in results[extender]["client_bssids"].items()
        }
        results[extender]["ping_outputs"] = client_utils.download_client_pings(
            initialize, clients, extender
        )
    except Exception as error:
        results[extender] = {"error": error}
