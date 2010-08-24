#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin

class TryIconConfig(ConfigPlugin):
    
    name = "Try Icon"
    
    def __init__(self):
        print "Create try icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        image_popup = gtk.CheckButton(label="Show album image in tryicon popup", use_underline=True)
        image_popup.show()
        
        text_popup = gtk.CheckButton(label="Show Artist - Title in tryicon popup", use_underline=True)
        text_popup.show()
        
        box.pack_start(image_popup, False, True, 0)
        box.pack_start(text_popup, False, True, 0)
        
        self.widget = box
    
