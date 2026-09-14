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
 
@pytest.fixture(autouse=True)
def common_setup(initialize):
    ctrl_ip = initialize.read_from_database("controller", "login_ip")
    extender1_ip = initialize.read_from_database("extender1", "login_ip")
    extender1_user = initialize.read_from_database("extender1", "username")
    monitoring_tool_path = path.join(path.dirname(path.abspath(__file__)), "monitoring_tool.py")
    monitor_service_path = path.join(path.dirname(path.abspath(__file__)), "monitor_service.service")
    if not copy_file_to_remote(monitoring_tool_path, ctrl_ip, "/nvram/"):
        raise RuntimeError("Failed to copy monitoring tool file to controller")
    if not copy_file_to_remote(monitor_service_path, ctrl_ip, "/etc/systemd/system/"):
        raise RuntimeError("Failed to copy service file to controller")
    initialize.copy_file_to_remote("controller", extender1_ip, extender1_user, "/nvram/monitoring_tool.py", "/nvram/")
    initialize.copy_file_to_remote("controller", extender1_ip, extender1_user, "/etc/systemd/system/monitor_service.service", "/etc/systemd/system/")
    zaero_obj = zaero.zaero()
    devices = zaero_obj.get_testbed_devices()
    yield devices

def test_stability_24hours(initialize, common_setup):
    print("common setup done")
    devices = common_setup
    initialize.start_monitoring_service("controller")
    initialize.start_monitoring_service("extender1")
    ctrl_timestamp = initialize.get_time_stamp("controller")
    ext1_timestamp = initialize.get_time_stamp("extender1")
    start_time = time.time()
    # Run the 24-hour stability check for the configured timeout duration.
    while (time.time() - start_time) < timeout:
        zi_logger.log(f"Checking core dump status...")
        if get_core_dump_status(initialize, "controller", ctrl_timestamp):
            zi_logger.print_error(f"Core dump found on controller after SSID update.")
            break;
        if get_core_dump_status(initialize, "extender1", ext1_timestamp):
            zi_logger.print_error(f"Core dump found on extender1 after SSID update.")
            break;

        #also check device is not "controller"
        for device in devices[:]:
            if device != "controller":
                # currently checking only wireless backhaul status wired has issues https://jira.rdkcentral.com/jira/browse/RDKBWIFI-580
                if not initialize.get_backhaul_status(device):
                    zi_logger.print_error(f"{device} is not connected to the backhaul.")
                    devices.remove(device)
                else:
                    zi_logger.print_success(f"{device} is connected to the backhaul.")
    initialize.stop_monitoring_service("controller")
    initialize.stop_monitoring_service("extender1")
    ctrl_local_dir = initialize.read_from_database("controller", "pcap_local_dir")
    ext1_local_dir = initialize.read_from_database("extender1", "pcap_local_dir")
    for log_file in log_paths:
        initialize.download_pcap("controller", log_file, ctrl_local_dir)
        initialize.delete_pcap("controller", log_file)
        if log_file != "/nvram/onewifi_em_ctrl_monitor.csv":
            initialize.download_pcap("extender1", log_file, ext1_local_dir)
            initialize.delete_pcap("extender1", log_file)
    log_analyzer(initialize)



def test_stability_ssid_update(initialize, common_setup):
    devices = common_setup
    initialize.start_monitoring_service("controller")
    initialize.start_monitoring_service("extender1")
    ssid_update_current_count = 0
    while ssid_update_current_count < ssid_update_max_count:
        ssid_update_current_count += 1
        ssid = initialize.get_random_ssid()
        zi_logger.print_step(f"count: {ssid_update_current_count} Updating SSID to {ssid}")
        initialize.set_ssid("controller", "mld_iface_index", ssid, 'gui')
        time.sleep(30)
        #check ssid update on indivdual devices
        for device in devices[:]:
            try:
                zi_logger.print_step(f"Checking SSID on {device}")
                initialize.check_ssid(device, "mld_iface_index", ssid, 'cli')
            except Exception as ERR:
                zi_logger.print_error(f"count :{ssid_update_current_count} check_ssid failed in {device}: {ERR}")
                devices.remove(device)
            else:
                zi_logger.print_success(f"SSID matched successfully in {device}")
        if not devices:
            break
    initialize.stop_monitoring_service("controller")
    initialize.stop_monitoring_service("extender1")
    ctrl_local_dir = initialize.read_from_database("controller", "pcap_local_dir")
    ext1_local_dir = initialize.read_from_database("extender1", "pcap_local_dir")
    for log_file in log_paths:
        initialize.download_pcap("controller", log_file, ctrl_local_dir)
        initialize.delete_pcap("controller", log_file)
        if log_file != "/nvram/onewifi_em_ctrl_monitor.csv":
            initialize.download_pcap("extender1", log_file, ext1_local_dir)
            initialize.delete_pcap("extender1", log_file)
    log_analyzer(initialize)


def test_stability_channel_update(initialize, common_setup):
    devices = common_setup
    channel_update_current_count = 0
    while channel_update_current_count < channel_update_max_count:
        operating_channel = initialize.get_operating_channel("controller")
        #  alter the channel preference like operating channel is other than 6 set it to 6 , if current operating channel is 6 set it to 1
        if operating_channel != 6:
            operating_channel_to_set = 6
            initialize.set_channel_preference("controller", uncheck_channel=operating_channel, check_channel=6, priority=14)
        else:
            initialize.set_channel_preference("controller", uncheck_channel=6, check_channel=1, priority=14)
            operating_channel_to_set = 1
        channel_update_current_count += 1
        time.sleep(30)
        for device in devices[:]:
            current_operating_channel = initialize.get_operating_channel(device)
            if current_operating_channel != operating_channel_to_set:
                zi_logger.print_error(f"count : {channel_update_current_count} Channel update failed in {device}: expected {operating_channel_to_set}, got {current_operating_channel}")
                devices.remove(device)
            else:
                zi_logger.print_success(f"count : {channel_update_current_count} Channel updated successfully in {device} to {current_operating_channel}")
        if not devices:
            break

def test_stability_fronthaul_toggle(initialize, common_setup):
    devices = common_setup
    print(devices)
    fronthaul_toggle_current_count = 0
    while fronthaul_toggle_current_count < fronthaul_toggle_max_count:
        current_mld_status = initialize.get_mld_status("controller", "cli")
        #toggle mld status
        set_mld_status = not current_mld_status
        initialize.toggle_network_profile("controller", "Home Network", enable=set_mld_status)
        fronthaul_toggle_current_count += 1
        time.sleep(30)
        for device in devices[:]:
            mld_status = initialize.get_mld_status(device, "cli")
            if mld_status != set_mld_status:
                zi_logger.print_error(f"count : {fronthaul_toggle_current_count} SSID toggle failed in {device}: expected {set_mld_status}, got {mld_status}")
                devices.remove(device)
            else:
                zi_logger.print_success(f"count : {fronthaul_toggle_current_count} SSID toggle succeeded in {device}")
        if not devices:
            break
