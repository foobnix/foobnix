'''
Created on Aug 26, 2010

@author: ivan
'''
from gi.repository import Gtk
import time
from foobnix.gui.menu import MyMenu
class Popup(Gtk.Menu):
    
    def __init__(self):        
        Gtk.Menu.__init__(self)
    
    def add_separator(self):
        separator = Gtk.SeparatorMenuItem()
        separator.show()
        self.append(separator)
    
    def add_item(self, text, gtk_stock="", func=None, arg=None):            
        item = Gtk.ImageMenuItem(text)
        if gtk_stock:
            img = Gtk.Image.new_from_stock(gtk_stock, Gtk.IconSize.MENU)
            item.set_image(img) 
        if func and arg:    
            item.connect("activate", lambda * a: func(arg))
        elif func:
            item.connect("activate", lambda * a: func())
        self.add(item)
        item.show()
        return item
        
    def add_image_item(self, title, gtk_stock, func=None, param=None):
        item = Gtk.ImageMenuItem(title)
        
        item.show()
        if gtk_stock:
            img = Gtk.Image.new_from_stock(gtk_stock, Gtk.IconSize.MENU)
            item.set_image(img)

        if func and param:
            item.connect("activate", lambda * a: func(param))
        elif func:
            item.connect("activate", lambda * a: func())
            
        self.append(item)
        return item
    
    def show(self, event):
        self.show_all()
        self.popup(None, None, lambda menu, data: (event.get_root_coords()[0], event.get_root_coords()[1], True), None, event.button, event.time) 
    
    def show_widget(self, w):
        self.show_all()
        self.popup(None, None, None, 3, long(time.time()))

    def add_submenu(self, title):
        menu = MyMenu()
        menu.show()

        file_item = Gtk.MenuItem(title)
        file_item.show()

        file_item.set_submenu(menu)
        self.append(file_item)
        return menu

    def clear(self):
        for w in self.get_children():
            self.remove(w)
            w.destroy()
