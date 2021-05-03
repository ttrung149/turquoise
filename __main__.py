#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: __main__.py
#
#  Description: Main driver for the turquoise VDHL linter + compilation
#  toolchain. Refer to README.md for specific usage.
#
# -----------------------------------------------------------------------------
from src.ArgParser import App
from src.Logger import Logger

if __name__ == '__main__':
    _logger = Logger()
    App(_logger)