#!/usr/bin/python

''' Profiler:
holds dict: breakpoint -> (num_of_snapshots, total_time)
total_time is the total diffs from the last snapshot. this suppose to measure deltas.
breakpoints order is not important, only order of calling to snapshot()
'''

import time
from Global import *


def curr_time():
    return int(time.time())

class Profiler:

    def __init__(self):
        self.debug = register_debugger()
        self.snapshots = {}
        self.lastTime = curr_time()
    
    def snapshot(self, bp):
        currTime = curr_time()
        if bp in  self.snapshots.keys():
            self.snapshots[bp][0] += 1
            self.snapshots[bp][1] += currTime - self.lastTime
        else:
            self.snapshots[bp] = [1, currTime - self.lastTime]
        self.lastTime = currTime

    def print_stats(self):
        sum_total_time = 0
        self.debug.logger('\n')
        self.debug.logger('{:<16} | {:<16} | {:<16} | {:<16}'.format('BP', 'num', 'total_time(sec)', 'average(sec)'))
        for bp in self.snapshots.keys():
           self.debug.logger('--------------------------------------------------------------------------')
           self.debug.logger('{:<16} | {:>16} | {:>16} | {:>16}'.format(bp, self.snapshots[bp][0], self.snapshots[bp][1], (float(self.snapshots[bp][1])/self.snapshots[bp][0])))
           sum_total_time += self.snapshots[bp][1]
        self.debug.logger('--------------------------------------------------------------------------')
        self.debug.logger('{:<16} | {:>35}'.format('Total', sum_total_time))
