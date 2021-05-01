from Error import Error, Warning
from colored import fg, bg, attr
import sys

class Logger:
    
    #Constructor
    def __init__(self, logs=[], filename="log.txt"):
        self.logs = logs
        self.filename = filename

    def get_logs(self):
        return self.logs

    #Add a new log to the logger
    def add_log(self, log):
        self.logs.append(log)

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
