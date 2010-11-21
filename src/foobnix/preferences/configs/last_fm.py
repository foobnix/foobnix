#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util.fc import FC

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
        
        self.music_srobbler = gtk.CheckButton(label=_("Enable Music Srobbler"), use_underline=True)
        self.music_srobbler.show()
        
        self.radio_srobbler = gtk.CheckButton(label=_("Enable Radio Srobbler"), use_underline=True)
        self.radio_srobbler.show()
        
        pbox.pack_start(password, False, False, 0)
        pbox.pack_start(self.password_text, False, True, 0)
        
        
        box.pack_start(lbox, False, True, 0)
        box.pack_start(pbox, False, True, 0)
        box.pack_start(self.music_srobbler, False, True, 0)
        #box.pack_start(self.radio_srobbler, False, True, 0)
        
        self.widget = box
    
    def on_load(self):
        self.login_text.set_text(FC().lfm_login)
        self.password_text.set_text(FC().lfm_password)
        self.music_srobbler.set_active(FC().enable_music_srobbler)
        self.radio_srobbler.set_active(FC().enable_radio_srobbler)
    
    def on_save(self):
        if FC().lfm_login != self.login_text.get_text() or FC().lfm_password != self.password_text.get_text():
            FC().cookie = None
        
        FC().lfm_login = self.login_text.get_text()
        FC().lfm_password = self.password_text.get_text() 
        
        FC().enable_music_srobbler = self.music_srobbler.get_active()
        FC().enable_radio_srobbler = self.radio_srobbler.get_active()
        
