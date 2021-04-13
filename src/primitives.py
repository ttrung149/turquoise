#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: primitives.py
#
#  Description: Implementation of DFAs that parse through primitive VHDL types
#
# -----------------------------------------------------------------------------

from state import DFA, State
from enum import Enum
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken


class STD_LOGIC:
    """ Represent a STD_LOGIC type """
    def __init__(self, val=None):
        self.val = val

    def __str__(self):
        return 'std_logic'


class STD_LOGIC_VECTOR:
    """ Represent a STD_LOGIC_VECTOR type """
    def __init__(self, start, end, val=None):
        self.start = start
        self.end = end
        self.val = val

    def __str__(self):
        return 'STD_LOGIC_VECTOR({} to {})'.format(self.start, self.end)

    def __eq__(self, other):
        return hasattr(other, 'start') and self.start == other.start and \
               hasattr(other, 'end') and self.end == other.end and \
               hasattr(other, 'val') and self.val == other.val

    def is_same_type(self, other):
        return hasattr(other, 'start') and self.start == other.start and \
               hasattr(other, 'end') and self.end == other.end


class StdLogicVectorStateEnum(Enum):
    START = State(0)
    VECTOR = State(1)
    OPEN_BRACK = State(2)
    FIRST = State(3)
    TO = State(4)
    SECOND = State(5)
    SUCCESS = State(6)


def _parse_std_logic_vector(_token_iter):
    parsed = None
    first = ''
    second = ''
    to_or_downto = ''

    # DFA callbacks
    def _set_first(name):
        nonlocal first
        first = name

    def _set_second(name):
        nonlocal second
        second = name

    def _set_to_or_downto(name):
        nonlocal to_or_downto
        to_or_downto = name

    def _set_parsed(_):
        nonlocal parsed, first, second, to_or_downto

        if to_or_downto == 'to':
            parsed = STD_LOGIC_VECTOR(first, second)
        elif to_or_downto == 'downto':
            parsed = STD_LOGIC_VECTOR(second, first)
        else:
            # TODO Add to logger
            pass

    dfa = DFA('parse_std_logic_vector', StdLogicVectorStateEnum.START,
              [StdLogicVectorStateEnum.SUCCESS])

    dfa.add_transition(StdLogicVectorStateEnum.START,
                       StdLogicVectorStateEnum.VECTOR, 'std_logic_vector')

    dfa.add_transition(StdLogicVectorStateEnum.VECTOR,
                       StdLogicVectorStateEnum.OPEN_BRACK, '(')
    dfa.add_transition(StdLogicVectorStateEnum.OPEN_BRACK,
                       StdLogicVectorStateEnum.FIRST, '_*_', _set_first)
    dfa.add_transition(StdLogicVectorStateEnum.FIRST,
                       StdLogicVectorStateEnum.TO, '_*_', _set_to_or_downto)
    dfa.add_transition(StdLogicVectorStateEnum.TO,
                       StdLogicVectorStateEnum.SECOND, '_*_', _set_second)

    dfa.add_transition(StdLogicVectorStateEnum.SECOND,
                       StdLogicVectorStateEnum.SUCCESS, ')', _set_parsed)

    while not dfa.is_finished:
        try:
            token = next(_token_iter)
            if isinstance(token, (StartOfDocumentToken, EndOfDocumentToken,
                                  LinebreakToken, SpaceToken,
                                  IndentationToken, CommentToken)):
                pass

            else:
                dfa.step(token.Value.lower())

        # Add logging

        except StopIteration as ex:
            # TODO: Logging
            print(ex)
            break

    print(parsed)

    dfa.reset()

