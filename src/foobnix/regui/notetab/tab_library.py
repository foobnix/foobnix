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
from foobnix.util.tab_utils import get_text_label_from_tab

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
        
    def on_button_press(self, w, e):
        if e.button == 3:
            w.menu.show_all()
            w.menu.popup(None, None, None, e.button, e.time)
          
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
                
        if FC().tab_close_element:      
            vbox.pack_start(self.button(tree.scroll), False, False)
        vbox.pack_start(self.label, False, False)
        event = gtk.EventBox()
        event.add(vbox)
        
        event.set_visible_window(False)
        
        event = self.tab_menu_creator(event, tree.scroll)
                
        event.connect("button-press-event", self.on_button_press)        
        
        event.show_all()             
                    
        self.prepend_page(tree.scroll, event)
        self.set_tab_reorderable(tree.scroll, True)
        
        self.show_all()
        
        """only after show_all() function"""
        self.set_current_page(0)
    
        
    def tab_menu_creator(self, widget, tab_child):
        widget.menu = Popup()
        widget.menu.add_item(_("Rename tab"), "", lambda: self.on_rename_tab(tab_child), None)
        widget.menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, lambda: self.on_update_music_tree(tab_child), None)
        widget.menu.add_item(_("Add folder"), gtk.STOCK_OPEN, self.on_add_folder, None)
        widget.menu.add_item(_("Add folder in new tab"), gtk.STOCK_OPEN, lambda : self.on_add_folder(True), None)
        widget.menu.add_item(_("Clear Music Tree"), gtk.STOCK_CLEAR, lambda : self.clear_tree(tab_child), None)
        widget.menu.add_item(_("Close tab"), gtk.STOCK_CLOSE, lambda: self.on_delete_tab(tab_child), None)
        return widget
    
    def button(self, tab_child):
            if FC().tab_close_element == "button":
                return tab_close_button(func=self.on_delete_tab, arg=tab_child)
            elif FC().tab_close_element == "label":
                return notetab_label(func=self.on_delete_tab, arg=tab_child, angel=90)
                    
    def reorder_callback(self, notebook, child, new_page_num):
        for list in [FC().music_paths, FC().tab_names, FC().cache_music_tree_beans]:
            reorderer_list(list, new_page_num, self.page_number, )
        
    def get_page_number(self, *a):
            self.page_number = self.get_current_page()
              
    def on_rename_tab(self, tab_child):
        
        """get old label value"""
        n = self.page_num(tab_child)
        old_label_text, vbox_lenth = get_text_label_from_tab(self, tab_child, True)
        
        window = gtk.Window()
        window.set_decorated(False)
        window.set_position(gtk.WIN_POS_MOUSE)
        window.set_border_width(5)
        entry = gtk.Entry()
        entry.set_text(old_label_text)
        entry.show()
        
        def on_key_press(w, e):
            if is_key(e, 'Escape'):
                window.hide()
                entry.set_text(old_label_text)
            elif is_key(e, 'Return'):
                window.hide()
                new_label_text = entry.get_text()
                if new_label_text:
                    label = gtk.Label(new_label_text + ' ')
                    label.set_angle(90)
                    new_vbox = gtk.VBox()
                    if vbox_lenth > 1:
                        new_vbox.pack_start(self.button(tab_child.get_child()), False, False)
                    new_vbox.pack_start(label, False, False)
                    event = gtk.EventBox()
                    event.add(new_vbox)
                    event = self.tab_menu_creator(event, tab_child)
                    event.set_style(self.change_event_style(event))
                    event.connect("button-press-event", self.on_button_press)
                    event.show_all()
                    self.set_tab_label(tab_child, event)
                    FC().tab_names[n] = new_label_text
        
        def on_focus_out(*a):
            window.hide()
            entry.set_text(old_label_text)
            
        window.connect("key_press_event", on_key_press)
        window.connect("focus-out-event", on_focus_out)
        window.add(entry)
        window.show_all()
        
    def on_add_folder(self, in_new_tab = False):
        n = self.get_current_page()
        tree = self.get_current_tree(n)
        tree.add_folder(in_new_tab)
        
    def clear_tree(self, tab_child):
        n = self.page_num(tab_child)
        tree = tab_child.get_child()
        tree.clear()
        FC().cache_music_tree_beans[n] = []
        FC().music_paths[n] = []
        self.controls.update_music_tree(tree, n)
    
    def on_update_music_tree(self, tab_child):
        n = self.page_num(tab_child)
        tree = tab_child.get_child()
        self.controls.update_music_tree(tree, n)
        
    def get_current_tree(self, number_of_page):
        scrolled_tree = self.get_nth_page(number_of_page)
        tree = scrolled_tree.get_child()
        return tree
    
    