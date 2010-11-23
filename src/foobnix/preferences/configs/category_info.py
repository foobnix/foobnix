#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
class CategoryInfoConfig(ConfigPlugin):
    name = _("Category Info")
    def __init__(self):
        box = gtk.VBox(False, 0)
        box.hide()
        
        similar_arists = gtk.CheckButton(label="Show Similar Artists", use_underline=True)
        similar_arists.show()
        
        similar_song = gtk.CheckButton(label="Show Similar Songs", use_underline=True)
        similar_song.show()
        
        similar_tags = gtk.CheckButton(label="Show Similar Tags", use_underline=True)
        similar_tags.show()
        
        box.pack_start(similar_arists, False, True, 0)
        box.pack_start(similar_song, False, True, 0)
        box.pack_start(similar_tags, False, True, 0)
        
        self.widget = box
