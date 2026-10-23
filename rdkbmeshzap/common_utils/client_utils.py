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

import re
from rdkbmeshzap.common_utils import report_logger

def get_present_device_bssids(initialize):
    """
    Syntax: get_present_device_bssids(initialize)
    Description: Returns the fronthaul BSSIDs of all present mesh devices in the topology. 
    Parameters: 
        initialize : Test initialization object.
    Return Value: set: Fronthaul BSSIDs of present mesh devices in lowercase format.
    """
    bssids = set()
    for device in initialize.get_testbed_devices():
        if device != "controller" and not re.fullmatch(r"extender\d+", device):
            continue
        present = initialize.read_from_database(device, "device_present")
        if present is False or (
            isinstance(present, str)
            and present.strip().lower() in {"false", "no", "0", "off"}):
            continue
        try:
            bssids.update(
                bssid.lower()
                for bssid in initialize.get_fronthaul_bssids(device))
        except Exception as error:
            report_logger.print_info(
                f"Unable to read fronthaul BSSIDs from present device "
                f"'{device}': {error}")
    return bssids

def connect_wlan_clients(initialize, client_devices, require_all=True):
    """
    Syntax: connect_wlan_clients(initialize, client_devices,require_all=True)
    Description: Connects WLAN clients to the fronthaul SSID and verifies successful association to a valid present-device BSSID.
    Parameters:
        initialize : Test initialization object.
        client_devices : List of WLAN client device names.
        require_all : If True, all clients must connect successfully.
        If False, returns only successfully connected clients.
    Return Value: list: Connected client devices.
    """
    clients = list(client_devices)
    if not clients:
        return []
    ssid, passphrase = initialize.get_fronthaul_credentials("controller")
    allowed_bssids = get_present_device_bssids(initialize)
    if not allowed_bssids:
        message = ("No fronthaul BSSIDs found for present mesh devices")
        raise Exception(message)  
    last_errors = {}
    connected_clients = []
    for client in clients:
        try:
            report_logger.print_info(f"Connecting WLAN client '{client}' to SSID '{ssid}'")
            initialize.remove_client_connection(client,ssid)
            initialize.check_ap_ssid_visibility(client,ssid)
            initialize.connect_client_to_ssid(device=client,ssid=ssid,password=passphrase)
            connected_bssid = initialize.get_association_status(client,"cli")
            if not connected_bssid:
                message = (f"{client} is not connected after connection attempt")
                raise Exception(message)
            connected_bssid = connected_bssid.lower()
            if connected_bssid not in allowed_bssids:
                message = (f"{client} is connected to {connected_bssid}, not an "
                            f"allowed present-device BSSID {sorted(allowed_bssids)}")
                raise Exception(message)
            report_logger.print_info(f"Client '{client}' successfully connected to BSSID '{connected_bssid}'")
            connected_clients.append(client)
        except Exception as error:
            last_errors[client] = error
            if not require_all:
                try:
                    connected_bssid = initialize.get_association_status(client, "cli").lower()
                except Exception:
                    connected_bssid = None
                if connected_bssid in allowed_bssids:
                    report_logger.print_info(
                        f"Client '{client}' remains connected to BSSID {connected_bssid}; connection setup failed ({error}), continuing with link validation")
                    connected_clients.append(client)
                    continue
            report_logger.print_info(f"Client '{client}' connection attempt failed: {error}")
    if not require_all:
        unavailable = [client for client in clients if client not in connected_clients]
        if unavailable:
            report_logger.print_info(f"Skipping unavailable WLAN clients after one attempt: {', '.join(unavailable)}")
        return connected_clients
    if len(connected_clients) == len(clients):
        return connected_clients
    raise Exception(
        f"Unable to connect all clients after one attempt: {last_errors}") from next(iter(last_errors.values()), None)
