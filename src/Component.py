from Tokenize import Tokenize
from State import DFA, State
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken

import sys
from enum import Enum
from collections import defaultdict

filename = sys.argv[1]
tokenize = Tokenize(filename)
token_iter = tokenize.get_token_iter()


class ComponentStateEnum(Enum):
    START = State(0)
    NAME = State(1)
    IS = State(2)
    PORT = State(3)
    OPEN_BRACK = State(4)
    SIGNAL = State(5)
    SIGNAL_DONE = State(6)
    NEXT_SIGNAL = State(7)
    SIGNAL_IN_OUT = State(8)
    SIGNAL_TYPE = State(9)
    CLOSE_BRACK = State(10)
    END_SEMICOLON = State(11)
    END = State(12)
    END_COMPONENT = State(13)
    END_NAME = State(14)
    SUCCESS = State(15)


def _parse_component(_token_iter):
    parsed = defaultdict(lambda: defaultdict(list))
    curr_sigs = []
    curr_sig_type = ''
    curr_sig_in_out = ''
    curr_component_name = ''

    # DFA callbacks
    def _set_curr_component_name(name):
        nonlocal curr_component_name
        curr_component_name = name

    def _set_sig_type(name):
        nonlocal curr_sig_type
        curr_sig_type = name

    def _set_sig_inout(name):
        nonlocal curr_sig_in_out
        curr_sig_in_out = name

    def _append_sig(name):
        nonlocal curr_sigs
        curr_sigs.append(name)

    def _add_to_parsed_obj(_):
        nonlocal parsed, curr_sigs, curr_sig_type, curr_sig_in_out

        # TODO: Log duplicated signals
        for sig in curr_sigs:
            parsed[curr_sig_in_out][curr_sig_type].append(sig)

        curr_sigs = []
        curr_sig_type = ''
        curr_sig_in_out = ''

    def _check_component_name(name):
        # TODO: Log if component name doesn't match
        nonlocal curr_component_name
        if name != curr_component_name:
            print('Not matching component name')

        curr_component_name = ''

    # =========================================================================
    # Build parse_component DFA
    # =========================================================================
    dfa = DFA('parse_component', ComponentStateEnum.START, [ComponentStateEnum.SUCCESS])

    # Parse component and port syntax
    dfa.add_transition(ComponentStateEnum.START, ComponentStateEnum.NAME, 'component')
    dfa.add_transition(ComponentStateEnum.NAME, ComponentStateEnum.IS, '_*_',
                       _set_curr_component_name)
    dfa.add_transition(ComponentStateEnum.IS, ComponentStateEnum.PORT, 'is')

    dfa.add_transition(ComponentStateEnum.PORT, ComponentStateEnum.OPEN_BRACK, 'port')
    dfa.add_transition(ComponentStateEnum.OPEN_BRACK, ComponentStateEnum.SIGNAL, '(')

    dfa.add_transition(ComponentStateEnum.SIGNAL,
                       ComponentStateEnum.NEXT_SIGNAL, '_*_', _append_sig)
    dfa.add_transition(ComponentStateEnum.NEXT_SIGNAL, ComponentStateEnum.SIGNAL, ',')
    dfa.add_transition(ComponentStateEnum.NEXT_SIGNAL, ComponentStateEnum.SIGNAL_DONE, ':')

    # Parse in out type
    dfa.add_transition(ComponentStateEnum.SIGNAL_DONE,
                       ComponentStateEnum.SIGNAL_IN_OUT, 'in', _set_sig_inout)
    dfa.add_transition(ComponentStateEnum.SIGNAL_DONE,
                       ComponentStateEnum.SIGNAL_IN_OUT, 'out', _set_sig_inout)
    dfa.add_transition(ComponentStateEnum.SIGNAL_DONE,
                       ComponentStateEnum.SIGNAL_IN_OUT, 'buffer', _set_sig_inout)
    dfa.add_transition(ComponentStateEnum.SIGNAL_DONE,
                       ComponentStateEnum.SIGNAL_IN_OUT, 'inout', _set_sig_inout)

    # Parse in signal type
    dfa.add_transition(ComponentStateEnum.SIGNAL_IN_OUT,
                       ComponentStateEnum.SIGNAL_TYPE, 'std_logic', _set_sig_type)
    dfa.add_transition(ComponentStateEnum.SIGNAL_TYPE,
                       ComponentStateEnum.SIGNAL, ';', _add_to_parsed_obj)
    dfa.add_transition(ComponentStateEnum.SIGNAL_TYPE,
                       ComponentStateEnum.CLOSE_BRACK, ')', _add_to_parsed_obj)

    # Parse end component
    dfa.add_transition(ComponentStateEnum.CLOSE_BRACK, ComponentStateEnum.END_SEMICOLON, ';')
    dfa.add_transition(ComponentStateEnum.END_SEMICOLON, ComponentStateEnum.END, 'end')
    dfa.add_transition(ComponentStateEnum.END,
                       ComponentStateEnum.END_COMPONENT, 'component')
    dfa.add_transition(ComponentStateEnum.END_COMPONENT,
                       ComponentStateEnum.END_NAME, '_*_', _check_component_name)
    dfa.add_transition(ComponentStateEnum.END_COMPONENT, ComponentStateEnum.SUCCESS, ';')
    dfa.add_transition(ComponentStateEnum.END_NAME, ComponentStateEnum.SUCCESS, ';')

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
                dfa.step(token.Value)

        except StopIteration as ex:
            # TODO: Logging
            print(ex)
            break

    print(curr_component_name)
    for p in parsed:
        print(p)

    dfa.reset()


_parse_component(token_iter)
