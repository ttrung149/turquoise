from colored import fg, bg, attr

class Error:

	#Error constructor that contains the line number, filename, and a specific 
	#error message
	def __init__(self, line_number, filename, error_message=None):
		self.line_number = line_number
		self.filename = filename
		self.message = "Error at line " + str(line_number) + \
			" of " + filename 
		if error_message != None:
			self.message = self.message + ": " + error_message

	def __repr__(self):
		color = fg('light_red')
		reset = attr('reset')
		return (color + self.message + reset)


class Warning:

	#Warning constructor that contains the line number, filename, and a specific 
	#warning message
	def __init__(self, line_number, filename, warning_message=None):
		self.line_number = line_number
		self.filename = filename
		self.message = "Warning at line " + str(line_number) + \
			" of " + filename 
		if warning_message != None:
			self.message = self.message + ": " + warning_message

	def __repr__(self):
		color = fg('light_yellow')
		reset = attr('reset')
		return (color + self.message + reset)

