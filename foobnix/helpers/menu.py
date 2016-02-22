'''
Created on Aug 26, 2010

@author: ivan
'''

from gi.repository import Gtk
from foobnix.gui.menu import MyMenu

import time


class Popup(Gtk.Menu):

    def __init__(self, *args, **kwargs):
        Gtk.Menu.__init__(self, *args, **kwargs)

    def add_separator(self):
        separator = Gtk.SeparatorMenuItem.new()
        separator.show()
        self.append(separator)

    def add_item(self, title, icon_name, func=None, param=None):
        item = Gtk.MenuItem.new()
        item_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)

        if icon_name:
            img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            item_box.pack_start(img, False, False, 0)
        item_box.pack_start(Gtk.Label.new(title), False, False, 0)

        item.add(item_box)
        item.show_all()

        if func and param:
            item.connect("activate", lambda * a: func(param))
        elif func:
            item.connect("activate", lambda * a: func())
        self.append(item)
        return item

    def add_image_item(self, title, icon_name, func=None, param=None):
        item = Gtk.MenuItem.new()
        item_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)

        if icon_name:
            img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            item_box.pack_start(img, False, False, 0)
        item_box.pack_start(Gtk.Label.new(title), False, False, 0)

        item.add(item_box)
        item.show_all()

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
