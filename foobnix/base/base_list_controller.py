'''
Created on 20.04.2010

@author: ivan
'''
import gtk
from foobnix.util.mouse_utils import is_double_click
class BaseListController():
    POSITION_0 = 0
    def __init__(self, widget):
        self.widget = widget
        self.model = gtk.ListStore(str)
        
        self.title = None
        self.column = gtk.TreeViewColumn(self.title, gtk.CellRendererText(), text=0)
        self.widget.append_column(self.column)        
        self.widget.set_model(self.model)
        
        self.widget.connect("button-press-event", self.__button_press)
    
    
    def set_title(self, title):
        self.column.set_title(title)
    
    def __button_press(self,w,e):
        if is_double_click(e):
            self.on_duble_click()
    
    def on_duble_click(self):
        pass
    
    
    def get_selected_item(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        return self._get_item_by_iter(selected)
    
    def _get_item_by_iter(self, iter):
        if iter:            
            item_value = self.model.get_value(iter, self.POSITION_0)
        return item_value    

    def add_item(self, value):
        self.model.append([value])
    
    def clear(self):
        self.model.clear()            
        
    
        
    
    