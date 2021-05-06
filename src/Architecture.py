#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Architecture.py
#
#  Description: Implementation of DFAs that parse through architecture syntax
#
# -----------------------------------------------------------------------------
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken
from pyVHDLParser.Base import ParserException
from enum import Enum
from itertools import chain

from .State import DFA, State
from .Messages import Error, Warning
from .Entity import parse_entity_component
from .Signal import parse_signal


class ArchStateEnum(Enum):
    START = State(0)
    ARCH = State(1)
    ARCH_NAME = State(2)
    OF = State(3)
    ENTITY_NAME = State(4)
    IS = State(5)
    BEGIN_ARCH = State(6)
    NEW_BEGIN_BLK = State(7)
    ASSIGN = State(8)
    ASSIGN_NEW_BEGIN_BLK = State(9)
    END = State(10)
    END_ARCH = State(11)
    SUCCESS = State(12)


class Architecture:
    def __init__(self):
        self._name = ''
        self._entity_name = ''
        self._declared_signals = []
        self._declared_components = []
        self._portmaps = []
        self._assigned_signals = []

    def set_name(self, name):
        self._name = name

    def set_entity_name(self, name):
        self._entity_name = name

    def add_declared_signal(self, signal_name, signal_type):
        self._declared_signals.append((signal_name, signal_type))

    def add_declared_component(self, component):
        self._declared_components.append(component)

    def add_assigned_signal(self, token):
        self._assigned_signals.append(token)

    @property
    def name(self):
        return self._name

    @property
    def entity_name(self):
        return self._entity_name

    @property
    def declared_components(self):
        return self._declared_components

    @property
    def declared_signals(self):
        return self._declared_signals

    def __str__(self):
        return 'ARCHITECTURE {} of {}'.format(self._name, self._entity_name)

    def __repr__(self):
        return 'ARCHITECTURE {} of {}'.format(self._name, self._entity_name)


def parse_architecture(_token_iter, _logger, _filename):
    """
    @brief Helper function. Parse architecture syntax
    @param _token_iter Token Iteration
    @param _logger Logger instance
    @param _filename Current file name that is being linted
    @return Parsed Architecture class
    """
    # Token tracker
    curr_token = None
    prev_token = None

    parsed = Architecture()
    arch_name = ''
    entity_name = ''

    # DFA callbacks
    def _set_arch_name(name):
        nonlocal parsed, arch_name
        arch_name = name.Value.lower()
        parsed.set_name(arch_name)

    def _set_entity_name(name):
        nonlocal parsed, entity_name
        entity_name = name.Value.lower()
        parsed.set_entity_name(entity_name)

    def _add_components_and_sigs(name):
        nonlocal parsed
        if name.Value.lower() == 'component':
            new_token_iter = chain([name], _token_iter)
            comp = parse_entity_component(new_token_iter, _logger, _filename)

            if comp is None:
                err = Error(name.Start, _filename, 'Invalid syntax for component declaration')
                _logger.add_log(err)
            else:
                parsed.add_declared_component(comp)

        elif name.Value.lower() == 'signal' or name.Value.lower() == 'constant':
            new_token_iter = chain([name], _token_iter)
            signal_dict = parse_signal(new_token_iter, _logger, _filename)

            if signal_dict is None:
                err = Error(name.Start, _filename, 'Invalid syntax for signal/constant declaration')
                _logger.add_log(err)
            else:
                for signal_name in signal_dict:
                    parsed.add_declared_signal(signal_name, signal_dict[signal_name])

    def _add_assigned_token(name):
        nonlocal prev_token, parsed
        parsed.add_assigned_signal(prev_token.Value)

    # =========================================================================
    # Build parse_architecture DFA
    # =========================================================================
    dfa = DFA('parse_arch', ArchStateEnum.START, [ArchStateEnum.SUCCESS])

    # Parse entity and port syntax
    dfa.add_transition(ArchStateEnum.START, ArchStateEnum.ARCH, 'architecture')
    dfa.add_transition(ArchStateEnum.ARCH, ArchStateEnum.ARCH_NAME, '_*_',
                       _set_arch_name)
    dfa.add_transition(ArchStateEnum.ARCH_NAME, ArchStateEnum.OF, 'of')
    dfa.add_transition(ArchStateEnum.OF, ArchStateEnum.ENTITY_NAME, '_*_',
                       _set_entity_name)
    dfa.add_transition(ArchStateEnum.ENTITY_NAME,ArchStateEnum.IS, 'is')
    dfa.add_transition(ArchStateEnum.IS, ArchStateEnum.IS, '_*_',
                       _add_components_and_sigs)

    dfa.add_transition(ArchStateEnum.IS, ArchStateEnum.BEGIN_ARCH, 'begin')
    dfa.add_transition(ArchStateEnum.BEGIN_ARCH,
                       ArchStateEnum.ASSIGN, '<=', _add_assigned_token)
    dfa.add_transition(ArchStateEnum.ASSIGN, ArchStateEnum.BEGIN_ARCH, '_*_')
    dfa.add_transition(ArchStateEnum.BEGIN_ARCH, ArchStateEnum.NEW_BEGIN_BLK, 'begin')
    dfa.add_transition(ArchStateEnum.NEW_BEGIN_BLK,
                       ArchStateEnum.ASSIGN_NEW_BEGIN_BLK, '<=', _add_assigned_token)
    dfa.add_transition(ArchStateEnum.ASSIGN_NEW_BEGIN_BLK,
                       ArchStateEnum.NEW_BEGIN_BLK, '_*_')

    dfa.add_transition(ArchStateEnum.NEW_BEGIN_BLK, ArchStateEnum.NEW_BEGIN_BLK, '_*_')
    dfa.add_transition(ArchStateEnum.NEW_BEGIN_BLK, ArchStateEnum.BEGIN_ARCH, 'end')

    dfa.add_transition(ArchStateEnum.BEGIN_ARCH, ArchStateEnum.BEGIN_ARCH, '_*_')
    dfa.add_transition(ArchStateEnum.BEGIN_ARCH, ArchStateEnum.END, 'end')
    dfa.add_transition(ArchStateEnum.END, ArchStateEnum.SUCCESS, ';')
    dfa.add_transition(ArchStateEnum.END, ArchStateEnum.END_ARCH, '_*_')
    dfa.add_transition(ArchStateEnum.END_ARCH, ArchStateEnum.SUCCESS, ';')

    # =========================================================================
    # Token stream iteration
    # =========================================================================
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
                prev_token = token

        except ParserException as ex:
            err = Error(token.Start, _filename, str(ex))
            _logger.add_log(err)
            break

        except StopIteration:
            break

    # @TODO Add specific warnings and errors to logger
    if not dfa.is_finished_successfully:
        return None

    # print(parsed._assigned_signals)
    return parsed