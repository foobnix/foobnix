
__author__ = 'popsul'

from gi.repository import Gtk
from foobnix.fc.fc import FCBase
from foobnix.gui.perspectives import BasePerspective
from foobnix.gui.treeview.lastfm_integration_tree import LastFmIntegrationControls


class LastFMPerspective(BasePerspective):

    def __init__(self, controls):
        super(LastFMPerspective, self).__init__()
        self.widget = LastFmIntegrationControls(controls)

    def get_id(self):
        return "lastfm"

    def get_icon(self):
        return "network-idle"

    def get_name(self):
        return _("Last.FM")

    def get_tooltip(self):
        return _("Last.FM Panel (Alt+5)")

    def get_widget(self):
        return self.widget.scroll

    def is_available(self):
        return (FCBase().lfm_login != "l_user_") and FCBase().lfm_password

    ## LoadSave implementation
    def on_load(self):
        pass

    def on_save(self):
        pass

