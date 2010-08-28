#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
from foobnix.preferences.config_plugin import ConfigPlugin
import gtk
from foobnix.util.configuration import FConfiguration
from foobnix.util import LOG
class TabsConfig(ConfigPlugin):
    
    name = _("Tabs")
    
    def __init__(self, online_controller):
        self.online_controller = online_controller
        print "Create try icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        """count"""
        cbox = gtk.HBox(False, 0)
        cbox.show()
        
        tab_label = gtk.Label(_("Count of tabs"))
        tab_label.set_size_request(150, -1)
        tab_label.show()
        
        adjustment = gtk.Adjustment(value=1, lower=1, upper=20, step_incr=1, page_incr=10, page_size=10)
        self.tabs_count = gtk.SpinButton(adjustment)
        self.tabs_count.connect("value-changed", self.on_chage_count_tabs)
        self.tabs_count.show()
        
        cbox.pack_start(tab_label, False, False, 0)
        cbox.pack_start(self.tabs_count, False, True, 0)
        
        
        """len"""
        lbox = gtk.HBox(False, 0)
        lbox.show()
        
        tab_label = gtk.Label(_("Max length of tab"))
        tab_label.set_size_request(150, -1)
        tab_label.show()
        
        adjustment = gtk.Adjustment(value=0, lower=0, upper=300, step_incr=1, page_incr=10, page_size=10)
        self.tab_len = gtk.SpinButton(adjustment)
        self.tab_len.connect("value-changed", self.on_chage_len_tab)
        self.tab_len.show()
        
        lbox.pack_start(tab_label, False, False, 0)
        lbox.pack_start(self.tab_len, False, True, 0)
        
        """position"""
        pbox = gtk.HBox(False, 0)
        pbox.show()
        
        label = gtk.Label(_("Tab position"))
        label.set_size_request(150, -1)
        label.show()
        
        self.radio_tab_left = gtk.RadioButton(None, _("Left"))
        self.radio_tab_left.connect("toggled", self.on_chage_tab_position)
        self.radio_tab_left.show()
        
        self.radio_tab_top = gtk.RadioButton(self.radio_tab_left, _("Top"))
        self.radio_tab_top.connect("toggled", self.on_chage_tab_position)
        self.radio_tab_top.show()
        
        self.radio_tab_no = gtk.RadioButton(self.radio_tab_left, _("No Tabs"))
        self.radio_tab_no.connect("toggled", self.on_chage_tab_position)
        self.radio_tab_no.show()
        
        pbox.pack_start(label, False, False, 0)
        pbox.pack_start(self.radio_tab_left, False, False, 0)
        pbox.pack_start(self.radio_tab_top, False, True, 0)
        pbox.pack_start(self.radio_tab_no, False, True, 0)
        
        
        box.pack_start(cbox, False, True, 0)
        box.pack_start(lbox, False, True, 0)
        box.pack_start(pbox, False, True, 0)
        
        self.widget = box
        
    
    def on_chage_tab_position(self, *args):
        if self.radio_tab_left.get_active():
            self.online_controller.set_tab_left()
        
        elif self.radio_tab_top.get_active():
            self.online_controller.set_tab_top()
        
        elif self.radio_tab_no.get_active():
            self.online_controller.set_tab_no()    
    
    def on_chage_count_tabs(self, w):
        val = w.get_value_as_int()
        FConfiguration().count_of_tabs = val
   
    def on_chage_len_tab(self, w):
        val = w.get_value_as_int()
        FConfiguration().len_of_tab = val
    
    def on_load(self):
        self.tabs_count.set_value(FConfiguration().count_of_tabs)
        self.tab_len.set_value(FConfiguration().len_of_tab)
        
        if  FConfiguration().tab_position == "left":
            self.radio_tab_left.set_active(True)
        
        elif  FConfiguration().tab_position == "top":
            self.radio_tab_top.set_active(True)
        
        elif FConfiguration().tab_position == "no":
            self.radio_tab_no.set_active(True)
        
            
    def on_save(self):
        FConfiguration().count_of_tabs = self.tabs_count.get_value_as_int() 
        FConfiguration().len_of_tab = self.tab_len.get_value_as_int()
     
