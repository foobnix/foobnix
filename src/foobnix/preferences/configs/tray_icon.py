#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util import const
from foobnix.util.configuration import FConfiguration

class TrayIconConfig(ConfigPlugin):
    
    name = _("Tray Icon")
    
    def __init__(self, controls):
        
        print "Create tray icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        self.tray_icon_button = gtk.CheckButton(label=_("Show tray icon"), use_underline=True)
        self.tray_icon_button.connect("clicked", self.on_show_tray_icon)
        self.tray_icon_button.show()
        
        self.close_button = gtk.RadioButton(None, label=_("On close window - close player"))
        self.close_button.show()
        
        self.hide_button = gtk.RadioButton(self.close_button, label=_("On close window - hide player"))
        self.hide_button.connect("toggled", self.on_show_tray_icon)
        self.hide_button.show()
        
        self.minimize_button = gtk.RadioButton(self.close_button, label=_("On close window - minimize player"))
        self.minimize_button.show()
        
        """close on leave popup"""
        self.tray_icon_auto_hide = gtk.CheckButton(label=_("Automatic hide tray icon popup on mouse leave"), use_underline=True)        
        self.tray_icon_auto_hide.show()
        
        box.pack_start(self.tray_icon_button, False, True, 0)
        box.pack_start(self.close_button, False, True, 0)
        box.pack_start(self.hide_button, False, True, 0)
        box.pack_start(self.minimize_button, False, True, 0)
        box.pack_start(self.tray_icon_auto_hide, False, True, 0)
        
        
        self.widget = box

    
    def on_show_tray_icon(self, *args):
        print "action" , self.tray_icon_button.get_active()
        if not self.tray_icon_button.get_active():
            self.hide_button.set_sensitive(False) 
            if self.hide_button.get_active():
                self.minimize_button.set_active(True)
            self.tray_icon.hide()
        else:
            self.tray_icon.show()
            self.hide_button.set_sensitive(True)
            
    def on_load(self):
        self.tray_icon_button.set_active(FConfiguration().show_tray_icon)
        self.tray_icon_auto_hide.set_active(FConfiguration().tray_icon_auto_hide)
        if FConfiguration().on_close_window == const.ON_CLOSE_CLOSE:
            self.close_button.set_active(True)
            
        elif FConfiguration().on_close_window == const.ON_CLOSE_HIDE:
            self.hide_button.set_active(True)
            
        elif FConfiguration().on_close_window == const.ON_CLOSE_MINIMIZE:
            self.minimize_button.set_active(True)
            
            
        
    def on_save(self):
        FConfiguration().show_tray_icon = self.tray_icon_button.get_active() 
        FConfiguration().tray_icon_auto_hide = self.tray_icon_auto_hide.get_active()
        
        if  self.close_button.get_active():
            FConfiguration().on_close_window = const.ON_CLOSE_CLOSE
        
        elif self.hide_button.get_active():
            FConfiguration().on_close_window = const.ON_CLOSE_HIDE
        
        elif self.minimize_button.get_active():
            FConfiguration().on_close_window = const.ON_CLOSE_MINIMIZE
