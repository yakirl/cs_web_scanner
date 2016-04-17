#!/bin/python

import signal
from utilities.Debug import Debug
from contextlib import contextmanager

'''
This class has not been checked yet!
'''

class TimeoutException(Exception): pass

DEFAULT_TIMEOUT = 8
debug = Debug()

def signal_handler(signum, frame):
    raise TimeoutException

class Misc:

    def print_types(self, *args):
        debug.logger("Printing Types:")
        for arg in args:
            debug.logger(type(arg))

    '''
        Set alarm
    '''
    @contextmanager
    def time_limit (self, seconds):
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)

    '''
    Params:
        func: function pointer
        args: tuple of arguments for func
        time_in_sec: time in seconds to run
        timeout_msg: message to print in case of timeout
    '''
    def run_with_timer(self, func, args, timeout_msg = "", throw_exp = True, time_in_sec = DEFAULT_TIMEOUT):
        res = None
        try:
            with self.time_limit(time_in_sec):
                res = func(*args)
        except TimeoutException:
            #debug.logger ("Timeout Expired: "+timeout_msg, 2)
            if throw_exp:
                raise TimeoutException
        return res






