#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''

from gi.repository import Gtk
import os.path
import logging

from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.gui.model import FDModel
from foobnix.gui.model.signal import FControl
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.preferences.configs import CONFIG_MUSIC_LIBRARY
from foobnix.gui.treeview.simple_tree import  SimpleListTreeControl
from foobnix.helpers.dialog_entry import show_entry_dialog,\
    directory_chooser_dialog
from foobnix.helpers.pref_widgets import FrameDecorator


class MusicLibraryConfig(ConfigPlugin, FControl):
    name = CONFIG_MUSIC_LIBRARY
    enable = True

    def __init__(self, controls):
        FControl.__init__(self, controls)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.hide()
        box.pack_start(self.tabs_mode(), False, True, 0)
        box.pack_start(self.dirs(), False, True, 0)
        box.pack_start(self.formats(), False, True, 0)

        self.widget = box
        uhbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        ulabel = Gtk.Label.new(_("Update library on start (more slow) "))
        self.update_on_start = Gtk.CheckButton.new()

        uhbox.pack_start(ulabel, False, True, 0)
        uhbox.pack_start(self.update_on_start, False, False, 0)
        box.pack_start(uhbox, False, True, 0)
        box.pack_start(self.gap(), False, True, 0)

    def dirs(self):
        frame_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        self.frame = FrameDecorator(_("Music dirs"), frame_box, 0.5, 0.5, border_width=0)
        self.frame.show()
        self.frame.set_no_show_all(True)

        self.tree_controller = SimpleListTreeControl(_("Paths"), None)

        """buttons"""
        button_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        button_box.show()

        bt_add = Gtk.Button.new_with_label(_("Add"))
        bt_add.connect("clicked", self.add_dir)
        bt_add.set_size_request(80, -1)
        bt_add.show()

        bt_remove = Gtk.Button.new_with_label(_("Remove"))
        bt_remove.connect("clicked", self.remove_dir)
        bt_remove.set_size_request(80, -1)
        bt_remove.show()

        empty = Gtk.Label.new("")
        empty.show()

        button_box.pack_start(bt_add, False, False, 0)
        button_box.pack_start(bt_remove, False, False, 0)
        button_box.pack_start(empty, True, True, 0)

        self.tree_controller.scroll.show_all()
        frame_box.pack_start(self.tree_controller.scroll, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)

        if FC().tabs_mode == "Multi":
            self.frame.hide()
        return self.frame

    def reload_dir(self, *a):
        FCache().music_paths[0] = self.temp_music_paths[:] #create copy of list
        self.controls.update_music_tree()

    def on_load(self):
        self.tree_controller.clear_tree()
        for path in FCache().music_paths[0]:
            self.tree_controller.append(FDModel(os.path.basename(path), path).add_is_file(False))

        self.files_controller.clear_tree()
        for ext in FC().all_support_formats:
            self.files_controller.append(FDModel(ext))

        self.adjustment.set_value(FC().gap_secs)

        if FC().tabs_mode == "Single":
            self.singletab_button.set_active(True)
            self.controls.perspectives.get_perspective('fs').get_tabhelper().set_show_tabs(False)

        if FC().update_tree_on_start:
            self.update_on_start.set_active(True)

        self.temp_music_paths = FCache().music_paths[0][:] #create copy of list

    def on_save(self):
        FC().all_support_formats = self.files_controller.get_all_beans_text()
        FC().gap_secs = self.adjustment.get_value()

        if self.singletab_button.get_active():
            '''for i in xrange(len(FCache().music_paths) - 1, 0, -1):
                del FCache().music_paths[i]
                del FCache().cache_music_tree_beans[i]
                del FCache().tab_names[i]
                self.controls.tabhelper.remove_page(i)'''
            FC().tabs_mode = "Single"
            self.controls.perspectives.get_perspective('fs').get_tabhelper().set_show_tabs(False)
            if self.temp_music_paths != FCache().music_paths[0]:
                self.reload_dir()

        else:
            FC().tabs_mode = "Multi"
            self.controls.perspectives.get_perspective('fs').get_tabhelper().set_show_tabs(True)
        if self.update_on_start.get_active():
            FC().update_tree_on_start = True
        else:
            FC().update_tree_on_start = False

    def add_dir(self, *a):
        current_folder = FCache().last_music_path if FCache().last_music_path else None
        paths = directory_chooser_dialog(_("Choose directory with music"), current_folder)
        if not paths:
            return
        path = paths[0]
        FCache().last_music_path = path[:path.rfind("/")]
        for path in paths:
            if path not in self.temp_music_paths:
                self.tree_controller.append(FDModel(os.path.basename(path), path).add_is_file(False))
                self.temp_music_paths.append(path)

    def remove_dir(self, *a):
        selection = self.tree_controller.get_selection()
        fm, paths = selection.get_selected_rows()#@UnusedVariable
        paths.reverse()
        for path in paths:
            del FCache().music_paths[0][path[0]]
            del FCache().cache_music_tree_beans[0][path[0]]

        self.tree_controller.delete_selected()
        remaining_beans = self.tree_controller.get_all_beans()
        if remaining_beans:
            self.temp_music_paths = [bean.path for bean in self.tree_controller.get_all_beans()]
        else:
            self.temp_music_paths = []

    def formats(self):
        frame_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        frame_box.set_border_width(5)
        frame_box.show()

        frame = FrameDecorator(_("File Types"), frame_box, 0.5, 0.5, border_width=0)
        frame.show()

        self.files_controller = SimpleListTreeControl(_("Extensions"), None)

        """buttons"""
        button_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        button_box.show()

        bt_add = Gtk.Button.new_with_label(_("Add"))
        bt_add.connect("clicked", self.on_add_file)
        bt_add.set_size_request(80, -1)
        bt_add.show()

        bt_remove = Gtk.Button.new_with_label(_("Remove"))
        bt_remove.connect("clicked", lambda *a: self.files_controller.delete_selected())
        bt_remove.set_size_request(80, -1)
        bt_remove.show()
        button_box.pack_start(bt_add, False, False, 0)
        button_box.pack_start(bt_remove, False, False, 0)

        scrool_tree = Gtk.ScrolledWindow()
        scrool_tree.set_size_request(-1, 160)
        scrool_tree.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrool_tree.add_with_viewport(self.files_controller.scroll)
        scrool_tree.show()

        frame_box.pack_start(scrool_tree, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)

        return frame

    def on_add_file(self, *a):
        val = show_entry_dialog(_("Please add audio extension"), _("Extension should be like '.mp3'"))
        if val and val.find(".") >= 0 and len(val) <= 5 and val not in self.files_controller.get_all_beans_text():
            self.files_controller.append(FDModel(val))
        else:
            logging.info("Can't add your value" + val)

    def gap(self):
        label = Gtk.Label.new(_("Gap between tracks"))

        self.adjustment = Gtk.Adjustment(value=0, lower=0, upper=5, step_incr=0.5)

        gap_len = Gtk.SpinButton.new(self.adjustment, 0.0, 1)
        gap_len.show()

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        hbox.pack_start(gap_len, False, False, 0)
        hbox.pack_start(label, False, False, 0)
        hbox.show_all()

        return hbox

    def tabs_mode(self):
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.multitabs_button = Gtk.RadioButton.new_with_label(None, _("Multi tab mode"))
        def on_toggle_multitab(widget, data=None):
            self.frame.hide()
        self.multitabs_button.connect("toggled", on_toggle_multitab)
        hbox.pack_start(self.multitabs_button, True, False, 0)

        self.singletab_button = Gtk.RadioButton.new_with_label_from_widget(self.multitabs_button, _("Single tab mode"))
        def on_toggle_singletab(widget, data=None):
            self.tree_controller.clear_tree()
            for path in FCache().music_paths[0]:
                self.tree_controller.append(FDModel(os.path.basename(path), path).add_is_file(False))
            self.temp_music_paths = FCache().music_paths[0][:]
            self.frame.show()
        self.singletab_button.connect("toggled", on_toggle_singletab)
        hbox.pack_end(self.singletab_button, True, False, 0)
        return hbox