'''
Created on Sep 27, 2010

@author: ivan
'''
from gi.repository import Gtk
import logging



class MyToolbar(Gtk.Toolbar):
    def __init__(self):
        rc_st = '''
        style "toolbar-style" {
            GtkToolbar::shadow_type = none
            }
        class "GtkToolbar" style "toolbar-style"
        '''
        Gtk.rc_parse_string(rc_st)

        Gtk.Toolbar.__init__(self)

        self.show()
        self.set_style(Gtk.ToolbarStyle.ICONS)
        self.set_show_arrow(False)
        self.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)

        self.i = 0

    def add_button(self, tooltip, gtk_stock, func, param):
        button = Gtk.ToolButton(gtk_stock)
        button.show()
        button.set_tooltip_text(tooltip)

        logging.debug("Button-Controls-Clicked" + str(tooltip)+ str(gtk_stock) + str(func) + str(param))
        if func and param:
            button.connect("clicked", lambda * a: func(param))
        elif func:
            button.connect("clicked", lambda * a: func())

        self.insert(button, self.i)
        self.i += 1

    def add_separator(self):
        sep = Gtk.SeparatorToolItem.new()
        sep.show()
        self.insert(sep, self.i)
        self.i += 1

class ToolbarSeparator(MyToolbar):
    def __init__(self):
        MyToolbar.__init__(self)
        self.add_separator()
