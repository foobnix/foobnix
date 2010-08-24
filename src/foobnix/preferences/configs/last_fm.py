#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util.configuration import FConfiguration

class LastFmConfig(ConfigPlugin):
    
    name = "Last FM"
    
    def __init__(self):
        print "Create try icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        """LOGIN"""
        lbox = gtk.HBox(False, 0)
        lbox.show()
        
        login = gtk.Label("Login")
        login.set_size_request(150, -1)
        login.show()
        
        self.login_text = gtk.Entry()
        self.login_text.show()
        
        lbox.pack_start(login, False, False, 0)
        lbox.pack_start(self.login_text, False, True, 0)
        
        """PASSWORD"""
        pbox = gtk.HBox(False, 0)
        pbox.show()
        
        password = gtk.Label("Password")
        password.set_size_request(150, -1)
        password.show()
        
        self.password_text = gtk.Entry()
        self.password_text.set_visibility(False)
        self.password_text.set_invisible_char("*")
        self.password_text.show()
        
        pbox.pack_start(password, False, False, 0)
        pbox.pack_start(self.password_text, False, True, 0)
        
        
        box.pack_start(lbox, False, True, 0)
        box.pack_start(pbox, False, True, 0)
        
        self.widget = box
    
    def on_load(self):
        self.login_text.set_text(FConfiguration().lfm_login)
        self.password_text.set_text(FConfiguration().lfm_password)
    
    def on_save(self):
        FConfiguration().lfm_login = self.login_text.get_text()
        FConfiguration().lfm_password = self.login_text.get_text() 
        
