#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.regui.state import LoadSave
class MusicTreeControl(TreeViewControl, LoadSave):
    def __init__(self, controls):
        TreeViewControl.__init__(self, controls)
        
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn("Music Lybrary", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            bean = self.get_selected_bean()
            self.controls.append_to_notebook(bean.text, [bean])
            print "double left"
      
    def on_load(self):
        pass
    
    def on_save(self):
        pass
