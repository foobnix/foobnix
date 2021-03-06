#-*- coding: utf-8 -*-
'''
Created on 1 sep. 2010

@author: ivan
'''

import logging
import urllib.request

from foobnix.fc.fc import FC

def set_proxy_settings():
    if not FC().proxy_url or not FC().proxy_enable:
        opener = urllib.request.build_opener()
        urllib.request.install_opener(opener)
        return
    if FC().proxy_user and FC().proxy_password:
        http_proxy = "http://%s:%s@%s" % (FC().proxy_user, FC().proxy_password, FC().proxy_url)
        https_proxy = "https://%s:%s@%s" % (FC().proxy_user, FC().proxy_password, FC().proxy_url)
    else:
        http_proxy = "http://%s" % FC().proxy_url
        https_proxy = "https://%s" % FC().proxy_url
    proxy = urllib.request.ProxyHandler({"http" : http_proxy, "https" : https_proxy})
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)
    logging.info("The proxy " + FC().proxy_url + " for http and https has been set")
    
if __name__ == '__main__':
    set_proxy_settings()
    res = urllib.request.urlopen('https://mail.ru')
    print(res.read())
