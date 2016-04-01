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

import sys
from Tkinter import *
from utilities.Debug import Debug
from utilities.Misc  import Misc
from abc import ABCMeta

debug = Debug()

def report_event(event):     ### (5)
	"""Print a description of an event, based on its attributes.
	"""
	event_name = {"2": "KeyPress", "4": "ButtonPress"}
	print("Time:" + str(event.time))
	print("EventType="+str(event.type)+" "+event_name[str(event.type)])
	print("EventWidgetId=" + str(event.widget))
	print("EventKeySymbol=" + str(event.keysym))

CURR_ROW = 0

def get_row(row_ix):
    return row_ix*3

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

### Pages: ###
PAGE_WEB_SCANNER = 'WebScannerPage'
PAGE_WEB_INSPECTOR = 'WebInspectorPage'
PAGE_WEB_INFO = 'InfoPage'

class WebScannerPage():
    def __init__(self, parent_frame, prev_page_name, controller):
        print('WebScannerPageCtor')
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        self.text_title = Text(self.my_frame, font = 5,width = 16, height = 1, bg = DEFAULT_COLOR, highlightbackground = DEFAULT_COLOR)
        self.text_title.grid(row = next_row(4), rowspan = 6,column = get_col(1))
        self.text_title.insert(INSERT, "WebScannerPage\n")
        v = StringVar()
        v.set("L")
        self.radio_scan_db   = Radiobutton(self.my_frame, pady = PADY,  variable = v, text = "scan DB", bg = DEFAULT_COLOR,highlightbackground = DEFAULT_COLOR)
        self.radio_scan_db.  grid(rowspan = 2, row = next_row(1), column = get_col(0), sticky = W)
        self.radio_scan_page = Radiobutton(self.my_frame, pady = PADY, text = "scan page.    Insert URL:", bg = DEFAULT_COLOR,highlightbackground = DEFAULT_COLOR)
        self.radio_scan_page.grid(rowspan = 2, row = next_row(0), column = get_col(0), sticky = W)
        self.radio_scan_db.deselect()    
        self.entry_url = Entry(self.my_frame)
        self.entry_url.grid(ipadx = PADX, columnspan = 4, row = next_row(10), column = get_col(1))
        self.press_start_check = Button(self.my_frame, text = "Start Check", background = "grey")
        self.press_start_check.grid(rowspan = 4,  row = next_row(0), column = get_col(0))
        '''
        self.press_start_check.bind("<Button-1>", self.button1Click) 
        self.press_start_check.bind("<Return>", self.button1Click)
        self.press_info = Button(self.my_frame, text = "Info", background="grey")
        self.press_info.grid(rowspan = 4, row = next_row(0), column = get_col(1))
        self.press_info.bind("<Button-1>", lambda event, arg1 = "EventParam" : self.button2Click(event, arg1))
        '''
        self.press_back = Button(self.my_frame, text = "Back",  background="grey", command = lambda: controller.show_page(prev_page_name))
        self.press_back.grid(rowspan = 10, row = next_row(0), column = get_col(2))

    def raise_me(self):
        self.my_frame.tkraise()
        

class WebInspectorPage():
    def __init__(self, parent_frame, prev_page_name, controller):
        debug.logger('WebInspectorPage Ctor')
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        self.text_title = Text(self.my_frame, font = 5,width = 16, height = 1, bg = DEFAULT_COLOR, highlightbackground = DEFAULT_COLOR)
        self.text_title.grid(row = next_row(4), rowspan = 6,column = get_col(1))
        self.text_title.insert(INSERT, "WebInspectorPage\n")
        v = StringVar()
        v.set("L")
        self.press_start_check = Button(self.my_frame, text = "Start Check", background = "grey")
        self.press_start_check.grid(rowspan = 4,  row = next_row(0), column = get_col(0))
        self.press_info = Button(self.my_frame, text = "Info", background="grey")
        self.press_info.grid(rowspan = 4, row = next_row(0), column = get_col(1))
        self.press_back = Button(self.my_frame, text = "Back",  background="grey", command = lambda: controller.show_page(prev_page_name))
        self.press_back.grid(rowspan = 10, row = next_row(0), column = get_col(2))
    
    def raise_me(self):
        debug.logger('Raising WebInspectorPage')
        self.my_frame.tkraise()


