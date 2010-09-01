#-*- coding: utf-8 -*-
'''
Created on 1 сент. 2010

@author: ivan
'''
import urllib2
from foobnix.util.configuration import FConfiguration
from foobnix.util import LOG
class ProxyPasswordMgr:
    def __init__(self):
        self.user = self.passwd = None
    def add_password(self, realm, uri, user, passwd):
        self.user = user
        self.passwd = passwd
    def find_user_password(self, realm, authuri):
        return self.user, self.passwd

def set_proxy_settings():
    if FConfiguration().proxy_enable and FConfiguration().proxy_url:
        #http://spys.ru/proxylist/
        proxy = FConfiguration().proxy_url
        user = FConfiguration().proxy_user
        password = FConfiguration().proxy_password
        
        LOG.info("Proxy enable:", proxy, user, password)
        
        proxy = urllib2.ProxyHandler({"http" : proxy})
        proxy_auth_handler = urllib2.ProxyBasicAuthHandler(ProxyPasswordMgr())
        proxy_auth_handler.add_password(None, None, user, password)
        opener = urllib2.build_opener(proxy, proxy_auth_handler)
        urllib2.install_opener(opener)
    else:
        LOG.info("Proxy not enable")
