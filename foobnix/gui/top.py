#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''

from gi.repository import Gtk

from foobnix.gui.model.signal import FControl
from foobnix.gui.state import LoadSave
from foobnix.gui.menu import MenuBarWidget
from foobnix.helpers.my_widgets import ImageButton
from foobnix.helpers.menu import Popup
from foobnix.fc.fc import FC
from foobnix.util.widget_utils import MenuStyleDecorator

class TopWidgets(FControl, LoadSave, Gtk.HBox):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        Gtk.HBox.__init__(self, False, 0)

        self.old_menu = MenuBarWidget(controls)


        self.pack_start(self.old_menu.widget, False, False, 0)

        self.new_menu_button = ImageButton(Gtk.STOCK_PREFERENCES, tooltip_text=_("Settings"))
        self.new_menu_button.connect("button-press-event", self.on_button_press)

        self.pack_start(self.new_menu_button, False, False, 0)
        self.pack_start(controls.playback, False, False, 0)
        self.pack_start(controls.os, False, False, 0)
        self.pack_start(controls.volume, False, False, 0)
        self.pack_start(Gtk.SeparatorToolItem.new(), False, False, 0)
        self.pack_start(controls.record, False, False, 0)
        self.pack_start(controls.seek_bar, True, True, 0)

        """menu init"""
        menu = Popup()
        decorator = MenuStyleDecorator()
        MenuBarWidget(self.controls, menu)
        menu.add_separator()
        menu.add_item(_("Preferences"), Gtk.STOCK_PREFERENCES, self.controls.show_preferences)
        menu.add_separator()
        menu.add_item(_("Quit"), Gtk.STOCK_QUIT, self.controls.quit)

        decorator.apply(menu)
        self.menu = menu

    def update_menu_style(self):
        if FC().menu_style == "new":
            self.old_menu.widget.hide()
            self.new_menu_button.show()
        else:
            self.old_menu.widget.show()
            self.new_menu_button.hide()

    def on_save(self):
        self.controls.volume.on_save()
        self.old_menu.on_save()

    def on_load(self):
        self.controls.volume.on_load()
        self.old_menu.on_load()
        self.controls.os.on_load()
        self.update_menu_style()

    def on_button_press(self, w, e):
        self.menu.show(e)
