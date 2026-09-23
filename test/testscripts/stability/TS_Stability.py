# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 Zilogic Systems
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
import os
import zaero
from os import path
file_path = "/nvram/stability_issue"
log_paths = ["/nvram/onewifi_em_ctrl_monitor.csv", "/nvram/onewifi_em_agent_monitor.csv", "/nvram/OneWifi_monitor.csv"]
import pytest
import time
from stability_config import (
    channel_update_max_count,
    fronthaul_toggle_max_count,
    ssid_update_max_count,
    timeout,
)
from stability_utils import *
from zaero.utils import zi_logger
from datetime import datetime
from rdkbmeshzap.common_utils import report_logger
 
@pytest.fixture(autouse=True)
def common_setup(initialize):
    ctrl_ip = initialize.read_from_database("controller", "login_ip")
    monitoring_tool_path = path.join(path.dirname(path.abspath(__file__)), "monitoring_tool.py")
    monitor_service_path = path.join(path.dirname(path.abspath(__file__)), "monitor_service.service")
    if not copy_file_to_remote(monitoring_tool_path, ctrl_ip, "/nvram/"):
        raise RuntimeError("Failed to copy monitoring tool file to controller")
    if not copy_file_to_remote(monitor_service_path, ctrl_ip, "/etc/systemd/system/"):
        raise RuntimeError("Failed to copy service file to controller")
    zaero_obj = zaero.zaero()
    devices = zaero_obj.get_testbed_devices()
    yield devices

def test_stability_24hours(initialize, common_setup):
    report_logger.print_test(f"[{get_timestamp()}] Entering test_stability_24hours")
    devices = common_setup
    report_logger.print_info("Starting monitor_service in controller")
    initialize.start_service("controller", "monitor_service.service")
    ctrl_timestamp = initialize.get_time_stamp("controller")
    start_time = time.time()
    # Run the 24-hour stability check for the configured timeout duration.
    report_logger.print_step("STEP1: Starting 24-hour stability check loop for verifying core dump and backhaul status")
    while (time.time() - start_time) < timeout:
        report_logger.print_info(f"Checking core dump status in controller")
        if initialize.get_file_presence_status("controller", "/tmp/*dmp"):
            report_logger.print_error(f"[{get_timestamp()}] Core dump found on controller.")
            break;
        else:
            report_logger.print_success(f"No core dump found on controller.")
        #also check device is not "controller"
        for device in devices[:]:
            if device != "controller":
                # currently checking only wireless backhaul status wired has issues https://jira.rdkcentral.com/jira/browse/RDKBWIFI-580
                report_logger.print_info(f"Checking wireless backhaul status for {device}")
                if not initialize.get_wireless_backhaul_connection_status(device):
                    report_logger.print_error(f"[{get_timestamp()}] {device} is not connected to the backhaul.")
                    devices.remove(device)
                else:
                    report_logger.print_success(f"{device} is connected to the backhaul.")
        time.sleep(30)  # Wait for 1 minute before the next iteration to avoid excessive polling
    report_logger.print_info("Stopping monitor_service in controller")
    initialize.stop_service("controller", "monitor_service.service")
    ctrl_local_dir = initialize.read_from_database("controller", "local_log_directory")
    # append test method name and timestamp to the local directory for better organization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ctrl_local_dir = os.path.join(ctrl_local_dir, "test_stability_24hours_" + str(timestamp))
    #create directory if not exist allready
    if not os.path.exists(ctrl_local_dir):
        os.makedirs(ctrl_local_dir)
    for log_file in log_paths:
        report_logger.print_info(f"Downloading log file locally and deleting remote file instance: {log_file}")
        initialize.download_pcap("controller", log_file, ctrl_local_dir)
        initialize.delete_pcap("controller", log_file)
    report_logger.print_step(f"STEP2: Analyzing downloaded log files in {ctrl_local_dir}")
    log_analyzer(ctrl_local_dir)
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_24hours")

