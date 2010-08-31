#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util import const
from foobnix.util.configuration import FConfiguration

class TryIconConfig(ConfigPlugin):
    
    name = _("Try Icon")
    
    def __init__(self, try_icon):
        self.try_icon = try_icon
        print "Create try icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        self.try_icon_button = gtk.CheckButton(label=_("Show try icon"), use_underline=True)
        self.try_icon_button.connect("clicked", self.on_show_try_icon)
        self.try_icon_button.show()
        
        self.close_button = gtk.RadioButton(None, label=_("On close window - close player"))
        self.close_button.show()
        
        self.hide_button = gtk.RadioButton(self.close_button, label=_("On close window - hide player"))
        self.hide_button.connect("toggled", self.on_show_try_icon)
        self.hide_button.show()
        
        self.minimize_button = gtk.RadioButton(self.close_button, label=_("On close window - minimize player"))
        self.minimize_button.show()
        
        box.pack_start(self.try_icon_button, False, True, 0)
        box.pack_start(self.close_button, False, True, 0)
        box.pack_start(self.hide_button, False, True, 0)
        box.pack_start(self.minimize_button, False, True, 0)
        
        self.widget = box

    
    def on_show_try_icon(self, *args):
        print "action" , self.try_icon_button.get_active()
        if not self.try_icon_button.get_active():
            self.hide_button.set_sensitive(False) 
            if self.hide_button.get_active():
                self.minimize_button.set_active(True)
            self.try_icon.hide()
        else:
            self.try_icon.show()
            self.hide_button.set_sensitive(True)
            
    def on_load(self):
        self.try_icon_button.set_active(FConfiguration().show_try_icon)
        
        if FConfiguration().on_close_window == const.ON_CLOSE_CLOSE:
            self.close_button.set_active(True)
            
        elif FConfiguration().on_close_window == const.ON_CLOSE_HIDE:
            self.hide_button.set_active(True)
            
        elif FConfiguration().on_close_window == const.ON_CLOSE_MINIMIZE:
            self.minimize_button.set_active(True)
        
    def on_save(self):
        FConfiguration().show_try_icon = self.try_icon_button.get_active() 
        
        if  self.close_button.get_active():
            FConfiguration().on_close_window = const.ON_CLOSE_CLOSE
        
        elif self.hide_button.get_active():
            FConfiguration().on_close_window = const.ON_CLOSE_HIDE
        
        elif self.minimize_button.get_active():
            FConfiguration().on_close_window = const.ON_CLOSE_MINIMIZE
