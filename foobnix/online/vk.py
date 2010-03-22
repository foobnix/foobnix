# -*- coding: utf-8 -*-
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
from string import replace
from base64 import encode
import sys

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
    
    def get_page(self, query):
        host = 'http://vkontakte.ru/gsearch.php?section=audio&q=vasya#c[q]=some%20id&c[section]=audio'
        post = urllib.urlencode({
                                 "c[q]" : query,
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
    
    def get_name_by(self, id, result_album):
            for album in result_album:
                id_album = album[0]
                name = album[1]
                if id_album == id:
                    return name
            
            return None   
        
    def find_most_relative_song(self, song_title):
        vkSongs = self.find_song_urls(song_title)
        if not vkSongs:
            return None
            
        times_count = {}
        for song in vkSongs:
            time = song.time
            if time in times_count:
                times_count[time] = times_count[time] + 1
            else:
                times_count[time] = 1 
        
        #get most relatives times time
        r_count = max(times_count.values())
        r_time = self.find_time_value(times_count, r_count)
        print r_time
        print r_count
        
        for song in vkSongs:
            if song.time == r_time:        
                return song
                    
        return vkSongs[0]
            
    def find_time_value(self, times_count, r_count):
        for i in times_count:
            if times_count[i] == r_count:
                return i
        return None              
    
    def find_song_urls(self, song_title):
        
        page = self.get_page(song_title)
        page = page.decode('cp1251')
        #page = page.decode("cp1251")
        #unicode(page, "cp1251")
        
        #print page
                
        
                
        reg_all = "([А-ЯA-Z0-9_ #!:;.?+=&%@!\-\/'()]*)"
        resultall = re.findall("return operate\(([\w() ,']*)\);", page, re.IGNORECASE)
        result_album = re.findall(u"<b id=\\\\\"performer([0-9]*)\\\\\">" + reg_all + "<", page, re.IGNORECASE | re.UNICODE)
        result_track = re.findall(u"<span id=\\\\\"title([0-9]*)\\\\\">" + reg_all + "<", page, re.IGNORECASE | re.UNICODE)
        result_time = re.findall("<div class=\\\\\"duration\\\\\">" + reg_all + "<", page, re.IGNORECASE)
        
        
        urls = []
        ids = []
        vkSongs = [] 
        for result in resultall:
            result = replace(result, "'", " ")
            result = replace(result, ",", " ")
            
            result = result.split()
            
            if len(result) > 4:
                id_id = result[0]
                id_server = result[1]
                id_folder = result[2]
                id_file = result[3]
                id_un2 = result[3]
            
                url = "http://cs" + id_server + ".vkontakte.ru/u" + id_folder + "/audio/" + id_file + ".mp3"
                urls.append(url)
                ids.append(id_id)
        
        #print len(resultall), resultall
        #print len(urls), urls
        print len(result_album), result_album
        print len(result_track), result_track
        #print len(result_time), result_time
        
        for i in xrange(len(result_time)):    
            id = ids[i]       
            path = urls[i] 
            album = self.get_name_by(id, result_album)
            track = self.get_name_by(id, result_track)
            time = result_time[i] 
            vkSong = VKSong(path, album, track, time)
            vkSongs.append(vkSong)            
        
        return vkSongs
        
        
       

class VKSong():
    def __init__(self, path, album, track, time):
        self.path = path
        self.album = album
        self.track = track
        self.time = time
    
    def getTime(self):
        if self.time:
            return time
        else: 
            return "no time" 
        
    def getFullDescription(self):
        return "[ " + self.s(self.album) + " ] " + self.s(self.track) + " " + self.s(self.time) 
    
    def __str__(self):
        return "" + self.s(self.album) + " " + self.s(self.track) + " " + self.s(self.time) + " " + self.s(self.path)

    def s(self, value):
        if value:
            return value
        else: 
            return ""   

        
#vk = Vkontakte("qax@bigmir.net", "foobnix")
#vkSongs = vk.find_song_urls("rammstein du hast")

#print "RESULT ", vk.find_more_relative_song("rammstein du hast")
#for vkSong in vkSongs:
#    print vkSong

line = """ <b id=\"performer87403420\"> mi123sdf ФЫВАв serdce Trofim)<\/b><span><b id=\"performer87403420"""
print line
print re.findall("<b id=\"performer([0-9]*)\">([А-ЯA-Z0-9 ()]*)<", line, re.IGNORECASE)

line = """nbsp;<\/span><span id=\"title76067271\">SHtil&#39;<\/span> <small class=\<span id="title87919392">
<a href="javascript: showLyrics(87919392,3966457);">Кто ты</a>
</span>"""
print re.findall(" < span id = \"title([0-9]*)\">([А-ЯA-ZёЁ0-9 \s#!;:.?+=&%@!\-\/'()]*)<", line, re.IGNORECASE)

map = {}
for i in xrange(3, 10):
    map[i] = -i * i
    
    
for el in map:
    print el, map[el]
    

print 4 in map    
print max(map)
print map.keys()
print max(map.values())
print max(map)
print [ k for k in sorted(map.values())] 

        

