#-*- coding: utf-8 -*-
'''
Created on 23 дек. 2010

@author: ivan
'''

import logging
from gi.repository import Gtk

from foobnix.fc.fc import FC
from foobnix.preferences.configs import CONFIG_OTHER
from foobnix.util.antiscreensaver import antiscreensaver
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.helpers.dialog_entry import info_dialog_with_link_and_donate


class OtherConfig(ConfigPlugin):

    name = CONFIG_OTHER

    def __init__(self, controls):
        self.controls = controls

        box = Gtk.VBox(False, 0)
        box.hide()

        download_frame = Gtk.Frame(label=_("File downloads"))
        df_vbox = Gtk.VBox(False, 5)
        df_vbox.set_border_width(4)

        """save to"""

        hbox = Gtk.HBox(False, 5)
        self.online_dir = Gtk.FileChooserButton("set place")
        self.online_dir.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        self.online_dir.connect("current-folder-changed", self.on_change_folder)

        hbox.pack_start(Gtk.Label(_("Save online music to folder:")), False, True, 0)
        hbox.pack_start(self.online_dir, True, True, 0)

        """automatic save"""
        self.automatic_save_checkbutton = Gtk.CheckButton(label=_("Automatic online music save"), use_underline=True)
        self.nosubfolder_checkbutton = Gtk.CheckButton(label=_("Save to one folder (no subfolders)"), use_underline=True)

        """download threads"""
        thbox = Gtk.HBox(False, 5)
        tab_label = Gtk.Label(_("Download in threads"))

        adjustment = Gtk.Adjustment(value=1, lower=1, upper=10, step_incr=1, page_incr=1, page_size=0)
        self.threads_count = Gtk.SpinButton(adjustment=adjustment)

        thbox.pack_start(tab_label, False, False, 0)
        thbox.pack_start(self.threads_count, False, True, 0)

        df_vbox.pack_start(hbox, False, False, 2)
        df_vbox.pack_start(self.automatic_save_checkbutton, False, False, 2)
        df_vbox.pack_start(self.nosubfolder_checkbutton, False, False, 2)
        df_vbox.pack_start(thbox, False, False, 2)
        download_frame.add(df_vbox)
        download_frame.show_all()

        """disc cover size"""
        dc_frame = Gtk.Frame(label=_("Disc cover settings"))

        cbox = Gtk.HBox(False, 5)
        cbox.set_border_width(4)

        tab_label = Gtk.Label(_("Disc cover size:"))

        adjustment = Gtk.Adjustment(value=1, lower=100, upper=350, step_incr=20, page_incr=50, page_size=0)
        self.image_size_spin = Gtk.SpinButton(adjustment=adjustment)

        cbox.pack_start(tab_label, False, False, 0)
        cbox.pack_start(self.image_size_spin, False, True, 0)

        dc_frame.add(cbox)
        dc_frame.show_all()

        """notification"""
        updates_frame = Gtk.Frame(label=_("Updates"))
        uhbox = Gtk.HBox(False, 5)
        uhbox.set_border_width(4)
        self.check_new_version = Gtk.CheckButton(label=_("Check for new foobnix release on start"), use_underline=True)

        demo = Gtk.Button(label=_("Check for update"))
        demo.connect("clicked", lambda * a: info_dialog_with_link_and_donate("foobnix [version]"))
        uhbox.pack_start(self.check_new_version, True, True, 0)
        uhbox.pack_start(demo, False, False, 0)
        updates_frame.add(uhbox)
        updates_frame.show_all()

        """background image"""
        theme_frame = Gtk.Frame(label=_("Theming"))
        thvbox = Gtk.VBox(False, 1)
        thvbox.set_border_width(4)

        """menu position"""
        pbox = Gtk.HBox(False, 5)
        pbox.show()

        label = Gtk.Label(_("Menu type: "))

        self.old_style = Gtk.RadioButton(_("Old Style (Menu Bar)"))

        self.new_style = Gtk.RadioButton.new_with_label_from_widget(self.old_style, _("New Style (Button)"))

        pbox.pack_start(label, False, False, 0)
        pbox.pack_start(self.new_style, False, True, 0)
        pbox.pack_start(self.old_style, False, False, 0)

        o_r_box = Gtk.HBox(False, 5)
        o_r_box.show()

        o_r_label = Gtk.Label(_("Order-Repeat Switcher Style:"))

        self.buttons = Gtk.RadioButton(None, _("Toggle Buttons"))

        self.labels = Gtk.RadioButton.new_with_label_from_widget(self.buttons, _("Text Labels"))

        o_r_box.pack_start(o_r_label, False, False, 0)
        o_r_box.pack_start(self.buttons, False, True, 0)
        o_r_box.pack_start(self.labels, False, False, 0)

        """opacity"""
        obox = Gtk.HBox(False, 5)
        obox.show()

        tab_label = Gtk.Label(_("Opacity:"))
        tab_label.show()

        adjustment = Gtk.Adjustment(value=1, lower=20, upper=100, step_incr=1, page_incr=1, page_size=0)
        self.opacity_size = Gtk.SpinButton(adjustment=adjustment)
        self.opacity_size.connect("value-changed", self.on_chage_opacity)
        self.opacity_size.show()

        obox.pack_start(tab_label, False, False, 0)
        obox.pack_start(self.opacity_size, False, True, 0)

        self.fmgrs_combo = self.fmgr_combobox()
        hcombobox = Gtk.HBox(False, 5)
        hcombobox.pack_start(Gtk.Label(_('Choose your preferred file manager:')), False, False, 0)
        hcombobox.pack_start(self.fmgrs_combo, False, False, 0)

        self.disable_screensaver = Gtk.CheckButton(label=_("Disable Xscreensaver"), use_underline=True)

        thvbox.pack_start(pbox, False, False, 1)
        thvbox.pack_start(o_r_box, False, False, 1)
        thvbox.pack_start(obox, False, False, 1)
        thvbox.pack_start(hcombobox, False, False, 1)
        thvbox.pack_start(self.disable_screensaver, False, False, 0)
        theme_frame.add(thvbox)
        theme_frame.show_all()

        """packaging"""
        box.pack_start(download_frame, False, True, 2)
        box.pack_start(dc_frame, False, True, 2)
        box.pack_start(theme_frame, False, False, 2)
        box.pack_start(updates_frame, False, True, 2)

        self.widget = box

    def on_chage_opacity(self, *a):
        opacity = self.opacity_size.get_value() / 100
        self.controls.main_window.set_opacity(opacity)
        self.controls.preferences.set_opacity(opacity)

    def on_change_menu_type(self, *a):
        if self.old_style.get_active():
            FC().menu_style = "old"
        elif self.new_style.get_active():
            FC().menu_style = "new"

        self.controls.top_panel.update_menu_style()

    def on_change_folder(self, *a):
        path = self.online_dir.get_filename()
        FC().online_save_to_folder = path
        logging.info("Change music online folder: " + path)

    def on_load(self):
        self.online_dir.set_current_folder(FC().online_save_to_folder)
        self.online_dir.set_sensitive(FC().is_save_online)

        """disc"""
        self.image_size_spin.set_value(FC().info_panel_image_size)
        self.threads_count.set_value(FC().amount_dm_threads)

        self.opacity_size.set_value(int(FC().window_opacity * 100))

        self.check_new_version.set_active(FC().check_new_version)

        if FC().automatic_online_save:
            self.automatic_save_checkbutton.set_active(True)

        if FC().nosubfolder:
            self.nosubfolder_checkbutton.set_active(True)

        """menu style"""
        if FC().menu_style == "new":
            self.new_style.set_active(True)
        else:
            self.old_style.set_active(True)

        if FC().order_repeat_style == "TextLabels":
            self.labels.set_active(True)

        self.fmgrs_combo.set_active(FC().active_manager[0])

        if FC().antiscreensaver:
            self.disable_screensaver.set_active(True)
            antiscreensaver()

    def on_save(self):
        if self.buttons.get_active():
            FC().order_repeat_style = "ToggleButtons"
        else:
            FC().order_repeat_style = "TextLabels"
        self.controls.os.on_load()

        FC().info_panel_image_size = self.image_size_spin.get_value_as_int()
        FC().amount_dm_threads = self.threads_count.get_value_as_int()

        FC().window_opacity = self.opacity_size.get_value() / 100
        FC().check_new_version = self.check_new_version.get_active()

        FC().automatic_online_save = self.automatic_save_checkbutton.get_active()
        FC().nosubfolder = self.nosubfolder_checkbutton.get_active()

        FC().active_manager = [self.fmgrs_combo.get_active(), self.fmgrs_combo.get_active_text().lower()]

        if self.disable_screensaver.get_active():
            FC().antiscreensaver = True
            antiscreensaver()
        else:
            FC().antiscreensaver = False

        self.on_change_menu_type()

    def fmgr_combobox(self):
        combobox = Gtk.ComboBoxText()
        combobox.append_text('--- Auto ---')
        combobox.append_text('Nautilus')
        combobox.append_text('Dolphin')
        combobox.append_text('Konqueror')
        combobox.append_text('Thunar')
        combobox.append_text('PCManFM')
        combobox.append_text('Krusader')
        combobox.append_text('Explorer')

        combobox.set_active(0)

        return combobox