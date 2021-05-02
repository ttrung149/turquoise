#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Entity.py
#
#  Description: Implementation of DFAs that parse through entity syntax
#
# -----------------------------------------------------------------------------
from State import DFA, State
from Tokenize import Tokenize
from State import DFA, State
from Prims import STD_LOGIC, STD_LOGIC_VECTOR, BIT, \
                       parse_std_logic_vector
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken
from pyVHDLParser.Base import ParserException
from Error import Error, Warning
from Logger import Logger

# TODO: delete sys
import sys
from enum import Enum
from collections import OrderedDict

logger = Logger()
filename = sys.argv[1]
tokenize = Tokenize(filename)
token_iter = tokenize.get_token_iter()


class EntityStateEnum(Enum):
    START = State(0)
    ENTITY = State(1)
    NAME = State(2)
    IS = State(3)

    # Generic states
    GENERIC = State(4)
    GENERIC_OPEN_BRACK = State(5)
    GENERIC_NAME = State(6)
    GENERIC_COLON = State(7)
    GENERIC_TYPE = State(8)
    GENERIC_ASSIGNMENT = State(9)
    GENERIC_VALUE = State(10)
    GENERIC_SEMICOLON = State(11)
    GENERIC_CLOSE_BRACK = State(12)
    GENERIC_END_SEMICOLON = State(13)

    # Port states
    PORT = State(14)
    PORT_OPEN_BRACK = State(15)
    SIGNAL = State(16)
    SIGNAL_DONE = State(17)
    NEXT_SIGNAL = State(18)
    SIGNAL_IN_OUT = State(19)
    SIGNAL_TYPE = State(20)
    PORT_CLOSE_BRACK = State(21)
    PORT_SEMICOLON = State(22)
    END = State(23)
    END_NAME = State(24)
    SUCCESS = State(25)


