# -*- coding: utf-8 -*-
'''
Created on Mar 17, 2010

@author: ivan
'''

import urllib2
import urllib
import re
import time
from string import replace

from foobnix.util import LOG
from foobnix.util.configuration import FConfiguration
from foobnix.model.entity import CommonBean

from xml.sax.saxutils import escape, unescape
import htmlentitydefs
from setuptools.package_index import htmldecode



class Vkontakte:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cookie = None
        self.execute_time = time.time()
       
        
    def isLive(self):
        return self.get_s_value()

    def get_s_value(self):

        host = 'http://login.vk.com/?act=login'
        #host = 'http://vkontakte.ru/login.php'
        post = urllib.urlencode({'email' : self.email,
                                 'expire' : '',
                                 'pass' : self.password,
                                 'vk' : ''})

        headers = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; uk; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.0',
                   'Host' : 'login.vk.com',
                   'Referer' : 'http://vkontakte.ru/index.php',
                   'Connection' : 'close',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache',
                  }

        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        result = data.read()               
        value = re.findall(r"name='s' value='(.*?)'", result)
        
        """old response format"""
        if not value:
            value = re.findall(r"name='s' id='s' value='(.*?)'", result)
            
        if value:
            return value[0]
        
        return None

    def get_cookie(self):
        
        if FConfiguration().cookie:
            LOG.info("Get VK cookie from cache") 
            return FConfiguration().cookie 
        
        if self.cookie: return self.cookie
        
        
        host = 'http://vkontakte.ru/login.php?op=slogin'
        post = urllib.urlencode({'s' : self.get_s_value()})
        headers = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; uk; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.0',
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
        
        FConfiguration().cookie = self.cookie 
        return self.cookie
    
    def get_page(self, query):
        if not query:
            return None
        
        #GET /gsearch.php?section=audio&q=madonna&name=1

        host = 'http://vkontakte.ru/gsearch.php?section=audio&q=vasya#c[q]=some%20id&c[section]=audio&name=1'
        post = urllib.urlencode({
                                 "c[q]" : query,
                                 "c[section]":"audio"
                                })
        headers = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; uk; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.0',
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
        
        #Do not run to offten
        cur_time = time.time()
        if cur_time - self.execute_time < 0.5:
            print "Sleep because to many requests..."
            time.sleep(0.8)        
        self.execute_time = time.time()
        
        data = urllib2.urlopen(conn);
        result = data.read()
        return result
    
       
    def get_page_by_url(self, host_url):
        if not host_url:
            return host_url
        host_url.replace("#","&")
        post = host_url[host_url.find("?")+1:]
        LOG.debug("post", post)
        headers = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; uk; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.0',
                   'Host' : 'vkontakte.ru',
                   'Referer' : 'http://vkontakte.ru/index.php',
                   'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                   'X-Requested-With' : 'XMLHttpRequest',
                   'Connection' : 'close',
                   'Cookie' : 'remixlang=0; remixchk=5; audio_vol=100; %s' % self.get_cookie(),
                   'Pragma' : 'no-cache',
                   'Cache-Control' : '    no-cache'
                  }
        conn = urllib2.Request(host_url, post, headers)
        
        #Do not run to offten
        cur_time = time.time()
        if cur_time - self.execute_time < 0.5:
            print "Sleep because to many requests..."
            time.sleep(0.8)        
        self.execute_time = time.time()
        
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
        print "Print Song time", r_time
        print "Print Count of congs", r_count
        
        for song in vkSongs:
            if song.time == r_time:        
                return song
                    
        return vkSongs[0]
            
    def find_time_value(self, times_count, r_count):
        for i in times_count:
            if times_count[i] == r_count:
                return i
        return None 
    
    def convert_vk_songs_to_beans(self, vk_songs):
        beans = []
        for vk_song in vk_songs:
            bean = CommonBean(name=vk_song.album + " - " + vk_song.track, path=vk_song.path, type=CommonBean.TYPE_MUSIC_URL);
            beans.append(bean)
        return beans

             
    
    def find_song_urls(self, song_title):
        
        page = self.get_page(song_title)
        print page
        page = page.decode('cp1251')
        #page = page.decode("cp1251")
        #unicode(page, "cp1251")
        
        #print page
                
        reg_all = "([^<>]*)"
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
            
                url = "http://cs" + id_server + ".vkontakte.ru/u" + id_folder + "/audio/" + id_file + ".mp3"
                urls.append(url)
                ids.append(id_id)
        
        #print len(resultall), resultall
        #print len(urls), urls
        #print len(result_album), result_album
        #print len(result_track), result_track
        #print len(result_time), result_time
        
        for i in xrange(len(result_time)):    
            id = ids[i]       
            path = urls[i] 
            album = self.get_name_by(id, result_album)
            track = self.get_name_by(id, result_track)
            time = result_time[i] 
            vkSong = VKSong(path, album, track, time)
            vkSongs.append(vkSong)            
        
        return self.convert_vk_songs_to_beans(vkSongs)
     
    def get_songs_by_url(self, url):
        LOG.debug("Search By URL")
        result = self.get_page_by_url(url) 
        try:       
            result=unicode(result)
        except:
            result=result
            LOG.error("VK connectino error, try other user")
        reg_all = "([^{</}]*)"
        result_url = re.findall(ur"http:([\\/.0-9A-Z]*)", result, re.IGNORECASE)
        result_artist = re.findall(u"q]="+reg_all+"'", result, re.IGNORECASE | re.UNICODE)
        result_title = re.findall(u"\"title([0-9]*)\\\\\">"+  reg_all+"", result, re.IGNORECASE | re.UNICODE)
        result_time = re.findall("duration\\\\\">" + reg_all, result, re.IGNORECASE | re.UNICODE)
        result_lyr = re.findall(ur"showLyrics"+reg_all, result, re.IGNORECASE | re.UNICODE)
        print "lyr:::", result_lyr
        songs = []
        j = 0
        for i, artist in enumerate(result_artist):
            path = "http:" +result_url[i].replace("\\/", "/")
            title =  self.to_good_chars(result_title[i][1])
            if not title:
                if len(result_lyr) > j:
                    title = result_lyr[j]
                    title = title[title.find(";'>")+3:]
                    j +=1                
            artist =  self.to_good_chars(artist)
            song = VKSong(path, artist, title, result_time[i]);            
            songs.append(song)        
        print len(songs)
        return self.convert_vk_songs_to_beans(songs)    

    def to_good_chars(self, line):
        try:
            return htmldecode(line)
        except:
            return unescape(line)
        
        
       

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

def get_group_id(str):
    search = "gid="
    index = str.find("gid=")
    return str[index+len(search):]
    
    
#vk = Vkontakte("qax@bigmir.net", "foobnix")
#print vk.get_s_value()
#print vk.get_cookie()
#line = "http://vkontakte.ru/audio.php?id=7185772"
#print vk.find_most_relative_song("madonna")

#s = "http://vkontakte.ru/audio.php?id=2765347 < & > ' &#39; &amp;"
#print unescape(s)    


