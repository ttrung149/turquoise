from Logger import Logger
from Error import Error, Warning

e1 = Error(5, "input.txt")
e2 = Error(5, "input.txt", "Generic error")
w1 = Warning(5, "input.txt")
w2 = Warning(5, "input.txt", "Generic warning")

logs = [e1, w1]
logger1 = Logger(logs)
logger1.add_log(e2)
logger1.add_log(w2)
logger1.print_logs_to_terminal()
logger1.print_logs_to_file()

logger2 = Logger(logs, "log2.txt")
logger2.print_logs_to_file()