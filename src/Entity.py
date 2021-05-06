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
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken
from pyVHDLParser.Base import ParserException
from enum import Enum
from collections import OrderedDict

from .State import DFA, State
from .Tokenize import Tokenize
from .Prims import STD_LOGIC, STD_LOGIC_VECTOR, BIT, SIGNED, UNSIGNED, \
                   INTEGER, BOOLEAN, TIME, STRING, \
                   parse_to_downto
from .Messages import Error, Warning, Info


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


class EntityComponent:
    def __init__(self, _is_component, _name, _generics, _ports):
        self._name = _name
        self._is_component = _is_component
        self._generics = _generics
        self._ports = _ports

    @property
    def name(self):
        return self._name

    @property
    def is_component(self):
        return self._is_component

    @property
    def generics(self):
        return self._generics

    @property
    def ports(self):
        return self._ports

    def __str__(self):
        if self._is_component:
            return 'COMPONENT {}'.format(self._name)
        else:
            return 'ENTITY {}'.format(self._name)

    def __repr__(self):
        if self._is_component:
            return 'COMPONENT {}'.format(self._name)
        else:
            return 'ENTITY {}'.format(self._name)


class EntityPortSignalTypeToken:
    def __init__(self, _inout, _type, _line):
        self._inout = _inout
        self._type = _type
        self._line = _line

    def __eq__(self, other):
        if not isinstance(other, EntityPortSignalTypeToken):
            return False
        return self._inout == other._inout and self._type == other._type

    @property
    def line(self):
        return self._line

    def __str__(self):
        return '({}) {}'.format(self._inout, self._type)

    def __repr__(self):
        return '({}) {}'.format(self._inout, self._type)


class EntityGenericSignalTypeToken:
    def __init__(self, _type, _line):
        self._type = _type
        self._line = _line

    def __eq__(self, other):
        if not isinstance(other, EntityGenericSignalTypeToken):
            return False
        return self._type == other._type

    @property
    def line(self):
        return self._line

    def __str__(self):
        return '{}'.format(self._type)

    def __repr__(self):
        return '{}'.format(self._type)


