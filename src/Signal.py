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

class SignalStateEnum(Enum):
    START = State(0)
    NAME = State(1)
    COLON = State(2)
    SIGNAL_TYPE = State(3)
    SEMICOLON = State(4)
    SUCCESS = State(5)
    ASSIGNMENT_SYMBOL = State(6)
    SIGNAL_VALUE = State(7)


def _parse_signal(_token_iter):

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
	dfa.add_transition(SignalStateEnum.START, SignalStateEnum.NAME, 'signal')
	dfa.add_transition(SignalStateEnum.NAME, SignalStateEnum.COLON, '_*_',
                       _set_signal_name)
	dfa.add_transition(SignalStateEnum.COLON, SignalStateEnum.SIGNAL_TYPE, ':')


	dfa.add_transition(SignalStateEnum.SIGNAL_TYPE, SignalStateEnum.SEMICOLON, '_*_', _set_signal_type)
	dfa.add_transition(SignalStateEnum.SEMICOLON, SignalStateEnum.SUCCESS, ';')

	dfa.add_transition(SignalStateEnum.SEMICOLON, SignalStateEnum.ASSIGNMENT_SYMBOL, ':=')
	dfa.add_transition(SignalStateEnum.ASSIGNMENT_SYMBOL,
                       SignalStateEnum.SIGNAL_VALUE, '_*_', _set_signal_value)
	dfa.add_transition(SignalStateEnum.SIGNAL_VALUE, SignalStateEnum.SUCCESS, ';')


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

	dfa.reset()

	return signal_name, [signal_type, signal_value]


signal_name, [signal_type, signal_value] = _parse_signal(token_iter)
print(signal_name)
print(signal_type)
print(signal_value)
    

   