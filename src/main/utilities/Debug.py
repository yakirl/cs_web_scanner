
import os

LOGS_DIR='logs/'
LOG_FILENAME = LOGS_DIR+'run.log'
ERR_FILENAME = LOGS_DIR+'run.err'
STDOUT = True

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Debug:
    def __init__(self, log_filename = LOG_FILENAME):
        self.kill_on_assrt = True
        self.curr_log_level = 0 # 0 - tmp prints. 
                                # 1 - logs. 
                                # 2 - errors
        if not os.path.isdir(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        self.flog = open(log_filename, 'w')
        self.ferr = open(ERR_FILENAME, 'w')

    def _print(self, msg):
        if STDOUT:
            print(msg)

    ''' log_level:
        0 - debug
        1 - info prints
        2 - warnings
        3 - errors
    '''
    def logger(self, msg, log_level = 0):
        if log_level >= self.curr_log_level:
            if log_level >= 2:
                color = bcolors.WARNING if log_level == 2 else bcolors.FAIL
                print (color + msg + bcolors.ENDC)
            else:
                self._print(msg)
            if type(msg) != type('str'):
                return
            msg = msg+'\n'
            self.flog.write(msg)
            if log_level >= 2:
                self.ferr.write(msg)

    def close_debugger(self):
        self.flog.close()
        self.ferr.close()

    def assrt(self, cond, msg, error = True):
        if not cond:
            log_level = 3 if error else 2
            self.logger (msg, log_level)
            if error and self.kill_on_assrt:
               exit(1)


