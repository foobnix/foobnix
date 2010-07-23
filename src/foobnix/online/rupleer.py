# -*- coding: utf-8 -*-
'''
Created on Mar 18, 2010

@author: ivan
'''
import urllib2
import re
from string import replace

def _engine_search(value):
    value = replace(value, " ", "+")
    host = "http://en.vpleer.ru/?q=" + value
    LOG.info(host)  
    data = urllib2.urlopen(host)
    return data.read()

def get_song_path(line):
    path = re.findall(r"href=\"([\w#!:.?+=&%@!\-\/]*.mp3)", line)
    if path:
        return path 

def get_auname(line):
    path = re.findall(r"class=\"auname\">(\w*)", line)
    if path:
        return path 

def get_ausong(line):
    path = re.findall(r"class=\"auname\">(\w*)<", line)
    if path:
        return path 

def find_song_urls(song_title):
    data = _engine_search(song_title)    
    paths = get_song_path(data)            
    return paths


#LOG.info("Result:", find_song_urls("Ария - Антихрист")  
    
    
