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
    - root == top.contains instance of Tk. main class for gui.
    - general GUI structure: Tk class, contains Containers (Frames etc), which contain widgets (buttons etc)

***************************************************************************
'''


import sys
from tkinter import *



def report_event(event):     ### (5)
	"""Print a description of an event, based on its attributes.
	"""
	event_name = {"2": "KeyPress", "4": "ButtonPress"}
	print("Time:" + str(event.time))
	print("EventType="+str(event.type)+" "+event_name[str(event.type)])
	print("EventWidgetId=" + str(event.widget))
	print("EventKeySymbol=" + str(event.keysym))


class MyApp:
    def __init__(self, parent):
        self.myParent = parent
        self.myContainer1 = Frame(parent, width=300, height=500, bg="white") # create some container into root
        self.myContainer1.pack(ipadx="50m", ipady="50m", side=TOP) # setting up visual relationship to parent


        self.button1 = Button(self.myContainer1, width=20, height=3)
        self.button1["text"] = "First"
        self.button1["background"] = "green"
        self.button1.pack(side=BOTTOM)
        self.button1.bind("<Button-1>", self.button1Click) # bind as event binding
        self.button1.bind("<Return>", self.button1Click)

        self.button2 = Button(self.myContainer1, text = "Second", background="cyan")
        self.button2.pack(side=LEFT)
        self.button2.bind("<Button-1>", lambda event, arg1 = "EventParam" : self.button2Click(event, arg1))

        self.button3 = Button(self.myContainer1, text = "Third", background="red", command = lambda arg1="CommandParam" : self.button3Click(arg1))# bind this button as command binding. wait for press and release
        self.button3.pack(side=RIGHT)


    def button1Click(self, event):
        report_event(event)
        if self.button1["background"] == "green":
            self.button1["background"] = "yellow"
        else:
            self.button1["background"] = "green"

    def button2Click(self, event, eventParam):
        print("button3Click: event binding: param="+eventParam)
        report_event(event)
        self.myParent.destroy()

    def button3Click(self, commandParam):
        print("button3Click: command binding: param="+commandParam)
        #self.myParent.destroy()


def test1():
    root = Tk() # cretae main root widget
    root.wm_title("My Program")
    myApp = MyApp(root)
    root.geometry("800x600")
    root.mainloop()

def main_gui():
    test1()
    #test2()
