
__author__ = 'popsul'

from gi.repository import Gtk
from gi.repository import GObject
from foobnix.gui.perspectives import BasePerspective
from foobnix.gui.treeview.radio_tree import RadioTreeControl


class RadioPerspective(BasePerspective):

    def __init__(self, controls):
        super(RadioPerspective, self).__init__()
        self.widget = RadioTreeControl(controls)

    def get_id(self):
        return "radio"

    def get_icon(self):
        return Gtk.STOCK_NETWORK

    def get_name(self):
        return _("Radio")

    def get_tooltip(self):
        return _("Radio Stantions (Alt+2)")

    def get_widget(self):
        return self.widget.scroll

    def on_load(self):
        pass

    def on_save(self):
        pass
