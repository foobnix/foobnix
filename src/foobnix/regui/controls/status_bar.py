#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: ivan
'''
from foobnix.regui.model.signal import FControl
from gi.repository import Gtk
from gi.repository import GObject

class StatusbarControls(Gtk.Statusbar, FControl):
    def __init__(self, controls):
        Gtk.Statusbar.__init__(self)
        FControl.__init__(self, controls)
        self.show()
        self.get_children()[0].set_shadow_type(Gtk.ShadowType.NONE)

    def set_text(self, text):
        def set_text_task():
            if text:
                self.push(0, text)
            else:
                self.push(0, "")
        GObject.idle_add(set_text_task)
    
