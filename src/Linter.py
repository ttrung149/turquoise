from Logger import Logger
from Error import Error, Warning

class Linter:

	def __init__(self, filename):
		self.filename = filename
		self.logs = []


	def get_logger(self):
		return Logger(logs=self.logs)


	def lint(self):
		e1 = Error(5, "input.txt")
		w1 = Warning(6, "input.txt", "Generic warning")

		self.logs.append(e1)
		self.logs.append(w1)