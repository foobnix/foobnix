#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''

import gtk

from foobnix.fc.fc import FC
from foobnix.fc.fc_base import FCBase
from foobnix.regui.state import LoadSave
from foobnix.regui.model.signal import FControl
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.helpers.my_widgets import PespectiveToogledButton, ButtonStockText
from foobnix.util.const import LEFT_PERSPECTIVE_INFO, LEFT_PERSPECTIVE_VIRTUAL, \
    LEFT_PERSPECTIVE_NAVIGATION, LEFT_PERSPECTIVE_RADIO, LEFT_PERSPECTIVE_MY_RADIO, \
    LEFT_PERSPECTIVE_LASTFM, LEFT_PERSPECTIVE_VK
import thread


class PerspectiveControls(FControl, gtk.VBox, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.VBox.__init__(self, False, 0)
        
        self.perspectivs = {
                     LEFT_PERSPECTIVE_NAVIGATION:controls.tabhelper,
                     LEFT_PERSPECTIVE_RADIO:controls.radio.scroll,
                     LEFT_PERSPECTIVE_MY_RADIO:controls.my_radio.scroll,
                     LEFT_PERSPECTIVE_VIRTUAL:controls.virtual.scroll,
                     LEFT_PERSPECTIVE_INFO:controls.info_panel,
                     LEFT_PERSPECTIVE_LASTFM:controls.lastfm_integration.scroll,
                     LEFT_PERSPECTIVE_VK:controls.vk_integration.scroll
                     }
        self.switch_radio_button = gtk.Button()
        self.switch_radio_button.connect("clicked", lambda *a: self.on_radio_buttons_click()) 
        self.buttons = PerspectiveButtonControlls(self.activate_perspective, controls)
        self.buttons.show_all()
        
        self.add_button = ButtonStockText(_("Add Folder(s) in tree"), gtk.STOCK_ADD)
        self.add_button.connect("clicked", lambda * a :controls.tree.add_folder())
        
        self.switch_radio_button = gtk.Button()
        self.switch_radio_button.connect("clicked", lambda *a: self.on_radio_buttons_click())        
         
        self.pack_start(self.add_button, False, False)
        
        for widget in self.perspectivs.values():
            self.pack_start(widget, True, True)
        self.pack_start(self.switch_radio_button, False, False)
        self.pack_start(controls.filter, False, False)
        self.pack_start(self.buttons, False, False)
    
    def show_add_button(self):
        self.add_button.show()
    
    def hide_add_button(self):
        self.add_button.hide()
    
    def activate_perspective(self, name):
        for widget in self.perspectivs.values():
            widget.hide()
        FC().left_perspective = name
        self.perspectivs[name].show()
        
        if name in (LEFT_PERSPECTIVE_INFO,LEFT_PERSPECTIVE_LASTFM):
            self.controls.filter.hide()
        else:
            self.controls.filter.show()

        if name in (LEFT_PERSPECTIVE_RADIO,LEFT_PERSPECTIVE_MY_RADIO):
            self.switch_radio_button.set_label(self.perspectivs[name]
                                               .get_child().switcher_label)
            self.switch_radio_button.show()
        else:
            self.switch_radio_button.hide()
            
    def on_radio_buttons_click(self):
        for name in self.perspectivs.keys():
            if self.perspectivs[name].get_visible():
                if name == LEFT_PERSPECTIVE_RADIO:
                    perspective_name = LEFT_PERSPECTIVE_MY_RADIO
                    FC().is_my_radio_active = True
                elif name == LEFT_PERSPECTIVE_MY_RADIO:
                    perspective_name = LEFT_PERSPECTIVE_RADIO
                    FC().is_my_radio_active = False
                break
        self.activate_perspective(perspective_name)
        self.switch_radio_button.set_label(self.perspectivs[perspective_name]
                                           .get_child().switcher_label)
   
    def activate_perspective_key(self, name):
        self.buttons.activate_button(name)
        
    def activate_radio_perspective(self):
        if FC().is_my_radio_active:
            self.activate_perspective(LEFT_PERSPECTIVE_MY_RADIO)
        else:
            self.activate_perspective(LEFT_PERSPECTIVE_RADIO)
    
    def on_load(self):  
        self.activate_perspective(LEFT_PERSPECTIVE_NAVIGATION)
        
    def on_save(self):
        pass

class PerspectiveButtonControlls(gtk.HBox):
    def __init__(self, activate_perspective, controls):
        
        gtk.HBox.__init__(self, False, 0)
        self.controls = controls
        self.active = None
               
        musics = PespectiveToogledButton(_("Music"), gtk.STOCK_HARDDISK, _("Music Navigation (Alt+1)"))
        musics.connect("button-press-event", lambda * a: activate_perspective(LEFT_PERSPECTIVE_NAVIGATION))        
        musics.set_active(True)
        
                
        radios = PespectiveToogledButton(_("Radio"), gtk.STOCK_NETWORK, _("Radio Stantions (Alt+2)"))
        radios.connect("button-press-event", lambda * a:
                       controls.perspective.activate_radio_perspective())
              
        virtuals = PespectiveToogledButton(_("Playlist"), gtk.STOCK_INDEX, _("Virtual Play Lists (Alt+3)"))
        virtuals.connect("button-press-event", lambda * a:activate_perspective(LEFT_PERSPECTIVE_VIRTUAL))
        
        
        info = PespectiveToogledButton(_("Info"), gtk.STOCK_INFO, _("Info Panel (Alt+4)"))
        info.connect("button-press-event", lambda * a: activate_perspective(LEFT_PERSPECTIVE_INFO))
        
        lastfm = PespectiveToogledButton(_("Last.Fm"), gtk.STOCK_CONNECT, _("Last.fm Panel (Alt+5)"))
        lastfm.connect("button-press-event", lambda * a: activate_perspective(LEFT_PERSPECTIVE_LASTFM))
        
        vk = PespectiveToogledButton(_("VK"), gtk.STOCK_UNINDENT, _("VK Panel (Alt+6)"))
        vk.connect("button-press-event", lambda * a: self.on_vk_click())
        vk.connect("button-press-event", lambda * a: activate_perspective(LEFT_PERSPECTIVE_VK))
        
                
        self.button_list = {
                     LEFT_PERSPECTIVE_NAVIGATION:musics,
                     LEFT_PERSPECTIVE_RADIO:radios,
                     LEFT_PERSPECTIVE_VIRTUAL:virtuals,
                     LEFT_PERSPECTIVE_LASTFM:lastfm,
                     LEFT_PERSPECTIVE_VK:vk,
                     LEFT_PERSPECTIVE_INFO:info                     
                     }
        
        OneActiveToggledButton(self.button_list.values())
        
        self.pack_start(musics, False, False, 0)
        self.pack_start(radios, False, False, 0)
        
        if "l_user_" != FCBase().lfm_login:
            self.pack_start(lastfm, False, False, 0)
 
        self.pack_start(vk, False, False, 0)
                
        self.pack_start(virtuals, False, False, 0)
        self.pack_start(info, False, False, 0)
    
    def activate_button(self, name):
        self.button_list[name].set_active(True)
        
    def on_vk_click(self):
        thread.start_new_thread(self.controls.vk_integration.lazy_load, ()) 
        #Otherwise you can't call authorization window,
        #it can be called only from not main loop
                                                