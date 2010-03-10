'''
Created on Mar 11, 2010

@author: ivan
'''
import gtk
import gobject

class DirectoryModel():
    POS_NAME = 0
    POS_PATH = 1
    POS_FONT = 2
    POS_VISIBLE = 3
    POS_TYPE = 4
    
    def __init__(self, widget):
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

class DirectoryBeen():
    TYPE_FOLDER = "TYPE_FOLDER"
    TYPE_FILE = "TYPE_FILE"
    TYPE_URL = "TYPE_URL"
    
    def __init__(self, name, path, font, is_visible, type):
        if name: self.name = name
        if path: self.path = path
        if font: self.font = font
        if is_visible: self.is_visible = is_visible
        if type: self.type = type       
    

