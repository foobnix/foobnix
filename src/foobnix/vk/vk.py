'''
Created on Mar 17, 2010

@author: ivan
'''
# -*- coding: utf-8 -*-
import urllib2
import urllib
import re
import gst
import time

# -*- coding: utf-8 -*-



class Vkontakte:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cookie = None

    def get_s_value(self):

        host = 'http://login.vk.com/?act=login'
        post = urllib.urlencode({'email' : self.email,
                                 'expire' : '',
                                 'pass' : self.password,
                                 'vk' : ''})

        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13 (.NET CLR 3.5.30729)',
                   'Host' : 'login.vk.com',
                   'Referer' : 'http://vkontakte.ru/index.php',
                   'Connection' : 'close',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache',
                  }

        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        result = data.read()
        
        return re.findall(r"name='s' id='s' value='(.*?)'", result)[0]

    def get_cookie(self):

        if self.cookie: return self.cookie

        host = 'http://vkontakte.ru/login.php?op=slogin'
        post = urllib.urlencode({'s' : self.get_s_value()})
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                   'Host' : 'vkontakte.ru',
                   'Referer' : 'http://login.vk.com/?act=login',
                   'Connection' : 'close',
                   'Cookie' : 'remixchk=5; remixsid=nonenone',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache'
                  }
        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        cookie_src = data.info().get('Set-Cookie')
        self.cookie = re.sub(r'(expires=.*?;\s|path=\/;\s|domain=\.vkontakte\.ru(?:,\s)?)', '', cookie_src)
        return self.cookie
    
    def get_page(self):
        host = 'http://vkontakte.ru/gsearch.php?section=audio&q=vasya#c[q]=some%20id&c[section]=audio'
        post = urllib.urlencode({
                                 "c[q]" :"ddt", 
                                 "c[section]":"audio"
                                })
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                   'Host' : 'vkontakte.ru',
                   'Referer' : 'http://vkontakte.ru/index.php',
                   'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                   'X-Requested-With' : 'XMLHttpRequest',
                   'Connection' : 'close',
                   'Cookie' : 'remixlang=0; remixchk=5; audio_vol=100; %s' % self.get_cookie(),
                   'Pragma' : 'no-cache',
                   'Cache-Control' : '    no-cache'
                  }
        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn);
        result = data.read()
        return result
    
def last_search_query(value):
    host = "http://en.vpleer.ru/?q="+value
    data = urllib2.urlopen(host)
    return data.read()

vk = Vkontakte('ivan.ivanenko@gmail.com', 'desteni')
vk.get_cookie()
#print vk.get_page()
ulr = "http://d1.vpleer.ru/download2/47/4404/3425657/3e404fb9b105/DDT-%D0%94%D0%BE%D1%80%D0%BE%D0%B3%D0%B0.mp3"
player = gst.element_factory_make("playbin", "player")
player.set_state(gst.STATE_NULL)
player.set_property("uri", ulr)
player.set_state(gst.STATE_PLAYING)

time.sleep(20)

result = search("ddt")
#result = "href=\"http://d3.vpleer.ru/download2/32/4503/51659145/2fbc500428d2/DDT-V_poslednyuyu_osen%26%2339%3B_%5B_wp-team_%5D.mp3"
name = '<span class="auname">some</span>' 
print re.findall(r"<span class=\"auname\">(\w*)</span>", name)[0]

regexp = "/(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/"

def get_song_path(line):
    path = re.findall(r"href=\"([\w#!:.?+=&%@!\-\/]*.mp3)", line)
    if path:
        return path[0] 

def get_auname(line):
    path = re.findall(r"class=\"auname\">(\w*)", line)
    if path:
        return path[0] 

def get_ausong(line):
    path = re.findall(r"class=\"auname\">(\w*)<", line)
    if path:
        return path[0] 

unicode(result, 'utf-8')

p1 = re.findall('href="([\w#!:.?+=&%@!\-\/]*.mp3)" title="Download"', result)
p2 = re.findall('<span class="auname">([a-zA-Z0-9_ \S]*)</span>', result)
p3 = re.findall('<span class="ausong">([a-zA-Z0-9_ \S]*)</span> -', result)
p4 = re.findall('<div class="time">([0-9:]*)</div>', result)

print "path  ",len(p1), p1
print "auname",len(p2), p2
print "ausong",len(p3), p3
print "time  ",len(p4), p4
   

    
  

