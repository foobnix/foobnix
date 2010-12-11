#-*- coding: utf-8 -*-
'''
Created on Dec 7, 2010

@author: zavlab1
'''

import gtk
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.helpers.my_widgets import tab_close_button, notetab_label
from foobnix.util.list_utils import reorderer_list
from foobnix.helpers.menu import Popup
from foobnix.util.key_utils import is_key

class TabLib(gtk.Notebook, FControl):
    def __init__(self, controls):
        gtk.Notebook.__init__(self)
        FControl.__init__(self, controls)
        
        self.set_tab_pos(gtk.POS_LEFT)
        self.on_append_tab(self.controls.tree)
        self.set_scrollable(True)
        
        """the only signal lets get the previous number of moved page"""
        self.connect("button-release-event", self.get_page_number)
        
        self.connect("page-reordered", self.reorder_callback)
          
        self.connect("button-press-event", self.on_button_press)
        
        
    def on_button_press(self, w, e):
        if e.button == 3:
            self.menu.show_all()
            self.menu.popup(None, None, None, e.button, e.time)
           
    def on_delete_tab(self, child):
        n = self.page_num(child)
        if self.get_n_pages() == 1: return
        self.remove_page(n)
        del FC().tab_names[n]
        del FC().music_paths[n]
        del FC().cache_music_tree_beans[n]
       
    def on_append_tab(self, tree, tab_name = _("Empty tab")):
        vbox = gtk.VBox()
        self.label = gtk.Label(tab_name + " ")
        self.label.set_angle(90)
        self.label.show()
        
        self.menu = Popup()
        self.menu.add_item(_("Rename tab"), "", self.manual_set_label, None)
        self.menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, self.controls.update_music_tree, None)
        self.menu.add_item(_("Add folder"), gtk.STOCK_OPEN, tree.add_folder, None)
        self.menu.add_item(_("Add folder in new tab"), gtk.STOCK_OPEN, lambda : tree.add_folder(True), None)
        self.menu.add_item(_("Clear Music Tree"), gtk.STOCK_OPEN, lambda: self.clear_tree(tree), None)       
        
        def button():
            if FC().tab_close_element == "button":
                return tab_close_button(func=self.on_delete_tab, arg=tree.scroll)
            else:
                return notetab_label(func=self.on_delete_tab, arg=tree.scroll, angel=90)
            
        vbox.pack_start(button(), False, False)
        vbox.pack_start(self.label, False, False)
        
        self.prepend_page(tree.scroll, vbox)
        self.set_tab_reorderable(tree.scroll, True)
        
        self.show_all()
        
        """only after show_all() function"""
        self.set_current_page(0)
         
        
    def reorder_callback(self, notebook, child, new_page_num):
        for list in [FC().music_paths, FC().tab_names, FC().cache_music_tree_beans]:
            reorderer_list(list, new_page_num, self.page_number, )
        
    def get_page_number(self, *a):
            self.page_number = self.get_current_page()
              
    def manual_set_label(self):
        window = gtk.Window()
        window.set_decorated(False)
        window.set_position(gtk.WIN_POS_MOUSE)
        window.set_border_width(10)
        Entry = gtk.Entry()
        Entry.set_editable(True)
        Entry.set_activates_default(True)
        Entry.set_visibility(True)
        old_label = self.label.get_label()
        Entry.set_text(old_label)
        Entry.show()
        def on_key_press(w, e):
            if is_key(e, 'Escape'):
                window.hide()
                Entry.set_text(old_label)
            elif is_key(e, 'Return'):
                window.hide()
                new_label = Entry.get_text()
                if new_label:
                    self.label.set_label(new_label)
        def on_focus_out(*a):
            window.hide()
            Entry.set_text(old_label)
        window.connect("key_press_event", on_key_press)
        window.connect("focus-out-event", on_focus_out)
        window.add(Entry)
        window.show_all()
        
    def clear_tree(self, tree):
        print "in"
        tree.clear()
        n = self.get_current_page()
        FC().cache_music_tree_beans[n] = []
        FC().music_paths[n] = []
        self.controls.update_music_tree(tree, n)
        