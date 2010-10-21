'''
Created on Sep 29, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
from foobnix.util.mouse_utils import is_double_left_click
import gtk
from foobnix.regui.treeview.common_tree import CommonTreeControl
class RadioTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn("Radio Lybrary", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)
        
        self.configure_send_drug()

        self.set_type_tree()
    
             
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            selected = self.get_selected_bean()
            print "selected", selected
            beans = self.get_all_child_beans_by_selected()  
            self.controls.append_to_new_notebook(selected.text, [selected] + beans)
                
      
    def on_load(self):
        self.scroll.hide()
        pass
    
    def on_save(self):
        pass
