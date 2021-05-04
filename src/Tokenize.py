#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Tokenize.py
#
#  Description: Implementation of tokenizer class
#
# -----------------------------------------------------------------------------
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