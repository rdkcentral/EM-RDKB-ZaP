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
import zaero
from zaero.utils.database import Database
import time
from pathlib import Path
from rdkbmeshzap.common_utils import report_logger

def test_discover_macs(initialize):
    """
    Discover 2G, 5G and 6G radio MACs for controller
    and all enabled extenders and store them in database.
    """
    report_logger.print_info("Discovering radio MACs for controller and extenders")
    try:
        # Controller
        devices = ["controller"]
        # Enabled extenders
        devices.extend(initialize.get_enabled_extenders())
        report_logger.print_info(f"Devices found for MAC discovery: {devices}")
        # Discover MACs for every device
        for device in devices:
            report_logger.print_info(f"Getting fronthaul BSSIDs for {device}")
            bssids = initialize.get_fronthaul_bssids(device,"cli")
            if len(bssids) < 3:
                raise RuntimeError(f"Expected 3 BSSIDs for {device}, but found {len(bssids)}: {bssids}")
            report_logger.print_info(f"{device} BSSIDs: {bssids}")
            # 2G
            initialize.db_obj.write_into_database(device,"2g_radio_mac",bssids[0])
            # 5G
            initialize.db_obj.write_into_database(device,"5g_radio_mac",bssids[1])
            # 6G
            initialize.db_obj.write_into_database(device,"6g_radio_mac",bssids[2])
            report_logger.print_success(f"{device} 2G MAC: {bssids[0]}")
            report_logger.print_success(f"{device} 5G MAC: {bssids[1]}")
            report_logger.print_success(f"{device} 6G MAC: {bssids[2]}")
    except Exception as e:
        report_logger.print_error(f"Failed to discover radio MACs: {e}")
        pytest.fail(f"Radio MAC discovery failed: {e}")


