# -*- coding: utf-8 -*-
'''
Created on Sep 29, 2010

@author: ivan
'''
import time
from foobnix.util.fc import FC, get_random_vk
import urllib2
import logging
import urllib
import re
from foobnix.regui.model import FModel
from foobnix.util.text_utils import html_decode
import json
from urllib2 import HTTPError

class VKService:
    
    def __init__(self):
        self.initialize_urllib2()
        self.login()
        
    def initialize_urllib2(self):
        self.cookie_processor = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(self.cookie_processor)
        urllib2.install_opener(self.opener)

    def login(self):
        post = {
                'email' : FC().vk_login,
                'pass' : FC().vk_password,
                'act' : 'login',
                'q' : '1',
                'al_frame' : '1'
        }
        self.get('http://login.vk.com/?act=login', post)
        if (not self.is_connected()):
            logging.error("failed connection to vk")

    def is_connected(self):
        return (str(self.cookie_processor.cookiejar).find('remixsid') > -1)
    
    def check_connection(self):
        if (not self.is_connected()):
            logging.warning("vk is not connected!")
    
    def find_tracks_by_query(self, query):
        if not self.is_connected():
            return []
        logging.info("start search songs"+ query)
        page = self.search(query)
        if not page:
            return []
        vk_audio = VKAudioResultsPage(page)
        return vk_audio.tracks()
        
    def search(self, query, type='audio'):
        return self.get("http://vk.com/gsearch.php?section=" + type + "&q=" + urllib.quote(query) + "&name=1")

    def find_videos_by_query(self, query):
        page = self.search(query, "video")
        if not page:
            return []
        vk_videos = VKVideoResultsPage(page)
        return vk_videos.tracks()
    
    def get(self, url, data=None, headers={}):
        if data:
            data = urllib.urlencode(data)
        time.sleep(1.2)
        try:
            handler= self.opener.open(url, data)
            data = handler.read()
            handler.close()
            return data
        except HTTPError, e:
            logging.error("VK Connection Error:"+ str(e) + "( Searching: "+str(url)+" with data "+str(data)+") ["+FC().vk_login+":"+FC().vk_password+"]")
            if e.code == 400:
                FC().vk_login, FC().vk_password = get_random_vk()
                self.initialize_urllib2()
                self.login()
            return None

    def find_tracks_by_url(self, url):
        logging.debug("Search By URL")
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
        logging.info("lyr:::"+ str(result_lyr))
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
        logging.info(len(songs))
        return songs 
        
    def find_one_track(self, query):        
        vkSongs = self.find_tracks_by_query(query)
        if not vkSongs:
            return None
        #We want the most common song, so we search it using the track duration
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
        logging.info("Song time"+ str(r_time))
        logging.info("Count of songs with this time"+ str(r_count))
        
        for song in vkSongs:
            if song.time == r_time:        
                return song

        return vkSongs[0]

    def find_time_value(self, times_count, r_count):
        for i in times_count:
            if times_count[i] == r_count:
                return i
        return None 

class VKAudioResultsPage:

    def __init__(self, page):
        self.page = page

    def tracks(self):
        tracks = []
        for html in self.page.split('<table><tbody>'):
            if html.find('audioTitle') == -1: continue
            tracks.append(self.generate_track(html))
        return tracks
        
    def generate_track(self, html):
        ids = re.findall("return operate\(([\w() ,']*)\);", html, re.IGNORECASE)[0]
        url = self.track_url(ids)
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

class VKVideoResultsPage:

    def __init__(self, page):
        self.page = page
        
    def tracks(self):
        tracks = []
        for html in self.page.split('<table cellpadding=0 cellspacing=0 border=0>'):
            if html.find('showVideoBoxCommon') == -1: continue
            track = self.generate_track(html)
            if track:
                tracks.append(track)
        return tracks
    
    def generate_track(self, html):
        video = self.get_json(html)
        if video:
            link = self.get_link(video)
            title = self.get_title(html)
            if link and title:
                return FModel(title, link)
        return None
    
    def get_json(self, html):
        json_code = re.findall("(\{.*\})", html)[0]
        json_code = html_decode(json_code)
        try:
            video = json.loads(json_code)
        except:
            return None #if is not valid json 
        if 'host' not in video:
            return None
        return video

    def get_link(self, video):
        if "http://" in video['host']:
            if video["no_flv"] == "0":
                link = video['host'] + "u" + video["uid"] + "/video/" + video["vtag"] + ".flv"
            else:
                quality_list = ("240", "360", "480", "720")
                quality = quality_list[int(video["hd"])]                    
                link = video['host'] + "u" + video["uid"] + "/video/" + video["vtag"] + ".%s.mp4" % quality
        else:
            link = "http://" + video['host'] + "/assets/videos/" + video["vtag"] + video["vkid"] + ".vk.flv"
        logging.debug(link)
        return link

    def get_title(self, html):
        try:
            text = re.findall('<a href="video[^"]*noiphone">(?!</a>)(.*)</a>', html, re.IGNORECASE | re.UNICODE)[0]
            text = unicode(text, 'cp1251')
            text = text.replace('<span class="match">', '').replace('</span>', '')
            return html_decode(text)
        except IndexError:
            return None
