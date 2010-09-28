#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''

from foobnix.model.entity import CommonBean
from foobnix.thirdparty import pylast
from foobnix.thirdparty.pylast import WSError
from foobnix.util import LOG
from foobnix.online.google.translate import translate
from foobnix.util.fc import FC
from foobnix.helpers.dialog_entry import show_login_password_error_dialog
from foobnix.regui.model import FModel

API_KEY = FC().API_KEY
API_SECRET = FC().API_SECRET        

class LastFmService():
    def __init__(self):
        self.network = None
        self.scrobler = None
        self.preferences_window = None
        
        #thread.start_new_thread(self.init_thread, ())
        
         
    
    def connect(self):
        if self.network and self.scrobler:
            return True            
        return self.init_thread()
    
    def init_thread(self):
        username = FC().lfm_login
        password_hash = pylast.md5(FC().lfm_password)

        try:
            self.network = pylast.get_lastfm_network(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
            if FC().proxy_enable and FC().proxy_url:
                proxy_rul = FC().proxy_url
                index = proxy_rul.find(":")
                proxy = proxy_rul[:index]
                port = proxy_rul[index + 1:]                
                self.network.enable_proxy(proxy, port)
                LOG.info("Enable proxy for last fm", proxy, port)
                
        
            """scrobler"""
            scrobler_network = pylast.get_lastfm_network(username=username, password_hash=password_hash)
            self.scrobler = scrobler_network.get_scrobbler("fbx", "1.0")
        except:
            LOG.error("Invalid last fm login or password or network problems", username, FC().lfm_password)
            val = show_login_password_error_dialog(_("Last.fm connection error"), _("Verify user and password"), username, FC().lfm_password)
            if val:
                FC().lfm_login = val[0]
                FC().lfm_password = val[1]
            return False
            
        return True
    def get_network(self):
        return self.network
    
    def get_scrobler(self):
        return self.scrobler
    
    def connected(self):
        return self.network is not None
    
    def search_top_albums(self, aritst_name):
        self.connect()  
        artist = self.network.get_artist(aritst_name)
        if not artist:
            return None
        try:
            albums = artist.get_top_albums()
        except WSError:
            LOG.info("No artist with that name")
            return None
        
        beans = []
        for album in albums:
            try:            
                album_txt = album.item
            except AttributeError:
                album_txt = album['item']
            
            name = album_txt.get_name()
            bean = FModel(name).add_album(name)
            beans.append(bean)
        return beans
    
    
    def search_top_tags(self, tag):
        self.connect()
        if not tag:
            LOG.warn("search_top_tags TAG is empty")
            return []
        tag = translate(tag, src="ru", to="en")
        print tag
        beans = [] 
        tags = self.network.search_for_tag(tag)
        print tags
        for tag in tags.get_next_page():       
                tag_name = tag.get_name()
                bean = FModel(tag_name).add_genre(tag_name)
                beans.append(bean)        
        return beans
    
    def search_top_tracks(self, artist_name): 
        self.connect()  
        artist = self.network.get_artist(artist_name)
        if not artist:
            return []
        try:
            tracks = artist.get_top_tracks()
        except WSError:
            LOG.info("No artist with that name")
            return []
        
        beans = []    
            
        for track in tracks:
            
            try:            
                track_item = track.item
            except AttributeError:
                track_item = track['item']
            
            #LOG.info(track_item.get_duration())
            
            #bean = CommonBean(name=str(track_item), path="", type=CommonBean.TYPE_MUSIC_URL, parent=query);
            artist = track_item.get_artist().get_name()
            title = track_item.get_title()
            text = artist + " - " + title 
            bean = FModel(text).add_artist(artist).add_title(title)
            #norm_duration = track_item.get_duration() / 1000
            #LOG.info(track_item.get_duration(), norm_duration
            #bean.time = normilize_time(norm_duration)
            beans.append(bean)
            
        return beans
    
    def search_top_similar_artist(self, artist_name, count=45):
        self.connect()
        if not artist_name:
            LOG.warn("search_top_similar_artist, Artist name is empty")
            return []
        
        artist = self.network.get_artist(artist_name)
        if not artist:
            return []
        
        artists = artist.get_similar(count)
        beans = []   
        for artist in artists:
            try:            
                artist_txt = artist.item
            except AttributeError:
                artist_txt = artist['item']
            
            artist_name = artist_txt.get_name()            
            bean = FModel(artist_name).add_artist(artist_name)
            
            beans.append(bean)
        return beans
    
    def search_top_similar_tracks(self, artist, title):
        self.connect()
        
        if not artist or not title:
            LOG.warn("search_top_similar_tags artist or title is empty")
            return []
        
        track = self.network.get_track(artist, title)
        
        similars = track.get_similar()
        beans = []
        for tsong in similars:
            try:            
                tsong_item = tsong.item
            except AttributeError:
                tsong_item = tsong['item']
            
            artist = tsong_item.get_artist().get_name()
            title  =  tsong_item.get_title()
            model = FModel(artist + " - " + title).add_artist(artist).add_title(title)
            beans.append(model)
        
        return beans
   
    def search_top_similar_tags(self, artist, title):
        self.connect()
        
        if not artist or not title:
            LOG.warn("search_top_similar_tags artist or title is empty")
            return []
        
        track = self.network.get_track(artist, title)
               
        tags = track.get_top_tags()
        beans = []
        for tag in tags:
            try:            
                tag_item = tag.item
            except AttributeError:
                tag_item = tag['item']
            
            tag_name = tag_item.get_name()
            model = FModel(tag_name).add_genre(tag_name)
            beans.append(model)        
        return beans 
    
    def get_album_name(self, artist, title):
        self.connect()
        album = self.get_album(artist, title);
        if album:
            return album.get_name()
    
    def get_album_year(self, artist, title):
        self.connect()
        album = self.get_album(artist, title);
        if album:
            return album.get_release_year()
    
    def get_album_image_url(self, artist, title, size=pylast.COVER_LARGE):
        self.connect()
        if not artist or not title:
            LOG.warn("get_album_image_url no artist or title",artist, title)
            return None
        self.connect()
        track = self.network.get_track(artist, title)
        album = track.get_album()
        if not album:
            return None
        return album.get_cover_image(size)      
    
    def get_track(self, artist, title):
        self.connect()
        if not artist or not title:
            LOG.warn("get_album_image_url no artist or title",artist, title)
            return None
        self.connect()
        return self.network.get_track(artist, title)
    
    def get_album(self, artist, title):
        self.connect()
        track = self.get_track(artist, title)
        if track:
            album = track.get_album();
            return album