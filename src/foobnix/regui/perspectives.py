#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.util.const import LEFT_PERSPECTIVE_INFO, LEFT_PERSPECTIVE_VIRTUAL, \
    LEFT_PERSPECTIVE_NAVIGATION, LEFT_PERSPECTIVE_RADIO
class PerspectiveControls(FControl, LoadSave, gtk.VBox):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.VBox.__init__(self, False, 0)
        
        self.perspectivs = {
                     LEFT_PERSPECTIVE_NAVIGATION:controls.tree.scroll,
                     LEFT_PERSPECTIVE_RADIO:controls.radio.scroll,
                     LEFT_PERSPECTIVE_VIRTUAL:controls.virtual.scroll,
                     LEFT_PERSPECTIVE_INFO:controls.info_panel
                     }
        
        self.buttons = PerspectiveButtonControlls(self.activate_perspective)
        self.buttons.show_all()
        
        for widget in self.perspectivs.values():
            self.pack_start(widget, True, True)
                
        self.pack_start(controls.filter, False, False)
        self.pack_start(self.buttons, False, False)
    
    
    def activate_perspective(self, name):
        for widget in self.perspectivs.values():
            widget.hide()
        FC().left_perspective = name
        self.perspectivs[name].show()
        
        if name == LEFT_PERSPECTIVE_INFO:
            self.controls.filter.hide()
            self.controls.info_panel.update_info_panel()
        else:
            self.controls.filter.show()
   
    def activate_perspective_key(self, name):
        self.buttons.activate_button(name)     
        
    def on_load(self):            
        pass            
   
    def on_save(self):
        pass

class PerspectiveButtonControlls(gtk.HBox):
    def __init__(self, activate_perspective):
        
        gtk.HBox.__init__(self, False, 0)
        
        self.active = None
               
        musics = self.custom_button(_("Music"), gtk.STOCK_HARDDISK, _("Music Navigation (Alt+1)"))
        musics.connect("clicked", lambda * a: activate_perspective(LEFT_PERSPECTIVE_NAVIGATION))        
        musics.set_active(True)
        
                
        radios = self.custom_button(_("Radio"), gtk.STOCK_NETWORK, _("Radio Stantions (Alt+2)"))
        radios.connect("clicked", lambda * a:activate_perspective(LEFT_PERSPECTIVE_RADIO))
        
        
        
        virtuals = self.custom_button(_("Lists"), gtk.STOCK_INDEX, _("Virtual Play Lists (Alt+3)"))
        virtuals.connect("clicked", lambda * a:activate_perspective(LEFT_PERSPECTIVE_VIRTUAL))
        
        
        info = self.custom_button(_("Info"), gtk.STOCK_INFO, _("Info Panel (Alt+4)"))
        info.connect("clicked", lambda * a: activate_perspective(LEFT_PERSPECTIVE_INFO))
                
        self.button_list = {
                     LEFT_PERSPECTIVE_NAVIGATION:musics,
                     LEFT_PERSPECTIVE_RADIO:radios,
                     LEFT_PERSPECTIVE_VIRTUAL:virtuals,
                     LEFT_PERSPECTIVE_INFO:info
                     }
        
        OneActiveToggledButton(self.button_list.values())
        
        self.pack_start(musics, False, False, 0)
        self.pack_start(radios, False, False, 0)
        self.pack_start(virtuals, False, False, 0)
        self.pack_start(info, False, False, 0)
    
    def activate_button(self, name):
        self.button_list[name].set_active(True) 
    
    def custom_button(self, title, gtk_stock, tooltip=None):
        button = gtk.ToggleButton(title)
        
        if not tooltip:
            tooltip = title
        
        button.set_tooltip_text(tooltip)
                
        button.set_relief(gtk.RELIEF_NONE)
        label = button.get_child()
        button.remove(label)
        
        vbox = gtk.VBox(False, 0)
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        vbox.add(img)
        vbox.add(gtk.Label(title))
        vbox.show_all()
        
        button.add(vbox)
        return button
