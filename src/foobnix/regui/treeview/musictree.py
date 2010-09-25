#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
class MusicTreeControl(TreeViewControl, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        TreeViewControl.__init__(self)
        
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn("Music Lybrary", gtk.CellRendererText(), text=self.text, font=self.font)
        column.set_resizable(True)
        self.append_column(column)
    
    def append(self, bean):           
        return super(MusicTreeControl, self).append(level=bean.level, text=bean.text, visible=True, font=bean.font, play_icon=None, time=bean.time)
  
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            bean = self.get_selected_bean()
            self.controls.append_to_notebook(bean.text, [bean])
            print "double left"
      
    def populate_from_scanner(self, beans):
        self.model.clear()
        hash = {None:None}
        for bean in beans:
            if hash.has_key(bean.level):
                level = hash[bean.level]
            else:
                level = None

            if bean.is_file:
                child_level = self.append(bean.add_font("normal").add_level(level))
            else:
                child_level = self.append(bean.add_font("bold").add_level(level))
                
            hash[bean.path] = child_level
    def on_load(self):
        pass
    
    def on_save(self):
        pass
