
__author__ = 'popsul'

from gi.repository import Gtk
from gi.repository import GObject
from foobnix.gui.state import Filterable
from foobnix.gui.perspectives import BasePerspective
from foobnix.gui.treeview.radio_tree import RadioTreeControl


class RadioPerspective(BasePerspective, Filterable):

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

    ## LoadSave implementation
    def on_load(self):
        pass

    def on_save(self):
        pass

    ## Filterable implementation
    def filter_by_folder(self, value):
        self.widget.filter_by_folder(value)

    def filter_by_file(self, value):
        self.widget.filter_by_file(value)
