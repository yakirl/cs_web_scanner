#!/usr/bin/python

''' Profiler:
holds dict: breakpoint -> (num_of_snapshots, total_time)
total_time is the total diffs from the last snapshot. this suppose to measure deltas.
breakpoints order is not important, only order of calling to snapshot()
'''

import time

def curr_time():
    return int(time.time())

class Profiler:

    def __init__(self):
        self.snapshots = {}
        self.lastTime = curr_time()
    
    def snapshot(self, bp):
        currTime = curr_time()
        if bp in  self.snapshots.keys():
            self.snapshots[bp][0] += 1
            self.snapshots[bp][1] += currTime - self.lastTime
        else:
            self.snapshots[bp] = (1, currTime - self.lastTime)
        self.lastTime = currTime

    def print_stats(self):
        sum_total_time = 0
        print('{:>12} | {:>12} | {:>12} | {:>12}}'.format('BP', 'num', 'total_time', 'average'))
        for bp in self.snapshots.keys():
           print('--------------------------------------------------')
           print('{} | {:>12} | {:>12} | {:>12}'.format(bp, self.snapshots[bp][0], self.snapshots[bp][1], (self.snapshots[bp][1]/self.snapshots[bp][0])))
           sum_total_time += self.snapshots[bp][1]
        print('{}'.format(sum_total_time))


