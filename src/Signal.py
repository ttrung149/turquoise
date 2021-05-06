#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Signal.py
#
#  Description: Implementation of DFAs that parse signal and constant syntax
#
# -----------------------------------------------------------------------------
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken
from pyVHDLParser.Base import ParserException
from enum import Enum
from collections import defaultdict

from .State import DFA, State
from .Prims import STD_LOGIC, STD_LOGIC_VECTOR, BIT, SIGNED, UNSIGNED, \
                   INTEGER, BOOLEAN, TIME, STRING, \
                   parse_to_downto
from .Messages import Error, Warning, Info


class SignalStateEnum(Enum):
    START = State(0)
    NAME = State(1)
    COLON = State(2)
    SIGNAL_TYPE = State(3)
    SEMICOLON = State(4)
    SUCCESS = State(5)
    ASSIGNMENT_SYMBOL = State(6)
    SIGNAL_VALUE = State(7)


def parse_signal(_token_iter, _logger, _filename):
    """
    @brief Helper function. Parse signal syntax
    @param _token_iter Token Iteration
    @param _logger Logger instance
    @param _filename Current file name that is being linted
    @return Dictionary of signal name and type
    """
    parsed_sigs = {}
    signal_type = None
    signal_names = []

    # DFA callbacks
    def _set_signal_name(name):
        nonlocal signal_names
        signal_names.append(name.Value.lower())

    def _set_signal_type(name):
        nonlocal signal_type

        if name.Value.lower() == 'std_logic':
            signal_type = STD_LOGIC()
        elif name.Value.lower() == 'bit':
            signal_type = BIT()
        elif name.Value.lower() == 'integer':
            signal_type = INTEGER()
        elif name.Value.lower() == 'boolean':
            signal_type = BOOLEAN()
        elif name.Value.lower() == 'time':
            signal_type = TIME()
        elif name.Value.lower() == 'string':
            signal_type = STRING()
        elif name.Value.lower() == 'std_logic_vector':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid STD_LOGIC_VECTOR parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for STD_LOGIC_VECTOR')
                _logger.add_log(err)

                info = Info('hint - STD_LOGIC_VECTOR(3 downto 0) or STD_LOGIC_VECTOR(0 to 3)')
                _logger.add_log(info)
            else:
                signal_type = STD_LOGIC_VECTOR(first, second)

        elif name.Value.lower() == 'signed':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid SIGNED parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for SIGNED')
                _logger.add_log(err)

                info = Info('hint - SIGNED(3 downto 0) or SIGNED(0 to 3)')
                _logger.add_log(info)
            else:
                signal_type = SIGNED(first, second)

        elif name.Value.lower() == 'unsigned':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid UNSIGNED parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for UNSIGNED')
                _logger.add_log(err)

                info = Info('hint - UNSIGNED(3 downto 0) or UNSIGNED(0 to 3)')
                _logger.add_log(info)
            else:
                signal_type = UNSIGNED(first, second)

        else:
            warn = Warning(name.Start, _filename,
                           'Type "' + name.Value.lower() + '" is not supported in signal linting')
            _logger.add_log(warn)

    def _add_to_parsed_sigs(name):
        nonlocal parsed_sigs, signal_type, signal_names

        for sig in signal_names:
            if sig not in parsed_sigs:
                parsed_sigs[sig] = signal_type
            else:
                warn = Warning(name.Start, _filename,
                               'Signal "' + sig + '" in architecture has already been declared')
                _logger.add_log(warn)

        signal_names = []
        curr_generic_sig_type = None

    # =========================================================================
    # Build parse_signal DFA
    # =========================================================================
    dfa = DFA('parse_signal', SignalStateEnum.START, [SignalStateEnum.SUCCESS])

    # Parse entity and port syntax
    dfa.add_transition(SignalStateEnum.START, SignalStateEnum.NAME, 'signal')
    dfa.add_transition(SignalStateEnum.START, SignalStateEnum.NAME, 'constant')
    dfa.add_transition(SignalStateEnum.NAME, SignalStateEnum.COLON, '_*_',
                       _set_signal_name)
    dfa.add_transition(SignalStateEnum.COLON, SignalStateEnum.NAME, ',')
    dfa.add_transition(SignalStateEnum.COLON, SignalStateEnum.SIGNAL_TYPE, ':')

    dfa.add_transition(SignalStateEnum.SIGNAL_TYPE,
                       SignalStateEnum.SEMICOLON, '_*_', _set_signal_type)
    dfa.add_transition(SignalStateEnum.SEMICOLON, SignalStateEnum.SUCCESS, ';',
                       _add_to_parsed_sigs)

    dfa.add_transition(SignalStateEnum.SEMICOLON, SignalStateEnum.ASSIGNMENT_SYMBOL, ':=')
    dfa.add_transition(SignalStateEnum.ASSIGNMENT_SYMBOL,
                       SignalStateEnum.SIGNAL_VALUE, '_*_')
    dfa.add_transition(SignalStateEnum.SIGNAL_VALUE,
                       SignalStateEnum.SIGNAL_VALUE, '_*_')
    dfa.add_transition(SignalStateEnum.SIGNAL_VALUE, SignalStateEnum.SUCCESS, ';',
                       _add_to_parsed_sigs)

    # =========================================================================
    # Token stream iteration
    # =========================================================================
    curr_token = None
    while not dfa.is_finished:
        try:
            token = next(_token_iter)
            curr_token = token
            if isinstance(token, (StartOfDocumentToken, EndOfDocumentToken,
                                  LinebreakToken, SpaceToken,
                                  IndentationToken, CommentToken)):
                pass
            else:
                dfa.step(token)

        except ParserException as ex:
            err = Error(token.Start, _filename, str(ex))
            _logger.add_log(err)
            break

        except StopIteration:
            break

    # Add specific warnings and errors to logger
    if not dfa.is_finished_successfully:
        if dfa.get_curr_state == SignalStateEnum.SEMICOLON:
            err = Error(curr_token.Start, _filename,
                        'Expecting ";" or assignment operator ":=", ' +
                        'got "' + curr_token.Value.lower() + '"')
            _logger.add_log(err)

        else:
            err = Error(curr_token.Start, _filename,
                        'Invalid declaration around token "' +
                        curr_token.Value.lower() + '"')
            _logger.add_log(err)

        return None

    return parsed_sigs