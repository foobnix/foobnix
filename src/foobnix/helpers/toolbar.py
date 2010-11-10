'''
Created on Sep 27, 2010

@author: ivan
'''
import gtk
from foobnix.util import LOG
class MyToolbar(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)            
        self.show()
        self.set_style(gtk.TOOLBAR_ICONS)
        self.set_show_arrow(False)
        self.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
         
        self.i = 0
    
    def add_button(self, tooltip, gtk_stock, func, param):
        button = gtk.ToolButton(gtk_stock)
        button.show()  
        button.set_tooltip_text(tooltip)
        
        LOG.debug("Button-Controls-Clicked", tooltip, gtk_stock, func, param)
        if func and param:             
            button.connect("clicked", lambda * a: func(param))
        elif func:
            button.connect("clicked", lambda * a: func())     
                
        self.insert(button, self.i)
        self.i += 1        
    
    def add_separator(self):
        sep = gtk.SeparatorToolItem()
        sep.show()        
        self.insert(sep, self.i)
        self.i += 1

class ToolbarSeparator(MyToolbar):
    def __init__(self):
        MyToolbar.__init__(self)
        self.add_separator()
