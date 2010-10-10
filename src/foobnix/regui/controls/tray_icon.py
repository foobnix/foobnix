#-*- coding: utf-8 -*-
'''
Created on 29 сент. 2010

@author: ivan
'''
from foobnix.regui.model.signal import FControl
import gtk
import os
from foobnix.util.fc import FC
from foobnix.helpers.toolbar import MyToolbar
from foobnix.util.mouse_utils import is_middle_click
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name

class PopupWindowMenu(gtk.Window, FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Window. __init__(self, gtk.WINDOW_POPUP)

        self.set_position(gtk.WIN_POS_MOUSE)

        self.connect("leave-notify-event", self.on_leave_window)

        vbox = gtk.VBox(False, 0)

        toolbar = MyToolbar()
        toolbar.add_button("Exit", gtk.STOCK_QUIT, self.controls.quit, None)
        toolbar.add_separator()
        toolbar.add_button("Stop", gtk.STOCK_MEDIA_STOP, self.controls.state_stop, None)
        toolbar.add_button("Play", gtk.STOCK_MEDIA_PLAY, self.controls.state_play, None)
        toolbar.add_button("Pause", gtk.STOCK_MEDIA_PAUSE, self.controls.state_pause, None)
        toolbar.add_button("Previous", gtk.STOCK_MEDIA_PREVIOUS, self.controls.prev, None)
        toolbar.add_button("Next", gtk.STOCK_MEDIA_NEXT, self.controls.next, None)
        toolbar.add_separator()
        toolbar.add_button("Close Popup", gtk.STOCK_OK, lambda * a:self.hide(), None)

        self.poopup_text = gtk.Label("Foobnix")
        self.poopup_text.set_line_wrap(True)

        vbox.pack_start(toolbar, False, False)
        vbox.pack_start(self.poopup_text, False, False)
        self.add(vbox)
        self.show_all()
        self.hide()

    def set_text(self, text):
        self.poopup_text.set_text(text)

    def on_leave_window(self, w, event):
        print w, event
        max_x, max_y = w.size_request()
        x, y = event.x, event.y
        if 0 < x < max_x and 0 < y < max_y:
            return True
        print "hide"
        self.hide()


class TrayIconControls(FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        self.icon = gtk.StatusIcon()
        self.icon.set_tooltip("Foobnix music player")

        self.popup_menu = PopupWindowMenu(self.controls)

        path = get_foobnix_resourse_path_by_name("foobnix.png")

        if path:
            self.icon.set_from_file(path)
        else:
            self.icon.set_from_stock("gtk-media-play")

        self.icon.connect("activate", self.on_activate)
        self.icon.connect("popup-menu", self.on_popup_menu)

        self.icon.connect("button-press-event", self.on_button_press)
        self.icon.connect("scroll-event", self.controls.volume.on_scroll_event)

        if FC().show_tray_icon:
            self.show()
        else:
            self.hide()

        self.paused = False

    def on_activate(self, *a):
        self.controls.windows_visibility()

    def on_button_press(self, w, e):
        if is_middle_click(e):
            self.paused = not self.paused
            if self.paused:
                self.controls.state_play()
            else:
                self.controls.state_pause()

    def hide(self):
        self.icon.set_visible(False)

    def show(self):
        self.icon.set_visible(True)

    def show_window(self, *a):
        self.popup_menu.reshow_with_initial_size()
        self.popup_menu.show()
        print "show"

    def hide_window(self, *a):
        self.popup_menu.hide()
        print "hide"

    def on_popup_menu(self, *a):
        self.show_window()

    def set_text(self, text):
        self.popup_menu.set_text(text)
        self.icon.set_tooltip(text)

    def get_pixbuf(self):
        return self.icon.get_pixbuf()
