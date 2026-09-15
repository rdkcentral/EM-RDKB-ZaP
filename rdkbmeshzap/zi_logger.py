"""EM-specific logging presentation built on top of Zaero logging."""

from zaero.utils.zi_logger import *

_error_logs = []


def print_step(message):
    print(f"\033[1m\033[94m{message}\033[0m")
    return f'<span style="color:#0055aa; font-weight:bold;">{message}</span>'


def print_test(message):
    print(f"\033[1m\033[33m{message}\033[0m")
    return f'<span style="color:#8a5a00; font-weight:bold;">{message}</span>'


def print_error(message, log_error=True):
    print(f"\033[91m{message}\033[0m")
    if log_error:
        _error_logs.append(message)
    return f'<span style="color:red; font-weight:bold;">{message}</span>'


def get_error_logs():
    return list(_error_logs)


def clear_error_logs():
    _error_logs.clear()
