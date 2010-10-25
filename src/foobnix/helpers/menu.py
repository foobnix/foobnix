'''
Created on Aug 26, 2010

@author: ivan
'''
import gtk
class Popup(gtk.Menu):
    
    def __init__(self):        
        gtk.Menu.__init__(self)
    
    def add_separator(self):
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.append(separator)
    
    def add_item(self, text, gtk_stock, func=None, arg=None):            
        item = gtk.ImageMenuItem(text)
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        item.set_image(img) 
        if func and arg:    
            item.connect("activate", lambda * a: func(arg))
        elif func:
            item.connect("activate", lambda * a: func())
        self.add(item)
    
    def show(self, event):
        self.show_all()
        self.popup(None, None, None, event.button, event.time) 

