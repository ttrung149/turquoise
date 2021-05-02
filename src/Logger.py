#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Logger.py
#
#  Description: Implementation of Logger class
#
# -----------------------------------------------------------------------------
import sys
import datetime


class Logger:
    """ Represent the error logging class """

    def __init__(self, init_logs=[], filename="turquoise.log"):
        self._logs = init_logs
        self._filename = filename

    def get_logs(self):
        return self._logs

    def add_log(self, log):
        curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._logs.append((curr_time, log))

    def print_logs_to_file(self):
        orig_stdout = sys.stdout

        with open(self._filename, 'w') as f:
            sys.stdout = f
            for (time, log) in self._logs:
                print('{}: {}'.format(time, log._message))
            sys.stdout = orig_stdout

    def print_logs_to_terminal(self):
        for (time, log) in self._logs:
            print('{}: {}'.format(time, log))
