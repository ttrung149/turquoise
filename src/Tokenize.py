from pyVHDLParser.Token.Parser import Tokenizer
from pyVHDLParser.Blocks import TokenToBlockParser
from pyVHDLParser.Base import ParserException

class Tokenize():

	def __init__(self, filename=None):
		self.filename = filename

	def get_token_stream(self):
		# Open a source file
		with open (self.filename, 'r') as fileHandle:
			content = fileHandle.read()

		#get a token generator
		tokenStream = Tokenizer.GetVHDLTokenizer(content)
		return tokenStream


	def get_tokens(self):
		tokenStream = self.get_token_stream()
		# get a block generator
		blockStream = TokenToBlockParser.Transform(tokenStream)

		tokens = []
		try:
			for token in tokenStream:
				tokens.append(token)
		except ParserException as ex:
			print("ERROR: {0!s}".format(ex))
		except NotImplementedError as ex:
			print("NotImplementedError: {0!s}".format(ex))

		return tokens


	def get_token_iter (self):
		tokenStream = self.get_token_stream()
		tokenIter = iter(tokenStream)
		return tokenIter

