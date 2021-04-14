
#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: logger.py
#
#  Description: Implementation of a logger class 
#
# -----------------------------------------------------------------------------

from Error import Error, Warning
from colored import fg, bg, attr
import sys

class Logger:
	
	#Constructor
	def __init__(self, logs=[], filename="log.txt"):
		self.logs = logs
		self.filename = filename

	#Pretty print the logs to the file
	def print_logs_to_file(self):
		original_stdout = sys.stdout
		with open(self.filename, 'w') as f:
			sys.stdout = f
			for x in self.logs:
				print(x.message)
			sys.stdout = original_stdout

	#Pretty print the logs to terminal
	def print_logs_to_terminal(self):
		for x in self.logs:
			print(x)





