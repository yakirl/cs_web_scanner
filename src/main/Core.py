#!/usr/bin/python

import sys
import argparse
import Queue
import Threading
import WebMapper
#import WebInspector
from enum import Enum

INTERFACE_GUI = 0
INTERFACE_CLI = 1

OP_INSPECT = 0
OP_MAP     = 1


MAPPING_OUTPUT_FILE = 'output/mapping.txt'
MAPPING_START_ADDR  = 'http://www.cs.technion.ac.il/'
MAPPING_BASE_URL    = 'cs.technion'
MAPPING_EXE_INTVL   = 60


incomingQ     = Queue.Queue(maxsize = 0)
interfaceOutQ = Queue.Queue(maxsize = 0)
inspectorOutQ = Queue.Queue(maxsize = 0)
mapperOutQ    = Queue.Queue(maxsize = 0)

class WorkID(Enum):
    GUI_EXIT,
    GUI_START_MAPPER,
    INSPECTOR_STOPPED,

class WorkObj:
    def __init(self, func_in, *args, **kwargs):
        self.input_block = kwargs


class Core:
    def __init__(self):
        webMapper    = WebMapper.WebMapper()
        webInspector = WebInspector.WebInspector()

    def start_mapping(self, cont_mode = False):
        webMapper.start_mapping(cont_mode)

    def config_web_mapper(self, output_dir = MAPPING_OUTPUT_FILE, start_addr = MAPPING_START_ADDR, base_url = MAPPING_BASE_URL, executions_interval = MAPPING_EXE_INTVL):
        webMapper.config(ouput_dir, start_addr, base_url, execution_interval)

    def execute_inspector(self):
        debug.logger('execute_inspector')
        #webInspector = WebInspector.WebInspector()
        #webInspector.execute_inspector()

    def config_web_inspector(self, input_file = INSPECTOR_INPUT_FILE, db_dir = INSPECTOR_DB_DIR): 
        debug.logger('config_web_inspector')
        #webInspector.config(input_file, db_dir)

    def interface_manager(self):

    def main_loop(self):
        while True:
            workObj = incomingQ.get()
            switcher = {
                WorkID.EXIT:
                WorkID.CONFIG_WEB_INSPECTOR: self.config_web_inspector()

            incomingQ.task_done()


    def execute(self):
        if INTERFACE_GUI == self.interface:
            self.gui_thread = Threading.Thread(target = Interface.main_gui)
            self.gui_thread.start()
            self.main_loop()
        else:
            if 

def main_core(interface = INTERFACE_GUI, operation = None, url= None):
    #debug.assrt(((interface = INTERFACE_GUI) and (operation == None) and ())
    core = Core(interface, operation, url)
    core.execute()

def parse_args(*args)
    #parser = argparse.ArgumentParser(description='WebMapper / WebInspector')
    #TODO
    interface = INTERFACE_GUI
    operation = None
    url       = None
    return 

if "__main__" == __name__:
    interface, operation, url = parse_args(*sys.argv)
    main_core(interface, operation, url)


