#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util import const
from foobnix.util.fc import FC
from foobnix.helpers.pref_widgets import FrameDecorator, IconBlock,\
    VBoxDecorator, ChooseDecorator

class TrayIconConfig(ConfigPlugin):
    
    name = ("Tray Icon")
    
    def __init__(self, controls):
        
        print "Create tray icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        self.tray_icon_button = gtk.CheckButton(label=_("Show tray icon"), use_underline=True)
        self.tray_icon_button.connect("clicked", self.on_show_tray_icon)
        
        self.close_button = gtk.RadioButton(None, label=_("On close window - close player"))

        self.hide_button = gtk.RadioButton(self.close_button, label=_("On close window - hide player"))
        self.hide_button.connect("toggled", self.on_show_tray_icon)
        
        self.minimize_button = gtk.RadioButton(self.close_button, label=_("On close window - minimize player"))
        
        """close on leave popup"""
        self.tray_icon_auto_hide = gtk.CheckButton(label=_("Automatic hide tray icon popup on mouse leave"), use_underline=True)        
        
        """change tray icon to cover icon"""
        self.change_tray_icon = gtk.CheckButton(label=_("Change tray icon to cover icon"), use_underline=True)
        
       
        tray_icon = ChooseDecorator(None,FrameDecorator("System Icon Static", IconBlock("Icon")))
        
        init_icon = IconBlock("Init")
        play_icon = IconBlock("Play")
        pause_icon = IconBlock("Pause")
        stop_icon = IconBlock("Stop")
        radio_icon = IconBlock("Radio")
        
        line = VBoxDecorator(init_icon, play_icon, pause_icon, stop_icon, radio_icon)
        controls = ChooseDecorator(tray_icon.get_radio_button(),FrameDecorator("System Icons Dynamic", line))
        
        
        box.pack_start(self.tray_icon_button, False, True, 0)
        box.pack_start(self.close_button, False, True, 0)
        box.pack_start(self.hide_button, False, True, 0)
        box.pack_start(self.minimize_button, False, True, 0)
        box.pack_start(self.tray_icon_auto_hide, False, True, 0)
        box.pack_start(self.change_tray_icon,False, True, 0)
        
        box.pack_start(tray_icon,False, True, 0)
        box.pack_start(controls,False, True, 0)
        
        self.widget = box

    
    def on_show_tray_icon(self, *args):
        print "action" , self.tray_icon_button.get_active()
        if not self.tray_icon_button.get_active():
            self.hide_button.set_sensitive(False) 
            if self.hide_button.get_active():
                self.minimize_button.set_active(True)
            self.trayicon.hide()
        else:
            self.trayicon.show()
            self.hide_button.set_sensitive(True)
            
    def on_load(self):
        self.tray_icon_button.set_active(FC().show_tray_icon)
        self.tray_icon_auto_hide.set_active(FC().tray_icon_auto_hide)
        self.change_tray_icon.set_active(FC().change_tray_icon)
        
        if FC().on_close_window == const.ON_CLOSE_CLOSE:
            self.close_button.set_active(True)
            
        elif FC().on_close_window == const.ON_CLOSE_HIDE:
            self.hide_button.set_active(True)
            
        elif FC().on_close_window == const.ON_CLOSE_MINIMIZE:
            self.minimize_button.set_active(True)
            
            
        
    def on_save(self):
        FC().show_tray_icon = self.tray_icon_button.get_active() 
        FC().tray_icon_auto_hide = self.tray_icon_auto_hide.get_active()
        FC().change_tray_icon = self.change_tray_icon.get_active()
        
        if  self.close_button.get_active():
            FC().on_close_window = const.ON_CLOSE_CLOSE
        
        elif self.hide_button.get_active():
            FC().on_close_window = const.ON_CLOSE_HIDE
        
        elif self.minimize_button.get_active():
            FC().on_close_window = const.ON_CLOSE_MINIMIZE
