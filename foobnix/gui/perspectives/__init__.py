
__author__ = 'popsul'

from gi.repository import Gtk
from gi.repository import GObject
from foobnix.gui.state import LoadSave, Quitable


class BasePerspective(GObject.GObject, LoadSave):
    """
    Base class for the perspectives
    """

    def __init__(self):
        super(BasePerspective, self).__init__()

    def get_icon(self):
        raise NotImplementedError()

    def get_widget(self):
        raise NotImplementedError()

    def get_name(self):
        raise NotImplementedError()

    def get_tooltip(self):
        raise NotImplementedError()

    def get_id(self):
        raise NotImplementedError()

    def on_load(self):
        raise NotImplementedError()

    def on_save(self):
        raise NotImplementedError()

GObject.signal_new("activated", BasePerspective, GObject.SIGNAL_RUN_LAST, None, ())
GObject.signal_new("deactivated", BasePerspective, GObject.SIGNAL_RUN_LAST, None, ())


class StackableWidget(Gtk.Notebook):

    def __init__(self):
        super(StackableWidget, self).__init__()
        self.set_property("show-tabs", False)

        self.connect("page-added", self.on_add_widget)
        self.connect("page-removed", self.on_remove_widget)

    def on_add_widget(self, c, widget, num):
        pass
        #for child in self.get_children():
        #    if child.is_visible():
        #        return
        #widget.show()

    def on_remove_widget(self, c, widget, num):
        pass

    def get_active_index(self):
        return self.get_current_page()

    def set_active_by_index(self, index):
        print("active by index", index)
        page = self.get_nth_page(index)
        if page and not page.get_visible():
            page.set_visible(True)
        self.set_current_page(index)
        print("now active", self.get_active_index())

    def add(self, widget):
        widget.show()
        return super(StackableWidget, self).append_page(widget, None)


class OneButtonToggled():

    def __init__(self, buttons=None):
        self.buttons = []

        if buttons:
            for button in buttons:
                self.add_button(button)

    def add_button(self, button):
        assert isinstance(button, Gtk.Button)
        self.buttons.append(button)
        button.connect("toggled", self.on_toggle)

    def on_toggle(self, clicked_button):
        for button in self.buttons:
            if button != clicked_button:
                button.set_active(False)

        if all([not button.get_active() for button in self.buttons]):
            clicked_button.set_active(True)

        # if the button should become unchecked, then do nothing
        if not clicked_button.get_active():
            return