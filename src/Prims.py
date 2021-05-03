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
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken
from pyVHDLParser.Base import ParserException
from enum import Enum
from .State import DFA, State
from .Messages import Error, Warning


class PrimEnum(Enum):
    STD_LOGIC = -1
    BIT = -2
    STD_LOGIC_VECTOR = -3
    SIGNED = -4
    UNSIGNED = -5
    INTEGER = -6
    BOOLEAN = -7
    TIME = -8
    STRING = -9


class STD_LOGIC(tuple):
    """ Represent a STD_LOGIC type """
    __slots__ = []
    def __new__(cls):
        return tuple.__new__(cls, (PrimEnum.STD_LOGIC, 0))

    def __str__(self):
        return 'STD_LOGIC'


class BIT(tuple):
    """ Represent a BIT type """
    __slots__ = []
    def __new__(cls):
        return tuple.__new__(cls, (PrimEnum.BIT, 0))

    def __str__(self):
        return 'BIT'


class STD_LOGIC_VECTOR(tuple):
    """ Represent a STD_LOGIC_VECTOR type """
    __slots__ = []
    def __new__(cls, start, end):
        return tuple.__new__(cls, (PrimEnum.STD_LOGIC_VECTOR, start, end))

    def __str__(self):
        return 'STD_LOGIC_VECTOR({} to {})'.format(
            tuple.__getitem__(self, 1),
            tuple.__getitem__(self, 2)
        )


class SIGNED(tuple):
    """ Represent a SIGNED type """
    __slots__ = []
    def __new__(cls, start, end):
        return tuple.__new__(cls, (PrimEnum.SIGNED, start, end))

    def __str__(self):
        return 'SIGNED({} to {})'.format(
            tuple.__getitem__(self, 1),
            tuple.__getitem__(self, 2)
        )


class UNSIGNED(tuple):
    """ Represent a UNSIGNED type """
    __slots__ = []
    def __new__(cls, start, end):
        return tuple.__new__(cls, (PrimEnum.UNSIGNED, start, end))

    def __str__(self):
        return 'UNSIGNED({} to {})'.format(
            tuple.__getitem__(self, 1),
            tuple.__getitem__(self, 2)
        )


class INTEGER(tuple):
    """ Represent a INTEGER type """
    __slots__ = []
    def __new__(cls):
        return tuple.__new__(cls, (PrimEnum.INTEGER, 0))

    def __str__(self):
        return 'INTEGER'


class BOOLEAN(tuple):
    """ Represent a BOOLEAN type """
    __slots__ = []
    def __new__(cls):
        return tuple.__new__(cls, (PrimEnum.BOOLEAN, 0))

    def __str__(self):
        return 'BOOLEAN'


class TIME(tuple):
    """ Represent a TIME type """
    __slots__ = []
    def __new__(cls):
        return tuple.__new__(cls, (PrimEnum.TIME, 0))

    def __str__(self):
        return 'TIME'


class STRING(tuple):
    """ Represent a STRING type """
    __slots__ = []
    def __new__(cls):
        return tuple.__new__(cls, (PrimEnum.STRING, 0))

    def __str__(self):
        return 'STRING'


class ToDownToStateEnum(Enum):
    START = State(1)
    OPEN_BRACK = State(2)
    FIRST = State(3)
    TO = State(4)
    SECOND = State(5)
    SUCCESS = State(6)


def parse_to_downto(_token_iter, _logger, _filename):
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
            parsed = (first, second)
            if int(first) >= int(second):
                warn = Warning(name.Start, _filename,
                               'Expecting first value to be smaller than ' +
                               'second value in "to" declaration')
                _logger.add_log(warn)

        elif to_or_downto == 'downto':
            parsed = (second, first)
            if int(first) <= int(second):
                warn = Warning(name.Start, _filename,
                               'Expecting first value to be smaller than ' +
                               'second value in "downto" declaration')
                _logger.add_log(warn)
        else:
            err = Error(name.Start, _filename,
                        'Expecting "to" or "downto" declaration')
            _logger.add_log(err)

    # =========================================================================
    # Build parse_to_downto DFA
    # =========================================================================
    dfa = DFA('parse_to_downto', ToDownToStateEnum.START,
              [ToDownToStateEnum.SUCCESS])

    dfa.add_transition(ToDownToStateEnum.START,
                       ToDownToStateEnum.OPEN_BRACK, '(')
    dfa.add_transition(ToDownToStateEnum.OPEN_BRACK,
                       ToDownToStateEnum.FIRST, '_*_', _set_first)
    dfa.add_transition(ToDownToStateEnum.FIRST,
                       ToDownToStateEnum.TO, '_*_', _set_to_or_downto)
    dfa.add_transition(ToDownToStateEnum.TO,
                       ToDownToStateEnum.SECOND, '_*_', _set_second)

    dfa.add_transition(ToDownToStateEnum.SECOND,
                       ToDownToStateEnum.SUCCESS, ')', _set_parsed)

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

        except ValueError as ex:
            err = Error(token.Start, _filename, str(ex))
            _logger.add_log(err)
            break

    if not dfa.is_finished_successfully:
        return (None, None)

    return parsed