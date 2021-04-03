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

class State:
    """ Represent a state in the state machine """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class DFA:
    """ Implementation of Deterministic Finite Automaton """
    def __init__(self, name: str, start_state: State):
        self.name = name
        self.start_state = start_state
        self.curr_state = start_state
        self.transitions = {}

    def add_transition(self, _from: State, _to: State, _input: str) -> None:
        self.transitions[_from][_input] = _to

    def reset(self):
        self.curr_state = self.start_state

    def step(self, _input: str) -> None:
        if _input in self.transitions[self.curr_state]:
            next_state = self.transitions[self.curr_state][_input]
            self.curr_state = next_state

    def get_curr_state(self) -> State:
        return self.curr_state

    def is_final(self) -> bool:
        return self.curr_state not in self.transitions

    def __str__(self):
        return self.name

