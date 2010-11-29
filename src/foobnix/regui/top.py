#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.helpers.toolbar import ToolbarSeparator
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.regui.menu import MenuBarWidget

class TopWidgets(FControl, LoadSave, gtk.HBox):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.HBox.__init__(self, False, 0)
        
        self.menu = MenuBarWidget(controls)
        sep = ToolbarSeparator()
        
        self.pack_start(self.menu.widget, False, False)
        self.pack_start(controls.playback, False, False)
        self.pack_start(controls.volume, False, False)
        self.pack_start(sep, False, False)
        self.pack_start(controls.seek_bar, True, True)
        
        self.show_all()
        
    def on_save(self):        
        self.controls.volume.on_save()
        self.menu.on_save()
        
    def on_load(self):        
        self.controls.volume.on_load()
        self.menu.on_load()
