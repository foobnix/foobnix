#-*- coding: utf-8 -*-
'''
Created on 1 сент. 2010

@author: ivan
'''

from gi.repository import Gtk
import time
import logging
import urllib2

from foobnix.fc.fc import FC
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util.proxy_connect import set_proxy_settings
from foobnix.gui.service.lastfm_service import LastFmService
from gi.repository import GObject


class NetworkConfig(ConfigPlugin):
    
    name = _("Network Settings")
    
    def __init__(self, controls):
        
        self.controls = controls
                
        box = Gtk.VBox(False, 0)
        box.hide()
        
        self.enable_proxy = Gtk.CheckButton(label=_("Enable HTTP proxy"), use_underline=True)
        self.enable_proxy.connect("clicked", self.on_enable_http_proxy)
        self.enable_proxy.show()
        
        self.frame = Gtk.Frame(label=_("Settings"))
        self.frame.set_border_width(0)
        self.frame.show()
        
        all = Gtk.VBox(False, 0)
        all.show()
        
        
        """URL"""
        proxy_box = Gtk.HBox(False, 0)
        proxy_box.show()
        
        proxy_lable = Gtk.Label(_("Server"))
        proxy_lable.set_size_request(150, -1)
        proxy_lable.show()
        
        self.proxy_server = Gtk.Entry()
        self.proxy_server.show()
        
        require = Gtk.Label(_("example: 66.42.182.178:3128"))
        require.show()
        
        proxy_box.pack_start(proxy_lable, False, False, 0)
        proxy_box.pack_start(self.proxy_server, False, True, 0)
        proxy_box.pack_start(require, False, True, 0)
        
        
        """LOGIN"""
        lbox = Gtk.HBox(False, 0)
        lbox.show()
        
        login = Gtk.Label(_("Login"))
        login.set_size_request(150, -1)
        login.show()
        
        self.login_text = Gtk.Entry()
        self.login_text.show()
        
        lbox.pack_start(login, False, False, 0)
        lbox.pack_start(self.login_text, False, True, 0)
        
        """PASSWORD"""
        pbox = Gtk.HBox(False, 0)
        pbox.show()
        
        password = Gtk.Label(_("Password"))
        password.set_size_request(150, -1)
        password.show()
        
        self.password_text = Gtk.Entry()
        self.password_text.set_visibility(False)
        self.password_text.set_invisible_char("*")
        self.password_text.show()
        
        pbox.pack_start(password, False, False, 0)
        pbox.pack_start(self.password_text, False, True, 0)
        
        """check"""
        
        check = Gtk.HBox(False, 0)
        check.show()

        self.vk_test = Gtk.Entry()
        self.vk_test.set_text("http://vkontakte.ru")        
        self.vk_test.show()
        
        self.test_button = Gtk.Button(_("Check Connection"))
        self.test_button.set_size_request(150, -1)
        self.test_button.connect("clicked", self.text_connection)        
        self.test_button.show()
        
        self.result = Gtk.Label(_("Result:"))
        self.result.show()
        
        check.pack_start(self.test_button, False, True, 0)
        check.pack_start(self.vk_test, False, False, 0)        
        check.pack_start(self.result, False, True, 0)
        
        """global"""
        all.pack_start(proxy_box, False, False, 0)
        all.pack_start(lbox, False, False, 0)
        all.pack_start(pbox, False, False, 0)        
        all.pack_start(check, False, False, 0)
        
        self.frame.add(all)

        frame_box = Gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
        self.net_ping = Gtk.CheckButton(label=_("Show message on network disconnection"), use_underline=True)
        
        box.pack_start(self.net_ping, False, True, 0)
        box.pack_start(self.enable_proxy, False, True, 0)
        box.pack_start(self.frame, False, True, 0)
                
        self.widget = box
        
        if  FC().proxy_enable and FC().proxy_url:
            set_proxy_settings()
        
    
    def text_connection(self, *a):
        self.on_save()
        set_proxy_settings()
        init = time.time()
        try:
            f = urllib2.urlopen(self.vk_test.get_text())
            f.read()
            f.close()
        except Exception, e:
            logging.error(e)
            self.result.set_text(str(e))
            return None
        
        seconds = time.time() - init
        self.result.set_text(_("Result:") + _(" OK in seconds: ") + str(seconds))
    
    def on_enable_http_proxy(self, *a):
        if  self.enable_proxy.get_active():
            self.frame.set_sensitive(True)
        else:
            self.frame.set_sensitive(False)

    def is_proxy_changed(self):
        if [FC().proxy_enable, FC().proxy_url, FC().proxy_user, FC().proxy_password] != [self.enable_proxy.get_active(), self.proxy_server.get_text(), self.login_text.get_text(), self.password_text.get_text()]:
            return True
        else:
            return False    
    
    def on_load(self):
        self.enable_proxy.set_active(FC().proxy_enable)
        self.frame.set_sensitive(FC().proxy_enable)
        
        if FC().proxy_url:
            self.proxy_server.set_text(FC().proxy_url)
        if FC().proxy_user:
            self.login_text.set_text(FC().proxy_user)
        if FC().proxy_password:
            self.password_text.set_text(FC().proxy_password)
            
        if FC().net_ping == True:
            self.net_ping.set_active(True)
            
            
    def on_save(self):
        if not self.is_proxy_changed():
            return
        proxy_url = self.proxy_server.get_text()
        if proxy_url:
            if not ":" in proxy_url:
                logging.error("No port specified")
                proxy_url = proxy_url + ":3128"
            FC().proxy_url = proxy_url.strip()  
        else:
            FC().proxy_url = None
            
        if self.enable_proxy.get_active() and FC().proxy_url:
            FC().proxy_enable = True
            if not self.controls.lastfm_service.network:
                self.controls.lastfm_service = LastFmService(self.controls)
            else:
                self.controls.lastfm_service.network.enable_proxy(FC().proxy_url)
        else:
            FC().proxy_enable = False
            if not self.controls.lastfm_service.network:
                self.controls.lastfm_service = LastFmService(self.controls)
            else:
                self.controls.lastfm_service.network.disable_proxy()

        
        if self.login_text.get_text():
            FC().proxy_user = self.login_text.get_text()
        else:
            FC().proxy_user = None
        
        if self.password_text.get_text():     
            FC().proxy_password = self.password_text.get_text()
        else:     
            FC().proxy_password = None
            
        if self.net_ping.get_active():
            self.controls.net_wrapper.set_ping(True)
        else:
            self.controls.net_wrapper.set_ping(False)

        set_proxy_settings()

        def set_new_vk_window():
            pass

