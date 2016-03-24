
LOG_FILENAME = 'logs/run.log'


class Debug:
    def __init__(self, log_filename = LOG_FILENAME):
        self.kill_on_assrt = True
        self.curr_log_level = 0 # 0 - tmp prints. 
                                # 1 - logs. 
                                # 2 - errors
        self.f = open(LOG_FILENAME, 'w')

    def logger(self, msg, log_level = 0):
        if log_level >= self.curr_log_level:
            print (msg+"\n")
            self.f.write(msg)

    def assrt(self, cond, msg):
        if not cond:
            self.logger (msg, 2)
            if self.kill_on_assrt:
               exit(1)
