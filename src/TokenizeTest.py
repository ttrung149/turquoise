from Tokenize import Tokenize
import sys

filename = sys.argv[1]
tokenize = Tokenize(filename)
tokenize.generate_tokens()
tokenize.print_tokens()