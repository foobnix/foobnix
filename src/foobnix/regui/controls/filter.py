#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.model.signal import FControl
import gtk
from foobnix.regui.state import LoadSave
class FilterControl(gtk.Entry, FControl, LoadSave):
    def __init__(self, controls):
        gtk.Entry.__init__(self)
        FControl.__init__(self, controls)
        self.connect("key-release-event", self.on_filter)
    
    def on_filter(self, w, e):
        value = w.get_text()
        self.controls.filter_tree(value)        
    
    def on_load(self):
        pass
    
    def on_save(self):
        pass
