#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util import const
from foobnix.util.fc import FC
from foobnix.helpers.pref_widgets import FrameDecorator, VBoxDecorator, ChooseDecorator, \
    IconBlock
from foobnix.helpers.image import ImageBase
from foobnix.util.const import ICON_BLANK_DISK, FTYPE_RADIO, STATE_PLAY, \
    STATE_PAUSE, STATE_STOP
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name

class TrayIconConfig(ConfigPlugin):
    
    name = ("Tray Icon")
    
    def __init__(self, controls):
        self.controls = controls
        box = gtk.VBox(False, 0)        
        box.hide()
        
        '''static_icon'''
        self.static_icon = IconBlock("Icon", controls, FC().static_icon_entry)
        
        """dynamic icons"""
        self.play_icon = IconBlock("Play", controls, FC().play_icon_entry)
        self.pause_icon = IconBlock("Pause", controls, FC().pause_icon_entry)
        self.stop_icon = IconBlock("Stop", controls, FC().stop_icon_entry)
        self.radio_icon = IconBlock("Radio", controls, FC().radio_icon_entry)
        
        
        
        self.tray_icon_button = gtk.CheckButton(label=_("Show tray icon"), use_underline=True)
        self.tray_icon_button.connect("clicked", self.on_show_tray_icon)
        
        self.close_button = gtk.RadioButton(None, label=_("On close window - close player"))

        self.hide_button = gtk.RadioButton(self.close_button, label=_("On close window - hide player"))
        self.hide_button.connect("toggled", self.on_show_tray_icon)
        
        self.minimize_button = gtk.RadioButton(self.close_button, label=_("On close window - minimize player"))
        

        """system icon"""
        self.static_tray_icon = ChooseDecorator(None, FrameDecorator(_("System Icon Static"), self.static_icon))
        
        """dynamic icons"""
        line = VBoxDecorator(self.play_icon,
                             self.pause_icon,
                             self.stop_icon,
                             self.radio_icon)
        

        self.icon_controls = ChooseDecorator(self.static_tray_icon.get_radio_button(), FrameDecorator(_("System Icons Dynamic"), line))
        
        """disc image icon"""        
        image = ImageBase(ICON_BLANK_DISK, 30)
        self.change_tray_icon = ChooseDecorator(self.static_tray_icon.get_radio_button(), FrameDecorator(_("Disc cover image"), image))
        
        self.notifier = gtk.CheckButton(_("Notification pop-up"))
        
        box.pack_start(self.tray_icon_button, False, True, 0)
        box.pack_start(self.close_button, False, True, 0)
        box.pack_start(self.hide_button, False, True, 0)
        box.pack_start(self.minimize_button, False, True, 0)
        
        box.pack_start(self.static_tray_icon, True, True, 0)
        box.pack_start(self.icon_controls, True, True, 0)
        box.pack_start(self.change_tray_icon, False, False, 0)
        
        box.pack_start(FrameDecorator(_("Notification"), self.notifier), False, False, 0)
        
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
   
    def on_dynamic_icons(self, state):
        if FC().static_tray_icon:
            self.check_active_dynamic_icon(self.static_icon)
        if FC().system_icons_dinamic:
            if state == FTYPE_RADIO:
                self.check_active_dynamic_icon(self.radio_icon)
            elif state == STATE_PLAY:
                self.check_active_dynamic_icon(self.play_icon)
            elif state == STATE_PAUSE:
                self.check_active_dynamic_icon(self.pause_icon)
            elif state == STATE_STOP:
                self.check_active_dynamic_icon(self.stop_icon)
                 
    def check_active_dynamic_icon(self, icon_object):
        icon_name = icon_object.entry.get_text()
        try:
            path = get_foobnix_resourse_path_by_name(icon_name)
            self.controls.trayicon.set_image_from_path(path)
        except TypeError:
            pass
    
    
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
        
        if FC().notifier:
            self.notifier.set_active(True)   

        self.static_icon.entry.set_text(FC().static_icon_entry)
        self.play_icon.entry.set_text(FC().play_icon_entry)
        self.pause_icon.entry.set_text(FC().pause_icon_entry)
        self.stop_icon.entry.set_text(FC().stop_icon_entry)
        self.radio_icon.entry.set_text(FC().radio_icon_entry)
             
    def on_save(self):
        FC().show_tray_icon = self.tray_icon_button.get_active() 
        FC().static_tray_icon = self.static_tray_icon.button.get_active()
        if FC().static_tray_icon: self.on_dynamic_icons(None)
        FC().system_icons_dinamic = self.icon_controls.button.get_active()
        FC().change_tray_icon = self.change_tray_icon.button.get_active()
                
        if  self.close_button.get_active():
            FC().on_close_window = const.ON_CLOSE_CLOSE
        
        elif self.hide_button.get_active():
            FC().on_close_window = const.ON_CLOSE_HIDE
        
        elif self.minimize_button.get_active():
            FC().on_close_window = const.ON_CLOSE_MINIMIZE
            
        if self.notifier.get_active():       
            FC().notifier = True
        else: 
            FC().notifier = False
            
        FC().static_icon_entry = self.static_icon.entry.get_text()
        FC().play_icon_entry = self.play_icon.entry.get_text()
        FC().pause_icon_entry = self.pause_icon.entry.get_text()
        FC().stop_icon_entry = self.stop_icon.entry.get_text()
        FC().radio_icon_entry = self.radio_icon.entry.get_text()
