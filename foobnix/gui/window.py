#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

import logging

from gi.repository import Gtk
from gi.repository import Gdk

from foobnix.fc.fc import FC
from foobnix.gui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.util import const
from foobnix.gui.state import LoadSave
from foobnix.version import FOOBNIX_VERSION
from foobnix.gui.model.signal import FControl
from foobnix.util.key_utils import is_key, is_key_alt, is_key_control


class MainWindow(Gtk.Window, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.set_title("Foobnix " + FOOBNIX_VERSION)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)
        self.connect("window-state-event", self.on_change_state)
        self.connect("delete-event", self.hide_window)
        self.connect("key-press-event", self.on_key_press)
        try:
            self.set_icon_from_file(get_foobnix_resourse_path_by_name(const.ICON_FOOBNIX))
        except TypeError as e:
            logging.error(str(e))

        self.set_opacity(FC().window_opacity)
        self.iconified = False

    def on_key_press(self, w, e):
        if is_key(e, 'Escape'):
            self.hide_window()
        elif is_key(e, 'space') and not isinstance(self.get_focus(), Gtk.Entry):
            self.controls.play_pause()
        elif is_key_alt(e) and is_key(e, "1"):
            self.controls.perspectives.activate_perspective("fs")
        elif is_key_alt(e) and is_key(e, "2"):
            self.controls.perspectives.activate_perspective("radio")
        elif is_key_alt(e) and is_key(e, "3"):
            self.controls.perspectives.activate_perspective("storage")
        elif is_key_alt(e) and is_key(e, "4"):
            self.controls.perspectives.activate_perspective("info")
        elif is_key_control(e) and (is_key(e, "q") or is_key(e, "Cyrillic_shorti")):
            self.controls.quit()
        elif is_key_control(e) and (is_key(e, "s") or is_key(e, "Cyrillic_yeru")):
            self.controls.notetabs.on_save_playlist(self.controls.notetabs.get_current_tree().scroll)

    def on_save(self, *a):
        pass

    def on_load(self):
        cfg = FC().main_window_size
        if cfg:
            self.resize(cfg[2], cfg[3])
            self.move(cfg[0], cfg[1])
        if FC().window_maximized:
            self.maximize()

    def show_hide(self):
        visible = self.get_property('visible')
        if visible:
            self.hide()
        else:
            self.show()

    def hide_window(self, *args):
        if FC().on_close_window == const.ON_CLOSE_CLOSE:
            self.controls.quit()

        elif FC().on_close_window == const.ON_CLOSE_HIDE:
            self.hide()

        elif FC().on_close_window == const.ON_CLOSE_MINIMIZE:
            self.iconify()

        logging.debug("On close window action %s" % FC().on_close_window)

        return True

    def on_change_state(self, w, e):

        if int(e.new_window_state) == 0:
            """window restored"""
            self.iconified = False
            FC().window_maximized = False

        elif e.new_window_state & Gdk.WindowState.ICONIFIED:#@UndefinedVariable
            """minimized"""
            self.iconified = True
            FC().window_maximized = False

        elif e.new_window_state & Gdk.WindowState.MAXIMIZED:#@UndefinedVariable
            """maximized"""
            self.iconified = False
            FC().window_maximized = True

        self.controls.layout.back_saved_allocation()




