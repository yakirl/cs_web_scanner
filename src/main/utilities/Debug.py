
import os
import Global

LOGS_DIR = os.path.join(Global.BASE_DIR, 'logs')
LOG_FILENAME = os.path.join(LOGS_DIR, 'last_run.out')
ERR_FILENAME = os.path.join(LOGS_DIR, 'last_run.err')
DEBUG_MODE_FILE = os.path.join('system' ,'debug_mode')
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

if 'nt' == os.name:
    USE_COLOR = False
else:
    USE_COLOR = True

MOD_DEBUG    = 0
MOD_INFO     = 1
MOD_WARNINGS = 2
MOD_ERRORS   = 3
MOD_SILENT   = 4

class Debug:
    def __init__(self):
        self.kill_on_assrt = True
        with open(DEBUG_MODE_FILE, 'r') as f:
            self.curr_log_level = int(f.read()[0][0])
        if not os.path.isdir(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        self.flog = open(LOG_FILENAME, 'w')
        self.ferr = open(ERR_FILENAME, 'w')

    def change_mod(self, debug_mod):
        with open(DEBUG_MODE_FILE, 'w') as f:
            f.write(str(debug_mod))
        self.curr_log_level = debug_mod

    def _print(self, msg):
        if STDOUT:
            print(msg)

    def logger(self, msg, log_level = 0):
        if log_level >= self.curr_log_level:
            if log_level >= 2:
                color = bcolors.WARNING if log_level == 2 else bcolors.FAIL
                if USE_COLOR:
                    print (color + msg + bcolors.ENDC)
                else:
                    print(msg)
            else:
                self._print(msg)
            #if type(msg) != type('str'):
            #    print(type(msg))
            #    return
            msg = msg+'\n'
            try:
                self.flog.write(msg)
            except:
                print("Couldnt write to file!")
        if log_level >= 2:
	    #print("PRINT_ERR")
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


