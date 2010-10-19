'''
Created on Sep 29, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
from foobnix.regui.treeview import TreeViewControl
from foobnix.util.mouse_utils import is_double_left_click
import gtk
class RadioTreeControl(TreeViewControl, LoadSave):
    def __init__(self, controls):
        TreeViewControl.__init__(self, controls)
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn("Radio Lybrary", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        self.set_type_tree()
    
             
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            current = self.get_selected_bean()
            if current.is_file:
                self.controls.notetabs.append_tab(current.text, [current])
            else:
                """folder"""
                beans = self.get_child_level1_beans_by_selected()
                self.controls.notetabs.append_tab(current.text, beans)
                
      
    def on_load(self):
        self.scroll.hide()
        pass
    
    def on_save(self):
        pass
