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


class EntityStateEnum(Enum):
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
    END_NAME = State(13)
    SUCCESS = State(14)


def _parse_entity(_token_iter):
    parsed = defaultdict(lambda: defaultdict(list))
    curr_sigs = []
    curr_sig_type = ''
    curr_sig_in_out = ''
    curr_entity_name = ''

    # DFA callbacks
    def _set_curr_entity_name(name):
        nonlocal curr_entity_name
        curr_entity_name = name

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

    def _check_entity_name(name):
        # TODO: Log if entity name doesn't match
        nonlocal curr_entity_name
        if name != curr_entity_name:
            print('Not matching entity name')

        curr_entity_name = ''

    # =========================================================================
    # Build parse_entity DFA
    # =========================================================================
    dfa = DFA('parse_entity', EntityStateEnum.START, [EntityStateEnum.SUCCESS])

    # Parse entity and port syntax
    dfa.add_transition(EntityStateEnum.START, EntityStateEnum.NAME, 'entity')
    dfa.add_transition(EntityStateEnum.NAME, EntityStateEnum.IS, '_*_',
                       _set_curr_entity_name)
    dfa.add_transition(EntityStateEnum.IS, EntityStateEnum.PORT, 'is')

    dfa.add_transition(EntityStateEnum.PORT, EntityStateEnum.OPEN_BRACK, 'port')
    dfa.add_transition(EntityStateEnum.OPEN_BRACK, EntityStateEnum.SIGNAL, '(')

    dfa.add_transition(EntityStateEnum.SIGNAL,
                       EntityStateEnum.NEXT_SIGNAL, '_*_', _append_sig)
    dfa.add_transition(EntityStateEnum.NEXT_SIGNAL, EntityStateEnum.SIGNAL, ',')
    dfa.add_transition(EntityStateEnum.NEXT_SIGNAL, EntityStateEnum.SIGNAL_DONE, ':')

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
                       EntityStateEnum.SIGNAL_TYPE, 'std_logic', _set_sig_type)
    dfa.add_transition(EntityStateEnum.SIGNAL_TYPE,
                       EntityStateEnum.SIGNAL, ';', _add_to_parsed_obj)
    dfa.add_transition(EntityStateEnum.SIGNAL_TYPE,
                       EntityStateEnum.CLOSE_BRACK, ')', _add_to_parsed_obj)

    # Parse end entity
    dfa.add_transition(EntityStateEnum.CLOSE_BRACK, EntityStateEnum.END_SEMICOLON, ';')
    dfa.add_transition(EntityStateEnum.PORT, EntityStateEnum.END, 'end')
    dfa.add_transition(EntityStateEnum.END_SEMICOLON, EntityStateEnum.END, 'end')
    dfa.add_transition(EntityStateEnum.END,
                       EntityStateEnum.END_NAME, '_*_', _check_entity_name)
    dfa.add_transition(EntityStateEnum.END_NAME, EntityStateEnum.SUCCESS, ';')

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

    print(curr_entity_name)
    print(parsed)

    dfa.reset()

    return parsed


_parse_entity(token_iter)
