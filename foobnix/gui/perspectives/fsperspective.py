
__author__ = 'popsul'

from gi.repository import Gtk
from gi.repository import GObject
from foobnix.gui.perspectives import BasePerspective
from foobnix.gui.notetab.tab_library import TabHelperControl


class FSPerspective(BasePerspective):

    def __init__(self, controls):
        super(FSPerspective, self).__init__()
        self.notetab = TabHelperControl(controls)

    def get_tabhelper(self):
        ## temporary duplicate for get_widget()
        return self.notetab

    def hide_add_button(self):
        ## TODO: implement it!
        pass

    def show_add_button(self):
        ## TODO: implement it!
        pass

    def get_id(self):
        return "fs"

    def get_icon(self):
        return Gtk.STOCK_HARDDISK

    def get_name(self):
        return _("Music")

    def get_tooltip(self):
        return _("Music Navigation (Alt+1)")

    def get_widget(self):
        return self.notetab

    def on_load(self):
        self.notetab.on_load()

    def on_save(self):
        self.notetab.on_save()
