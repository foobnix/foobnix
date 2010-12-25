'''
Created on Aug 26, 2010

@author: ivan
'''
import gtk
import time
from foobnix.regui.menu import MyMenu
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
        return item
        
    def add_image_item(self, title, gtk_stock, func=None, param=None):
        item = gtk.ImageMenuItem(title)
        
        item.show()
        if gtk_stock:
            img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
            item.set_image(img)

        if func and param:
            item.connect("activate", lambda * a: func(param))
        elif func:
            item.connect("activate", lambda * a: func())
            
        self.append(item)
        return item
    
    def show(self, event):
        self.show_all()
        self.popup(None, None, None, event.button, event.time) 
    
    def show_widget(self, w):
        self.show_all()
        self.popup(None, None, None, 3, long(time.time()))

    def add_submenu(self, title):
        menu = MyMenu()
        menu.show()

        file_item = gtk.MenuItem(title)
        file_item.show()

        file_item.set_submenu(menu)
        self.append(file_item)
        return menu
