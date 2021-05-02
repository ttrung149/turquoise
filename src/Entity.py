from Tokenize import Tokenize
from State import DFA, State
from Primitives import STD_LOGIC, STD_LOGIC_VECTOR, BIT, \
                       parse_std_logic_vector
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken

from Error import Error, Warning
from Logger import Logger

# TODO: delete sys
import sys
from enum import Enum
from collections import defaultdict

logger = Logger()
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


def parse_entity(_token_iter, _logger, _filename):
    parsed = defaultdict(lambda: defaultdict(set))
    curr_sigs = []
    curr_sig_type = None
    curr_sig_in_out = ''
    curr_entity_name = ''

    # DFA callbacks
    def _set_curr_entity_name(name):
        nonlocal curr_entity_name
        curr_entity_name = name.Value.lower()

    def _set_sig_type(name):
        nonlocal curr_sig_type

        if name == 'std_logic':
            curr_sig_type = STD_LOGIC()
        elif name == 'bit':
            curr_sig_type = BIT()
        elif name == 'std_logic_vector':
            curr_sig_type = parse_std_logic_vector(_token_iter, _logger, _filename)

            # Invalid STD_LOGIC_VECTOR parsing
            if curr_sig_type is None:
                err = Error(name.Start, _filename, 'Invalid syntax for STD_LOGIC_VECTOR')
                _logger.add_log(err)

    def _set_sig_inout(name):
        nonlocal curr_sig_in_out
        curr_sig_in_out = name.Value.lower()

    def _append_sig(name):
        nonlocal curr_sigs
        curr_sigs.append(name.Value.lower())

    def _add_to_parsed_obj(name):
        nonlocal parsed, curr_sigs, curr_sig_type, curr_sig_in_out

        for sig in curr_sigs:
            signals = parsed[curr_sig_in_out][curr_sig_type]
            if sig in signals:
                err = Error(name.Start, _filename,
                            'Signal "' + sig + '" in entity "' + curr_entity_name +
                            '" is already declared.')
                _logger.add_log(err)
                return
            else:
                signals.add(sig)

        curr_sigs = []
        curr_sig_type = ''
        curr_sig_in_out = ''

    def _check_entity_name(name):
        nonlocal curr_entity_name
        if name.Value.lower() != curr_entity_name:
            err = Error(name.Start, _filename,
                        'Expecting entity "' + curr_entity_name + '", got: ' +
                        '"' + name.Value.lower() + '".')
            _logger.add_log(err)

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
    dfa.add_transition(EntityStateEnum.SIGNAL_IN_OUT,
                       EntityStateEnum.SIGNAL_TYPE, 'std_logic_vector', _set_sig_type)
    dfa.add_transition(EntityStateEnum.SIGNAL_IN_OUT,
                       EntityStateEnum.SIGNAL_TYPE, 'bit', _set_sig_type)

    dfa.add_transition(EntityStateEnum.SIGNAL_TYPE,
                       EntityStateEnum.SIGNAL, ';', _add_to_parsed_obj)
    dfa.add_transition(EntityStateEnum.SIGNAL_TYPE,
                       EntityStateEnum.CLOSE_BRACK, ')', _add_to_parsed_obj)

    # Parse end entity
    dfa.add_transition(EntityStateEnum.CLOSE_BRACK, EntityStateEnum.END_SEMICOLON, ';')
    dfa.add_transition(EntityStateEnum.END_SEMICOLON, EntityStateEnum.END, 'end')
    dfa.add_transition(EntityStateEnum.PORT, EntityStateEnum.END, 'end')
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

        except StopIteration as ex:
            err = Error(token.Start, _filename, ex)
            _logger.add_log(err)
            break

    # Add specific warnings and errors to logger
    if not dfa.is_finished_successfully:
        if dfa.get_curr_state == EntityStateEnum.PORT:
            err = Error(curr_token.Start, _filename,
                        'Expecting "port", ' +
                        'got "' + curr_token.Value.lower() + '".')
            _logger.add_log(err)
        elif dfa.get_curr_state == EntityStateEnum.SIGNAL_DONE:
            err = Error(curr_token.Start, _filename,
                        'Expecting "in", "out", "buffer", "inout" for signal type, ' +
                        'got "' + curr_token.Value.lower() + '".')
            _logger.add_log(err)

        elif dfa.get_curr_state == EntityStateEnum.SIGNAL_IN_OUT:
            warn = Warning(curr_token.Start, _filename,
                           'Type "' + curr_token.Value.lower() + '" is not supported.')
            _logger.add_log(warn)

        return None

    return parsed


a = parse_entity(token_iter, logger, 'a.txt')
print(a)

logger.print_logs_to_terminal()
