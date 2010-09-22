#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.menu import MenuWidget
from foobnix.regui.controls import PlaybackControls, VolumeControls, \
    ToolbarSeparator, SeekProgressBarControls
class TopWidgets():
    def __init__(self):
        hbox = gtk.HBox(False, 0)
        hbox.show()
        
        menu = MenuWidget().widget
        buttons = PlaybackControls().widget
        volume = VolumeControls().widget
        sep = ToolbarSeparator().widget
        seek = SeekProgressBarControls().widget
        
        hbox.pack_start(menu, False, False)
        hbox.pack_start(buttons, False, False)
        hbox.pack_start(volume, False, False)
        hbox.pack_start(sep, False, False)
        hbox.pack_start(seek, True, True)
        
        self.widget = hbox
