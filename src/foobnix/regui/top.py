#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.menu import MenuWidget
from foobnix.regui.all_controls import  VolumeControls
     
from foobnix.helpers.toolbar import ToolbarSeparator
from foobnix.regui.controls.seekbar import SeekProgressBarControls
from foobnix.regui.model.signal import FControl

class TopWidgets(FControl):
    def __init__(self, controls):
        hbox = gtk.HBox(False, 0)
        hbox.show()
        
        self.menu = MenuWidget()
        self.volume = VolumeControls()
        sep = ToolbarSeparator()
        
        hbox.pack_start(self.menu.widget, False, False)
        hbox.pack_start(controls.playback, False, False)
        hbox.pack_start(self.volume.widget, False, False)
        hbox.pack_start(sep, False, False)
        hbox.pack_start(controls.seek_bar, True, True)
        
        self.widget = hbox
        
    def on_save(self):        
        self.volume.on_save()
        
    def on_load(self):
        self.volume.on_load()
