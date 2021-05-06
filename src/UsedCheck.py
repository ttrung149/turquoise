#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: UsedCheck.py
#
#  Description: Implementation of functions to check if signals are used or
#  declared, etc.
#
# -----------------------------------------------------------------------------
from .Messages import Error, Warning

def check_signal_declared_not_used(_declared, _body, _filename, _logger):
    used_sigs = set()

    for token in _body:
        if token.Value.lower() in _declared:
            used_sigs.add(token.Value.lower())

    for sig in _declared:
        if sig not in used_sigs:
            warn = Warning('', _filename, 'Signal "' + sig + '" is declared but never used')
            _logger.add_log(warn)


def check_signal_assigned_not_declared(_declared, _assigned, _filename, _logger):
    for sig in _assigned:
        if sig.Value.lower() not in _declared:
            err = Error(sig.Start, _filename, 'Signal "' + sig.Value.lower() + 
                        '" is assigned but not declared' )
            _logger.add_log(err)