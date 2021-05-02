from Tokenize import Tokenize
from State import DFA, State
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken

import sys
from enum import Enum
from collections import defaultdict
from Error import Error, Warning
from Logger import Logger

from Primitives import STD_LOGIC, STD_LOGIC_VECTOR, BIT


logger = Logger()
filename = sys.argv[1]
tokenize = Tokenize(filename)
token_iter = tokenize.get_token_iter()


class SignalStateEnum(Enum):

    START = State(0)
    SIGNAL = State(1)
    NAME = State(2)
    COLON = State(3)
    SIGNAL_TYPE = State(4)
    SUCCESS = State(5)
    ASSIGNMENT_SYMBOL = State(6)
    SIGNAL_VALUE = State(7)


def parse_signal(_token_iter, _logger, _filename):

	signal_type = ''
	signal_name = ''
	signal_value = None

    # DFA callbacks
	def _set_signal_name(name):
		nonlocal signal_name
		signal_name = name

	def _set_signal_type(name):
		nonlocal signal_type
		signal_type = name

	def _set_signal_value(name):
		nonlocal signal_value
		signal_value = name

	# =========================================================================
    # Build parse_signal DFA
    # =========================================================================
	dfa = DFA('parse_signal', SignalStateEnum.START, [SignalStateEnum.SUCCESS])

    # Parse entity and port syntax
	dfa.add_transition(SignalStateEnum.START, SignalStateEnum.SIGNAL, 'signal')
	dfa.add_transition(SignalStateEnum.SIGNAL, SignalStateEnum.NAME, '_*_',
                       _set_signal_name)
	dfa.add_transition(SignalStateEnum.NAME, SignalStateEnum.COLON, ':')


	dfa.add_transition(SignalStateEnum.COLON, SignalStateEnum.SIGNAL_TYPE, '_*_', _set_signal_type)
	dfa.add_transition(SignalStateEnum.SIGNAL_TYPE, SignalStateEnum.SUCCESS, ';')

	dfa.add_transition(SignalStateEnum.SIGNAL_TYPE, SignalStateEnum.ASSIGNMENT_SYMBOL, ':=')
	dfa.add_transition(SignalStateEnum.ASSIGNMENT_SYMBOL,
                       SignalStateEnum.SIGNAL_VALUE, '_*_', _set_signal_value)
	dfa.add_transition(SignalStateEnum.SIGNAL_VALUE, SignalStateEnum.SUCCESS, ';')


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

	dfa.reset()
	return signal_name, signal_type, signal_value


signal_name, signal_type, signal_value = parse_signal(token_iter, logger, 'a.txt')
print(signal_name)
print(signal_type)
print(signal_value)

logger.print_logs_to_terminal()
