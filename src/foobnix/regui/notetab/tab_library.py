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
        self.menu.add_item(_("Rename tab"), "", self.on_rename_tab, None)
        self.menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, self.on_update_music_tree, None)
        self.menu.add_item(_("Add folder"), gtk.STOCK_OPEN, self.on_add_folder, None)
        self.menu.add_item(_("Add folder in new tab"), gtk.STOCK_OPEN, lambda : self.on_add_folder(True), None)
        self.menu.add_item(_("Clear Music Tree"), gtk.STOCK_OPEN, self.clear_tree, None)       
                   
        vbox.pack_start(self.button(tree), False, False)
        vbox.pack_start(self.label, False, False)
        event = gtk.EventBox()
        event.add(vbox)
        
        """change style of event"""
        event.set_style(self.change_event_style(event))
        
        def on_active(*a):
            n = self.page_num(tree.scroll)
            self.set_current_page(n)
        
        event.connect("button-press-event", on_active)
        event.show_all()             
                    
        self.prepend_page(tree.scroll, event)
        self.set_tab_reorderable(tree.scroll, True)
        
        self.show_all()
        
        """only after show_all() function"""
        self.set_current_page(0)
    
    def change_event_style(self, event):
        style = event.get_style().copy()
        colour = style.bg[gtk.STATE_NORMAL]
        style.bg[gtk.STATE_ACTIVE] = colour
        return style     
    
    def button(self, tree):
            if FC().tab_close_element == "button":
                return tab_close_button(func=self.on_delete_tab, arg=tree.scroll)
            else:
                return notetab_label(func=self.on_delete_tab, arg=tree.scroll, angel=90)
        
    def reorder_callback(self, notebook, child, new_page_num):
        for list in [FC().music_paths, FC().tab_names, FC().cache_music_tree_beans]:
            reorderer_list(list, new_page_num, self.page_number, )
        
    def get_page_number(self, *a):
            self.page_number = self.get_current_page()
              
    def on_rename_tab(self):
        
        """get old label value"""
        n = self.get_current_page()
        scrolled_tree = self.get_nth_page(n)
        eventbox = self.get_tab_label(scrolled_tree)
        old_vbox = eventbox.get_child()
        if len(old_vbox.get_children()) == 1:
            label_object = old_vbox.get_children()[0]
        else:
            label_object = old_vbox.get_children()[1]
        old_label = label_object.get_label()
        
        window = gtk.Window()
        window.set_decorated(False)
        window.set_position(gtk.WIN_POS_MOUSE)
        window.set_border_width(5)
        entry = gtk.Entry()
        entry.set_text(old_label)
        entry.show()
        
        def on_key_press(w, e):
            if is_key(e, 'Escape'):
                window.hide()
                entry.set_text(old_label)
            elif is_key(e, 'Return'):
                window.hide()
                new_label = entry.get_text()
                if new_label:
                    label = gtk.Label(new_label + ' ')
                    label.set_angle(90)
                    new_vbox = gtk.VBox()
                    if len(old_vbox.get_children()) > 1:
                        new_vbox.pack_start(self.button(scrolled_tree.get_child()), False, False)
                    new_vbox.pack_start(label, False, False)
                    event = gtk.EventBox()
                    event.add(new_vbox)
                    event.set_style(self.change_event_style(event))
                    event.show_all()
                    self.set_tab_label(scrolled_tree, event)
                    FC().tab_names[n] = new_label
        
        def on_focus_out(*a):
            window.hide()
            entry.set_text(old_label)
            
        window.connect("key_press_event", on_key_press)
        window.connect("focus-out-event", on_focus_out)
        window.add(entry)
        window.show_all()
        
    def on_add_folder(self, in_new_tab = False):
        n = self.get_current_page()
        tree = self.get_current_tree(n)
        tree.add_folder(in_new_tab)
        
    def clear_tree(self):
        n = self.get_current_page()
        tree = self.get_current_tree(n)
        tree.clear()
        
        FC().cache_music_tree_beans[n] = []
        FC().music_paths[n] = []
        self.controls.update_music_tree(tree, n)
    
    def on_update_music_tree(self):
        n = self.get_current_page()
        tree = self.get_current_tree(n)
        self.controls.update_music_tree(tree, n)
         
    def get_current_tree(self, number_of_page):
        scrolled_tree = self.get_nth_page(number_of_page)
        tree = scrolled_tree.get_child()
        return tree  