'''
Created on Sep 28, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
from foobnix.regui.treeview import TreeViewControl
from foobnix.regui.model.signal import FControl
import gtk

class SimpleTreeControl(TreeViewControl, LoadSave):
    def __init__(self, title_name, controls):        
        TreeViewControl.__init__(self, controls)
        
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn(title_name, gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        
    def on_load(self):
        pass
    
    def on_save(self):
        pass