def test_stability_ssid_update(initialize, common_setup):
    report_logger.print_test(f"[{get_timestamp()}] Entering test_stability_ssid_update")
    devices = common_setup
    report_logger.print_info("Starting monitor_service in controller")
    initialize.start_service("controller","monitor_service.service")
    ssid_update_current_count = 0
    while ssid_update_current_count < ssid_update_max_count:
        ssid_update_current_count += 1
        ssid = initialize.get_random_ssid()
        report_logger.print_step(f"count: {ssid_update_current_count} Updating SSID to {ssid}")
        initialize.set_ssid("controller", "mld_iface_index", ssid, 'gui')
        time.sleep(30)
        #check ssid update on indivdual devices
        for device in devices[:]:
            try:
                report_logger.print_info(f"Checking SSID on {device}")
                initialize.check_ssid(device, "mld_iface_index", ssid, 'cli')
            except Exception as ERR:
                report_logger.print_error(f"count :{ssid_update_current_count} check_ssid failed in {device}: {ERR}")
                devices.remove(device)
            else:
                report_logger.print_success(f"SSID matched successfully in {device}")
        if not devices:
            break
    report_logger.print_info("Stopping monitor_service in controller")
    initialize.stop_service("controller", "monitor_service.service")
    ctrl_local_dir = initialize.read_from_database("controller", "pcap_local_dir")
    # append test method name and timestamp to the local directory for better organization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ctrl_local_dir = os.path.join(ctrl_local_dir, "test_stability_ssid_update_" + str(timestamp))
    #create directory if not exist allready
    if not os.path.exists(ctrl_local_dir):
        os.makedirs(ctrl_local_dir)
    for log_file in log_paths:
        report_logger.print_info(f"Downloading log file locally and deleting remote file instance: {log_file}")
        initialize.download_pcap("controller", log_file, ctrl_local_dir)
        initialize.delete_pcap("controller", log_file)
    report_logger.print_step(f"Analyzing downloaded log files in {ctrl_local_dir}")
    log_analyzer(ctrl_local_dir)
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_ssid_update")

def test_stability_channel_update(initialize, common_setup):
    report_logger.print_test(f"[{get_timestamp()}] Entering test_stability_channel_update")
    devices = common_setup
    channel_update_current_count = 0
    while channel_update_current_count < channel_update_max_count:
        report_logger.print_step(f"Starting channel update iteration {channel_update_current_count + 1}")
        report_logger.print_info(f"Fetching current operating channel from the controller")
        operating_channel = initialize.get_operating_channel("controller","2.4")
        report_logger.print_info(f"Current operating channel is {operating_channel}")
        #  alter the channel preference like operating channel is other than 6 set it to 6 , if current operating channel is 6 set it to 1
        if operating_channel != 6:
            operating_channel_to_set = 6
            report_logger.print_info(f"Setting operating channel to 6")
            initialize.set_channel_preference_for_2_4_band("controller", uncheck_channel=operating_channel, check_channel=6, priority=14)
        else:
            report_logger.print_info(f"Setting operating channel to 1")
            initialize.set_channel_preference_for_2_4_band("controller", uncheck_channel=6, check_channel=1, priority=14)
            operating_channel_to_set = 1
        channel_update_current_count += 1
        time.sleep(30)
        for device in devices[:]:
            report_logger.print_info(f"Fetching current operating channel from the device {device}")
            current_operating_channel = initialize.get_operating_channel(device,"2.4")
            if current_operating_channel != operating_channel_to_set:
                report_logger.print_error(f"count : {channel_update_current_count} Channel update failed in {device}: expected {operating_channel_to_set}, got {current_operating_channel}")
                devices.remove(device)
            else:
                report_logger.print_success(f"count : {channel_update_current_count} Channel updated successfully in {device} to {current_operating_channel}")
        if not devices:
            break
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_channel_update")

def test_stability_fronthaul_toggle(initialize, common_setup):
    report_logger.print_test(f"[{get_timestamp()}] Entering test_stability_fronthaul_toggle")
    devices = common_setup
    print(devices)
    fronthaul_toggle_current_count = 0
    while fronthaul_toggle_current_count < fronthaul_toggle_max_count:
        report_logger.print_info(f"Starting fronthaul toggle iteration {fronthaul_toggle_current_count + 1}")
        report_logger.print_info(f"Fetching current MLD status from the controller")
        current_mld_status = initialize.get_mld_status("controller")
        report_logger.print_info(f"Current MLD status from the controller: {current_mld_status}")
        #toggle mld status
        set_mld_status = not current_mld_status
        report_logger.print_info(f"Setting MLD status to: {set_mld_status}")
        initialize.set_fronthaul_network_state("controller", "Home Network", enable=set_mld_status)
        fronthaul_toggle_current_count += 1
        time.sleep(60)
        for device in devices[:]:
            report_logger.print_info(f"Fetching current MLD status from the device {device}")
            mld_status = initialize.get_mld_status(device)
            if mld_status != set_mld_status:
                report_logger.print_error(f"count : {fronthaul_toggle_current_count} Fronthaul network profile toggle failed in {device}: expected {set_mld_status}, got {mld_status}")
                devices.remove(device)
            else:
                report_logger.print_success(f"count : {fronthaul_toggle_current_count} Fronthaul network profile toggle succeeded in {device}")
        if not devices:
            break
    report_logger.print_test(f"[{get_timestamp()}] Exiting test_stability_fronthaul_toggle")
