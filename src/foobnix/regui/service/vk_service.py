# -*- coding: utf-8 -*-
'''
Created on Sep 29, 2010

@author: ivan
'''
import time
from foobnix.util.fc import FC
import urllib2
from foobnix.util import LOG
import urllib
import re
from foobnix.helpers.dialog_entry import show_login_password_error_dialog
from setuptools.package_index import htmldecode
from setuptools.command.sdist import unescape
from string import replace
from foobnix.regui.model import FModel
    
class VKService:
    def __init__(self, email=None, password=None):
        self.vk_cookie = None
        self.execute_time = time.time()
       
        
    def isLive(self):
        return self.get_s_value()

    def get_s_value(self):

        host = 'http://login.vk.com/?act=login'
        #host = 'http://vkontakte.ru/login.php'
        post = urllib.urlencode({'email' : FC().vk_login,
                                 'expire' : '',
                                 'pass' : FC().vk_password,
                                 'vk' : ''})

        headers = {'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686; uk; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB7.0',
                   'Host' : 'login.vk.com',
                   'Referer' : 'http://vkontakte.ru/index.php',
                   'Connection' : 'close',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache',
                  }

        conn = urllib2.Request(host, post, headers)
        try:
            data = urllib2.urlopen(conn)
        except:
            LOG.error("Error VK connection")
            return None
            
        result = data.read()               
        value = re.findall(r"name='s' value='(.*?)'", result)
        
        """old response format"""
        if not value:
            value = re.findall(r"name='s' id='s' value='(.*?)'", result)
            
        if value:
            return value[0]
        
        return None

    def get_cookie(self):
        if FC().vk_cookie:
            LOG.info("Get VK cookie from cache") 
            return FC().vk_cookie
        
        s_value = self.get_s_value()
        if not s_value:    
            FC().vk_cookie = None    
            val = show_login_password_error_dialog(_("VKontakte connection error"), _("Verify user and password"), FC().vk_login, FC().vk_password)
            if val:
                FC().vk_cookie = None
                FC().vk_login = val[0]
                FC().vk_password = val[1]
            return None 
        
        if self.vk_cookie: 
            return self.vk_cookie
        
        
        host = 'http://vkontakte.ru/login.php?op=slogin'
        post = urllib.urlencode({'s' : s_value})
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
        
        FC().vk_cookie = self.vk_cookie 
        return self.cookie
    
    def get_page(self, query, section="audio"):
        if not query:
            return None

        host = 'http://vkontakte.ru/gsearch.php?section=' + section + '&q=vasya#c[q]=some%20id&c[section]=audio&name=1'
        post = urllib.urlencode({
                                 "c[q]" : query,
                                 "c[section]":section
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
            LOG.info("Sleep because to many requests...")
            time.sleep(0.8)        
        self.execute_time = time.time()
        
        data = urllib2.urlopen(conn);
        result = data.read()
        return result
    
       
    def get_page_by_url(self, host_url):
        if not host_url:
            return host_url
        host_url.replace("#", "&")
        post = host_url[host_url.find("?") + 1:]
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
            LOG.info("Sleep because to many requests...")
            time.sleep(0.8)        
        self.execute_time = time.time()
        
        try:
            data = urllib2.urlopen(conn);
        except Exception, e:
            LOG.error("VK Connection Erorr", e)
            return None
        result = data.read()
        return result
    
    def get_name_by(self, id, result_album):
            for album in result_album:
                id_album = album[0]
                name = album[1]
                if id_album == id:
                    return name
            
            return None   
    
    def to_good_chars(self, line):
        try:
            return htmldecode(line)
        except:
            return unescape(line)
    
    def get_content_len(self, path):
        open = urllib.urlopen(path)
        return open.info().getheaders("Content-Length")[0]
 
                
    
    def find_time_value(self, times_count, r_count):
        for i in times_count:
            if times_count[i] == r_count:
                return i
        return None 
    
    def find_video_by_query(self, query):        
        page = self.get_page(query, "video")
        
        beans = []
        urls = re.findall(ur'showVideoBoxCommon([{}(\\"\a-z:0-9,/);.% _A-Zа-яА-Я+-]*)' , page, re.UNICODE)
        for url in urls:
            res = {}
            for line in url.split(","):
                line = line.replace("\\", '')
                line = line.replace('(', '')
                line = line.replace('{', '')
                line = line.replace('}', '')
                if line and '":' in line:
                    key, value = line.split('":')
                    key = key.replace('"', '')
                    value = value.replace('"', '')
                    value = value.replace('+', ' ')
                    print key, value
                    res[key] = value
                
            host = res["host"]
                
            if "http://" in host:
                if res["no_flv"] == "0":
                    link = host + "u" + res["uid"] + "/video/" + res["vtag"] + ".flv"
                else:
                    link = host + "u" + res["uid"] + "/video/" + res["vtag"] + ".360.mp4"
                    #link = host + "u" + res["uid"] + "/video/" + res["vtag"] + ".flv"
            else:
                link = "http://" + host + "/assets/videos/" + res["vtag"] + res["vkid"] + ".vk.flv"
            
            text = res["md_title"]
            text = urllib.unquote(text)
            text = self.to_good_chars(text)
            beans.append(FModel(text, link)) 
        return beans
    
    "http://v525.vkadre.ru/assets/videos/adda2e950c01-105202975.vk.flv"
    
    def find_tracks_by_query(self, query):
        LOG.info("start search songs", query)
        page = self.get_page(query)
                        
                
        reg_all = "([^<>]*)"
        resultall = re.findall("return operate\(([\w() ,']*)\);", page, re.IGNORECASE)
        result_album = re.findall(ur'<b id=\\"performer([_0-9]*)\\">' + reg_all + "<", page, re.IGNORECASE | re.UNICODE)
        result_track = re.findall(u"<span id=\\\\\"title([_0-9]*)\\\\\">" + reg_all + "<", page, re.IGNORECASE | re.UNICODE)
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
        
        for i in xrange(len(result_time)):    
            id = ids[i]       
            path = urls[i] 
            album = self.get_name_by(id, result_album)
            track = self.get_name_by(id, result_track)
            time = result_time[i] 
            text = album + " - " + track
            vkSong = FModel(text, path).add_artist(album).add_title(track).add_time(time)
            vkSongs.append(vkSong)            
        
        return vkSongs
     
    def find_tracks_by_url(self, url):
        LOG.debug("Search By URL")
        result = self.get_page_by_url(url) 
        try:       
            result = unicode(result)
        except:
            result = result
      
        
        reg_all = "([^{<}]*)"
        result_url = re.findall(ur"http:([\\/.0-9_A-Z]*)", result, re.IGNORECASE)
        result_artist = re.findall(u"q]=" + reg_all + "'", result, re.IGNORECASE | re.UNICODE)
        result_title = re.findall(u"\"title([0-9_]*)\\\\\">" + reg_all + "", result, re.IGNORECASE | re.UNICODE)
         
        result_time = re.findall("duration\\\\\">" + reg_all, result, re.IGNORECASE | re.UNICODE)
        result_lyr = re.findall(ur"showLyrics" + reg_all, result, re.IGNORECASE | re.UNICODE)
        LOG.info("lyr:::", result_lyr)
        songs = []
        j = 0
        for i, artist in enumerate(result_artist):
            path = "http:" + result_url[i].replace("\\/", "/")
            title = self.to_good_chars(result_title[i][1])
            if not title:
                if len(result_lyr) > j:
                    title = result_lyr[j]
                    title = title[title.find(";'>") + 3:]
                    j += 1                
            artist = self.to_good_chars(artist)
            #song = VKSong(path, artist, title, result_time[i]);
            text = artist + " - " + title            
            song = FModel(text, path).add_artist(artist).add_title(title).add_time(result_time[i])
            songs.append(song)        
        LOG.info(len(songs))
        return songs    
    
    def find_one_track(self, query):        
        vkSongs = self.find_tracks_by_query(query)
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
        LOG.info("LOG.info(Song time", r_time)
        LOG.info("LOG.info(Count of congs", r_count)
        
        
        for song in vkSongs:
            if song.time == r_time:        
                return song

        return vkSongs[0]

#vk = VKService()
#list = vk.find_video_by_query("Мадона")
#for i, bean in enumerate(list):
#    print i, bean.path, bean.text
    

#a = "%D0%9C%D0%90%D0%94%D0%9E%D0%9D%D0%9D%D0%90%21%21%21%21%21"
#print urllib.unquote(a)
#print a.encode("ASCII")

