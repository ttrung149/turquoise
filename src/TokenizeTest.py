from Tokenize import Tokenize
import sys

filename = sys.argv[1]
tokenize = Tokenize(filename)
tokens = tokenize.get_tokens()
token_iter = tokenize.get_token_iter()
print(tokens)
for t in token_iter:
	print(t)