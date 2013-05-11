
__author__ = 'popsul'

from gi.repository import Gtk
from gi.repository import GObject
from foobnix.gui.state import LoadSave, Quitable
from foobnix.gui.perspectives import StackableWidget, BasePerspective, OneButtonToggled
from foobnix.helpers.my_widgets import PerspectiveButton


class Controller(Gtk.VBox, LoadSave, Quitable):

    def __init__(self):
        super(Controller, self).__init__(False, 0)

        self.perspectives_container = StackableWidget()
        self.button_container = Gtk.HBox(False, 0)
        self.button_controller = OneButtonToggled()
        self.perspectives = {}
        ## internal property
        self._perspectives = []

        self.pack_start(self.perspectives_container, True, True, 0)
        self.pack_start(self.button_container, False, False, 0)

        ## insert dummy page
        self.perspectives_container.add(Gtk.Label(""))
        self.show_all()

    def attach_perspective(self, perspective):
        assert isinstance(perspective, BasePerspective)
        perspective_id = perspective.get_id()
        self.perspectives[perspective_id] = perspective
        self._perspectives.append(perspective)
        widget = perspective.get_widget()
        perspective.widget_id = self.perspectives_container.add(widget)
        print ("perspective added", perspective, perspective.widget_id, widget)
        button = PerspectiveButton(perspective.get_name(), perspective.get_icon(), perspective.get_tooltip())

        def toggle_handler(btn, handler, *args):
            if btn.get_active():
                handler()
        button.connect("toggled", toggle_handler, lambda *a: self.activate_perspective(perspective_id))
        perspective.button = button
        self.button_container.pack_start(button, False, False, 0)
        self.button_controller.add_button(button)

    def activate_perspective(self, perspective_id):
        if self.is_activated(perspective_id):
            print(perspective_id, "is activated")
            return
        perspective = self.get_perspective(perspective_id)
        assert perspective
        for _id in self.perspectives.keys():
            if self.is_activated(_id):
                self.get_perspective(_id).emit("deactivated")
        self.perspectives_container.set_active_by_index(perspective.widget_id)
        perspective.button.set_active(True)
        perspective.emit("activated")

    def is_activated(self, perspective_id):
        perspective = self.get_perspective(perspective_id)
        assert perspective
        print("widget id", perspective.widget_id, "active id", self.perspectives_container.get_active_index())
        return perspective.widget_id == self.perspectives_container.get_active_index()

    def get_perspective(self, perspective_id):
        if perspective_id in self.perspectives:
            return self.perspectives[perspective_id]
        return None

    def on_load(self):
        print("on load")
        for perspective in self._perspectives:
            if isinstance(perspective, LoadSave):
                perspective.on_load()
        self.activate_perspective(self._perspectives[0].get_id())

    def on_save(self):
        for perspective in self._perspectives:
            if isinstance(perspective, LoadSave):
                perspective.on_save()

    def on_quit(self):
        for perspective in self._perspectives:
            if isinstance(perspective, Quitable):
                perspective.on_quit()
