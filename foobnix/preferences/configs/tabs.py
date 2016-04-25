#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''

from foobnix.preferences.config_plugin import ConfigPlugin
from gi.repository import Gtk
from foobnix.helpers.my_widgets import tab_close_button
from foobnix.fc.fc import FC


class TabsConfig(ConfigPlugin):

    name = _("Tabs")

    def __init__(self, controls):
        self.controls = controls
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.hide()

        """count"""
        cbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        cbox.show()

        tab_label = Gtk.Label.new(_("Count of tabs:"))
        tab_label.set_size_request(150, -1)
        tab_label.set_alignment(0, .5)

        adjustment = Gtk.Adjustment(value=1, lower=1, upper=20, step_incr=1, page_incr=10, page_size=0)
        self.tabs_count = Gtk.SpinButton.new(adjustment, 0.0, 0)

        cbox.pack_start(tab_label, False, False, 0)
        cbox.pack_start(self.tabs_count, False, True, 0)

        """len"""
        lbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        lbox.show()

        tab_label = Gtk.Label.new(_("Max length of tab:"))
        tab_label.set_size_request(150, -1)
        tab_label.set_alignment(0, .5)

        adjustment = Gtk.Adjustment(value=0, lower=-1, upper=300, step_incr=1, page_incr=10, page_size=0)
        self.tab_len = Gtk.SpinButton(adjustment=adjustment)

        lbox.pack_start(tab_label, False, False, 0)
        lbox.pack_start(self.tab_len, False, True, 0)

        """position"""
        pbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)

        label = Gtk.Label.new(_("Tab position:"))
        label.set_size_request(150, -1)
        label.set_alignment(0, .5)

        self.radio_tab_left = Gtk.RadioButton.new_with_label(None, _("Left"))
        self.radio_tab_left.set_size_request(55, -1)

        self.radio_tab_top = Gtk.RadioButton.new_with_label_from_widget(self.radio_tab_left, _("Top"))
        self.radio_tab_top.set_size_request(55, -1)

        self.radio_tab_no = Gtk.RadioButton.new_with_label_from_widget(self.radio_tab_left, _("No Tabs"))
        self.radio_tab_no.set_size_request(55, -1)

        pbox.pack_start(label, False, False, 0)
        pbox.pack_start(self.radio_tab_left, False, False, 0)
        pbox.pack_start(self.radio_tab_top, False, False, 0)
        pbox.pack_start(self.radio_tab_no, False, False, 0)

        """closed type """
        close_label_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)

        close_label = Gtk.Label.new(_("Close tab sign:"))
        close_label.set_size_request(150, -1)
        close_label.set_alignment(0, .5)

        self.radio_tab_label = Gtk.RadioButton.new_with_label(None, "x")
        self.radio_tab_label.set_size_request(55, -1)

        self.radio_tab_button = Gtk.RadioButton.new_from_widget(self.radio_tab_label)

        self.tab_close_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.tab_close_box.pack_start(self.radio_tab_button, False, True, 0)
        self.tab_close_box.pack_start(tab_close_button(), False, False, 0)
        self.tab_close_box.set_size_request(55, -1)

        self.radio_tab_none = Gtk.RadioButton.new_with_label_from_widget(self.radio_tab_label, _("None"))
        self.radio_tab_none.set_size_request(55, -1)

        close_label_box.pack_start(close_label, False, False, 0)
        close_label_box.pack_start(self.radio_tab_label, False, False, 0)
        close_label_box.pack_start(self.tab_close_box, False, False, 0)
        close_label_box.pack_start(self.radio_tab_none, False, False, 0)

        """global pack"""
        box.pack_start(cbox, False, True, 2)
        box.pack_start(lbox, False, True, 2)
        box.pack_start(pbox, False, True, 2)
        box.pack_start(close_label_box, False, True, 2)
        box.show_all()

        self.widget = box


    def removing_of_extra_tabs(self, number_of_tabs):
        overage = self.controls.notetabs.get_n_pages() - number_of_tabs
        while overage > 0:
            self.controls.notetabs.remove_page(self.controls.notetabs.get_n_pages() - 1)
            overage -= 1

    def on_load(self):
        self.tabs_count.set_value(FC().count_of_tabs)
        self.tab_len.set_value(FC().len_of_tab)

        if  FC().tab_position == "left":
            self.radio_tab_left.set_active(True)

        elif  FC().tab_position == "top":
            self.radio_tab_top.set_active(True)

        elif FC().tab_position == "no":
            self.radio_tab_no.set_active(True)

        if  FC().tab_close_element == "label":
            self.radio_tab_label.set_active(True)

        elif FC().tab_close_element == "button":
            self.radio_tab_button.set_active(True)

        else: self.radio_tab_none.set_active(True)

    def on_save(self):
        FC().count_of_tabs = self.tabs_count.get_value_as_int()

        if self.controls.notetabs.get_n_pages() > FC().count_of_tabs:
            self.removing_of_extra_tabs(FC().count_of_tabs)
        FC().len_of_tab = self.tab_len.get_value_as_int()

        if self.radio_tab_label.get_active():
            FC().tab_close_element = "label"
        elif self.radio_tab_button.get_active():
            FC().tab_close_element = "button"
        else:
            FC().tab_close_element = None

        if self.radio_tab_left.get_active():
            FC().tab_position = "left"
            self.controls.notetabs.set_tab_left()
        elif self.radio_tab_top.get_active():
            FC().tab_position = "top"
            self.controls.notetabs.set_tab_top()
        else:
            FC().tab_position = "no"
            self.controls.notetabs.set_tab_no()

        self.controls.notetabs.crop_all_tab_names()
