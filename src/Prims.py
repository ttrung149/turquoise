#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Prims.py
#
#  Description: Implementation of DFAs that parse through primitive VHDL types
#
# -----------------------------------------------------------------------------
from State import DFA, State
from enum import Enum
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken
from Error import Error, Warning
from enum import Enum
from pyVHDLParser.Base import ParserException

class PrimEnum(Enum):
    STD_LOGIC = -1
    BIT = -2
    STD_LOGIC_VECTOR = -3


# -----------------------------------------------------------------------------
# STD_LOGIC
# -----------------------------------------------------------------------------
class STD_LOGIC(tuple):
    """ Represent a STD_LOGIC type """
    __slots__ = []
    def __new__(cls):
        return tuple.__new__(cls, (PrimEnum.STD_LOGIC, 0))

    def __str__(self):
        return 'std_logic'


# -----------------------------------------------------------------------------
# BIT
# -----------------------------------------------------------------------------
class BIT(tuple):
    """ Represent a BIT type """
    __slots__ = []
    def __new__(cls):
        return tuple.__new__(cls, (PrimEnum.BIT, 0))

    def __str__(self):
        return 'bit'


# -----------------------------------------------------------------------------
# STD_LOGIC_VECTOR
# -----------------------------------------------------------------------------
class STD_LOGIC_VECTOR(tuple):
    """ Represent a STD_LOGIC_VECTOR type """
    __slots__ = []
    def __new__(cls, start, end):
        return tuple.__new__(cls, (PrimEnum.STD_LOGIC_VECTOR, start, end))

    def __str__(self):
        return 'STD_LOGIC_VECTOR({} to {})'.format(
            tuple.__getitem__(self, 0),
            tuple.__getitem__(self, 1)
        )


class StdLogicVectorStateEnum(Enum):
    START = State(1)
    OPEN_BRACK = State(2)
    FIRST = State(3)
    TO = State(4)
    SECOND = State(5)
    SUCCESS = State(6)


def parse_std_logic_vector(_token_iter, _logger, _filename):
    parsed = None
    first = ''
    second = ''
    to_or_downto = ''

    # DFA callbacks
    def _set_first(name):
        nonlocal first
        first = name.Value.lower()

    def _set_second(name):
        nonlocal second
        second = name.Value.lower()

    def _set_to_or_downto(name):
        nonlocal to_or_downto
        to_or_downto = name.Value.lower()

    def _set_parsed(name):
        nonlocal parsed, first, second, to_or_downto

        if to_or_downto == 'to':
            parsed = STD_LOGIC_VECTOR(first, second)
            if int(first) >= int(second):
                warn = Warning(name.Start, _filename,
                               'Expecting first value to be smaller than ' +
                               'second value in "to" declaration for STD_LOGIC_VECTOR')
                _logger.add_log(warn)

        elif to_or_downto == 'downto':
            parsed = STD_LOGIC_VECTOR(second, first)
            if int(first) <= int(second):
                warn = Warning(name.Start, _filename,
                               'Expecting first value to be smaller than ' +
                               'second value in "downto" declaration for STD_LOGIC_VECTOR')
                _logger.add_log(warn)
        else:
            err = Error(name.Start, _filename,
                        'Expecting "to" or "downto" decl for STD_LOGIC_VECTOR')
            _logger.add_log(err)

    # =========================================================================
    # Build parse_std_logic_vector DFA
    # =========================================================================
    dfa = DFA('parse_std_logic_vector', StdLogicVectorStateEnum.START,
              [StdLogicVectorStateEnum.SUCCESS])

    dfa.add_transition(StdLogicVectorStateEnum.START,
                       StdLogicVectorStateEnum.OPEN_BRACK, '(')
    dfa.add_transition(StdLogicVectorStateEnum.OPEN_BRACK,
                       StdLogicVectorStateEnum.FIRST, '_*_', _set_first)
    dfa.add_transition(StdLogicVectorStateEnum.FIRST,
                       StdLogicVectorStateEnum.TO, '_*_', _set_to_or_downto)
    dfa.add_transition(StdLogicVectorStateEnum.TO,
                       StdLogicVectorStateEnum.SECOND, '_*_', _set_second)

    dfa.add_transition(StdLogicVectorStateEnum.SECOND,
                       StdLogicVectorStateEnum.SUCCESS, ')', _set_parsed)

    # =========================================================================
    # Token stream iteration
    # =========================================================================
    while not dfa.is_finished:
        try:
            token = next(_token_iter)
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

    if not dfa.is_finished_successfully:
        return None

    return parsed