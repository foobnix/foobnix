#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
from foobnix.preferences.config_plugin import ConfigPlugin
import gtk
from foobnix.helpers.my_widgets import tab_close_button, notetab_label
from foobnix.fc.fc import FC
class TabsConfig(ConfigPlugin):
    
    name = _("Tabs")
    
    def __init__(self, controls):
        self.controls = controls
        box = gtk.VBox(False, 0)        
        box.hide()
        
        """count"""
        cbox = gtk.HBox(False, 0)
        cbox.show()
        
        tab_label = gtk.Label(_("Count of tabs:"))
        tab_label.set_size_request(150, -1)
        tab_label.show()
        
        adjustment = gtk.Adjustment(value=1, lower=1, upper=20, step_incr=1, page_incr=10, page_size=0)
        self.tabs_count = gtk.SpinButton(adjustment)
        self.tabs_count.connect("value-changed", self.on_chage_count_tabs)
        self.tabs_count.show()
        
        cbox.pack_start(tab_label, False, False, 0)
        cbox.pack_start(self.tabs_count, False, True, 0)
        
        
        """len"""
        lbox = gtk.HBox(False, 0)
        lbox.show()
        
        tab_label = gtk.Label(_("Max length of tab:"))
        tab_label.set_size_request(150, -1)
        tab_label.show()
        
        adjustment = gtk.Adjustment(value=0, lower= -1, upper=300, step_incr=1, page_incr=10, page_size=0)
        self.tab_len = gtk.SpinButton(adjustment)
        self.tab_len.connect("value-changed", self.on_chage_len_tab)
        self.tab_len.show()
        
        lbox.pack_start(tab_label, False, False, 0)
        lbox.pack_start(self.tab_len, False, True, 0)
        
        """position"""
        pbox = gtk.HBox(False, 10)
        pbox.show()
        
        label = gtk.Label(_("Tab position:"))
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
        pbox.pack_start(self.radio_tab_top, False, False, 0)
        pbox.pack_start(self.radio_tab_no, False, False, 0)
        
        """closed type """
        close_label_box = gtk.HBox(False, 10)
        close_label_box.show()
        
        close_label = gtk.Label(_("Close tab sign:"))
        close_label.set_size_request(150, -1)
        close_label.show()
        
        self.radio_tab_label = gtk.RadioButton(None, "x")
        self.radio_tab_label.connect("toggled", self.on_chage_tab_position)
        self.radio_tab_label.show()
        
        self.radio_tab_button = gtk.RadioButton(self.radio_tab_label, None)
        self.radio_tab_button.connect("toggled", self.on_chage_tab_position)
        self.radio_tab_button.show()
        
        self.tab_close_box = gtk.HBox()
        self.tab_close_box.pack_start(self.radio_tab_button, False, True, 0)
        self.tab_close_box.pack_start(tab_close_button(), False, False, 0)
        self.tab_close_box.show()
        
        self.radio_tab_none = gtk.RadioButton(self.radio_tab_label, _("None"))
        self.radio_tab_none.connect("toggled", self.on_chage_tab_position)
        self.radio_tab_none.show()
        
        close_label_box.pack_start(close_label, False, False, 0)
        close_label_box.pack_start(self.radio_tab_label, False, False, 0)
        close_label_box.pack_start(self.tab_close_box, False, False, 0)
        close_label_box.pack_start(self.radio_tab_none, False, False, 0)
        
        
        """global pack"""
        box.pack_start(cbox, False, True, 0)
        box.pack_start(lbox, False, True, 0)
        box.pack_start(pbox, False, True, 0)
        box.pack_start(close_label_box, False, True, 0)
        
        self.widget = box
        
    
    def on_chage_tab_position(self, *args):
        if self.radio_tab_left.get_active():
            self.controls.notetabs.set_tab_left()
        
        elif self.radio_tab_top.get_active():
            self.controls.notetabs.set_tab_top()
        
        elif self.radio_tab_no.get_active():
            self.controls.notetabs.set_tab_no()    
        
    
    def on_chage_count_tabs(self, w):
        val = w.get_value_as_int()
        FC().count_of_tabs = val
        
    def removing_of_extra_tabs(self, number_of_tabs):
            overage = (self.controls.notetabs.get_n_pages() - 1) - number_of_tabs
            counter = 0
            while counter < overage:
                self.controls.notetabs.remove_page(self.controls.notetabs.get_n_pages() - 1)
                counter += 1
   
    def on_chage_len_tab(self, w):
        val = w.get_value_as_int()
        FC().len_of_tab = val
    
    def on_load(self):
        self.tabs_count.set_value(FC().count_of_tabs)
        self.tab_len.set_value(FC().len_of_tab)
        
        if  FC().tab_position == "left":
            self.radio_tab_left.set_active(True)
        
        elif  FC().tab_position == "top":
            self.radio_tab_top.set_active(True)
        
        elif FC().tab_position == "no":
            self.radio_tab_no.set_active(True)
            
        if  FC().tab_close_element == "label":
            self.radio_tab_label.set_active(True)
            
        elif FC().tab_close_element == "button":
            self.radio_tab_button.set_active(True)
            
        else: self.radio_tab_none.set_active(True)
            
    def on_save(self):
        FC().count_of_tabs = self.tabs_count.get_value_as_int()
        if self.controls.notetabs.get_n_pages() - 1 > FC().count_of_tabs:
            self.removing_of_extra_tabs(FC().count_of_tabs) 
        FC().len_of_tab = self.tab_len.get_value_as_int()
        
        if self.radio_tab_label.get_active():
            FC().tab_close_element = "label"
        elif self.radio_tab_button.get_active():
            FC().tab_close_element = "button"
        else: FC().tab_close_element = None
            
        if self.radio_tab_left.get_active():
            FC().tab_position = "left"
        elif self.radio_tab_top.get_active(): 
            FC().tab_position = "top"
        else: FC().tab_position = "no"
        
