#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
from foobnix.util.configuration import FConfiguration
from foobnix.preferences.configs.last_fm import LastFmConfig

class VkontakteConfig(LastFmConfig):
    
    name = _("Vkontakte")
    
    def __init__(self, controls):
        LastFmConfig.__init__(self, controls)
        
    def on_load(self):
        self.login_text.set_text(FConfiguration().vk_login)
        self.password_text.set_text(FConfiguration().vk_password)
    
    def on_save(self):
        if FConfiguration().vk_login !=  self.login_text.get_text() or FConfiguration().vk_password != self.password_text.get_text():
            FConfiguration().cookie = None
                        
        FConfiguration().vk_login = self.login_text.get_text()
        FConfiguration().vk_password = self.password_text.get_text() 
        
        
