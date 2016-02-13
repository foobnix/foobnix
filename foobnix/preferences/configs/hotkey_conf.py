'''
Created on Sep 7, 2010

@author: ivan
'''

import collections
import gi
import logging

gi.require_version("Keybinder", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Keybinder

from copy import copy
from foobnix.fc.fc import FC
from foobnix.helpers.menu import Popup
from foobnix.helpers.pref_widgets import FrameDecorator
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util.key_utils import is_key_control, is_key_shift, is_key_super, \
    is_key_alt

Keybinder.init()


def activate_hot_key(hotkey, command):
    logging.debug("Run command: " + command + " Hotkey: " + hotkey)
    if HotKeysConfig.controls:
        eval('HotKeysConfig.controls.' + command + '()')


def add_key_binder(command, hotkey):
    try:
        logging.debug("binding a key %s with command %s" % (hotkey, command))
        Keybinder.bind(hotkey, activate_hot_key, command)
    except Exception, e:
        logging.warn("add_key_binder exception: %s %s" % (str(hotkey), str(e)))


def bind_all():
    binder(FC().action_hotkey)
    if FC().media_keys_enabled:
        items = to_form_dict_of_mmkeys()
        logging.debug(items)
        if items:
            binder(items)
    else:
        logging.debug("media keys has been disabled")

    HotKeysConfig.binded = True


def binder(items):
    for key in items:
        command = key
        hotkey = items[key]
        add_key_binder(command, hotkey)


def load_foobnix_hotkeys():
    logging.debug("LOAD HOT KEYS")
    bind_all()


def to_form_dict_of_mmkeys():
    if FC().media_keys_enabled:
        items = copy(FC().multimedia_keys)
        if not FC().media_volume_keys_enabled:
            for key in FC().media_volume_keys:
                if key in items:
                    del items[key]
        return items


class HotKeysConfig(ConfigPlugin):

    name = _("Global Hotkeys")
    binded = True
    controls = None

    def __init__(self, controls):
        HotKeysConfig.controls = controls
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.hide()

        self.tree_widget = Gtk.TreeView()
        self.tree_widget.connect("button-press-event", self.on_populate_click)

        self.tree_widget.show()
        self.model = Gtk.ListStore(str, str)

        self.title = None
        self.column1 = Gtk.TreeViewColumn(_("Action"), Gtk.CellRendererText(), text=0)
        self.column2 = Gtk.TreeViewColumn(_("Hotkey"), Gtk.CellRendererText(), text=1)
        self.tree_widget.append_column(self.column1)
        self.tree_widget.append_column(self.column2)
        self.tree_widget.set_model(self.model)

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox.show()

        add_button = Gtk.Button.new_with_label(_("Add"))
        add_button.set_size_request(80, -1)
        add_button.connect("clicked", self.on_add_row)
        add_button.show()

        remove_button = Gtk.Button.new_with_label(_("Remove"))
        remove_button.connect("clicked", self.on_remove_row)
        remove_button.set_size_request(80, -1)
        remove_button.show()

        hbox.pack_start(add_button, False, True, 0)
        hbox.pack_start(remove_button, False, True, 0)

        hotbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hotbox.show()

        self.action_text = Gtk.Entry()
        self.action_text.set_size_request(150, -1)
        self.action_text.connect("button-press-event", self.on_mouse_click)

        self.hotkey_text = Gtk.Entry()
        self.hotkey_text.set_editable(False)
        self.hotkey_text.connect("key-press-event", self.on_key_press)
        self.hotkey_text.set_size_request(150, -1)

        self.hotkey_auto = Gtk.CheckButton.new_with_label(_("Auto key"))
        self.hotkey_auto.set_active(True)

        hotbox.pack_start(self.action_text, False, True, 0)
        hotbox.pack_start(self.hotkey_text, False, True, 0)
        hotbox.pack_start(self.hotkey_auto, False, True, 0)

        self.disable_mediakeys = Gtk.CheckButton.new_with_label(_("Disable Multimedia Keys"))
        self.disable_volume_keys = Gtk.CheckButton.new_with_label(_("Don't try to bind volume control keys"))
        def on_toggle(*a):
            if self.disable_mediakeys.get_active():
                self.disable_volume_keys.set_sensitive(False)
            else:
                self.disable_volume_keys.set_sensitive(True)

        self.disable_mediakeys.connect("toggled", on_toggle)

        mmbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        mmbox.pack_start(self.disable_mediakeys, False, False, 0)
        mmbox.pack_start(self.disable_volume_keys, False, False, 0)
        self.mm_frame_decorator = FrameDecorator(_("Multimedia keys"), mmbox, 0.5, 0.5)

        box.pack_start(self.tree_widget, False, True, 0)
        box.pack_start(hotbox, False, True, 0)
        box.pack_start(hbox, False, True, 0)
        box.pack_start(self.mm_frame_decorator, False, False, 0)
        self.widget = box
        self.menu = self.create_menu()

    def create_menu(self):
        menu = Popup()
        menu.add_item(_("Play-Pause"), "media-playback-pause", self.set_action_text, "play_pause")
        menu.add_item(_("Stop"), "media-playback-stop", self.set_action_text, "state_stop")
        menu.add_item(_("Next song"), "go-next", self.set_action_text, "next")
        menu.add_item(_("Previous song"), "go-previous", self.set_action_text, "prev")
        menu.add_item(_("Volume up"), "go-up", self.set_action_text, "volume_up")
        menu.add_item(_("Volume down"), "go-down", self.set_action_text, "volume_down")
        menu.add_item(_("Show-Hide"), "view-fullscreen", self.set_action_text, "show_hide")
        menu.add_item(_('Download'), "list-add", self.set_action_text, "download")
        return menu

    def set_action_text(self, text):
        self.action_text.set_text(text)

    def set_hotkey_text(self, text):
        text = text.replace("Super_L", "<SUPER>").replace("Super_R", "<SUPER>").replace("Control_L", "<Control>").replace("Control_R", "<Control>").replace("Shift_L", "<Shift>").replace("Shift_R", "<Shift>").replace("Alt_L", "<Alt>").replace("Alt_R", "<Alt>")
        text = text.replace("<Shift>", "") #because of bug in python-keybinder https://bugs.launchpad.net/kupfer/+bug/826075
        if text.count("<") > 2 or text.endswith("ISO_Next_Group"): return
        self.hotkey_text.set_text(text)

    def get_hotkey_text(self):
        text = self.hotkey_text.get_text()
        if not text:
            text = ""
        return text

    def on_add_row(self, *args):
        command = self.action_text.get_text()
        hotkey = self.hotkey_text.get_text()
        if command and hotkey:
            if hotkey not in self.get_all_items():
                if command in self.get_all_items():
                    for item in self.model:
                        if item[0] == command:
                            item[1] = hotkey
                else:
                    self.model.append([command, hotkey])

        self.action_text.set_text("")
        self.hotkey_text.set_text("")

    def on_remove_row(self, *args):
        selection = self.tree_widget.get_selection()
        model, selected = selection.get_selected()
        if selected:
            model.remove(selected)

    def unbind_all(self):
        self.unbinder(FC().action_hotkey)
        self.unbinder(FC().multimedia_keys)

        HotKeysConfig.binded = False

    def unbinder(self, items):
        for keystring in items:
            try:
                Keybinder.unbind(items[keystring])
            except:
                pass
        HotKeysConfig.binded = False

    def on_populate_click(self, w, event):
        if is_double_left_click(event):
            selection = self.tree_widget.get_selection()
            model, selected = selection.get_selected()

            command = self.model.get_value(selected, 0)
            keystring = self.model.get_value(selected, 1)
            self.action_text.set_text(command)
            self.hotkey_text.set_text(keystring)

    def on_mouse_click(self, w, event):
        self.menu.show(event)

    def on_load(self):
        if not FC().media_keys_enabled:
            self.disable_mediakeys.set_active(True)
        if not FC().media_volume_keys_enabled:
            self.disable_volume_keys.set_active(True)
        self.fill_hotkey_list()

    def fill_hotkey_list(self):
        items = FC().action_hotkey
        self.model.clear()
        for key in items:
            command = key
            hotkey = items[key]
            self.model.append([command, hotkey])

    def on_save(self):
        if self.disable_mediakeys.get_active():
            FC().media_keys_enabled = False
        else:
            FC().media_keys_enabled = True
        if self.disable_volume_keys.get_active():
            FC().media_volume_keys_enabled = False
        else:
            FC().media_volume_keys_enabled = True
        self.unbind_all()
        FC().action_hotkey = self.get_all_items()
        bind_all()

    def get_all_items(self):
        items = collections.OrderedDict()
        for item in self.model:
            action = item[0]
            hotkey = item[1]
            items[action] = hotkey
        return items

    def on_key_press(self, w, event):
        if not self.hotkey_auto.get_active():
            self.hotkey_text.set_editable(True)
            return None
        self.hotkey_text.set_editable(False)

        self.unbind_all()

        keyname = Gdk.keyval_name(event.keyval) #@UndefinedVariable

        logging.debug("Key %s (%d) was pressed. %s" % (keyname, event.keyval, str(event.state)))
        if is_key_control(event):
            self.set_hotkey_text(self.get_hotkey_text() + keyname)
        elif is_key_shift(event):
            self.set_hotkey_text(self.get_hotkey_text() + keyname)
        elif is_key_super(event):
            self.set_hotkey_text(self.get_hotkey_text() + keyname)
        elif is_key_alt(event):
            self.set_hotkey_text(self.get_hotkey_text() + keyname)
        else:
            self.set_hotkey_text(keyname)

    def on_key_release(self, w, event):
        keyname = Gdk.keyval_name(event.keyval) #@UndefinedVariable
        logging.debug("Key release %s (%d) was pressed" % (keyname, event.keyval))

    def on_close(self):
        if not HotKeysConfig.binded:
            self.fill_hotkey_list()
            bind_all()

