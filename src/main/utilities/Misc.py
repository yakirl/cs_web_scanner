#!/bin/python

import signal
from utilities.Debug import Debug
from Global import *
from contextlib import contextmanager
import threading

'''
This class has not been checked yet!
'''

class TimeoutException(Exception): pass

DEFAULT_TIMEOUT = 8

def signal_handler(signum, frame):
    raise TimeoutException

class Misc:

    def __init__(self):
        self.debug = register_debugger()

    def print_types(self, *args):
        self.debug.logger("Printing Types:")
        for arg in args:
            self.debug.logger(type(arg))

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
      
    Note: this is not implemented yet, since signals supported only for main thread. TODO.
    '''
    def run_with_timer(self, func, args, timeout_msg = "", throw_exp = True, time_in_sec = DEFAULT_TIMEOUT):
        res = func(*args)
        return res
        res = None
        try:
            ''' non-main thread cant set signal handler '''
            if isinstance(threading.current_thread(), threading._MainThread):
                with self.time_limit(time_in_sec):
                    res = func(*args)
            else: 
                res = func(*args)
        except TimeoutException:
            #self.debug.logger ("Timeout Expired: "+timeout_msg, 2)
            if throw_exp:
                raise TimeoutException
        return res






