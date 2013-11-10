# -*- coding: utf-8 -*-
'''
Created on 16  2010

@author: ivan
'''
import urllib2
import logging
import re
site = "http://myradio.ua/player/50"


def load_urls_name_page():
    connect = urllib2.urlopen(site)
    data = connect.read()  
    result = {}  
    file = open("MYRADIO_UA.fpl", "w")
    for line in data.split("\n"):
        line = line.decode("cp1251").decode('utf8')
        reg_all = "([-\w0-9,. ]*)"
        findall = re.findall('name="'+reg_all+'" value="([0-9]*)" external="0" mount="'+reg_all+'"', line, re.IGNORECASE | re.UNICODE)
        if findall:
            name = findall[0][0]
            url = findall[0][2]
            out = name + " = " + "http://relay.myradio.ua/" + url + "128.mp3 \n"
            print out
            file.write(out)
        

def test():
    reg_all = "([-\w/0-9,. ]*)"
    url = """<a onclick="MRPlayer.changeFormat(this);" id="format_62" name="фіasdf-123" value="62" external="0" mount="eurovision2010" server="1" class="radio__dropdown-link" slogan="Музыка ежегодного телевизионного конкурса" url="eurovision" comments="40" fm="0">Евровидение</a>"""
    findall = re.findall('name="'+reg_all+'" value="([0-9]*)" external="0" mount="'+reg_all+'"', url.decode('utf8'),re.UNICODE)
    if findall:
        print findall
             

#test();
load_urls_name_page()