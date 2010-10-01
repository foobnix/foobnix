#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.util import const
class MainWindow(gtk.Window, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.set_title("Foobnix Music Player by assistent")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(True)        
        self.connect("delete-event", self.hide_window)
        self.connect("configure-event", self.on_configure_event)
    
    def on_configure_event(self, w, e):
        FC().main_window_size = [e.x, e.y, e.width, e.height]
        
    def on_save(self, *a):        
        pass
    
    def on_load(self):
        cfg = FC().main_window_size
        if cfg:
            self.set_default_size(cfg[2], cfg[3])            
            self.move(cfg[0], cfg[1])         
            
        
    def hide_window(self, *args):       
        
        if FC().on_close_window == const.ON_CLOSE_CLOSE:
            self.destroy()

        elif FC().on_close_window == const.ON_CLOSE_HIDE:
            self.hide()
            
        elif FC().on_close_window == const.ON_CLOSE_MINIMIZE:
            self.iconify()
        
        return True