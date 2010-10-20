'''
Created on Sep 28, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
import gtk
from foobnix.regui.treeview.common_tree import CommonTreeControl

class SimpleTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, title_name, controls):        
        CommonTreeControl.__init__(self, controls)
        
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn(title_name, gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        self.set_headers_visible(False)
        
        self.configure_send_drug()
        
        self.set_type_plain()
        
    def on_load(self):
        pass
    
    def on_save(self):
        pass
