#-*- coding: utf-8 -*-
'''
Created on Dec 7, 2010

@author: zavlab1
'''

import gtk
from foobnix.util.fc import FC
#from foobnix.regui.model.signal import FControl
#from foobnix.helpers.my_widgets import tab_close_button, notetab_label
from foobnix.util.list_utils import reorderer_list
from foobnix.helpers.menu import Popup
from foobnix.regui.notetab import TabGeneral

class TabLib(TabGeneral):
    def __init__(self, controls):
        #gtk.Notebook.__init__(self)
        TabGeneral.__init__(self, controls)
        
        self.set_tab_pos(gtk.POS_LEFT)
        self.on_append_tab(self.controls.tree)
        #self.set_scrollable(True)
        
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
        vbox.pack_end(self.label, False, False)
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
        widget.menu.add_item(_("Rename tab"), "", lambda: self.on_rename_tab(tab_child, 90, FC().tab_names), None)
        widget.menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, lambda: self.on_update_music_tree(tab_child), None)
        widget.menu.add_item(_("Add folder"), gtk.STOCK_OPEN, lambda: self.on_add_folder(tab_child), None)
        widget.menu.add_item(_("Add folder in new tab"), gtk.STOCK_OPEN, lambda : self.on_add_folder(tab_child, True), None)
        widget.menu.add_item(_("Clear Music Tree"), gtk.STOCK_CLEAR, lambda : self.clear_tree(tab_child), None)
        widget.menu.add_item(_("Close tab"), gtk.STOCK_CLOSE, lambda: self.on_delete_tab(tab_child), None)
        return widget
    
    
                    
    def reorder_callback(self, notebook, child, new_page_num):
        for list in [FC().music_paths, FC().tab_names, FC().cache_music_tree_beans]:
            reorderer_list(list, new_page_num, self.page_number, )
        
    def get_page_number(self, *a):
            self.page_number = self.get_current_page()
              
            
    def on_add_folder(self, tab_child, in_new_tab = False):
        tree = tab_child.get_child()
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
    
    