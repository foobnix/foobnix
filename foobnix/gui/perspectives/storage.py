
__author__ = 'popsul'

from gi.repository import Gtk
from gi.repository import GObject
from foobnix.gui.state import Quitable, Filterable
from foobnix.gui.perspectives import BasePerspective
from foobnix.gui.treeview.virtual_tree import VirtualTreeControl


class StoragePerspective(BasePerspective, Quitable, Filterable):

    def __init__(self, controls):
        super(StoragePerspective, self).__init__()
        self.widget = VirtualTreeControl(controls)

    def get_id(self):
        return "storage"

    def get_icon(self):
        return Gtk.STOCK_INDEX

    def get_name(self):
        return _("Storage")

    def get_tooltip(self):
        return _("Storage (Alt+3)")

    def get_widget(self):
        return self.widget.scroll

    ## LoadSave implementation
    def on_load(self):
        self.widget.on_load()

    def on_save(self):
        self.widget.on_save()

    ## Quitable implementation
    def on_quit(self):
        self.widget.on_quit()

    ## Filterable implementation
    def filter_by_file(self, value):
        self.widget.filter_by_file(value)

    def filter_by_folder(self, value):
        self.widget.filter_by_folder(value)
