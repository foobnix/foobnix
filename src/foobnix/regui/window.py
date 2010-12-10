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
from foobnix.util.key_utils import is_key, is_key_alt
from foobnix.version import FOOBNIX_VERSION
from foobnix.util.const import LEFT_PERSPECTIVE_NAVIGATION, \
    LEFT_PERSPECTIVE_RADIO, LEFT_PERSPECTIVE_VIRTUAL, LEFT_PERSPECTIVE_INFO
class MainWindow(gtk.Window, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.set_title("Foobnix " + FOOBNIX_VERSION)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(True)        
        self.connect("delete-event", self.hide_window)
        self.connect("configure-event", self.on_configure_event)
        self.connect("key-press-event", self.on_key_press)
        self.set_icon(self.controls.trayicon.get_pixbuf())
    
    def on_key_press(self, w, e):
        if is_key(e, 'Escape'):
            self.hide_window()
        elif is_key_alt(e) and is_key(e, "1"):
            self.controls.perspective.activate_perspective_key(LEFT_PERSPECTIVE_NAVIGATION)
        elif is_key_alt(e) and is_key(e, "2"):
            self.controls.perspective.activate_perspective_key(LEFT_PERSPECTIVE_RADIO)
        elif is_key_alt(e) and is_key(e, "3"):
            self.controls.perspective.activate_perspective_key(LEFT_PERSPECTIVE_VIRTUAL)
        elif is_key_alt(e) and is_key(e, "4"):
            self.controls.perspective.activate_perspective_key(LEFT_PERSPECTIVE_INFO)
        
                    
    def on_configure_event(self, w, e):
        FC().main_window_size = [e.x, e.y, e.width, e.height]
        
    def on_save(self, *a):        
        pass
    
    def on_load(self):
        cfg = FC().main_window_size
        if cfg:
            self.resize(cfg[2], cfg[3])            
            self.move(cfg[0], cfg[1])         
   
    def show_hide(self):
        visible = self.get_property('visible')
        if visible:            
            self.hide_window()
        else:
            self.show()
        
    def hide_window(self, *args):
        
        if FC().on_close_window == const.ON_CLOSE_CLOSE:
            self.controls.quit()

        elif FC().on_close_window == const.ON_CLOSE_HIDE:
            self.hide()
            
        elif FC().on_close_window == const.ON_CLOSE_MINIMIZE:
            self.iconify()
        
        return True
