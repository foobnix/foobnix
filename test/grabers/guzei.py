# -*- coding: utf-8 -*-
'''
Created on Jul 16, 2010

@author: ivan
'''

import re
import sys
import logging
import urllib2
from multiprocessing import Pool

def load_urls_name_page():
    site = "http://guzei.com/online_radio/"
    file = open("GUZEI.COM.fpl", "w")
    j = 1
    result = []
    while True:
        print "Opening page %d" % j
        site = "http://guzei.com/online_radio/?p=" + str(j)
        connect = urllib2.urlopen(site)
        data = connect.read()
        for line in data.split("\n"):
            reg_all = "([^{</}]*)"

            re_link = '<a target="guzei_online" href="./listen.php\?online_radio_id=([0-9]*)" title="' + reg_all + '"><span class="name">' + reg_all + '</span></a>'
            re_region = '<a href="\./index\.php\?radio_region=([0-9]*)">' + reg_all + '</a>'
            re_bitrate = '\d*Kbps'

            links = re.findall(re_link, line, re.IGNORECASE | re.UNICODE)

            if links:
                region = re.findall(re_region, line, re.IGNORECASE | re.UNICODE)
                re_bitrate = re.findall(re_bitrate, line, re.IGNORECASE | re.UNICODE)
                i = 0
                pool_queue = []
                for line in links:
                    id = line[0]
                    name = line[2]
                    if region:
                        name = name + " (" + region[i][1] + ")" + ' - ' + re_bitrate[i]
                    i += 1
                    pool_queue.append({
                        'name': name,
                        'id': id
                    })
                pool = Pool(processes=12)
                actual = pool.map(get_url_by_id, pool_queue)
                for entry in actual:
                    if "url" in entry:
                        result.append("%s =  %s\n" % (entry["name"], entry["url"]))

        if re.search('<span class="nav_bar">\d*</span><a class="nav_bar"', data):
            j += 1
            continue
        else:
            print "The end"
            #map(sys.stdout.write, result)
            map(file.write, result)
            break


def get_url_by_id(entry):
    id = entry["id"]
    print "\tGetting url for station %s" % id
    url = "http://guzei.com/online_radio/listen.php?online_radio_id=" + id
    connect = urllib2.urlopen(url)
    data = connect.read()
    for line in data.split("\n"):
        line = line.strip()
        cr = '<audio autoplay="autoplay" controls="controls" style="margin: 2px auto"><source src="'
        if line.startswith(cr):
            subline = line[len(cr) : ]
            link = subline[0 : subline.find('"')]
            link = link.strip()
            entry["url"] = link
            return entry
    return entry

if __name__ == '__main__':
    load_urls_name_page()
