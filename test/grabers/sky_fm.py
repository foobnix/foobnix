# -*- coding: utf-8 -*-
'''
Created on 16  2010

@author: ivan
'''
import urllib2
import simplejson
from HTMLParser import HTMLParser


def load_urls_name_page():
    connect = urllib2.urlopen("http://listen.sky.fm/public3")
    data = connect.read()
    p = HTMLParser()
    data = p.unescape(data)
    for i in simplejson.loads(data):
        print "%s =  %s" % (i["name"], i["playlist"])

if __name__ == "__main__":
    load_urls_name_page()