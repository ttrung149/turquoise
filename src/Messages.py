#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Messages.py
#
#  Description: Implementation of Error class, Warning class, Info class
#
# -----------------------------------------------------------------------------
from colored import fg, attr


class Error:
    """
    Error constructor that contains the line number, filename, and a specific
    error message
    """
    def __init__(self, line_number, filename, error_message=None):
        self._line_number = line_number
        self._filename = filename
        self._message = "ERR: " + str(line_number) + " @ " + filename
        if error_message is not None:
            self._message += ": " + error_message

    def __repr__(self):
        color = fg('light_red')
        reset = attr('reset')
        return (color + str(self._message) + reset)


class Warning:
    """
    Warning constructor that contains the line number, filename, and a specific
    warning message
    """
    def __init__(self, line_number, filename, warning_message=None):
        self._line_number = line_number
        self._filename = filename
        self._message = "WARNING: " + str(line_number) + " @ " + filename
        if warning_message is not None:
            self._message += ": " + warning_message

    def __repr__(self):
        color = fg('light_yellow')
        reset = attr('reset')
        return (color + str(self._message) + reset)

class Info:
    """
    Info constructor that contains the line number, filename, and a specific
    Info message
    """
    def __init__(self, info_message):
        self._message = "INFO: " + info_message

    def __repr__(self):
        color = fg('light_blue')
        reset = attr('reset')
        return (color + str(self._message) + reset)

def pp(_status, _message):
    """
    Pretty print. Status accepted: success, warning, error, info
    """
    reset = attr('reset')
    if _status == 'success':
        print(fg('light_green') + 'SUCCESS: ' + str(_message) + str(reset) + '\n')
    elif _status == 'warning':
        print(fg('light_yellow') + 'WARNING: ' + str(_message) + str(reset) + '\n')
    elif _status == 'error':
        print(fg('light_red') + 'ERR: ' + str(_message) + str(reset) + '\n')
    elif _status == 'info':
        print('INFO: ' + str(_message) + '\n')
    else:
        print('\n')
