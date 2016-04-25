# -*- coding: utf-8 -*-

import os
import thread
import logging
from gi.repository import Gtk
from gi.repository import GLib

from foobnix.fc.fc import FC
from foobnix.gui.model import FDModel
from foobnix.gui.state import LoadSave
from foobnix.gui.model.signal import FControl
from foobnix.gui.treeview.simple_tree import SimpleListTreeControl
from foobnix.helpers.window import ChildTopWindow
from foobnix.preferences.configs.tabs import TabsConfig
from foobnix.preferences.configs.last_fm import LastFmConfig
from foobnix.preferences.configs import CONFIG_MUSIC_LIBRARY
from foobnix.preferences.configs.other_conf import OtherConfig
from foobnix.preferences.configs.network_conf import NetworkConfig
from foobnix.preferences.configs.tray_icon_conf import TrayIconConfig
from foobnix.preferences.configs.music_library import MusicLibraryConfig
from foobnix.util import analytics


class PreferencesWindow(ChildTopWindow, FControl, LoadSave):

    configs = []
    POS_NAME = 0

    def __init__(self, controls):
        FControl.__init__(self, controls)

        controls = self.controls
        self.configs.append(MusicLibraryConfig(controls))
        self.configs.append(TabsConfig(controls))
        self.configs.append(LastFmConfig(controls))
        self.configs.append(TrayIconConfig(controls))
        self.configs.append(NetworkConfig(controls))

        try:
            """check keybinder installed, debian"""
            import gi
            gi.require_version('Keybinder', '3.0')
            from gi.repository import Keybinder #@UnresolvedImport @UnusedImport
            from foobnix.preferences.configs.hotkey_conf import HotKeysConfig
            self.configs.append(HotKeysConfig(controls))
        except Exception, e:
            logging.warn("Keybinder not installed" + str(e))

        self.configs.append(OtherConfig(controls))

        self.label = None

        mainVBox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        ChildTopWindow.__init__(self, _("Preferences"), 900, 550)

        paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        paned.set_position(250)

        def func():
            bean = self.navigation.get_selected_bean()
            if bean:
                self.populate_config_category(bean.text)

        self.navigation = SimpleListTreeControl(_("Categories"), controls, True)

        for plugin in self.configs:
            self.navigation.append(FDModel(plugin.name))

        self.navigation.set_left_click_func(func)

        paned.add1(self.navigation.scroll)

        cbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        for plugin in self.configs:
            cbox.pack_start(plugin.widget, False, True, 0)

        self._container = self.create_container(cbox)
        paned.add2(self._container)

        mainVBox.pack_start(paned, True, True, 0)
        mainVBox.pack_start(self.create_save_cancel_buttons(), False, False, 0)

        #self.add(mainVBox)
        GLib.idle_add(self.add, mainVBox)

    def show(self, current=CONFIG_MUSIC_LIBRARY):
        self.show_all()
        self.populate_config_category(current)
        self.on_load()
        analytics.action("PreferencesWindow")

    def on_load(self):
        logging.debug("LOAD PreferencesWindow")
        for plugin in self.configs:
            plugin.on_load()

    def on_save(self):
        for plugin in self.configs:
            plugin.on_save()
        FC().save()
        bean = self.navigation.get_selected_bean()
        if bean:
            self.populate_config_category(bean.text)

    def hide_window(self, *a):
        self.hide()
        for plugin in self.configs:
            if hasattr(plugin, "on_close"):
                plugin.on_close()
        self.navigation.set_cursor_on_cell(Gtk.TreePath(0), None, None, False)
        return True

    def populate_config_category(self, name):
        for plugin in self.configs:
            if plugin.name == name:
                plugin.widget.show()
                try:
                    self.update_label(name)
                except:
                    pass
            else:
                plugin.widget.hide()

    def create_save_cancel_buttons(self):
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.show()

        button_restore = Gtk.Button.new_with_label(_("Restore Defaults Settings"))
        button_restore.connect("clicked", lambda * a: self.restore_defaults())
        button_restore.show()

        button_apply = Gtk.Button.new_with_label(_("Apply"))
        button_apply.set_size_request(100, -1)
        button_apply.connect("clicked", lambda * a: self.on_save())
        button_apply.show()

        button_close = Gtk.Button.new_with_label(_("Close"))
        button_close.set_size_request(100, -1)
        button_close.connect("clicked", self.hide_window)
        button_close.show()

        empty = Gtk.Label.new("")
        empty.show()

        box.pack_start(button_restore, False, True, 0)
        box.pack_start(empty, True, True, 0)
        box.pack_start(button_apply, False, True, 0)
        box.pack_start(button_close, False, True, 0)

        return box

    def restore_defaults(self):
        logging.debug("restore defaults settings")
        Gtk.main_quit()
        FC().delete()
        thread.start_new_thread(os.system, ("foobnix",))


    def update_label(self, title):
        self.label.set_markup('<b><i><span  size="x-large" >' + title + '</span></i></b>');

    def create_container(self, widget):
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.show()

        self.label = Gtk.Label.new(None)
        self.label.show()

        separator = Gtk.HSeparator.new()
        separator.show()

        box.pack_start(self.label, False, True, 0)
        box.pack_start(separator, False, True, 0)
        box.pack_start(widget, False, True, 0)

        return box

if __name__ == "__main__":
    w = PreferencesWindow(None)
    w.show()
    Gtk.main()