def parse_entity_component(_token_iter, _logger, _filename):
    """
    @brief Helper function. Parse entity/component object
    @param _token_iter Token Iteration
    @param _logger Logger instance
    @param _filename Current file name that is being linted
    @return EntityComponent
    """
    parsed_generic = OrderedDict()
    parsed_port = OrderedDict()

    # Ports state
    is_component = False
    curr_sigs = []
    curr_sig_type = None
    curr_sig_in_out = ''
    curr_entity_name = ''

    # Generics state
    curr_generic_sigs = []
    curr_generic_sig_type = None

    def _set_is_component(name):
        nonlocal is_component
        is_component = (name.Value.lower() == 'component')

    # =========================================================================
    # DFA generic callbacks
    def _set_curr_generic_sig(name):
        nonlocal curr_generic_sigs
        curr_generic_sigs.append(name.Value.lower())

    def _set_generic_sig_type(name):
        nonlocal curr_generic_sig_type

        if name.Value.lower() == 'std_logic':
            curr_generic_sig_type = STD_LOGIC()
        elif name.Value.lower() == 'bit':
            curr_generic_sig_type = BIT()
        elif name.Value.lower() == 'integer':
            curr_generic_sig_type = INTEGER()
        elif name.Value.lower() == 'boolean':
            curr_generic_sig_type = BOOLEAN()
        elif name.Value.lower() == 'time':
            curr_generic_sig_type = TIME()
        elif name.Value.lower() == 'string':
            curr_generic_sig_type = STRING()
        elif name.Value.lower() == 'std_logic_vector':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid STD_LOGIC_VECTOR parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for STD_LOGIC_VECTOR')
                _logger.add_log(err)

                info = Info('hint - STD_LOGIC_VECTOR(3 downto 0) or STD_LOGIC_VECTOR(0 to 3)')
                _logger.add_log(info)
            else:
                curr_generic_sig_type = STD_LOGIC_VECTOR(first, second)

        elif name.Value.lower() == 'signed':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid SIGNED parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for SIGNED')
                _logger.add_log(err)

                info = Info('hint - SIGNED(3 downto 0) or SIGNED(0 to 3)')
                _logger.add_log(info)
            else:
                curr_generic_sig_type = SIGNED(first, second)

        elif name.Value.lower() == 'unsigned':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid UNSIGNED parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for UNSIGNED')
                _logger.add_log(err)

                info = Info('hint - UNSIGNED(3 downto 0) or UNSIGNED(0 to 3)')
                _logger.add_log(info)
            else:
                curr_generic_sig_type = UNSIGNED(first, second)

        else:
            warn = Warning(name.Start, _filename,
                           'Type "' + name.Value.lower() + '" is not supported in generic linting')
            _logger.add_log(warn)

    def _add_to_parsed_generic(name):
        nonlocal parsed_generic, curr_generic_sigs, curr_generic_sig_type

        for sig in curr_generic_sigs:
            if sig not in parsed_generic:
                parsed_generic[sig] = EntityGenericSignalTypeToken(curr_generic_sig_type, name.Start)
            else:
                warn = Warning(name.Start, _filename,
                               'Generic signal "' + sig + '" in entity "' +
                                curr_entity_name + '" is already declared')
                _logger.add_log(warn)

        curr_generic_sigs = []
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
        elif name.Value.lower() == 'integer':
            curr_sig_type = INTEGER()
        elif name.Value.lower() == 'boolean':
            curr_sig_type = BOOLEAN()
        elif name.Value.lower() == 'time':
            curr_sig_type = TIME()
        elif name.Value.lower() == 'string':
            curr_sig_type = STRING()
        elif name.Value.lower() == 'std_logic_vector':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid STD_LOGIC_VECTOR parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for STD_LOGIC_VECTOR')
                _logger.add_log(err)

                info = Info('hint - STD_LOGIC_VECTOR(3 downto 0) or STD_LOGIC_VECTOR(0 to 3)')
                _logger.add_log(info)
            else:
                curr_sig_type = STD_LOGIC_VECTOR(first, second)

        elif name.Value.lower() == 'signed':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid SIGNED parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for SIGNED')
                _logger.add_log(err)

                info = Info('hint - SIGNED(3 downto 0) or SIGNED(0 to 3)')
                _logger.add_log(info)
            else:
                curr_sig_type = SIGNED(first, second)

        elif name.Value.lower() == 'unsigned':
            first, second = parse_to_downto(_token_iter, _logger, _filename)

            # Invalid UNSIGNED parsing
            if first is None and second is None:
                err = Error(name.Start, _filename, 'Invalid syntax for UNSIGNED')
                _logger.add_log(err)

                info = Info('hint - UNSIGNED(3 downto 0) or UNSIGNED(0 to 3)')
                _logger.add_log(info)
            else:
                curr_sig_type = UNSIGNED(first, second)

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
                parsed_port[sig] = EntityPortSignalTypeToken(curr_sig_in_out, curr_sig_type, name.Start)
            else:
                warn = Warning(name.Start, _filename,
                               'Signal "' + sig + '" in entity "' + curr_entity_name +
                               '" is already declared')
                _logger.add_log(warn)

        curr_sigs = []
        curr_sig_type = None
        curr_sig_in_out = ''

    def _check_entity_name(name):
        nonlocal curr_entity_name, is_component
        if not is_component and name.Value.lower() != curr_entity_name:
            err = Error(name.Start, _filename,
                        'Expecting entity "' + curr_entity_name + '", got: ' +
                        '"' + name.Value.lower() + '"')
            _logger.add_log(err)

        elif is_component and name.Value.lower() != 'component':
            err = Error(name.Start, _filename,
                        'Expecting "component" at end of component declaration, got: ' +
                        '"' + name.Value.lower() + '"')
            _logger.add_log(err)

    def _check_end_component(name):
        nonlocal curr_entity_name, is_component
        if not is_component:
            err = Error(name.Start, _filename,
                        'Expecting ";" at the end of entity')
            _logger.add_log(err)

        elif is_component and name.Value.lower() != curr_entity_name:
            err = Error(name.Start, _filename,
                        'Expecting component "' + curr_entity_name + '", got: ' +
                        '"' + name.Value.lower() + '"')
            _logger.add_log(err)

    # =========================================================================
    # Build parse_entity DFA
    # =========================================================================
    dfa = DFA('parse_entity', EntityStateEnum.START, [EntityStateEnum.SUCCESS])

    # Parse entity starting syntax
    dfa.add_transition(EntityStateEnum.START,
                       EntityStateEnum.ENTITY, 'entity', _set_is_component)
    dfa.add_transition(EntityStateEnum.START,
                       EntityStateEnum.ENTITY, 'component', _set_is_component)
    dfa.add_transition(EntityStateEnum.ENTITY, EntityStateEnum.NAME, '_*_',
                       _set_curr_entity_name)
    dfa.add_transition(EntityStateEnum.NAME, EntityStateEnum.IS, 'is')
    dfa.add_transition(EntityStateEnum.NAME, EntityStateEnum.GENERIC, 'generic')

    # Parse generic syntax
    dfa.add_transition(EntityStateEnum.IS, EntityStateEnum.GENERIC, 'generic')
    dfa.add_transition(EntityStateEnum.GENERIC, EntityStateEnum.GENERIC_OPEN_BRACK, '(')
    dfa.add_transition(EntityStateEnum.GENERIC_OPEN_BRACK,
                       EntityStateEnum.GENERIC_NAME, '_*_', _set_curr_generic_sig)
    dfa.add_transition(EntityStateEnum.GENERIC_NAME,
                       EntityStateEnum.GENERIC_OPEN_BRACK, ',')
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
    dfa.add_transition(EntityStateEnum.NAME, EntityStateEnum.PORT, 'port')
    dfa.add_transition(EntityStateEnum.IS, EntityStateEnum.PORT, 'port')
    dfa.add_transition(EntityStateEnum.PORT, EntityStateEnum.PORT_OPEN_BRACK, '(')

    dfa.add_transition(EntityStateEnum.PORT_OPEN_BRACK,
                       EntityStateEnum.SIGNAL, '_*_', _append_sig)
    dfa.add_transition(EntityStateEnum.SIGNAL, EntityStateEnum.PORT_OPEN_BRACK, ',')
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
    dfa.add_transition(EntityStateEnum.END_NAME,
                       EntityStateEnum.END_NAME, '_*_', _check_end_component)

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
        if dfa.get_curr_state == EntityStateEnum.IS:
            err = Error(curr_token.Start, _filename,
                        'Expecting "port" or "generic", ' +
                        'got "' + curr_token.Value.lower() + '"')
            _logger.add_log(err)
        elif dfa.get_curr_state == EntityStateEnum.SIGNAL_DONE:
            err = Error(curr_token.Start, _filename,
                        'Expecting "in", "out", "buffer", "inout" for signal type, ' +
                        'got "' + curr_token.Value.lower() + '"')
            _logger.add_log(err)

        elif dfa.get_curr_state == EntityStateEnum.GENERIC_TYPE:
            err = Error(curr_token.Start, _filename,
                        'Invalid generic type declaration around token "' +
                        curr_token.Value.lower() + '"')
            _logger.add_log(err)

            info = Info('hint - check syntax for declared generic type')
            _logger.add_log(info)

        elif dfa.get_curr_state == EntityStateEnum.SIGNAL_TYPE:
            err = Error(curr_token.Start, _filename,
                        'Invalid port type declaration around token "' +
                        curr_token.Value.lower() + '"')
            _logger.add_log(err)

            info = Info('hint - check syntax for declared port type')
            _logger.add_log(info)

        else:
            err = Error(curr_token.Start, _filename,
                        'Invalid declaration around token "' +
                        curr_token.Value.lower() + '"')
            _logger.add_log(err)

        return None

    return EntityComponent(is_component, curr_entity_name, parsed_generic, parsed_port)