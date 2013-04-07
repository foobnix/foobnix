#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.model.signal import FControl
from gi.repository import Gtk
from foobnix.regui.state import LoadSave
from foobnix.helpers.my_widgets import tab_close_button, ToggleImageButton
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.util.key_utils import is_key
class FilterControl(Gtk.HBox, FControl, LoadSave):
    def __init__(self, controls):
        Gtk.HBox.__init__(self, False, 0)
        FControl.__init__(self, controls)
        
        self.entry = Gtk.Entry()
        self.entry.connect("key-release-event", self.on_key_press)
        
        self.search_func = self.controls.filter_by_file
        
        file_search = ToggleImageButton(Gtk.STOCK_FILE, func=self.set_search_by, param=self.controls.filter_by_file)
        file_search.set_tooltip_text(_("File search"))
        file_search.set_active(True)
        
        folder_search = ToggleImageButton(Gtk.STOCK_DIRECTORY, func=self.set_search_by, param=self.controls.filter_by_folder)
        folder_search.set_tooltip_text(_("Folder search"))
        
        self.list = [file_search, folder_search]
        OneActiveToggledButton(self.list)
        
        """search button"""
        search = tab_close_button(func=self.on_filter, stock=Gtk.STOCK_FIND)
        
        self.pack_start(file_search, False, False, 0)
        self.pack_start(folder_search, False, False, 0)
        self.pack_start(self.entry, True, True, 0)
        self.pack_start(search, False, False, 0)
        
    
    def set_search_by(self, search_func):
        self.search_func = search_func
    
    def on_key_press(self, w, e):
        if is_key(e, 'Return'):
            self.on_filter()
        
        if not self.entry.get_text():
            self.on_filter()
                
                
    def on_filter(self, *a):
        value = self.entry.get_text()
        self.search_func(value)        
    
    def on_load(self):
        pass
    
    def on_save(self):
        pass
