#-*- coding: utf-8 -*-
'''
Created on Dec 7, 2010

@author: zavlab1
'''

from gi.repository import Gtk

from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.util.list_utils import reorderer_list
from foobnix.helpers.menu import Popup
from foobnix.gui.notetab import TabGeneral


class TabHelperControl(TabGeneral):
    def __init__(self, controls):
        TabGeneral.__init__(self, controls)

        self.set_tab_pos(Gtk.PositionType.LEFT)

        """the only signal lets get the previous number of moved page"""
        self.connect("button-release-event", self.get_page_number)
        self.connect('switch-page', self.save_selected_tab)
        self.loaded = False

    def save_selected_tab(self, notebook, page, page_num, *args):
        if not self.loaded: #bbecause the "switch-page" event is fired after every tab's addtion
            return
        FC().nav_selected_tab = page_num

    def on_add_button_click(self):
        self._append_tab()
        self.controls.perspectives.get_perspective('fs').show_add_button()
        FCache().music_paths.insert(0, [])
        FCache().tab_names.insert(0, self.get_full_tab_name(self.get_current_tree().scroll))
        FCache().cache_music_tree_beans.insert(0, {})

    def on_button_press(self, w, e, *a):
        if e.button == 3:
            w.menu.show_all()
            w.menu.popup(None, None, None, None, e.button, e.time)

    def tab_menu_creator(self, widget, tab_child):
        widget.menu = Popup()
        widget.menu.add_item(_("Rename tab"), "", lambda: self.on_rename_tab(tab_child, 90, FCache().tab_names), None)
        widget.menu.add_item(_("Update Music Tree"), "view-refresh", lambda: self.on_update_music_tree(tab_child), None)
        widget.menu.add_item(_("Add folder"), "folder-open", lambda: self.on_add_folder(tab_child), None)
        widget.menu.add_item(_("Add folder in new tab"), "folder-open", lambda : self.on_add_folder(tab_child, True), None)
        widget.menu.add_item(_("Clear Music Tree"), "edit-clear", lambda : self.clear_tree(tab_child), None)
        widget.menu.add_item(_("Close tab"), "window-close", lambda: self.on_delete_tab(tab_child), None)
        return widget

    def reorder_callback(self, notebook, child, new_page_num):
        for list in [FCache().music_paths, FCache().tab_names, FCache().cache_music_tree_beans]:
            reorderer_list(list, new_page_num, self.page_number,)
        self.on_save_tabs()

    def get_page_number(self, *a):
            self.page_number = self.get_current_page()

    def on_add_folder(self, tab_child, in_new_tab=False):
        tree = tab_child.get_child()
        tree.add_folder(in_new_tab)

    def clear_tree(self, tab_child):
        n = self.page_num(tab_child)
        tree = tab_child.get_child()
        tree.clear_tree()
        FCache().cache_music_tree_beans[n] = {}

    def on_update_music_tree(self, tab_child):
        n = self.page_num(tab_child)
        tree = tab_child.get_child()
        self.controls.update_music_tree(tree, n)

    def on_load(self):
        if FC().tabs_mode == "Single":
            self.set_show_tabs(False)

        self.controls.load_music_tree()
        self.set_current_page(FC().nav_selected_tab)
        self.loaded = True

    def save_tabs(self):
        '''need for one_thread_save method'''
        pass
