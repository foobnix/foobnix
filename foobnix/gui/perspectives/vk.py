
__author__ = 'popsul'

import thread
from gi.repository import Gtk
from foobnix.gui.state import Filterable
from foobnix.gui.perspectives import BasePerspective
from foobnix.gui.treeview.vk_integration_tree import VKIntegrationControls


class VKPerspective(BasePerspective, Filterable):

    def __init__(self, controls):
        super(VKPerspective, self).__init__()
        self.widget = VKIntegrationControls(controls)

        self.connect("activated", self.on_activated)

    def on_activated(self, perspective):
        thread.start_new_thread(self.widget.lazy_load, ())

    def get_id(self):
        return "vk"

    def get_icon(self):
        return "format-indent-less"

    def get_name(self):
        return _("VK")

    def get_tooltip(self):
        return _("VK Panel (Alt+6)")

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
        pass
