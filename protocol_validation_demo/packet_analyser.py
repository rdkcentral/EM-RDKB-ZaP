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

def common_protocol_validation(pcap_file):
    print(f"Executing COMMON PROTOCOL validation  : {pcap_file}")

def analyse_onboarding(pcap_file):
    print(f"Executing PROTOCOL SPECIFIC validation - analyse_onboarding : {pcap_file}")

def analyse_propogation(pcap_file):
    print(f"Executing PROTOCOL SPECIFIC validation - analyse_propogation : {pcap_file}")

def analyse_failover(pcap_file):
    print(f"Executing PROTOCOL SPECIFIC validation - analyse_failover : {pcap_file}")
