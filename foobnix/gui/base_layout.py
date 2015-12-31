#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

import logging

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

from threading import Timer

from foobnix.fc.fc import FC
from foobnix.gui.model.signal import FControl
from foobnix.gui.state import LoadSave
from foobnix.util import idle_task

## TODO: move into resources
foobnix_style = """
GtkComboBox .button {
    /* fix for very large size of combobox */
    padding: 2px 5px;
}
/*
foobnix\+gui\+window\+MainWindow {
    background-image: url("/usr/share/pixmaps/foobnix-big.png");
    background-size:100% 100%;
    background-repeat:no-repeat;
}
GtkHPaned {
    background-color: rgba(255, 255, 255, 0.5);
}
*/
"""

class BaseFoobnixLayout(FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        self.controls = controls
        """ set application stylesheet"""
        self.style_provider = Gtk.CssProvider()
        ## TODO: after moving style to resource - replace to load_from_file
        self.style_provider.load_from_data(foobnix_style)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.controls = controls

        notebox = Gtk.Overlay.new()
        notebox.add(controls.notetabs)
        notebox.add_overlay(controls.search_progress)

        bbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        bbox.pack_start(notebox, True, True, 0)

        center_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        center_box.pack_start(controls.searchPanel, False, False, 0)
        center_box.pack_start(bbox, True, True, 0)

        self.hpaned_left = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.hpaned_left.pack1(child=controls.perspectives.scroll, resize=True, shrink=False)
        self.hpaned_left.pack2(child=center_box, resize=True, shrink=True)

        self.hpaned_right = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.hpaned_right.pack1(child=self.hpaned_left, resize=True, shrink=True)
        self.hpaned_right.pack2(child=controls.coverlyrics, resize=True, shrink=False)

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.pack_start(controls.top_panel, False, False, 0)
        vbox.pack_start(self.hpaned_right, True, True, 0)
        vbox.pack_start(controls.statusbar, False, True, 0)
        vbox.show_all()

        self.hpaned_left.connect("button-release-event", self.on_border_release)
        self.hpaned_right.connect("button-release-event", self.on_border_release)

        controls.main_window.connect("configure-event", self.on_configure_event)
        controls.main_window.add(vbox)

    def set_visible_search_panel(self, flag=True):
        logging.info("set_visible_search_panel " + str(flag))
        if flag:
            self.controls.searchPanel.show_all()
        else:
            self.controls.searchPanel.hide()
        FC().is_view_search_panel = flag

    def set_visible_musictree_panel(self, flag):
        logging.info("set_visible_musictree_panel " + str(flag))
        if flag:
            self.controls.perspectives.scroll.show()
            self.hpaned_left.set_position(FC().hpaned_left)
        else:
            self.controls.perspectives.scroll.hide()
        FC().is_view_music_tree_panel = flag

    def set_visible_coverlyrics_panel(self, flag):
        logging.info("set_visible_coverlyrics_panel " + str(flag))
        if flag:
            self.hpaned_right.set_position(self.hpaned_right.get_allocated_width() - FC().hpaned_right_right_side_width)
            self.controls.coverlyrics.show()
        else:
            self.controls.coverlyrics.hide()

        FC().is_view_coverlyrics_panel = flag

    def on_border_release(self, w, *a):
        self.save_right_panel()
        if w is self.hpaned_left:
            self.save_left_panel()
        elif w is self.hpaned_right:
            self.configure_hl()
            self.save_left_panel()

    def save_right_panel(self):
        if self.controls.coverlyrics.get_property("visible"):
            right_position = self.hpaned_right.get_position()
            if right_position != FC().hpaned_right and right_position > 0:
                FC().hpaned_right = right_position
            FC().hpaned_right_right_side_width = self.hpaned_right.get_allocated_width() - right_position

    def save_left_panel(self):
        left_position = self.hpaned_left.get_position()
        if left_position != FC().hpaned_left and left_position > 0:
            FC().hpaned_left = left_position
            self.normalize_columns()

    def normalize_columns(self):
        tabhelper = self.controls.perspectives.get_perspective('fs').get_tabhelper()
        for page in xrange(tabhelper.get_n_pages()):
            tab_content = tabhelper.get_nth_page(page)
            tree = tab_content.get_child()
            tree.normalize_columns_width()

    def on_configure_event(self, w, e):
        FC().main_window_size = [e.x, e.y, e.width, e.height]

    def configure_hl(self):
        if FC().is_view_music_tree_panel and self.hpaned_left.get_position() != FC().hpaned_left:
            self.hpaned_left.set_position(FC().hpaned_left)

    def configure_hr(self):
        if self.controls.coverlyrics.get_property("visible"):
            hrw = self.hpaned_right.get_allocated_width()
            if (hrw - self.hpaned_right.get_position()) != FC().hpaned_right_right_side_width:
                self.hpaned_right.set_position(hrw - FC().hpaned_right_right_side_width)

    @idle_task
    def back_saved_allocation(self):
        self.configure_hr()
        Timer(0.1, GLib.idle_add, [self.configure_hl,]).start()

    def on_load(self):
        self.set_visible_search_panel(FC().is_view_search_panel)
        GLib.idle_add(self.set_visible_musictree_panel, FC().is_view_music_tree_panel,
                         priority = GLib.PRIORITY_DEFAULT_IDLE - 10)
        self.set_visible_coverlyrics_panel(FC().is_view_coverlyrics_panel)
