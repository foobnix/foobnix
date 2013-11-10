#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: ivan
'''
from gi.repository import Gtk
from gi.repository import GObject
from foobnix.util import idle_task
from foobnix.gui.model.signal import FControl


class StatusbarControls(Gtk.Statusbar, FControl):
    def __init__(self, controls):
        Gtk.Statusbar.__init__(self)
        FControl.__init__(self, controls)
        self.show()
        self.get_children()[0].set_shadow_type(Gtk.ShadowType.NONE)

    @idle_task
    def set_text(self, text):
        if text:
            self.push(0, text)
        else:
            self.push(0, "")

