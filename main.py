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

# If not stated otherwise in this file or this component LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2026 RDK Management
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

import datetime
from pathlib import Path
import os
import subprocess
import sys

def run_tests(base_dir, test_files, cli_args=None):
    cli_args = list(cli_args or [])
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_path = base_dir / "Reports" / f"TestRun_{timestamp}"
    os.environ["TEST_RUN_DIR"] = str(base_dir / "Reports")
    reports_path.mkdir(parents=True, exist_ok=True)
    pytest_command = [
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--capture=tee-sys",
        "--show-capture=no",
        f"--html={reports_path}/report.html",
        "--self-contained-html",
        "--log-cli-level=INFO",
        *cli_args,
        *(str(path) for path in test_files),
    ]
    return subprocess.run(pytest_command, cwd=base_dir).returncode

