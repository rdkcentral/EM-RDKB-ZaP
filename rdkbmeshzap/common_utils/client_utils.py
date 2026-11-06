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
import shlex
import time
from rdkbmeshzap.common_utils import report_logger

def remove_and_connect_client(initialize, client, ssid, password):
    """
    Syntax: remove_and_connect_client(initialize, client, ssid, password)
    Description: Remove existing Wi-Fi connections from the client and attempt to connect it to the specified SSID using the available 2.4 GHz, 5 GHz, or 6 GHz radio BSSID of the associated device.
<<<<<<< HEAD
    Parameters: initialize - Testbed interface, 
                client - Client device name, 
                ssid - Wi-Fi network SSID, 
                password - Wi-Fi network password.
=======
    Parameters: initialize - Testbed interface; client - Client device name; ssid - Wi-Fi network SSID; password - Wi-Fi network password.
>>>>>>> 92c86c6 (Issue #133 Test Script Development for Client Association Phase2)
    Return Value: True if the client successfully connects through any available radio; otherwise, False.
    Example: remove_and_connect_client(initialize, "controller_wlan_client_1", "EasyMesh_SSID", "password123")
    """
    if not initialize.read_from_database(client, "device_present"):
        report_logger.print_info(f"INFO: {client} is not present, skipping")
        return False
    device = client.split("_wlan_client")[0]
    try:
        radio_macs = {
            "2G": initialize.read_from_database(device, "2g_radio_mac"),
            "5G": initialize.read_from_database(device, "5g_radio_mac"),
            "6G": initialize.read_from_database(device, "6g_radio_mac")
        }
        for radio, device_bssid in radio_macs.items():
            if not device_bssid:
                report_logger.print_info(f"INFO: {radio} radio MAC is not available for {device}, skipping")
                continue
            report_logger.print_info(f"INFO: Removing existing Wi-Fi connections for {client}")
            initialize.remove_all_wifi_connections(client)
            report_logger.print_info(f"INFO: Trying to connect {client} through {radio} radio ({device_bssid})")
            try:
                initialize.connect_client_to_ssid(client, ssid, password, device_bssid)
                time.sleep(10)
                report_logger.print_success(f"PASS: {client} connected through {radio} radio ({device_bssid})")
                return True
            except Exception as e:
                report_logger.print_info(f"INFO: {client} failed to connect through {radio} radio ({device_bssid}): {e} ")
        report_logger.print_info(f"INFO: {client} could not connect through 2G, 5G or 6G radio")
        return False
    except Exception as e:
        report_logger.print_info(f"INFO: Failed to connect client {client} to SSID {ssid}: {e}")
        return False

def verify_client_association(initialize, client):
    """
    Syntax: verify_client_association(initialize, client)
    Description: Verify whether a Wi-Fi client is successfully associated with any known 2.4 GHz, 5 GHz, or 6 GHz radio of its corresponding device by comparing the associated MAC address with the available radio MAC addresses.
    Parameters: initialize - Testbed interface,
                client - Client device name.
    Return Value: True if the client is successfully associated with any known radio; otherwise, False.
    Example: verify_client_association(initialize, "controller_wlan_client_1")
    """
    try:
        device = client.split("_wlan_client")[0]
        radio_macs = {"2G": initialize.read_from_database(device, "2g_radio_mac"),"5G": initialize.read_from_database(device, "5g_radio_mac"),"6G": initialize.read_from_database(device, "6g_radio_mac")}
        associated_mac = initialize.get_association_status(client, "cli")
        if not associated_mac:
            report_logger.print_error(f"FAIL: No associated MAC found for {client}.")
            return False
        associated_radio = None
        for radio, radio_mac in radio_macs.items():
            if radio_mac and associated_mac.lower() == radio_mac.lower():
                associated_radio = radio
                break
        if associated_radio:
            report_logger.print_info(f"INFO: {client} is associated with {device} {associated_radio} radio ({associated_mac})")           
            return True
        report_logger.print_error(f"FAIL: {client} is not associated with any known radio of {device}. Associated MAC: {associated_mac}")        
        return False
    except Exception as e:
        report_logger.print_error(f"FAIL: Association verification failed for {client}: {e}")
        return False
