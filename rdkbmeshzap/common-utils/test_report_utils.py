"""Minimal logging helpers used by pytest report generation."""

import logging
import re
from html import escape

_error_logs = []
_enable_log = True
_ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

def format_report_line(line):
    """Strip terminal markup and return a bold, HTML-safe report line."""
    plain_line = _ANSI_ESCAPE.sub("", line)
    plain_line = re.sub(r"</?span[^>]*>", "", plain_line, flags=re.IGNORECASE)
    if plain_line.lstrip().startswith(("Entering Test", "Exiting Test")):
        color, weight = "#0055aa", "bold"
    elif plain_line.lstrip().startswith(("Step", "STEP")):
        color, weight = "#8a5a00", "bold"
    elif "PASS:" in plain_line or plain_line.lstrip().startswith("Pass:"):
        color, weight = "green", "bold"
    elif "FAIL:" in plain_line or "ERROR" in plain_line:
        color, weight = "red", "bold"
    else:
        color, weight = "black", "normal"
    return (
        f'<span style="color:{color}; white-space:pre-wrap; '
        f'font-family:monospace; font-weight:{weight};">{escape(plain_line)}</span>'
    )

def format_result_status(report):
    """Return the styled pytest result label for a report object."""
    if report.failed:
        return '<span style="color:red; font-weight:bold;">FAIL</span>'
    if report.passed:
        return '<span style="color:green; font-weight:bold;">PASS</span>'
    if report.skipped:
        return '<span style="color:orange; font-weight:bold;">SKIPPED</span>'
    return '<span>UNKNOWN</span>'

def set_log_state(status):
    """Enable or disable report logging."""
    global _enable_log
    _enable_log = status

def log(message, status="INFO", log_error=False):
    """Send diagnostic messages to logging without adding report stdout."""
    if not _enable_log:
        return
    if status == "INFO":
        logging.getLogger(__name__).info(message)
    else:
        logging.getLogger(__name__).error(message)
        if log_error:
            _error_logs.append(message)

def print_step(message):
    """Print and return a formatted test step."""
    print(f"\033[1m\033[94m{message}\033[0m")
    return f'<span style="color:#0055aa; font-weight:bold;">{message}</span>'

def print_step_with_number(step, message):
    """Print and return a numbered test step."""
    return print_step(f"STEP {step}: {message}")

def print_test(message):
    """Print and return a formatted test name."""
    print(f"\033[1m\033[33m{message}\033[0m")
    return f'<span style="color:#8a5a00; font-weight:bold;">{message}</span>'

def print_success(message):
    """Print and return a formatted passing message."""
    print(f"\033[92m{message}\033[0m")
    return f'<span style="color:green; font-weight:bold;">{message}</span>'

def print_error(message, log_error=True):
    """Print and optionally store a failing report message."""
    print(f"\033[91m{message}\033[0m")
    if log_error:
        _error_logs.append(message)
    return f'<span style="color:red; font-weight:bold;">{message}</span>'

def get_error_logs():
    """Return failure messages collected for the current test."""
    return list(_error_logs)

def clear_error_logs():
    """Clear failure messages before the next test."""
    _error_logs.clear()
