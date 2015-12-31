#-*- coding: utf-8 -*-
'''
Created on 1 дек. 2010

@author: ivan
'''
import urllib
import httplib
import urlparse


""""
Server: nginx/0.8.53
Date: Wed, 01 Dec 2010 07:37:42 GMT
Content-Type: text/html
Content-Length: 169
Connection: close
"""

def get_url_length(path):
    open = urllib.urlopen(path)
    return open.info().getheaders("Content-Length")[0]

def get_url_type(path):
    open = urllib.urlopen(path)
    return open.info().getheaders("Content-Type")[0]

"""method is not reliable. too dependent on the server configuration"""
def is_exists(url):
    p = urlparse.urlparse(url)
    h = httplib.HTTP(p[1])
    h.putrequest('HEAD', p[2])
    h.endheaders()
    if h.getreply()[0] == 200:
        return 1
    else:
        return 0

if __name__ == '__main__':
    is_exists("")