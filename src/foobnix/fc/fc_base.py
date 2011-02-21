#-*- coding: utf-8 -*-
'''
Created on 23 сент. 2010

@author: ivan
'''
from __future__ import with_statement
from foobnix.fc.fc_helper import FCStates, CONFIG_DIR
from foobnix.util.singleton import Singleton
import random
import uuid
import os

def get_random_vk():
    vks = {
       "c891888@bofthew.com":"c891888",
       "c892009@bofthew.com":"c892009",
       "c892406@bofthew.com":"c892406",
       "c892588@bofthew.com":"c892588"
       }

    return random.choice(vks.items())


CONFIG_BASE_FILE = os.path.join(CONFIG_DIR, "foobnix_base.pkl") 

"""Foobnix base configuration, not change after installation, stable"""
class FCBase():
    __metaclass__ = Singleton

    API_KEY = "bca6866edc9bdcec8d5e8c32f709bea1"
    API_SECRET = "800adaf46e237805a4ec2a81404b3ff2"
    LASTFM_USER = "l_user_"
    LASTFM_PASSWORD = "l_pass_"
    
    def __init__(self):
        """vk"""
        self.vk_login, self.vk_password = get_random_vk()
        self.vk_cookie = None
        
        """last fm"""
        self.lfm_login = self.LASTFM_USER
        self.lfm_password = self.LASTFM_PASSWORD
        
        self.uuid = uuid.uuid4().hex

         
        self.load();
    
    def save(self):
        FCStates().save(self, CONFIG_BASE_FILE)
    
    def load(self):
        FCStates().load(self, CONFIG_BASE_FILE)
