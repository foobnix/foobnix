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
from string import replace
from foobnix.regui.model import FModel
import logging
import sys
from foobnix.util.text_utils import html_decode

class VKService:
    
    def __init__(self):
        self.initialize_urllib2()
        self.login()
        
    def initialize_urllib2(self):
        self.cookie_processor = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener( self.cookie_processor )
        urllib2.install_opener( self.opener )

    def login(self):
        post = {
                'email' : FC().vk_login,
                'pass' : FC().vk_password,
                'act' : 'login',
                'q' : '1',
                'al_frame' : '1'
        }
        self.get('http://login.vk.com/?act=login', post)
    
    def find_tracks_by_query(self, query):
        LOG.info("start search songs", query)
        page = self.search(query)
        return self.find_tracks_in_page(page)
        
    def search(self, query, type='audio'):
        return self.get("http://vk.com/gsearch.php?section="+type+"&q="+urllib.quote(query)+"&name=1")
    
    def find_tracks_in_page(self, page):
        vkpage = VKResultsPage(page)
        return vkpage.audio_tracks()
    
    def get(self, url, data=None, headers={}):
        if data:
            data = urllib.urlencode(data)
        
        time.sleep(0.8)
        try:
            handler = self.opener.open(url, data)
            data = handler.read()
            handler.close()
            return data
        except Exception, e:
            LOG.error("VK Connection Error", e)
            return None
#
# METHODS TO REFACTOR
#

    def find_video_by_query(self, query):        
        page = self.search(query, "video")
        
        uniq = []
        beans = []
        
        page = page.replace("&quot;", '"')
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
                    res[key] = value
            LOG.debug(res)
            if "host" not in res:
                continue;
            host = res["host"]
                
            if "http://" in host:
                if res["no_flv"] == "0":
                    link = host + "u" + res["uid"] + "/video/" + res["vtag"] + ".flv"
                else:                    
                    quality_list = ("240", "360", "480", "720")
                    quality = quality_list[int(res["hd"])]                    
                    link = host + "u" + res["uid"] + "/video/" + res["vtag"] + ".%s.mp4" % quality
                    #link = host + "u" + res["uid"] + "/video/" + res["vtag"] + ".flv"
            else:
                link = "http://" + host + "/assets/videos/" + res["vtag"] + res["vkid"] + ".vk.flv"
            
            LOG.debug(link)
            
            text = res["md_title"]
            text = urllib.unquote(text)
            text = html_decode(text)
            if text not in uniq:
                uniq.append(text)
                beans.append(FModel(text, link)) 
        return beans
    
    "http://v525.vkadre.ru/assets/videos/adda2e950c01-105202975.vk.flv"
    
     
    def find_tracks_by_url(self, url):
        LOG.debug("Search By URL")
        result = self.get(url) 
        try:       
            result = unicode(result)
        except:
            result = result
        
        reg_all = "([^{<}]*)"
        result_url = re.findall(ur"http:([\\/.0-9_A-Z]*)", result, re.IGNORECASE)
        result_artist = re.findall(u"q]=" + reg_all + "'", result, re.IGNORECASE | re.UNICODE)
        result_title = re.findall('"title([0-9_]*)">' + reg_all + '<', result, re.IGNORECASE | re.UNICODE)
         
        result_time = re.findall('duration">' + reg_all, result, re.IGNORECASE | re.UNICODE)
        result_lyr = re.findall(ur"showLyrics" + reg_all, result, re.IGNORECASE | re.UNICODE)
        LOG.info("lyr:::", result_lyr)
        songs = []
        j = 0
        for i, artist in enumerate(result_artist):
            path = "http:" + result_url[i].replace("\\/", "/")
            title = html_decode(result_title[i][1])
            if not title:
                if len(result_lyr) > j:
                    title = result_lyr[j]
                    title = title[title.find(";'>") + 3:]
                    j += 1                
            artist = html_decode(artist)
            #song = VKSong(path, artist, title, result_time[i]);
            if "\">" in title:
                title = title[title.find("\">") + 2:]
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

    def find_time_value(self, times_count, r_count):
        for i in times_count:
            if times_count[i] == r_count:
                return i
        return None 

class VKResultsPage:

    def __init__(self, page):
        self.page = page

    def audio_tracks(self):
        tracks = []
        for html in self.page.split('<table><tbody>'):
            if html.find('audioTitle') == -1: continue
            tracks.append(self.generate_track(html))
        return tracks
        
    def generate_track(self, html):
        ids = re.findall("return operate\(([\w() ,']*)\);", html, re.IGNORECASE)[0]
        url = self.track_url(ids)
        reg_all = "([^<>]*)"
        artist = self.field('<b id="performer[_0-9]*">', html)
        title = self.field('<span id="title[_0-9]*">', html)
        duration = self.field('<div class="duration">', html)
        text = artist + " - " + title
        return FModel(text, url).add_artist(artist).add_title(title).add_time(duration)
    
    def track_url(self, parameters):
        id, id_server, id_folder, id_file, trash = parameters.replace("'", "").split(',')
        return "http://cs" + id_server + ".vkontakte.ru/u" + id_folder + "/audio/" + id_file + ".mp3"

    def field(self, regexp_before, html):
        reg_all = "([^<>]*)"
        try:
            text = re.findall(regexp_before + reg_all + '<', html, re.IGNORECASE | re.UNICODE)[0]
            text = unicode(text, 'cp1251')
            return html_decode(text)
        except IndexError:
            return ""


