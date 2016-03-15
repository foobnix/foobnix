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

        self.i = 0

    def add_button(self, tooltip, icon_name, func, param):
        button = Gtk.ToolButton.new(Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR), None)
        button.show()
        button.set_tooltip_text(tooltip)

        logging.debug("Button-Controls-Clicked" + " | Tooltip: " + str(tooltip) + " | Icon: " +  str(icon_name) + " | Function: " +  func.__name__ + " | Parameters: " +  str(param))
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
