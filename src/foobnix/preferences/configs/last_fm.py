#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.fc.fc import FC
from foobnix.fc.fc_base import FCBase

class LastFmConfig(ConfigPlugin):
    
    name = _("Last FM")
    
    def __init__(self, controls):
        box = gtk.VBox(False, 0)        
        box.hide()
        
        """LOGIN"""
        lbox = gtk.HBox(False, 0)
        lbox.show()
        
        login = gtk.Label(_("Login"))
        login.set_size_request(150, -1)
        login.show()
        
        self.login_text = gtk.Entry()
        self.login_text.show()
        
        lbox.pack_start(login, False, False, 0)
        lbox.pack_start(self.login_text, False, True, 0)
        
        """PASSWORD"""
        pbox = gtk.HBox(False, 0)
        pbox.show()
        
        password = gtk.Label(_("Password"))
        password.set_size_request(150, -1)
        password.show()
        
        self.password_text = gtk.Entry()
        self.password_text.set_visibility(False)
        self.password_text.set_invisible_char("*")
        self.password_text.show()
        
        self.music_scrobbler = gtk.CheckButton(label=_("Enable Music Scrobbler"), use_underline=True)
        self.music_scrobbler.show()
        
        self.radio_scrobbler = gtk.CheckButton(label=_("Enable Radio Scrobbler"), use_underline=True)
        self.radio_scrobbler.show()
        
        pbox.pack_start(password, False, False, 0)
        pbox.pack_start(self.password_text, False, True, 0)
        
        
        box.pack_start(lbox, False, True, 0)
        box.pack_start(pbox, False, True, 0)
        box.pack_start(self.music_scrobbler, False, True, 0)
        
        self.widget = box
    
    def on_load(self):
        self.login_text.set_text(FCBase().lfm_login)
        self.password_text.set_text(FCBase().lfm_password)
        self.music_scrobbler.set_active(FC().enable_music_scrobbler)
        self.radio_scrobbler.set_active(FC().enable_radio_scrobbler)
    
    def on_save(self):
        if FCBase().lfm_login != self.login_text.get_text() or FCBase().lfm_password != self.password_text.get_text():
            FCBase().cookie = None
        
        FCBase().lfm_login = self.login_text.get_text()
        FCBase().lfm_password = self.password_text.get_text() 
        
        FC().enable_music_scrobbler = self.music_scrobbler.get_active()
        FC().enable_radio_scrobbler = self.radio_scrobbler.get_active()
