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

from zaero.utils import zi_logger

def common_protocol_validation(pcap_file):
    zi_logger.log(f"Executing COMMON PROTOCOL validation : {pcap_file}")
 
def analyse_ssid_packets(pcap_file):
    zi_logger.log(f"Executing PROTOCOL SPECIFIC validation - analyse_ssid : {pcap_file}")
