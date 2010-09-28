#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util.fc import FC
from foobnix.regui.state import LoadSave

class StatusbarControls():
    def __init__(self):
        statusbar = gtk.Statusbar()
        statusbar.show()
        
        self.widget = statusbar

