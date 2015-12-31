#-*- coding: utf-8 -*-
'''
Created on 29 сент. 2010

@author: ivan
'''

import logging

from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Notify

from foobnix.fc.fc import FC
from foobnix.gui.controls.playback import PlaybackControls
from foobnix.gui.model import FModel
from foobnix.gui.model.signal import FControl
from foobnix.gui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.gui.state import LoadSave
from foobnix.helpers.image import ImageBase
from foobnix.helpers.my_widgets import ImageButton, AlternateVolumeControl
from foobnix.helpers.pref_widgets import VBoxDecorator
from foobnix.util import idle_task
from foobnix.util.const import ICON_FOOBNIX
from foobnix.util.mouse_utils import is_middle_click
from foobnix.util.text_utils import split_string


class PopupTrayWindow (Gtk.Window, FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP)

        self.set_position(Gtk.WindowPosition.MOUSE)
        self.connect("leave-notify-event", self.on_leave_window)
        Notify.init('Foobnix')

    def on_leave_window(self, w, event):
        requisition = w.size_request()
        x, y = event.x, event.y
        if 0 < x < requisition.width and 0 < y < requisition.height:
            return True
        self.hide()


class PopupMenuWindow(PopupTrayWindow):
    def __init__ (self, controls):
        PopupTrayWindow.__init__(self, controls)
        #self.modify_bg(Gtk.StateType.NORMAL, self.get_colormap().alloc_color("gray23"))
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        playcontrols = PlaybackControls(controls)
        playcontrols.pack_start(ImageButton("application-exit", controls.quit, _("Exit")), False, False, 0)
        playcontrols.pack_start(ImageButton("", self.hide, _("Close Popup")), False, False, 0)

        self.poopup_text = Gtk.Label.new(None)
        self.set_text("Foobnix")
        self.poopup_text.set_line_wrap(True)

        vbox.pack_start(playcontrols, False, False, 0)
        vbox.pack_start(self.poopup_text, False, False, 0)
        self.add(vbox)
        self.show_all()
        self.hide()

    @idle_task
    def set_text(self, text):
        self.poopup_text.set_text(text[:40])

        '''set colour of text'''
        self.poopup_text.modify_fg(Gtk.StateType.NORMAL,
                                   Gdk.color_parse('#FFFFFF'))


class PopupVolumeWindow(PopupTrayWindow):
    def __init__(self, controls, popup_menu_window):
        PopupTrayWindow.__init__(self, controls)
        height = popup_menu_window.get_size()[1]
        width = height * 3
        self.set_size_request(width, height)
        self.avc = AlternateVolumeControl(levels=35, s_width=2, interval=1, v_step=1)
        #self.avc.modify_bg(Gtk.StateType.NORMAL, self.get_colormap().alloc_color("gray23"))
        self.avc.connect("scroll-event", self.controls.volume.on_scroll_event)
        self.add(self.avc)
        self.show_all()
        self.hide()

class TrayIconControls(Gtk.StatusIcon, ImageBase, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        Gtk.StatusIcon.__init__(self)
        self.hide()
        ImageBase.__init__(self, ICON_FOOBNIX, 150)

        self.popup_menu = PopupMenuWindow(self.controls)
        self.popup_volume_contol = PopupVolumeWindow(self.controls, self.popup_menu)

        self.connect("activate", self.on_activate)
        self.connect("popup-menu", self.on_popup_menu)

        try:
            self.set_has_tooltip(True)
            #self.set_tooltip("Foobnix music player")
            self.connect("query-tooltip", self.on_query_tooltip)
            self.connect("button-press-event", self.on_button_press)
            self.connect("scroll-event", self.on_scroll)
        except Exception, e:
            logging.warn("Tooltip doesn't work " + str(e))

        self.current_bean = FModel().add_artist("Artist").add_title("Title")
        self.tooltip_image = ImageBase(ICON_FOOBNIX, 75)

        self._previous_notify = None

    def on_save(self):
        pass

    def on_scroll(self, button, event):
        self.controls.volume.on_scroll_event(button, event)
        self.popup_volume_contol.show()

    def on_load(self):
        if FC().show_tray_icon:
            self.set_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
            self.show()

    def update_info_from(self, bean):
        self.current_bean = bean
        if bean.artist:
            artist = bean.artist
            self.tooltip_image.size = 150
        else:
            artist = 'Unknown artist'
            self.tooltip_image.size = 75
            self.tooltip_image.resource = ICON_FOOBNIX
        self.tooltip_image.update_info_from(bean)

        if bean.title:
            title = bean.title
        else:
            title = bean.text
        if FC().change_tray_icon:
            super(TrayIconControls, self).update_info_from(bean)

        if FC().notifier:
            self.to_notify(artist, title)

    @idle_task
    def to_notify(self, artist, title):
            message = "%s%s" % (artist, title)
            if self._previous_notify == message:
                return
            self._previous_notify = message
            notification = Notify.Notification.new(artist, title, "")
            notification.set_urgency(Notify.Urgency.LOW)
            notification.set_timeout(FC().notify_time)
            if self.tooltip_image.get_pixbuf() != None:
                notification.set_icon_from_pixbuf(self.tooltip_image.get_pixbuf())
            notification.show()

    def on_query_tooltip(self, widget, x, y, keyboard_tip, tooltip):
        artist = "Artist"
        title = "Title"
        if self.current_bean:
            if self.current_bean.artist and self.current_bean.title:
                artist = self.current_bean.artist
                #artist = string.join(["&amp;" if x == '&' else x for x in artist], '')
                artist = artist.replace('&', '&amp;')
                title = self.current_bean.title
            else:
                artist = "Unknown artist"
                title = self.current_bean.text

        max_str_len = 40
        if len(title) > max_str_len:
            title = split_string(title, max_str_len)

        alabel = Gtk.Label.new(None)
        alabel.set_markup("<b>%s</b>" % artist)
        hbox1 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox1.pack_start(alabel, False, False, 0)
        hbox2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox2.pack_start(Gtk.Label.new(title), False, False, 0)
        vbox = VBoxDecorator(Gtk.Label.new(None), hbox1, Gtk.Label.new(None), hbox2)
        """if self.tooltip_image.size == 150:
            alignment = Gtk.Alignment(0, 0.4)
        else:
            alignment = Gtk.Alignment()
        alignment.set_padding(padding_top=0, padding_bottom=0, padding_left=10, padding_right=10)
        alignment.add(vbox)"""
        vbox.set_halign(Gtk.Align.CENTER)
        tooltip.set_icon(self.tooltip_image.get_pixbuf())
        tooltip.set_custom(vbox)
        return True

    def on_activate(self, *a):
        self.controls.windows_visibility()

    def on_button_press(self, w, e):
        if is_middle_click(e):
            self.controls.play_pause()

    def hide(self):
        self.set_visible(False)

    def show(self):
        self.set_visible(True)

    def show_window(self, *a):
        #self.popup_menu.reshow_with_initial_size()
        self.popup_menu.show()

    def hide_window(self, *a):
        self.popup_menu.hide()

    def on_popup_menu(self, *a):
        self.show_window()

    @idle_task
    def set_text(self, text):
        self.popup_menu.set_text(text)
        self.set_tooltip_text(text)
