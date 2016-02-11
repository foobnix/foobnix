
__author__ = 'popsul'

from gi.repository import Gtk
from foobnix.gui.state import Filterable, Quitable
from foobnix.gui.perspectives import BasePerspective, StackableWidget
from foobnix.gui.treeview.radio_tree import RadioTreeControl, MyRadioTreeControl


class RadioPerspective(BasePerspective, Filterable, Quitable):

    def __init__(self, controls):
        super(RadioPerspective, self).__init__()

        self.auto_radio = RadioTreeControl(controls)
        self.my_radio = MyRadioTreeControl(controls)

        self.switch_button = Gtk.Button.new()
        self.switch_button.connect("clicked", self.switch_radio)

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.radios = StackableWidget()
        self.radios.add(self.auto_radio.scroll)
        self.radios.add(self.my_radio.scroll)

        self.vbox.pack_start(self.radios, True, True, 0)
        self.vbox.pack_start(self.switch_button, False, False, 0)
        self.vbox.show_all()

        self.update_button_label()

    def switch_radio(self, *args):
        index = self.radios.get_active_index()
        new_index = abs(index - 1)
        self.radios.set_active_by_index(new_index)
        self.update_button_label()

    def update_button_label(self):
        index = self.radios.get_active_index()
        radio = self.radios.get_nth_page(index)
        self.switch_button.set_label(radio.get_child().switcher_label)

    def get_id(self):
        return "radio"

    def get_icon(self):
        return "network-idle"

    def get_name(self):
        return _("Radio")

    def get_tooltip(self):
        return _("Radio Stantions (Alt+2)")

    def get_widget(self):
        return self.vbox

    ## LoadSave implementation
    def on_load(self):
        self.auto_radio.on_load()
        self.my_radio.on_load()

    def on_save(self):
        self.auto_radio.on_save()
        self.my_radio.on_save()

    ## Quitable implementation
    def on_quit(self):
        self.auto_radio.on_quit()
        self.my_radio.on_quit()

    ## Filterable implementation
    def filter_by_folder(self, value):
        self.auto_radio.filter_by_folder(value)
        self.my_radio.filter_by_folder(value)

    def filter_by_file(self, value):
        self.auto_radio.filter_by_file(value)
        self.my_radio.filter_by_file(value)
