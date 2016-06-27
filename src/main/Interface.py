# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 00:53:11 2016

@author: yakir
"""

'''
**************    Python Tkinter GUI package    ***************************

Tkinter is the standard packsge for Python GUI.
Pointers:
    - 3 main comonents: appeareance (widget), type of event and behaviour (event handler)
    - root == top. contains instance of Tk. main class for gui.
    - general GUI structure: Tk class, contains Containers (Frames etc), which contain widgets (buttons etc)

***************************************************************************
'''

'''
*********** Modules Design *******************
Because Threading in Python == Garbage, we owe to implement the GUI module as main thread.
all the thread managing going here.
'''

import os
import sys
import argparse
from multiprocessing import Queue
import threading
from enum import Enum
from Global import *
from Tkinter import *
from utilities.Debug import Debug
from utilities.Misc  import Misc
from utilities.Misc  import TimeoutException
import WebMapper
import WebInspector
import Interface

inQ           = coreRX
mapperOutQ    = coreMSX
InspectorOutQ = coreISX

DEFAULT_DEBUG_MOD=0
PROGRAM_LOCK=1
PROGRAM_LOCK_FILE=os.path.join('system', 'program_lock')
INTERFACE_GUI = 'GUI'
INTERFACE_CLI = 'CLI'
OP_INSPECT = 'INSPECT'
OP_MAP     = 'MAP'


''' Configurable '''
REFRESH_TIME = 4000
MAPPING_OUTPUT_DIR  = os.path.join(BASE_DIR, 'data', 'mapper')
MAPPING_OUTPUT_FILE = os.path.join(MAPPING_OUTPUT_DIR, 'mapper_pages.txt')
INSPECTOR_DB_DIR     = os.path.join(BASE_DIR, 'data', 'reports')
INSPECTOR_INPUT_FILE = MAPPING_OUTPUT_FILE


README_FILE = os.path.join(BASE_DIR, 'README.md')
# default values (configurable via parameters):
MAPPING_BASE_URL    = 'cs.technion.ac.il/'
MAPPING_START_ADDR  = 'http://'+MAPPING_BASE_URL
MAPPING_EXE_INTVL   = 0 # 0 - run once. else - run every interval


CURR_ROW = 0

def get_row(row_ix):
    return row_ix

def next_row(skip):
    global CURR_ROW
    ret_row = get_row(CURR_ROW)
    CURR_ROW += skip
    return ret_row

def get_col(col_ix):
    return col_ix*3

DEFAULT_COLOR = "cyan"
PADX = 40
PADY = 10

'''
### Pages Managing: ###
In order to add new page, do the following:
* define new class with __init__ and raise_me methods, following given declarations of other pages
* add class to MainGUI page_calss loop
* add to MainGUI get_prev_page_name method with the page's ancestor
'''

def set_title(parent, _text):
    Label(parent, font = 5, text = _text, bg = DEFAULT_COLOR, highlightbackground = DEFAULT_COLOR).grid(pady = 5, columnspan = 10) # large columnspan to cetner the title
    next_row(1)

class GenericPopUp:
    def __init__(self, parent, message):
        self.debug = register_debugger()
        self.debug.logger('GenericToplevel Ctor')
        self.parent     = parent
        self.my_window  = Toplevel(self.parent)
        my_frame        = Frame(self.my_window)
        label_message   = Label(my_frame, text = message)
        press_ok        = Button(my_frame, text = 'ok', command = self.close_window)
        label_message.grid()
        press_ok.grid()
        my_frame.grid()

    def close_window(self):
        self.my_window.destroy()


class InfoPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'Info')
        Label(self.my_frame, text = '''--- Created By Levi Yakir and Amar Samuel ---''', bg = DEFAULT_COLOR, font = 7).grid(columnspan = 10)
        self.press_readme = Button(self.my_frame, text = "README", background="grey", command = lambda: self.open_readme())
        self.press_back   = Button(self.my_frame, text = "Back",   background="grey", command = lambda: controller.show_page(prev_page_name))
        self.press_readme.grid(padx = 10, pady = 10, row = next_row(0), column = get_col(0))
        self.press_back.  grid(padx = 10, pady = 10, row = next_row(0), column = get_col(1))
        self.my_frame.rowconfigure(1, weight = 10)

    def raise_me(self):
        self.my_frame.tkraise()

    def open_readme(self):
        os.system('%s %s &' % ('gedit', README_FILE))


class ScannerSettingsPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'Web Mapper Settings')

        self.label_url_desc  = Label(self.my_frame,  text = 'domain name to scan:')
        self.entry_url       = Entry(self.my_frame)
        self.entry_url.insert(0, MAPPING_BASE_URL)
        self.label_intv_desc = Label(self.my_frame,  text = 'interval in minutes. legal values: '+str(WebMapper.EXE_INTV_MIN)+' to '+str(WebMapper.EXE_INTV_MAX)+'.  0 for single run')
        self.entry_interval  = Entry(self.my_frame)
        self.entry_interval.insert(0, MAPPING_EXE_INTVL)
        self.press_apply     = Button(self.my_frame, text = "Apply", background = "grey", command = lambda: controller.config_mapper())
        self.press_back      = Button(self.my_frame, text = "Back",  background = "grey", command = lambda: controller.show_page(prev_page_name))

        #self.my_frame.rowconfigure(1, weight = 10)
        #self.my_frame.rowconfigure(2, weight = 3)
        self.label_url_desc. grid(pady = 5, row = next_row(0), sticky = S)
        self.entry_url.      grid(pady = 5, padx = 10, row = next_row(0), column = get_col(1), sticky = S)
        next_row(1)
        self.label_intv_desc.grid()
        self.entry_interval. grid(pady = 5, padx = 10, row = next_row(0), column = get_col(1), sticky = S)
        next_row(1)
        self.press_apply.    grid(pady = 5, padx = 10, row = next_row(0), column = get_col(0), sticky = S)
        self.press_back.     grid(pady = 5, padx = 10, row = next_row(0), column = get_col(1), sticky = S)

    def raise_me(self):
        self.my_frame.tkraise()


class WebScannerPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        self.controller = controller
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'WebMapper')
        self.label_state       = Label (self.my_frame, text = 'State: Idle',   background = DEFAULT_COLOR, font = 7)
        self.press_start_check = Button(self.my_frame, text = "Start Mapping", background = "grey",                   command = lambda arg1 = 1, arg2 = 'mapper': controller.start_stop_module(arg1, arg2))
        self.press_stop_check  = Button(self.my_frame, text = "Stop  Mapping", background = "grey", state = DISABLED, command = lambda arg1 = 0, arg2 = 'mapper': controller.start_stop_module(arg1, arg2))
        self.press_settings    = Button(self.my_frame, text = "Settings",      background = "grey",                   command = lambda: controller.show_page('ScannerSettingsPage'))
        self.press_back        = Button(self.my_frame, text = "Back",          background = "grey",                   command = lambda: controller.show_page(prev_page_name))
        self.my_frame.rowconfigure(1, weight = 10)
        self.label_state.      grid(columnspan = 10)
        self.press_start_check.grid(pady = 10, padx = 10, row = next_row(0), column = get_col(0), sticky = S)
        self.press_stop_check. grid(pady = 10, padx = 10, row = next_row(0), column = get_col(1), sticky = S)
        self.press_settings.   grid(pady = 10, padx = 10, row = next_row(0), column = get_col(2), sticky = S)
        self.press_back.       grid(pady = 10, padx = 10, row = next_row(0), column = get_col(3), sticky = S)

    def raise_me(self):
        self.my_frame.tkraise()


class WebInspectorPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        self.debug = register_debugger()
        self.debug.logger('WebInspectorPage Ctor')
        self.controller = controller
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'WebInpsector')
        self.label_state       = Label (self.my_frame, text = 'State: Idle',   background = DEFAULT_COLOR, font = 7)
        self.press_start_check = Button(self.my_frame, text = "Start Inspector", background = "grey",                   command = lambda arg1 = 1, arg2 = 'inspector': controller.start_stop_module(arg1, arg2))
        self.press_stop_check  = Button(self.my_frame, text = "Stop  Inspector", background = "grey", state = DISABLED, command = lambda arg1 = 0, arg2 = 'inspector': controller.start_stop_module(arg1, arg2))
        self.press_back        = Button(self.my_frame, text = "Back",            background = "grey",                   command = lambda: controller.show_page(prev_page_name))
        self.my_frame.rowconfigure(1, weight = 10)
        self.label_state.      grid(columnspan = 10)
        self.press_start_check.grid(pady = 10, padx = 10, row = next_row(0), column = get_col(0), sticky = S)
        self.press_stop_check. grid(pady = 10, padx = 10, row = next_row(0), column = get_col(1), sticky = S)
        self.press_back.       grid(pady = 10, padx = 10, row = next_row(0), column = get_col(3), sticky = S)


        # curr_row = CURR_ROW
        # self.my_frame = parent_frame
        # set_title(self.my_frame, 'Web Inspector')

        # self.label_state       = Label (self.my_frame, text = 'State: Idle',   background = DEFAULT_COLOR, font = 7)

        # self.press_start_check = Button(self.my_frame, text = "Start Inspector", background = "grey",                   command = lambda arg1 = 1, arg2 = 'inspector': controller.start_stop_module(arg1, arg2))
        # self.press_stop_check  = Button(self.my_frame, text = "Stop  Inspector", background = "grey", state = DISABLED, command = lambda arg1 = 0, arg2 = 'inspector': controller.start_stop_module(arg1, arg2))
        # self.press_back        = Button(self.my_frame, text = "Back",        background = "grey", command = lambda: controller.show_page(prev_page_name))


        # self.my_frame.rowconfigure(2, weight = 3)

        # self.label_state.      grid(columnspan = 10)
        # next_row(1)
        # self.press_start_check.grid(pady = 6, row = next_row(0), column = get_col(0), sticky = S)
        # self.press_stop_check. grid(pady = 6, row = next_row(0), column = get_col(1), sticky = S)
        # self.press_back.       grid(pady = 6, row = next_row(0), column = get_col(2), sticky = S)

    def raise_me(self):
        self.debug.logger('Raising WebInspectorPage')
        self.my_frame.tkraise()



class MainMenuPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        self.debug = register_debugger()
        self.debug.logger('MainMenuPage Ctor')
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'Main Menu')
        self.menu_buttons = []
        menu_options = [('WebScanner',   lambda arg1 = 'WebScannerPage'  : controller.show_page(arg1)),
                        ('WebInspector', lambda arg1 = 'WebInspectorPage': controller.show_page(arg1)),
                        ('Info',         lambda arg1 = 'InfoPage'        : controller.show_page(arg1)),
                        ('Exit',         lambda arg1 = prev_page_name:     controller.show_page(arg1))]
        for button_text, button_command in menu_options:
            button = Button(self.my_frame, text = button_text, background = 'grey', command = button_command)
            button.grid(pady= 3, padx = 100,sticky = W+E+N+S)
            self.menu_buttons.append(button)

        #self.press_exit = Button(self.my_frame, text = "Exit",  background="grey", command = lambda: controller.show_page(prev_page_name))
        #self.press_exit.grid(rowspan = 10, row = next_row(0), column = get_col(2))

    def raise_me(self):
        self.my_frame.tkraise()

Threads = ['mapper', 'inspector']

class MainGUI:
    def __init__(self):
        self.debug = register_debugger()
        self.debug.logger('MainGUI Ctor')
        self.root = Tk() # create main root widget
        self.root.wm_title("CS Web Scanner")
        self.pages = {}
        for page_class in (MainMenuPage, WebScannerPage, WebInspectorPage, InfoPage, ScannerSettingsPage):
            page_name = page_class.__name__
            frame = Frame(self.root, bg=DEFAULT_COLOR, height = 500)
            frame.grid(row = 0, column = 0, rowspan = 3, columnspan = 2, sticky = W+E+N+S,  ipadx = 10, ipady = 17)
            frame.columnconfigure(0, weight = 1)
            self.pages[page_name] = page_class(frame, self.get_prev_page_name(page_name), self)
        self.show_page('MainMenuPage')
        self.threads = {}
        self.outQs   = {}
        self.outQs['mapper'] = mapperOutQ
        #self._exit  = 0

    def get_prev_page_name(self, page_name):
        switcher = {
            'MainMenuPage'         : None,
            'WebScannerPage'       : 'MainMenuPage',
            'WebInspectorPage'     : 'MainMenuPage',
            'InfoPage'             : 'MainMenuPage',
            'ScannerSettingsPage'  : 'WebScannerPage',
        }
        return switcher[page_name]

    ''' manage pages navigation: working as frames stack'''
    def show_page(self, page_name):
        if page_name == None:
            self.debug.logger('show_page: about to Exit...')
            if self.some_thread_exists():
                GenericPopUp(self.root, 'cannot exit while process is running!')
            else:
                self.exit_program()
        else:
            self.debug.logger('Going to page: '+page_name)
            self.pages[page_name].raise_me()

    def some_thread_exists(self):
        one_live = False
        for thread in Threads:
            one_live = one_live or self.thread_exists(thread)
        return one_live

    def thread_exists(self, thread_name):
        return (thread_name in self.threads.keys()) #and (self.threads[thread_name].is_alive())

    def exit_program(self):
        self.debug.logger('exit_program:')
        for thread_name in Threads:
            if self.thread_exists(thread_name):
                self.outQs[thread_name].put(WorkObj(WorkID.EXIT, 2))
                self.threads[thread_name].join()
        self.root.destroy()

    def config_mapper(self):
        page = self.pages['ScannerSettingsPage']
        interval = int(page.entry_interval.get())
        url      = page.entry_url.get()
        try:
           self.webMapper.config(interval, url, MAPPING_OUTPUT_DIR, MAPPING_OUTPUT_FILE)
        except ValueError:
           GenericPopUp(self.root, 'bad value!')

    ''' Start or Stop module immediately '''
    def start_stop_module(self, start_stop_, module_name):
        self.debug.assrt((not self.thread_exists(module_name)) == start_stop_, 'start_'+module_name+': process already running!' if start_stop_ else 'stop_'+module_name+': process is not running!')
        if  start_stop_:
            if module_name == 'mapper':
                self.threads[module_name] = threading.Thread(target = self.webMapper.start_mapping)
            else:
                self.threads[module_name] = threading.Thread(target = self.webInspector.url_scan)
            self.threads[module_name].start()
        else:
            self.outQs[module_name].put(WorkObj(WorkID.EXIT, 2))
            self.debug.logger('Interface put exit of type 2 in Queue to '+module_name)
            GenericPopUp(self.root, module_name+' will stop now!')

        page_name = 'WebScannerPage' if ('mapper' == module_name) else 'WebInspectorPage'
        page = self.pages[page_name]
        if start_stop_:
            page.press_start_check.config(state = DISABLED)
            page.press_stop_check. config(state = NORMAL)
        else:
            page.press_start_check.config(state = NORMAL)
            page.press_stop_check. config(state = DISABLED)
        message = 'State: Working' if start_stop_ else 'State: Idle'
        page.label_state.      config(text = message)

        if 'mapper' == module_name:
            page = self.pages['ScannerSettingsPage']
            if start_stop_:
                page.entry_interval.config(state = 'readonly')
                page.press_apply.config(state = DISABLED)
            else:
                page.entry_interval.config(state = NORMAL)
                page.press_apply.config(state = NORMAL)

    def module_stopped(self, module_name):
        self.debug.logger('Interface.module_stopped:')
        page_name = 'WebScannerPage' if ('mapper' == module_name) else 'WebInspectorPage'
        page = self.pages[page_name]
        page.press_start_check.config(state = NORMAL)
        page.label_state.      config(text = 'State: Idle')

        if 'mapper' == module_name:
            page = self.pages['ScannerSettingsPage']
            page.entry_interval.config(state = NORMAL)
            page.press_apply.config(state = NORMAL)

        GenericPopUp(self.root, module_name+' Done!')

    def refresh(self):
        #self.debug.logger('GUI refresh:')
        if self.thread_exists('mapper'):
            self.threads['mapper'].join(0.1)
            if not self.threads['mapper'].isAlive():
                self.module_stopped('mapper')
                del self.threads['mapper']
        if self.thread_exists('inspector'):
            self.threads['inspector'].join(0.1)
            if not self.threads['inspector'].isAlive():
                self.module_stopped('inspector')
                del self.threads['inspector']
        self.root.after(REFRESH_TIME, self.refresh)

    def mainloop(self):
        self.refresh()
        self.root.mainloop()

    def run_gui(self):
        self.webMapper    = WebMapper.WebMapper()
        self.webMapper.   config(MAPPING_EXE_INTVL, MAPPING_BASE_URL, MAPPING_OUTPUT_DIR, MAPPING_OUTPUT_FILE)
        self.webInspector = WebInspector.WebInspector()
        self.webInspector.config(INSPECTOR_INPUT_FILE, INSPECTOR_DB_DIR)
        self.mainloop()

    def run_gui_wrapper(self):
        try:
            self.run_gui()
        except:
            self.debug.logger('run_gui: got expcetion: '+str(sys.exc_info()[0]))
            self.exit_program()
            raise

class Core:
    def __init__(self, interface, op, url):
        self.debug = register_debugger()
        self.debug.logger('Core init: interface='+interface+'. op='+op+'. url='+url)
        self.interface = interface
        self.op        = op
        self.url       = url

    '''
    def start_mapping(self, cont_mode = False):
        self.threads['mapper'] = threading.Thread(target = webMapper.start_mapping, args=())
        self.threads['mapper'].start()

    def stop_mapping(self):
        workObj = WorkObj(EXIT)
        outQs['mapper'].put(workObj)
    '''

    '''
    Params:
        exit_type: 1 - exit. 2 - immediate_exit
    '''
    def exit_core(self, exit_type):
        nothing = 0

    def execute(self):
        try:
            self.debug.logger('Core execute'+self.op)
            if self.op == OP_MAP:
                self.debug.logger('creating mapper')
                self.webMapper = WebMapper.WebMapper()
                self.webMapper.config(MAPPING_EXE_INTVL, self.url, MAPPING_OUTPUT_DIR, MAPPING_OUTPUT_FILE)
                self.webMapper.start_mapping()
            else: # OP_INSPECT
                self.debug.logger('execute_inspector')
                self.webInspector = WebInspector.WebInspector()
                self.webInspector.config(INSPECTOR_INPUT_FILE, INSPECTOR_DB_DIR)
                self.webInspector.url_scan()
        except:
            self.exit_core(1)
            raise


def main_core(interface = INTERFACE_GUI, operation = OP_MAP, url= MAPPING_BASE_URL):
    debug = register_debugger()
    debug.logger('main_core: '+operation+' '+MAPPING_BASE_URL)
    if INTERFACE_GUI == interface:
        mainGUI = MainGUI()
        mainGUI.run_gui()
    else:
        core = Core(interface, operation, url)
        core.execute()

def arg_parsing():
    parser = argparse.ArgumentParser(description='CS WebScanner')
    parser.add_argument('--intf', nargs=1, choices=['GUI', 'CLI'],    help='interface. default is GUI')
    parser.add_argument('--op',   nargs=1, choices=['INSPECT','MAP'], help='''operation: available only for CLI mode. INSPECT: check content accessibility. MAP: map urls''')
    parser.add_argument('--url',  nargs=1,                            help='the accessibility checker will check all addresses in this domain (available only when op=INSPECT). Default is cs.technion.ac.il')
    parser.add_argument('--debug_mod', nargs=1, choices=['0', '1', '2', '3', '4'],  help='debug_mod: 0 - debug. 1 - info. 2 - warnings. 3 - errors. 4 - silent')
    args = parser.parse_args()
    interface = args.intf[0]  if args.intf   is not None else INTERFACE_GUI
    operation = args.op[0]    if args.op     is not None else OP_MAP
    url       = args.url[0]   if args.url    is not None else MAPPING_BASE_URL
    debug_mod = args.debug_mod[0] if args.debug_mod  is not None else DEFAULT_DEBUG_MOD
    #self.debug.logger(str(type(args.op)))
    return (interface, operation, url, int(debug_mod))

def program_lock_unlock(lock_unlock_):
    #self.debug.logger('program_lock_unlock: lock_unlock_='+str(lock_unlock_))
    if PROGRAM_LOCK == 0:
        return 1
    is_locked = os.path.isfile(PROGRAM_LOCK_FILE)
    if lock_unlock_ == 1 and is_locked:
        return 0
    elif lock_unlock_ == 1:
        f = open(PROGRAM_LOCK_FILE, 'w')
        f.close()
    else:
        os.remove(PROGRAM_LOCK_FILE)
    return 1

if "__main__" == __name__:
    debug = register_debugger(master = True)
    #debug.assrt(program_lock_unlock(1), 'there is already running instance of this program! (to force start, remove system/lock file. on your responsibility)')
    try:
        (interface, operation, url, debug_mod) = arg_parsing()
        if debug_mod != None:
            debug.change_mod(debug_mod)
        main_core(interface, operation, url)
    except:
        #program_lock_unlock(0)
        close_debugger()
        raise
    #program_lock_unlock(0)

