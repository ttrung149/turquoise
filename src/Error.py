#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Error.py
#
#  Description: Implementation of Error class and Warning class
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
        return (color + self._message + reset)


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
        return (color + self._message + reset)
