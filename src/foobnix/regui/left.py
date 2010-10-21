#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
class LeftWidgets(FControl, LoadSave, gtk.VBox):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.VBox.__init__(self, False, 0)
        
        controls.tree.set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        controls.radio.set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        controls.virtual.set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
               
        
                
        buttons = PerspectiveButtonControlls(controls)
        buttons.show_all()
        
        self.pack_start(controls.tree.scroll, True, True)
        self.pack_start(controls.radio.scroll, True, True)
        self.pack_start(controls.virtual.scroll, True, True)
        
        self.pack_start(controls.filter, False, False)
        self.pack_start(buttons, False, False)
        
        self.show_all()
        
    
    def on_load(self):            
        pass
            
   
    def on_save(self):
        pass

class PerspectiveButtonControlls(FControl, gtk.HBox):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.HBox.__init__(self, False, 0)
               
        musics = self.custom_button("Music", gtk.STOCK_HARDDISK)
        musics.connect("clicked", self.on_change_perspective, controls.tree)
        musics.set_active(True)
                
        radios = self.custom_button("Radio", gtk.STOCK_NETWORK)
        radios.connect("clicked", self.on_change_perspective, controls.radio)
        #radios.connect("clicked", lambda * a: controls.update_radio_tree())
        
        virtuals = self.custom_button("Lists", gtk.STOCK_INDEX)
        virtuals.connect("clicked", self.on_change_perspective, controls.virtual)
        
        
       
        
        self.button_list = [musics, radios, virtuals]
        OneActiveToggledButton(self.button_list)
        
        self.pack_start(musics, False, False, 0)
        self.pack_start(radios, False, False, 0)
        self.pack_start(virtuals, False, False, 0)
    
    def on_change_perspective(self, w, perspective):
        self.controls.tree.scroll.hide()
        self.controls.radio.scroll.hide()
        self.controls.virtual.scroll.hide()
        perspective.scroll.show()
                    
        
    def custom_button(self, title, gtk_stock, func=None, param=None):
        button = gtk.ToggleButton(title)

        if param and func:             
            button.connect("toggled", lambda * a: func(param))
        elif func:
            button.connect("toggled", lambda * a: func())         
                
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