class InfoPage():
    def __init__(self, parent_frame, prev_page_name, controller):
        debug.logger('WebInspectorPage Ctor')
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        self.text_title = Text(self.my_frame, font = 5,width = 16, height = 1, bg = DEFAULT_COLOR, highlightbackground = DEFAULT_COLOR)
        self.text_title.grid(row = next_row(4), rowspan = 6,column = get_col(1))
        self.text_title.insert(INSERT, "InfoPage\n")
        self.press_back = Button(self.my_frame, text = "Back",  background="grey", command = lambda: controller.show_page(prev_page_name))
        self.press_back.grid(rowspan = 10, row = next_row(0), column = get_col(2))
    
    def raise_me(self):
        debug.logger('Raising WebInspectorPage')
        self.my_frame.tkraise()


class MainMenuPage():
    def __init__(self, parent_frame, prev_page_name, controller):
        debug.logger('MainMenuPage Ctor')
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        self.text_title = Text(self.my_frame, font = 5,width = 16, height = 1, bg = DEFAULT_COLOR, highlightbackground = DEFAULT_COLOR)
        self.text_title.grid(row = next_row(4), rowspan = 6,column = get_col(1))
        self.text_title.insert(INSERT, "MainMenuPage\n")
    
        self.menu_buttons = []
        menu_options = [('WebScanner',   lambda arg1 = 'WebScannerPage'  : controller.show_page(arg1)), 
                        ('WebInspector', lambda arg1 = 'WebInspectorPage': controller.show_page(arg1)),
                        ('Info',         lambda arg1 = 'InfoPage'        : controller.show_page(arg1)), 
                        ('Exit',         lambda arg1 = prev_page_name: controller.show_page(arg1))]
        for button_text, button_command in menu_options:
            button = Button(self.my_frame, text = button_text, background = 'grey', command = button_command)
            button.grid()
            self.menu_buttons.append(button)

        #self.press_exit = Button(self.my_frame, text = "Exit",  background="grey", command = lambda: controller.show_page(prev_page_name))
        #self.press_exit.grid(rowspan = 10, row = next_row(0), column = get_col(2))

    def raise_me(self):
        self.my_frame.tkraise()

#class BasePage(metaclass = ABCMeta): pass
        
        
class MainGUI:
    def __init__(self):
        debug.logger('MainGUI Ctor')
        self.root = Tk() # create main root widget
        self.root.wm_title("CS Web Scanner")
        self.pages_names = ['WebScannerPage', 
                            'WebInspectorPage', 
                             
                            'MainMenuPage']
        frames = {}
        self.pages = {}
        for page_name in self.pages_names:
            frames[page_name] = Frame(self.root, bg=DEFAULT_COLOR, height = 500)
            frames[page_name].grid(row = 0, column = 0, rowspan = 3, columnspan = 2, sticky = W+E+N+S,  ipadx = 10, ipady = 17) 
        self.pages['WebScannerPage']     = WebScannerPage  (frames['WebScannerPage'],   'MainMenuPage', self)
        self.pages['WebInspectorPage']   = WebInspectorPage(frames['WebInspectorPage'], 'MainMenuPage', self)
        self.pages['MainMenuPage']       = MainMenuPage    (frames['MainMenuPage'],     None,           self)
        self.show_page('MainMenuPage')
        #self.root.geometry("500x250")
        self.root.mainloop()

    ''' manage pages nevigation: working as frames stack'''
    def show_page(self, page_name):
        if page_name == None:
            debug.logger('Exiting...')
            self.quit_program()
        else:   
            debug.logger('Going to page: '+page_name)
            self.pages[page_name].raise_me()
    
    def quit_program(self):
        # do some killing stuff here
        self.root.destroy()

    def run_gui(self):
        self.root.mainloop()

def main_gui():
    mainGUI = MainGUI()
    mainGUI.run_gui()

'''
def test1():
    for F in (WebScannerPage, WebInspectorPage):
        page_name = F.__name__
        frame = F(1)
        print(page_name)
'''

if __name__ == "__main__":
    #test1()
    main_gui()

