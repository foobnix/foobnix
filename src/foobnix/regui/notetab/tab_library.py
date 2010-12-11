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
              
               
