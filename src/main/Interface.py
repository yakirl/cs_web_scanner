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

import os
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

class InfoPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        print('InfoPageCtor')
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'Info')
        Label(self.my_frame, text = '''--- Created By Levi Yakir and Amar Samuel ---''', bg = DEFAULT_COLOR, font = 7).grid(columnspan = 10)
        self.press_readme = Button(self.my_frame, text = "README",    background="grey", command = lambda: self.open_readme())
        self.press_back   = Button(self.my_frame, text = "Back",        background="grey", command = lambda: controller.show_page(prev_page_name))
        self.press_readme.grid(padx = 10, pady = 10, row = next_row(0), column = get_col(0))
        self.press_back.  grid(padx = 10, pady = 10, row = next_row(0), column = get_col(1))
        self.my_frame.rowconfigure(1, weight = 10)

    def raise_me(self):
        self.my_frame.tkraise()

    def open_readme(self):
        os.system('%s %s' % (os.getenv('EDITOR'), 'README.md'))

'''
class WebScannerSettingsPage:
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'Web Inspector')
        label_output_loc = Label(parent, text = 'choose location to save output file', bg = DEFAULT_COLOR, highlightbackground = DEFAULT_COLOR)
        self.entry_output_loc = Entry(self.my_frame)
        self.entry_outpu_loc.grid(ipadx = PADX, columnspan = 4, row = next_row(1), column = get_col(1))
 
    def raise_me(self):
        debug.logger('Raising WebInspectorPage')
        self.my_frame.tkraise()
'''


class WebScannerPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        print('WebScannerPageCtor')
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'Web Mapper')
        self.press_start_check = Button(self.my_frame, text = "Start Mapping", background = "grey")
        self.press_settings    = Button(self.my_frame, text = "Settings", background="grey")
        self.press_back        = Button(self.my_frame, text = "Back",     background="grey", command = lambda: controller.show_page(prev_page_name))
        self.my_frame.rowconfigure(1, weight = 10)
        self.press_start_check.grid(pady = 10, padx = 10, row = next_row(0), column = get_col(0), sticky = S)
        self.press_settings.grid   (pady = 10, padx = 10, row = next_row(0), column = get_col(1), sticky = S)
        self.press_back.grid       (pady = 10, padx = 10, row = next_row(0), column = get_col(2), sticky = S)

    def raise_me(self):
        self.my_frame.tkraise()
        

class WebInspectorPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        debug.logger('WebInspectorPage Ctor')
        curr_row = CURR_ROW
        self.my_frame = parent_frame
        set_title(self.my_frame, 'Web Inspector')
        v = StringVar()
        v.set("L")
        self.radio_scan_db     = Radiobutton(self.my_frame, pady = PADY, variable = v, value = 'A', text = "scan DB",                   bg = DEFAULT_COLOR,highlightbackground = DEFAULT_COLOR)
        self.radio_scan_page   = Radiobutton(self.my_frame, pady = PADY, variable = v, value = 'B', text = "scan page.    Insert URL:", bg = DEFAULT_COLOR,highlightbackground = DEFAULT_COLOR)
        self.entry_url         = Entry(self.my_frame)
        self.press_start_check = Button(self.my_frame, text = "Start Check", background = "grey")
        self.press_settings    = Button(self.my_frame, text = "Settings",    background = "grey")
        self.press_back        = Button(self.my_frame, text = "Back",        background="grey", command = lambda: controller.show_page(prev_page_name))
        #self.radio_scan_db.deselect()    
        next_row(1)
        self.my_frame.rowconfigure(2, weight = 3)
        self.radio_scan_db.    grid(row = next_row(1), column = get_col(0), sticky = W+N)
        self.radio_scan_page.  grid(row = next_row(0), column = get_col(0), sticky = W+N)
        self.entry_url.        grid(padx = 6, ipadx = PADX, columnspan = 4, row = next_row(1), column = get_col(1))
        self.press_start_check.grid(pady = 6, row = next_row(0), column = get_col(0), sticky = S)
        self.press_settings.   grid(pady = 6, row = next_row(0), column = get_col(1), sticky = S)
        self.press_back.       grid(pady = 6, row = next_row(0), column = get_col(2), sticky = S)
 
    def raise_me(self):
        debug.logger('Raising WebInspectorPage')
        self.my_frame.tkraise()



class MainMenuPage:
    def __init__(self, parent_frame, prev_page_name, controller):
        debug.logger('MainMenuPage Ctor')
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

#class BasePage(metaclass = ABCMeta): pass
        
        
class MainGUI:
    def __init__(self):
        debug.logger('MainGUI Ctor')
        self.root = Tk() # create main root widget
        self.root.wm_title("CS Web Scanner")
        self.pages = {}
        for page_class in (MainMenuPage, WebScannerPage, WebInspectorPage, InfoPage):
            page_name = page_class.__name__
            frame = Frame(self.root, bg=DEFAULT_COLOR, height = 500)
            frame.grid(row = 0, column = 0, rowspan = 3, columnspan = 2, sticky = W+E+N+S,  ipadx = 10, ipady = 17) 
            frame.columnconfigure(0, weight = 1)
            self.pages[page_name] = page_class(frame, self.get_prev_page_name(page_name), self)
        self.show_page('MainMenuPage')
        self.root.mainloop()

    def get_prev_page_name(self, page_name):
        switcher = {
            'MainMenuPage'     : None,
            'WebScannerPage'   : 'MainMenuPage',
            'WebInspectorPage' : 'MainMenuPage',
            'InfoPage'         : 'MainMenuPage',
        }
        return switcher[page_name]

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

