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
import pytest
import time
from zaero.utils import zi_logger
def test_wifi_reset(initialize: zaero.zaero):
    ssid = initialize.get_random_ssid()
    initialize.set_ssid("controller", "mld_iface_index", ssid, 'gui')
    for i in range(1, 31):
        try:            
            initialize.check_ssid("controller", "mld_iface_index", ssid, 'cli')
            initialize.check_ssid("extender1", "mld_iface_index", ssid, 'cli')
        except Exception as err:
            zi_logger.print_error(f"Retry after : {err}", log_error=False)
        else:
            zi_logger.print_success(f"SSID matched {ssid} on controller and extenders")
            break
        time.sleep(5)
    else:
        pytest.fail("SSID is not changed in DUT by checking with iw command")
    time.sleep(10)
    initialize.wifi_reset("controller", 'gui')
    time.sleep(10)
    initialize.reboot_device("extender1", "cli")
    initialize.reboot_device("controller", "cli")
    initialize.close_connection("controller")
    initialize.close_connection("extender1")
    time.sleep(10)
    for i in range(1, 41):
        zi_logger.log(f"FOR loop iteration : {i}")
        try:
            initialize.connect_with_device("controller")
        except Exception:
            zi_logger.print_error("Connection FAILED with 'Controller'", log_error=False)
        else: 
            zi_logger.print_success("Connection SUCCESS with 'Controller'")
            break
        time.sleep(10)
    else:
        pytest.fail("Could not re-establish connection with Controller")
    ssid = initialize.read_from_database("controller", "default_ssid")
    for i in range(1, 31):
        try:            
            initialize.check_ssid("controller", "mld_iface_index", ssid, 'cli')
        except Exception as err:
            zi_logger.print_error(f"Retry after : {err}", log_error=False)
        else:
            zi_logger.print_success("Both SSIDs are matched")
            break
        time.sleep(5)
    else:
        pytest.fail("SSID is not changed in DUT by checking with iw command")
    for i in range(1, 41):
        zi_logger.log(f"FOR loop iteration : {i}")
        try:
            initialize.connect_with_device("extender1")
        except Exception:
            zi_logger.print_error("Connection FAILED with 'Extender1'", log_error=False)
        else:
            zi_logger.print_success("Connection SUCCESS with 'Extender1'")
            break
        time.sleep(10)
    else:
        pytest.fail("Could not re-establish connection with - extender1")
    ssid = initialize.read_from_database("controller", "default_ssid")
    for i in range(1, 31):
        try:
            initialize.check_ssid("extender1", "mld_iface_index", ssid, 'cli')
        except Exception as err:
            zi_logger.print_error(f"Retry after : {err}", log_error=False)
        else:
            zi_logger.print_success("Both SSIDs are matched")
            break
        time.sleep(5)
    else:
        pytest.fail("SSID is not changed in DUT by checking with iw command")
    time.sleep(10)
