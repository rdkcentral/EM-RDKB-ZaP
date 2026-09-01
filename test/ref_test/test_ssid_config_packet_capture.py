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
import pytest
import time
import os
from zaero.utils import zi_logger
def test_config_ssid_with_packet_capture(initialize):
    ssid = initialize.get_random_ssid()
    pcap_file_name = "sample_6"
    pcap_remote_dir = initialize.read_from_database("controller", "pcap_remote_dir")
    pcap_local_dir = initialize.read_from_database("controller", "pcap_local_dir")
    backhaul_iface = initialize.read_from_database("controller", "backhaul_capture_iface")
    frame_filter = initialize.read_from_database("controller", "filter_1905")
    initialize.set_sniffer_log_file("controller", pcap_file_name)
    zi_logger.log(f"Starting packet capture on controller for interface {backhaul_iface} with filter {frame_filter}")
    initialize.start_frame_capture("controller", backhaul_iface, frame_filter)
    initialize.set_ssid("controller", "mld_iface_index", ssid, 'gui')
    for i in range(1, 31):
        try:
            initialize.check_ssid("controller", "mld_iface_index", ssid, 'cli')
        except Exception as ERR:
            zi_logger.print_step(f"{ERR}")
        else:
            zi_logger.print_success(f"SSID matched {ssid} on controller")
            break
        time.sleep(5)
    else:
        pytest.fail("SSID is not changed in DUT by checking with iw command")
    initialize.stop_frame_capture("controller")
    pcap_remote_dir = os.path.join(pcap_remote_dir, pcap_file_name + '.pcapng')
    initialize.download_pcap("controller", pcap_remote_dir, pcap_local_dir)
    initialize.delete_pcap("controller", f"{pcap_file_name}.pcapng")
    time.sleep(10)
