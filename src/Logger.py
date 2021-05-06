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
from .Messages import Error, Warning, pp


class Logger:
    """ Represent the error logging class """

    def __init__(self, init_logs=[], filename=".turquoise.log"):
        self._logs = init_logs
        self._filename = filename

    @property
    def logs(self):
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

            self.print_status()
            sys.stdout = orig_stdout

    def print_logs_to_terminal(self):
        for (time, log) in self._logs:
            print('{}: {}\n'.format(time, log))

    def print_status(self):
        num_err = 0
        num_warn = 0
        for (_, log) in self._logs:
            if isinstance(log, Error):
                num_err += 1
            elif isinstance(log, Warning):
                num_warn += 1

        print('-----------------------------------------------------')
        pp('info', 
           'LINT STATUS: {} error(s), {} warning(s) found.'.format(num_err, num_warn))