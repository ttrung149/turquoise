#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: state.py
#
#  Description: Implementation of state machine for parsing some
#  VHDL syntax (used in the linter)
#
# -----------------------------------------------------------------------------
from collections import defaultdict
from typing import List


class State:
    """ Represent a state in the state machine """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return hasattr(other, 'name') and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class DFA:
    """ Implementation of Deterministic Finite Automaton """
    def __init__(self, name: str, start: State, finish: List[State]):
        self._name = name
        self._start = start
        self._curr_state = start

        self._finish = finish
        self._is_finished = False
        self._success = False

        self._transitions = defaultdict(dict)
        self._callbacks = defaultdict(dict)

    def add_transition(self, _from: State, _to: State, _input='', _cb=None):
        self._transitions[_from][_input] = _to
        self._callbacks[_from][_input] = _cb

    def reset(self):
        self._curr_state = self._start
        self._is_finished = False
        self._success = False

    def step(self, _input_token) -> None:
        _input = _input_token.Value.lower()
        _from = self._curr_state
        if _input in self._transitions[_from]:
            next_state = self._transitions[_from][_input]
            self._curr_state = next_state

            if self._callbacks[_from][_input] is not None:
                self._callbacks[_from][_input](_input_token)

            if self._curr_state not in self._transitions:
                self._is_finished = True
                self._success = self._curr_state in self._finish

        elif '_*_' in self._transitions[_from]:
            next_state = self._transitions[_from]['_*_']
            self._curr_state = next_state

            if self._callbacks[_from]['_*_'] is not None:
                self._callbacks[_from]['_*_'](_input_token)

            if self._curr_state not in self._transitions:
                self._is_finished = True
                self._success = self._curr_state in self._finish

        else:
            self._is_finished = True
            self._success = _from in self._finish

    @property
    def get_curr_state(self) -> State:
        return self._curr_state

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def is_finished_successfully(self) -> bool:
        return self._is_finished and self._success

    def __str__(self):
        return self._name
