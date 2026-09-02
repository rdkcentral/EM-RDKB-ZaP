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

common_protocol_validation = True

@pytest.fixture
def protocol_validation(request):
    print(f"{' START ':#^80}")
    print (f"START packet capture : {request.node.name}.pcap")
        
    yield True
    
    print ("\nSTOP packet capture...")
    print (f"DOWNLOAD captured pcap : {request.node.name}.pcap")
    
    if common_protocol_validation:
        print ("Executing COMMON PROTOCOL analysis")

    if hasattr(request.node, 'protocol_specific_function'):
        try:
            request.node.protocol_specific_function(f"{request.node.name}.pcap")
        except Exception as ERR:
            raise RuntimeError(f"{ERR}")
    print(f"\n{' END ':#^80}")
