#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.menu import MenuWidget
from foobnix.regui.all_controls import PlaybackControls, VolumeControls, \
    ToolbarSeparator, SeekProgressBarControls

class TopWidgets():
    def __init__(self):
        hbox = gtk.HBox(False, 0)
        hbox.show()
        
        self.menu = MenuWidget()
        buttons = PlaybackControls().widget
        self.volume = VolumeControls()
        sep = ToolbarSeparator().widget
        seek = SeekProgressBarControls().widget
        
        hbox.pack_start(self.menu.widget, False, False)
        hbox.pack_start(buttons, False, False)
        hbox.pack_start(self.volume.widget, False, False)
        hbox.pack_start(sep, False, False)
        hbox.pack_start(seek, True, True)
        
        self.widget = hbox
        
    def on_save(self):        
        self.volume.on_save()
        
    def on_load(self):
        self.volume.on_load()
