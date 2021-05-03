from pyVHDLParser.Token.Parser import Tokenizer
from pyVHDLParser.Blocks import TokenToBlockParser
from pyVHDLParser.Base import ParserException

class Tokenize():

    def __init__(self, filename=None):
        self._filename = filename

    def get_token_stream(self):
        with open (self._filename, 'r') as handle:
            content = handle.read()

        stream = Tokenizer.GetVHDLTokenizer(content)
        return stream

    def get_token_iter(self):
        stream = self.get_token_stream()
        token_iter = iter(stream)
        return token_iter