def parse_entity(_token_iter, _logger, _filename):
    """
    @brief Helper function. Parse entity object
    @param _token_iter Token Iteration
    @param _logger Logger instance
    @param _filename Current file name that is being linted
    @return Tuple of parsed generic (if any), and parsed entity (in that order)
    """
    parsed_generic = OrderedDict()
    parsed_port = OrderedDict()

    # Ports state
    curr_sigs = []
    curr_sig_type = None
    curr_sig_in_out = ''
    curr_entity_name = ''

    # Generics state
    curr_generic_sig = ''
    curr_generic_sig_type = None

    # =========================================================================
    # DFA generic callbacks
    def _set_curr_generic_sig(name):
        nonlocal curr_generic_sig
        curr_generic_sig = name.Value.lower()

    def _set_generic_sig_type(name):
        nonlocal curr_generic_sig_type

        if name.Value.lower() == 'std_logic':
            curr_generic_sig_type = STD_LOGIC()
        elif name.Value.lower() == 'bit':
            curr_generic_sig_type = BIT()
        elif name.Value.lower() == 'std_logic_vector':
            curr_generic_sig_type = parse_std_logic_vector(_token_iter, _logger, _filename)

            # Invalid STD_LOGIC_VECTOR parsing
            if curr_generic_sig_type is None:
                err = Error(name.Start, _filename, 'Invalid syntax for STD_LOGIC_VECTOR')
                _logger.add_log(err)
        else:
            warn = Warning(name.Start, _filename,
                           'Type "' + name.Value.lower() + '" is not supported in generic linting')
            _logger.add_log(warn)

    def _add_to_parsed_generic(name):
        nonlocal parsed_generic, curr_generic_sig, curr_generic_sig_type

        if curr_generic_sig not in parsed_generic:
            parsed_generic[curr_generic_sig] = curr_generic_sig_type
        else:
            warn = Warning(name.Start, _filename,
                           'Generic signal "' + curr_generic_sig + '" in entity "' +
                           curr_entity_name + '" is already declared')
            _logger.add_log(warn)

        curr_generic_sig = ''
        curr_generic_sig_type = None

    # =========================================================================
    # DFA ports callbacks
    def _set_curr_entity_name(name):
        nonlocal curr_entity_name
        curr_entity_name = name.Value.lower()

    def _set_sig_type(name):
        nonlocal curr_sig_type

        if name.Value.lower() == 'std_logic':
            curr_sig_type = STD_LOGIC()
        elif name.Value.lower() == 'bit':
            curr_sig_type = BIT()
        elif name.Value.lower() == 'std_logic_vector':
            curr_sig_type = parse_std_logic_vector(_token_iter, _logger, _filename)

            # Invalid STD_LOGIC_VECTOR parsing
            if curr_sig_type is None:
                err = Error(name.Start, _filename, 'Invalid syntax for STD_LOGIC_VECTOR')
                _logger.add_log(err)

        else:
            warn = Warning(name.Start, _filename,
                           'Type "' + name.Value.lower() + '" is not supported in port linting')
            _logger.add_log(warn)

    def _set_sig_inout(name):
        nonlocal curr_sig_in_out
        curr_sig_in_out = name.Value.lower()

    def _append_sig(name):
        nonlocal curr_sigs
        curr_sigs.append(name.Value.lower())

    def _add_to_parsed_port(name):
        nonlocal parsed_port, curr_sigs, curr_sig_type, curr_sig_in_out

        for sig in curr_sigs:
            if sig not in parsed_port:
                parsed_port[sig] = (curr_sig_in_out, curr_sig_type)
            else:
                warn = Warning(name.Start, _filename,
                               'Signal "' + sig + '" in entity "' + curr_entity_name +
                               '" is already declared')
                _logger.add_log(warn)

        curr_sigs = []
        curr_sig_type = None
        curr_sig_in_out = ''

    def _check_entity_name(name):
        nonlocal curr_entity_name
        if name.Value.lower() != curr_entity_name:
            err = Error(name.Start, _filename,
                        'Expecting entity "' + curr_entity_name + '", got: ' +
                        '"' + name.Value.lower())
            _logger.add_log(err)

        curr_entity_name = ''

    # =========================================================================
    # Build parse_entity DFA
    # =========================================================================
    dfa = DFA('parse_entity', EntityStateEnum.START, [EntityStateEnum.SUCCESS])

    # Parse entity starting syntax
    dfa.add_transition(EntityStateEnum.START, EntityStateEnum.ENTITY, 'entity')
    dfa.add_transition(EntityStateEnum.ENTITY, EntityStateEnum.NAME, '_*_',
                       _set_curr_entity_name)
    dfa.add_transition(EntityStateEnum.NAME, EntityStateEnum.IS, 'is')

    # Parse generic syntax
    dfa.add_transition(EntityStateEnum.IS, EntityStateEnum.GENERIC, 'generic')
    dfa.add_transition(EntityStateEnum.GENERIC, EntityStateEnum.GENERIC_OPEN_BRACK, '(')
    dfa.add_transition(EntityStateEnum.GENERIC_OPEN_BRACK,
                       EntityStateEnum.GENERIC_NAME, '_*_', _set_curr_generic_sig)
    dfa.add_transition(EntityStateEnum.GENERIC_NAME, EntityStateEnum.GENERIC_COLON, ':')
    dfa.add_transition(EntityStateEnum.GENERIC_COLON,
                       EntityStateEnum.GENERIC_TYPE, '_*_', _set_generic_sig_type)

    dfa.add_transition(EntityStateEnum.GENERIC_TYPE, EntityStateEnum.GENERIC_ASSIGNMENT, ':=')
    dfa.add_transition(EntityStateEnum.GENERIC_ASSIGNMENT, EntityStateEnum.GENERIC_VALUE, '_*_')
    dfa.add_transition(EntityStateEnum.GENERIC_VALUE, EntityStateEnum.GENERIC_VALUE, '_*_')
    dfa.add_transition(EntityStateEnum.GENERIC_VALUE,
                       EntityStateEnum.GENERIC_OPEN_BRACK, ';', _add_to_parsed_generic)

    dfa.add_transition(EntityStateEnum.GENERIC_TYPE,
                       EntityStateEnum.GENERIC_OPEN_BRACK, ';', _add_to_parsed_generic)
    dfa.add_transition(EntityStateEnum.GENERIC_TYPE,
                       EntityStateEnum.GENERIC_CLOSE_BRACK, ')', _add_to_parsed_generic)

    dfa.add_transition(EntityStateEnum.GENERIC_VALUE,
                       EntityStateEnum.GENERIC_CLOSE_BRACK, ')', _add_to_parsed_generic)
    dfa.add_transition(EntityStateEnum.GENERIC_CLOSE_BRACK, EntityStateEnum.GENERIC_END_SEMICOLON, ';')

    dfa.add_transition(EntityStateEnum.GENERIC_END_SEMICOLON, EntityStateEnum.PORT, 'port')

    # Parse port syntax
    dfa.add_transition(EntityStateEnum.IS, EntityStateEnum.PORT, 'port')
    dfa.add_transition(EntityStateEnum.PORT, EntityStateEnum.PORT_OPEN_BRACK, '(')

    dfa.add_transition(EntityStateEnum.PORT_OPEN_BRACK,
                       EntityStateEnum.SIGNAL, '_*_', _append_sig)
    dfa.add_transition(EntityStateEnum.SIGNAL, EntityStateEnum.SIGNAL, ',')
    dfa.add_transition(EntityStateEnum.SIGNAL, EntityStateEnum.SIGNAL_DONE, ':')

    # Parse in out type
    dfa.add_transition(EntityStateEnum.SIGNAL_DONE,
                       EntityStateEnum.SIGNAL_IN_OUT, 'in', _set_sig_inout)
    dfa.add_transition(EntityStateEnum.SIGNAL_DONE,
                       EntityStateEnum.SIGNAL_IN_OUT, 'out', _set_sig_inout)
    dfa.add_transition(EntityStateEnum.SIGNAL_DONE,
                       EntityStateEnum.SIGNAL_IN_OUT, 'buffer', _set_sig_inout)
    dfa.add_transition(EntityStateEnum.SIGNAL_DONE,
                       EntityStateEnum.SIGNAL_IN_OUT, 'inout', _set_sig_inout)

    # Parse in signal type
    dfa.add_transition(EntityStateEnum.SIGNAL_IN_OUT,
                       EntityStateEnum.SIGNAL_TYPE, '_*_', _set_sig_type)
    dfa.add_transition(EntityStateEnum.SIGNAL_TYPE,
                       EntityStateEnum.PORT_OPEN_BRACK, ';', _add_to_parsed_port)
    dfa.add_transition(EntityStateEnum.SIGNAL_TYPE,
                       EntityStateEnum.PORT_CLOSE_BRACK, ')', _add_to_parsed_port)

    # Parse end entity
    dfa.add_transition(EntityStateEnum.PORT_CLOSE_BRACK, EntityStateEnum.PORT_SEMICOLON, ';')
    dfa.add_transition(EntityStateEnum.PORT_SEMICOLON, EntityStateEnum.END, 'end')
    dfa.add_transition(EntityStateEnum.IS, EntityStateEnum.END, 'end')
    dfa.add_transition(EntityStateEnum.END,
                       EntityStateEnum.END_NAME, '_*_', _check_entity_name)
    dfa.add_transition(EntityStateEnum.END_NAME, EntityStateEnum.SUCCESS, ';')

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

    # Add specific warnings and errors to logger
    if not dfa.is_finished_successfully:
        if dfa.get_curr_state == EntityStateEnum.IS:
            err = Error(curr_token.Start, _filename,
                        'Expecting "port" or "generic", ' +
                        'got "' + curr_token.Value.lower())
            _logger.add_log(err)
        elif dfa.get_curr_state == EntityStateEnum.SIGNAL_DONE:
            err = Error(curr_token.Start, _filename,
                        'Expecting "in", "out", "buffer", "inout" for signal type, ' +
                        'got "' + curr_token.Value.lower())
            _logger.add_log(err)

        return None

    return (parsed_generic, parsed_port)


a = parse_entity(token_iter, logger, 'a.txt')
print(a)

logger.print_logs_to_terminal()