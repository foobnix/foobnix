'''
Created on Mar 11, 2010

@author: ivan
'''
import gtk
import gobject
from foobnix.model.entity import DirectoryBean

class DirectoryModel():
    POS_NAME = 0
    POS_PATH = 1
    POS_FONT = 2
    POS_VISIBLE = 3
    POS_TYPE = 4
    
    def __init__(self, widget):
        self.widget = widget
        column = gtk.TreeViewColumn("Title", gtk.CellRendererText(), text=0, font=2)
        column.set_resizable(True)
        widget.append_column(column)
        self.model =gtk.TreeStore(str, str, str, gobject.TYPE_BOOLEAN, str)
                
        filter = self.model.filter_new()
        filter.set_visible_column(self.POS_VISIBLE)
        widget.set_model(filter)
        
    def append(self, level, been):
        return self.model.append(level, [been.name, been.path, been.font, been.is_visible, been.type])
        
    def clear(self):
        self.model.clear() 
        
    def getSelectedBean(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        if selected:
            name = model.get_value(selected, self.POS_NAME)
            path = model.get_value(selected, self.POS_PATH)
            type = model.get_value(selected, self.POS_TYPE)
            font = model.get_value(selected, self.POS_FONT)
            visible = model.get_value(selected, self.POS_VISIBLE)
        return DirectoryBean(name, path, font, visible, type);                                 
    

