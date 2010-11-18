#-*- coding: utf-8 -*-
'''
Created on 27 окт. 2010

@author: ivan
'''
import gtk
from foobnix.util.key_utils import is_key
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.util.const import ICON_FOOBNIX

class ChildTopWindow(gtk.Window):
    def __init__(self, title=None, width=None, height=None):         
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title(title)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)
        self.set_border_width(5)
        try:
            self.set_icon_from_file (self.get_fobnix_logo())
        except TypeError: pass
        if width and height:
            self.set_size_request(width, height)
        self.connect("delete-event", self.hide_window)
        self.connect("key-press-event", self.on_key_press)
    
    def get_fobnix_logo(self):
        return get_foobnix_resourse_path_by_name(ICON_FOOBNIX)
    
    def on_key_press(self, w, e):
        if is_key(e, 'Escape'):
            self.hide()
    
    def hide_window(self, *a):
        self.hide()
        return True
    
    def show(self):
        self.show_all()
