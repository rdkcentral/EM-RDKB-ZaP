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

import logging
import re
from html import escape

_error_logs = []
_enable_log = True
_ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

_WHITE_REPORT_STYLE = (
    "<style>"
    ".logwrapper, .logwrapper .log, "
    ".logwrapper .logexpander { background-color: #fff !important; }"
    ".setup-accessibility { margin-bottom: 10px; }"
    ".setup-accessibility summary { cursor: pointer; font-weight: bold; "
    "color: #0055aa; padding: 4px 0; }"
    "</style>"
)

def format_report_line(line):
    """
    Syntax: format_report_line(line)
    Description: Strip terminal markup and return a styled HTML-safe report line.
    Parameters: line - Report text to format.
    Return Value: HTML span containing the formatted report line.
    Example: format_report_line("PASS: Capture completed")
    """
    plain_line = _ANSI_ESCAPE.sub("", line)
    plain_line = re.sub(r"</?span[^>]*>", "", plain_line, flags=re.IGNORECASE)
    if plain_line.lstrip().lower().startswith(("entering test", "exiting test")):
        color, weight = "#0055aa", "bold"
    elif plain_line.lstrip().startswith("INFO:"):
        color, weight = "#007a8a", "bold"
    elif plain_line.lstrip().startswith(("Step", "STEP")):
        color, weight = "#8a5a00", "bold"
    elif "PASS:" in plain_line or plain_line.lstrip().startswith("Pass:"):
        color, weight = "green", "bold"
    elif (
        "FAIL:" in plain_line
        or "ERROR" in plain_line
        or any(error in plain_line for error in _error_logs)
    ):
        color, weight = "red", "bold"
    else:
        color, weight = "black", "normal"
    return (
        f'<span style="color:{color}; white-space:pre-wrap; '
        f'font-family:monospace; font-weight:{weight};">{escape(plain_line)}</span>'
    )

def get_report_style():
    """
    Syntax: get_report_style()
    Description: Return custom CSS for the pytest HTML report.
    Parameters: None.
    Return Value: A CSS style string.
    Example: get_report_style()
    """
    return _WHITE_REPORT_STYLE

def set_log_state(status):
    """
    Syntax: set_log_state(status)
    Description: Enable or disable diagnostic logging.
    Parameters: status - Boolean logging state.
    Return Value: None.
    Example: set_log_state(True)
    """
    global _enable_log
    _enable_log = status

def log(message, status="INFO", log_error=False):
    """
    Syntax: log(message, status="INFO", log_error=False)
    Description: Send diagnostic messages to logging without adding report stdout.
    Parameters: message - Diagnostic text; status - Log severity; log_error - Store as an error.
    Return Value: None.
    Example: log("Capture started")
    """
    if not _enable_log:
        return
    if status == "INFO":
        logging.getLogger(__name__).info(message)
    else:
        logging.getLogger(__name__).error(message)
        if log_error:
            _error_logs.append(message)

def print_step(message):
    """
    Syntax: print_step(message)
    Description: Print a formatted test step.
    Parameters: message - Step text.
    Return Value: Styled HTML for the step.
    Example: print_step("STEP 1: Start capture")
    """
    print(f"\033[1m\033[94m{message}\033[0m")
    return f'<span style="color:#0055aa; font-weight:bold;">{message}</span>'

def print_info(message):
    """
    Syntax: print_info(message)
    Description: Print a bold informational report message.
    Parameters: message - Informational text.
    Return Value: Styled HTML for the message.
    Example: print_info("INFO: Capture started")
    """
    print(f"\033[1m\033[96m{message}\033[0m")
    return f'<span style="color:#007a8a; font-weight:bold;">{message}</span>'

def print_test(message):
    """
    Syntax: print_test(message)
    Description: Print a formatted test name.
    Parameters: message - Test name.
    Return Value: Styled HTML for the test name.
    Example: print_test("Controller Recovery")
    """
    print(f"\033[1m\033[33m{message}\033[0m")
    return f'<span style="color:#8a5a00; font-weight:bold;">{message}</span>'

def print_success(message):
    """
    Syntax: print_success(message)
    Description: Print a formatted passing message.
    Parameters: message - Passing message.
    Return Value: Styled HTML for the passing message.
    Example: print_success("PASS: Capture completed")
    """
    print(f"\033[92m{message}\033[0m")
    return f'<span style="color:green; font-weight:bold;">{message}</span>'

def print_error(message, log_error=True):
    """
    Syntax: print_error(message, log_error=True)
    Description: Print and optionally store a failing report message.
    Parameters: message - Failure message; log_error - Store the message for test reporting.
    Return Value: Styled HTML for the failure message.
    Example: print_error("FAIL: Capture was empty")
    """
    formatted_message = (
        message if message.lstrip().startswith("FAIL:") else f"FAIL: {message}"
    )
    print(f"\033[91m{formatted_message}\033[0m")
    if log_error:
        _error_logs.append(formatted_message)
    return f'<span style="color:red; font-weight:bold;">{formatted_message}</span>'

def get_error_logs():
    """
    Syntax: get_error_logs()
    Description: Return failure messages collected for the current test.
    Parameters: None.
    Return Value: A list of failure messages.
    Example: get_error_logs()
    """
    return list(_error_logs)

def clear_error_logs():
    """
    Syntax: clear_error_logs()
    Description: Clear failure messages before the next test.
    Parameters: None.
    Return Value: None.
    Example: clear_error_logs()
    """
    _error_logs.clear()
