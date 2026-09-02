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
import packet_analyser

def test_onboarding(protocol_validation, request):
    print("\nTest onboarding step - 1")
    print("Test onboarding step - 2")
    print("Test onboarding step - 3")
    print("Test onboarding step - 4")
    print("Test onboarding step - 5")
    print("Test onboarding step - N")    
    request.node.protocol_specific_function = packet_analyser.analyse_onboarding

def test_propogation(protocol_validation, request):
    print("\nTest propogation step - 1")
    print("Test propogation step - 2")
    print("Test propogation step - N")    
    request.node.protocol_specific_function = packet_analyser.analyse_propogation

def test_failover(protocol_validation):
    print("\nTest Failover step - 1")
    print("Test Failover step - 2")
    print("Test Failover step - 3")
    print("Test Failover step - N")

def test_failover(protocol_validation, request):
    request.node.protocol_specific_function = packet_analyser.analyse_propogation
