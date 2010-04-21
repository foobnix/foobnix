'''
Created on 20.04.2010

@author: ivan
'''
import gtk
from foobnix.util.mouse_utils import is_double_click

"""Base list controller for similar functional on any listview or treeview"""
class BaseListController():
    POSITION_NAME = 0
    def __init__(self, widget):
        self.widget = widget
        self.model = gtk.ListStore(str)
        
        self.title = None
        self.column = gtk.TreeViewColumn(self.title, gtk.CellRendererText(), text=0)
        self.widget.append_column(self.column)        
        self.widget.set_model(self.model)
        
        self.widget.connect("button-press-event", self.__on_button_press)
        self.widget.connect("drag-end", self.__on_drag_end)
    
    
    def set_title(self, title):
        self.column.set_title(title)
    
    def __on_drag_end(self, *args):
        self.on_drag()
    
    def __on_button_press(self,w,e):
        if is_double_click(e):
            self.on_duble_click()
    
    def on_drag(self):
        pass
    
    def on_duble_click(self):
        pass
    
    def get_item_by_position(self, position):        
        return self.model[position][self.POSITION_NAME]
    
    def get_all_items(self):
        items = []
        for item in self.model:              
            item = item[self.POSITION_NAME]
            items.append(item)        
        return items        
    
    def get_selected_item(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        return self._get_item_by_iter(selected)
    
    def _get_item_by_iter(self, iter):
        if iter:            
            item_value = self.model.get_value(iter, self.POSITION_NAME)
        return item_value    

    def add_item(self, value):                
        self.model.append([value])
    
    def clear(self):
        self.model.clear()            
        
    
        
    
    