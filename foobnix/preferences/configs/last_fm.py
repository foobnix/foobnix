#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''

import thread

from gi.repository import Gtk
from gi.repository import GLib

from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.fc.fc import FC
from foobnix.fc.fc_base import FCBase
from foobnix.helpers.pref_widgets import FrameDecorator
from foobnix.util import idle_task


class LastFmConfig(ConfigPlugin):

    name = _("Last FM + VK")

    def __init__(self, controls):
        self.controls = controls

        box = VBox(self, Gtk.Orientation.VERTICAL, 0)
        box.hide()

        """LAST.FM"""
        l_layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        l_frame = FrameDecorator(_("Last.FM"), l_layout, border_width=0)

        """LOGIN"""
        lbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        lbox.show()

        login = Gtk.Label.new(_("Login"))
        login.set_size_request(150, -1)
        login.show()

        self.login_text = Gtk.Entry()
        self.login_text.show()

        lbox.pack_start(login, False, False, 0)
        lbox.pack_start(self.login_text, False, True, 0)

        """PASSWORD"""
        pbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        pbox.show()

        password = Gtk.Label.new(_("Password"))
        password.set_size_request(150, -1)
        password.show()

        self.password_text = Gtk.Entry()
        self.password_text.set_visibility(False)
        self.password_text.set_invisible_char("*")
        self.password_text.show()

        limit_text = Gtk.Label.new(_("Limit search results:  "))
        limit_text.show()

        self.adjustment = Gtk.Adjustment(value=50, lower=10, upper=200, step_incr=10)
        limit = Gtk.SpinButton.new(self.adjustment, 0.0, 0)
        limit.show()

        limitbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        limitbox.pack_start(limit_text, False, False, 0)
        limitbox.pack_start(limit, False, False, 0)

        self.music_scrobbler = Gtk.CheckButton.new_with_label(_("Enable Music Scrobbler"))
        self.music_scrobbler.show()

        self.radio_scrobbler = Gtk.CheckButton.new_with_label(_("Enable Radio Scrobbler"))
        self.radio_scrobbler.show()

        pbox.pack_start(password, False, False, 0)
        pbox.pack_start(self.password_text, False, True, 0)

        l_layout.pack_start(lbox, False, True, 0)
        l_layout.pack_start(pbox, False, True, 0)
        l_layout.pack_start(limitbox, False, True, 10)
        l_layout.pack_start(self.music_scrobbler, False, True, 0)
        l_layout.pack_start(self.radio_scrobbler, False, True, 0)

        """VK"""
        vk_layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vk_frame = FrameDecorator(_("VKontakte"), vk_layout, border_width=0)

        self.default_label_value = _("Not connected")

        self.frase_begin = _("You vk account is:")
        self.vk_account_label = Gtk.Label.new(self.frase_begin + " %s" % self.default_label_value)
        self.reset_vk_auth_button = Gtk.Button.new_with_label(_("Reset vk authorization"))
        self.reset_vk_auth_button.connect("button-release-event", self.on_reset_vk_click)
        self.vk_autocomplete = Gtk.CheckButton.new_with_label(_("Enable VK autocomplete"))
        self.vk_autocomplete.show()
        vk_layout.pack_start(self.vk_account_label, False, False, 0)
        vk_layout.pack_start(self.reset_vk_auth_button, False, False, 0)
        vk_layout.pack_start(self.vk_autocomplete, False, False, 0)

        """all"""
        box.pack_start(l_frame, False, True, 0)
        box.pack_start(vk_frame, False, True, 0)

        self.widget = box

    @idle_task
    def on_reset_vk_click(self, *a):
        self.controls.vk_service.reset_vk()
        self.vk_account_label.set_text(self.frase_begin + " %s" % self.default_label_value)

    def get_and_set_profile(self):
        def task_get_and_set_profile():
            profile = self.controls.net_wrapper.execute(self.controls.vk_service.get_profile, True)
            if profile:
                fname = profile[0]["first_name"]
                sname = profile[0]["last_name"]
                GLib.idle_add(self.vk_account_label.set_text, self.frase_begin + " %s %s" % (fname, sname))
        thread.start_new_thread(task_get_and_set_profile, () )

    def on_load(self):
        self.login_text.set_text(FCBase().lfm_login)
        self.password_text.set_text(FCBase().lfm_password)
        self.adjustment.set_value(FC().search_limit)
        self.music_scrobbler.set_active(FC().enable_music_scrobbler)
        self.radio_scrobbler.set_active(FC().enable_radio_scrobbler)
        self.vk_autocomplete.set_active(FC().enable_vk_autocomlete)

    def on_save(self):
        if FCBase().lfm_login != self.login_text.get_text() or FCBase().lfm_password != self.password_text.get_text():
            FCBase().cookie = None

        FCBase().lfm_login = self.login_text.get_text()
        FCBase().lfm_password = self.password_text.get_text()
        FC().search_limit = self.adjustment.get_value()
        FC().enable_music_scrobbler = self.music_scrobbler.get_active()
        FC().enable_radio_scrobbler = self.radio_scrobbler.get_active()
        FC().enable_vk_autocomlete  = self.vk_autocomplete.get_active()

class VBox(Gtk.Box):
    def __init__(self, config, orientation, spacing):
            Gtk.Box.__init__(self, orientation=orientation, spacing=spacing)
            self.config = config

    def show(self):
            self.config.get_and_set_profile()
            super(VBox, self).show()
