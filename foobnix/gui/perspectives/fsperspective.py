
__author__ = 'popsul'

from gi.repository import Gtk
from foobnix.util import idle_task
from foobnix.gui.state import Filterable
from foobnix.gui.perspectives import BasePerspective
from foobnix.helpers.my_widgets import ButtonStockText
from foobnix.gui.notetab.tab_library import TabHelperControl


class FSPerspective(BasePerspective, Filterable):

    def __init__(self, controls):
        super(FSPerspective, self).__init__()
        self.tabhelper = TabHelperControl(controls)
        self.vbox = Gtk.VBox(False, 0)

        self.add_button = ButtonStockText(_(" Add Folder(s) in tree"), "list-add")
        self.add_button.connect("clicked", lambda * a: self.tabhelper.get_current_tree().add_folder())

        self.vbox.pack_start(self.add_button, False, False, 0)
        self.vbox.pack_start(self.tabhelper, True, True, 0)
        self.vbox.show_all()

    def get_tabhelper(self):
        ## temporary duplicate for get_widget()
        return self.tabhelper

    @idle_task
    def hide_add_button(self):
        self.add_button.hide()

    @idle_task
    def show_add_button(self):
        self.add_button.show()

    def get_id(self):
        return "fs"

    def get_icon(self):
        return "drive-harddisk"

    def get_name(self):
        return _("Music")

    def get_tooltip(self):
        return _("Music Navigation (Alt+1)")

    def get_widget(self):
        return self.vbox

    ## LoadSave implementation
    def on_load(self):
        self.tabhelper.on_load()

    def on_save(self):
        self.tabhelper.on_save()

    ## Filterable implementation
    def filter_by_file(self, value):
        self.tabhelper.get_current_tree().filter_by_file(value)

    def filter_by_folder(self, value):
        self.tabhelper.get_current_tree().filter_by_folder(value)
