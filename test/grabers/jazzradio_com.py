# -*- coding: utf-8 -*-
'''
Created on 17 Nov 2013

@author: Viktor Suprun
'''
import urllib2
import simplejson
from HTMLParser import HTMLParser


def load_urls_name_page():
    connect = urllib2.urlopen("http://listen.jazzradio.com/public3")
    data = connect.read()
    p = HTMLParser()
    data = p.unescape(data)
    for i in simplejson.loads(data):
        print "%s =  %s" % (i["name"].encode('utf-8'), i["playlist"].encode('utf-8'))

if __name__ == "__main__":
    load_urls_name_page()