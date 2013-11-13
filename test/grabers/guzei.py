# -*- coding: utf-8 -*-
'''
Created on Jul 16, 2010

@author: ivan
'''

import re
import logging
import urllib2
from foobnix.util.plsparser import is_valid_station
import os

def load_urls_name_page():
    file_name = "GUZEI.COM.fpl";
    if os.path.isfile(file_name):
        os.remove(file_name)
    file = open(file_name, "w")
    for j in range(1,30):
        result = []
        print "==========", "page", str(j),"============================"
        site = "http://guzei.com/online_radio/index.php?f[mp3]=on&radio_format=0&p=" + str(j)
        print site
        connect = urllib2.urlopen(site)
        data = connect.read()  
        
        for line in data.split("\n"):
            if '<a target="guzei_online" href="./listen.php?online_radio_id=' in line:
                reg_all = "([^{</}]*)"
              
                re_link = '<a target="guzei_online" href="./listen.php\?online_radio_id=([0-9]*)" title="' + reg_all + '"><span class="name">' + reg_all + '</span></a>'
                re_region = '<a href="./\?radio_region=([0-9]*)">' + reg_all + '</a>'
                re_bitrate = '\d*Kbps'
                
                links = re.findall(re_link, line, re.IGNORECASE | re.UNICODE)
                if links:
                    region = re.findall(re_region, line, re.IGNORECASE | re.UNICODE)
                    re_bitrate = re.findall(re_bitrate, line, re.IGNORECASE | re.UNICODE)
                    i = 0
                    for line in links:
                        
                        id = line[0]
                        name = line[2]
                        if region:
                            name = name + " (" + region[i][1] + ")" + ' - ' + re_bitrate[i]
                        i += 1
                        print id,name
                        url = get_ulr_by_id(id)
                        print url
                        if not url:
                            continue
                        if not is_valid_station(url):
                            continue
                                                     
                        res = name + " = " + url
                        logging.info(j)
                        logging.info(res)
                        print "page", j, res
                        result.append(res + '\n')
                        #file.write(res + '\n')
            
        map(file.write, result)

def get_ulr_by_id(id):
    url = "http://guzei.com/online_radio/listen.php?online_radio_id=" + str(id)
    connect = urllib2.urlopen(url)
    data = connect.read()
    reg_all = "([^{<}]*)"
    links = re.findall(u'<source src="'+reg_all+'"', data, re.IGNORECASE | re.UNICODE)
    if links and links[0]:
        path = links[0].replace('" width="300px" height="94','')
        return path
    else:
        return None
        
            
if __name__ == '__main__':
    load_urls_name_page()
    #get_ulr_by_id(2728)  
