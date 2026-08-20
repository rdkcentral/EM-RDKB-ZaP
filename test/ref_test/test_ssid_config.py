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
from zaero.utils import zi_logger

def test_config_ssid(initialize):
    ssid = initialize.get_random_ssid()
    initialize.set_ssid("controller", "mld_iface_index", ssid, 'gui')
    for i in range(1, 31):
        try:
            curr_ssid = initialize.get_ssid("controller", "2g_ssid_index", 'de')
            if curr_ssid != ssid:
                raise Exception(f"Both SSIDs are not matched {ssid} : {curr_ssid}")
            initialize.check_ssid("controller", "mld_iface_index", ssid, 'cli')
        except Exception as ERR:
            zi_logger.print_step(f"{ERR}")
        else:
            zi_logger.print_success("SSID matched successfully")
            break
        time.sleep(5)
    else:
        pytest.fail("SSID is not changed in DUT by checking with iw command")
    time.sleep(5)
