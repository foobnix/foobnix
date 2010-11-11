#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util import const
from foobnix.util.fc import FC
from foobnix.helpers.pref_widgets import FrameDecorator, IconBlock, \
    VBoxDecorator, ChooseDecorator
from foobnix.helpers.image import ImageBase

class TrayIconConfig(ConfigPlugin):
    
    name = ("Tray Icon")
    
    def __init__(self, controls):
        self.controls = controls
        print "Create tray icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        self.tray_icon_button = gtk.CheckButton(label=_("Show tray icon"), use_underline=True)
        self.tray_icon_button.connect("clicked", self.on_show_tray_icon)
        
        self.close_button = gtk.RadioButton(None, label=_("On close window - close player"))

        self.hide_button = gtk.RadioButton(self.close_button, label=_("On close window - hide player"))
        self.hide_button.connect("toggled", self.on_show_tray_icon)
        
        self.minimize_button = gtk.RadioButton(self.close_button, label=_("On close window - minimize player"))
        

        """system icon"""
        self.static_tray_icon = ChooseDecorator(None,FrameDecorator("System Icon Static", controls.trayicon.static_icon))
        
        """dynamic icons"""
        line = VBoxDecorator(controls.trayicon.play_icon,
                             controls.trayicon.pause_icon, 
                             controls.trayicon.stop_icon, 
                             controls.trayicon.radio_icon)
        

        self.icon_controls = ChooseDecorator(self.static_tray_icon.get_radio_button(),FrameDecorator("System Icons Dynamic", line))
        
        """disc image icon"""        
        image = ImageBase("blank-disc.jpg", 30)
        self.change_tray_icon = ChooseDecorator(self.static_tray_icon.get_radio_button(),FrameDecorator("Disc cover image",image))
        
        box.pack_start(self.tray_icon_button, False, True, 0)
        box.pack_start(self.close_button, False, True, 0)
        box.pack_start(self.hide_button, False, True, 0)
        box.pack_start(self.minimize_button, False, True, 0)
        

        box.pack_start(self.static_tray_icon,True, True, 0)
        box.pack_start(self.icon_controls,True, True, 0)
        box.pack_start(self.change_tray_icon,False, False, 0)
        
        self.widget = box
        
    
                        
    def on_show_tray_icon(self, *args):
        if not self.tray_icon_button.get_active():
            self.hide_button.set_sensitive(False) 
            if self.hide_button.get_active():
                self.minimize_button.set_active(True)
            self.controls.trayicon.hide()
        else:
            self.controls.trayicon.show()
            self.hide_button.set_sensitive(True)
            
    def on_load(self):
        self.tray_icon_button.set_active(FC().show_tray_icon)
        self.static_tray_icon.button.set_active(FC().static_tray_icon)
        self.icon_controls.button.set_active(FC().system_icons_dinamic)
        self.change_tray_icon.button.set_active(FC().change_tray_icon)
        
        if FC().on_close_window == const.ON_CLOSE_CLOSE:
            self.close_button.set_active(True)
            
        elif FC().on_close_window == const.ON_CLOSE_HIDE:
            self.hide_button.set_active(True)
            
        elif FC().on_close_window == const.ON_CLOSE_MINIMIZE:
            self.minimize_button.set_active(True)
            
    def on_save(self):
        FC().show_tray_icon = self.tray_icon_button.get_active() 
        FC().static_tray_icon = self.static_tray_icon.button.get_active()
        FC().system_icons_dinamic = self.icon_controls.button.get_active()
        FC().change_tray_icon = self.change_tray_icon.button.get_active()
                
        if  self.close_button.get_active():
            FC().on_close_window = const.ON_CLOSE_CLOSE
        
        elif self.hide_button.get_active():
            FC().on_close_window = const.ON_CLOSE_HIDE
        
        elif self.minimize_button.get_active():
            FC().on_close_window = const.ON_CLOSE_MINIMIZE
