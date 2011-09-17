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
    
    name = _("Last FM + VK")
    
    def __init__(self, controls):
        box = gtk.VBox(False, 0)        
        box.hide()
        
        """LAST.FM"""
        l_frame = gtk.Frame(label=_("Last.FM"))
        l_frame.set_border_width(0)
        l_layout = gtk.VBox(False, 0)
        
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
        
        l_layout.pack_start(lbox, False, True, 0)
        l_layout.pack_start(pbox, False, True, 0)
        l_layout.pack_start(self.music_scrobbler, False, True, 0)
        l_layout.pack_start(self.radio_scrobbler, False, True, 0)
        l_frame.add(l_layout)
        
        """VK"""
        
        vk_frame = gtk.Frame(label=_("VKontakte"))
        vk_frame.set_border_width(0)
        
        vk_layout = gtk.VBox(False, 0)
        
        profile = controls.net_wrapper.execute(controls.vk_service.get_profile)
        fname, sname = _("VKontakte"), _("Disable")
        if profile:
            fname = profile[0]["first_name"] 
            sname = profile[0]["last_name"]
               
        vk_layout.pack_start(gtk.Label(_("You vk account is:") + " %s %s" % (fname, sname)), False,False)
        
        
        """VK LOGIN"""
        vlbox = gtk.HBox(False, 0)
        vlbox.show()
        
        vlogin = gtk.Label(_("Login"))
        vlogin.set_size_request(150, -1)
        vlogin.show()
        
        
        self.vlogin_text = gtk.Entry()
        self.vlogin_text.set_text(fname)
        self.vlogin_text.show()
        
        vlbox.pack_start(vlogin, False, False, 0)
        vlbox.pack_start(self.vlogin_text, False, True, 0)
        
        """VK PASSWORD"""
        vpbox = gtk.HBox(False, 0)
        vpbox.show()
        
        vpassword = gtk.Label(_("Password"))
        vpassword.set_size_request(150, -1)
        vpassword.show()
        
        self.vpassword_text = gtk.Entry()
        self.vpassword_text.set_visibility(False)
        self.vpassword_text.set_invisible_char("*")
        self.vpassword_text.show()
        
        vpbox.pack_start(vpassword, False, False, 0)
        vpbox.pack_start(self.vpassword_text, False, True, 0)
        
        #vk_layout.pack_start(vlbox)
        #vk_layout.pack_start(vpbox)
        
        vk_exit = gtk.Button(_("Authorization (then need player restart)"))
        
        def show_vk(*a):
            controls.vk_service.show_vk()
        
        vk_exit.connect("clicked",show_vk)
        
        vk_layout.pack_start(vk_exit, False, False)
        
        vk_frame.add(vk_layout)
        
        """all"""        
        box.pack_start(l_frame, False, True, 0)
        box.pack_start(vk_frame, False, True, 0)
        
        
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
