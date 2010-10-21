#-*- coding: utf-8 -*-
'''
Created on 29 авг. 2010

@author: ivan
'''
from foobnix.preferences.config_plugin import ConfigPlugin
import gtk
from foobnix.util.configuration import FConfiguration
class InfoPagenConfig(ConfigPlugin):
    
    name = _("Info panel")
    
    def __init__(self, controls):
        print "Create try icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        """count"""
        cbox = gtk.HBox(False, 0)
        cbox.show()
        
        tab_label = gtk.Label(_("Disc cover size"))
        tab_label.show()
        
        adjustment = gtk.Adjustment(value=1, lower=100, upper=500, step_incr=20, page_incr=50, page_size=0)
        self.image_size_spin = gtk.SpinButton(adjustment)
        self.image_size_spin.show()
        
        cbox.pack_start(tab_label, False, False, 0)
        cbox.pack_start(self.image_size_spin, False, True, 0)
        
        """lyric panel size"""
        lbox = gtk.HBox(False, 0)
        lbox.show()
        
        lyric_label = gtk.Label(_("Lyric panel size"))
        lyric_label.show()
        
        adjustment = gtk.Adjustment(value=1, lower=100, upper=500, step_incr=20, page_incr=50, page_size=0)
        self.lyric_size_spin = gtk.SpinButton(adjustment)
        self.lyric_size_spin.show()

        lbox.pack_start(lyric_label, False, False, 0)
        lbox.pack_start(self.lyric_size_spin, False, True, 0)
        
        box.pack_start(cbox, False, True, 0)
        box.pack_start(lbox, False, True, 0)
        self.widget = box
    
    def on_load(self):
        self.image_size_spin.set_value(FConfiguration().info_panel_image_size)
        self.lyric_size_spin.set_value(FConfiguration().lyric_panel_image_size)
        
    
    def on_save(self):
        FConfiguration().lyric_panel_image_size = self.lyric_size_spin.get_value_as_int()
         
        
