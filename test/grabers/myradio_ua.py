# -*- coding: utf-8 -*-
'''
Created on 16  2010

@author: ivan
'''
import urllib2
import logging
import re
site = "http://myradio.ua/player/7"


def load_urls_name_page():
    connect = urllib2.urlopen(site)
    data = connect.read()  
    result = {}  
    file = open("MYRADIO_UA.fpl", "w")
    for line in data.split("\n"):
        line = line.decode('utf8')

        if "<a href" in line and "mount" in line:
            reg_all = "([-\w0-9,. &]*)"
            findall = re.findall('name="'+reg_all+'"', line, re.IGNORECASE | re.UNICODE)
            print findall
            if findall:
                name = findall[0]

                findall = re.findall('mount="'+reg_all+'"', line, re.IGNORECASE | re.UNICODE)
                if findall:
                    url = findall[0]
                    out = name + " = " + "http://relay.myradio.ua/" + url + "192.mp3 \n"
                    print out
                    file.write(out.encode("utf-8", "replace"))
        

def test():
    reg_all = "([-\w/0-9,. ]*)"
    url = """ <a href="/player/4" name="Русские хиты 90-х" onclick="MRPlayer.changeFormat(this);" id="format_4" mount="russkie-hity-90-h" server="2" external="0" value="4" image="" slogan="Самые яркие и популярные русские хиты 90-х" url="russkie-hity-90-h" comments="170">Русские хиты 90-х</a> """
    findall = re.findall('name="'+reg_all+'"', url.decode('utf8'),re.UNICODE)
    print findall[0]

    findall = re.findall('mount="'+reg_all+'"', url.decode('utf8'),re.UNICODE)
    print findall[0]
             

#test()
load_urls_name_page()