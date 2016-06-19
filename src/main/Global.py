#!/usr/bin/python


#from utilities.Debug import Debug
import imp
import Queue
#import Queue
import enum
import os

if 'nt' == os.name:
    BASE_DIR=os.path.join('E:\\files', 'backups', 'latest_linux_backup', 'cs_web_scanner_proj', 'cs_web_scanner')
else:
    BASE_DIR='/home/yakir/cs_web_scanner_proj/cs_web_scanner/'
    
Debug = imp.load_source('Debug', os.path.join(BASE_DIR, 'src', 'main', 'utilities', 'Debug.py'))

class WorkID(enum.Enum):
    EXIT = 1

class WorkObj:
    def __init__(self, work_id, param = 0):
        self.workID = work_id
        self.param  = param


''' Scratchpad '''
coreRX  = Queue.Queue()
coreMSX = Queue.Queue()
coreISX = Queue.Queue()
global_debug = None
''' ----------'''


def register_debugger(master = False):
    global global_debug
    if None == global_debug:
        global_debug = Debug.Debug()
    return global_debug

def close_debugger():
    global global_debug
    global_debug.close_debugger()

