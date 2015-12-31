#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

from gi.repository import Gtk
from foobnix.gui.state import LoadSave, Filterable
from foobnix.helpers.my_widgets import tab_close_button, ToggleImageButton
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.util.key_utils import is_key


class FilterControl(Gtk.HBox, LoadSave):

    def __init__(self, filterabe):
        Gtk.HBox.__init__(self, False, 0)
        LoadSave.__init__(self)

        assert isinstance(filterabe, Filterable)

        self.entry = Gtk.Entry()
        self.entry.connect("key-release-event", self.on_key_press)

        self.search_func = filterabe.filter_by_file

        file_search = ToggleImageButton("document-new", func=self.set_search_by, param=filterabe.filter_by_file)
        file_search.set_tooltip_text(_("File search"))
        file_search.set_active(True)

        folder_search = ToggleImageButton("folder", func=self.set_search_by, param=filterabe.filter_by_folder)
        folder_search.set_tooltip_text(_("Folder search"))

        self.list = [file_search, folder_search]
        OneActiveToggledButton(self.list)

        """search button"""
        search = tab_close_button(func=self.on_filter, stock="edit-find")

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
