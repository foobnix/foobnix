'''
Created on Aug 26, 2010

@author: ivan
'''
import gtk
class Popup():
    
    def __init__(self):        
        self.menu = gtk.Menu()
    
    def get_menu(self):
        return self.menu    
    
    def add_item(self, text, gtk_stock, func, arg=None):            
        item = gtk.ImageMenuItem(text)
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        item.set_image(img) 
        if arg:    
            item.connect("activate", lambda * a: func(arg))
        else:
            item.connect("activate", lambda * a: func())
        self.menu.add(item)
    
    def show(self, event):
        self.menu.show_all()
        self.menu.popup(None, None, None, event.button, event.time) 

