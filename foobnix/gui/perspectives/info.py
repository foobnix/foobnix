
__author__ = 'popsul'

from gi.repository import Gtk
from foobnix.gui.state import Quitable
from foobnix.gui.perspectives import BasePerspective
from foobnix.gui.infopanel import InfoPanelWidget


class InfoPerspective(BasePerspective, Quitable):

    def __init__(self, controls):
        super(InfoPerspective, self).__init__()
        self.widget = InfoPanelWidget(controls)

    def update(self, bean):
        self.widget.update(bean)

    def clear(self):
        self.widget.clear()

    def get_id(self):
        return "info"

    def get_icon(self):
        return Gtk.STOCK_INFO

    def get_name(self):
        return _("Info")

    def get_tooltip(self):
        return _("Info Panel (Alt+4)")

    def get_widget(self):
        return self.widget

    def on_load(self):
        self.widget.on_load()

    def on_save(self):
        self.widget.on_save()

    def on_quit(self):
        self.widget.on_quit()
