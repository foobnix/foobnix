# -*- coding: utf-8 -*-

'''
Created on Mar 16, 2010

@author: ivan
'''
from foobnix.radio.radio_model import RadioListModel
from foobnix.util.plsparser import getStationPath, getPlsName
from foobnix.online import pylast
import time
from foobnix.online.online_model import OnlineListModel
from foobnix.online.rupleer import find_song_urls
'''
Created on Mar 11, 2010

@author: ivan
'''

import gtk

from foobnix.playlist.playlist_model import PlaylistModel
from foobnix.model.entity import PlaylistBean, URLBeen, EntityBean
from foobnix.util.mouse_utils import is_double_click


class OnlineListCntr():
    
    API_KEY = "cd461af0871de8509abee1e982cae29e"
    API_SECRET = "0d25b8eedef9bf50108646b14d504463"
    
    username = "foobnix"
    password_hash = pylast.md5("foobnix")    
    
    TOP_SONGS = "TOP_SONG"
    TOP_ALBUMS = "TOP_ALBUMS"
    TOP_SIMILAR = "TOP_SIMILAR"
    
    def __init__(self, gxMain, playerCntr):
        self.playerCntr = playerCntr
        
        self.search_text = gxMain.get_widget("search_entry")
        self.search_text.connect("key-press-event", self.on_key_pressed)
        search_button = gxMain.get_widget("search_button")
        search_button.connect("clicked", self.on_search)
        
        
        self.radio_song = gxMain.get_widget("radiobutton_song")        
        self.radio_album = gxMain.get_widget("radiobutton_album")
        self.radio_similar = gxMain.get_widget("radiobutton_similar")
        
        self.treeview = gxMain.get_widget("online_treeview")
        
        self.treeview .connect("button-press-event", self.onPlaySong)
        
        self.model = OnlineListModel(self.treeview)
                
        self.entityBeans = []
        self.index = self.model.getSize();
        
        self.network = pylast.get_lastfm_network(api_key=self.API_KEY, api_secret=self.API_SECRET, username=self.username, password_hash=self.password_hash)
        
        self.last_search_query = None
        
        pass #end of init
    
    
    def on_key_pressed(self, w, event):
        if event.type == gtk.gdk.KEY_PRESS: #@UndefinedVariable
            #Enter pressed
            print "keyval", event.keyval, "keycode", event.hardware_keycode
            if event.hardware_keycode == 36:                
                self.on_search()
        
    
    def get_search_by(self):
        if self.radio_song.get_active(): return self.TOP_SONGS
        if self.radio_album.get_active(): return self.TOP_ALBUMS
        if self.radio_similar.get_active(): return self.TOP_SIMILAR
        #default is
        return self.TOP_SONGS
    
    def get_search_query(self):
        query = self.search_text.get_text()
        if query and len(query.strip()) > 0:
            print query            
            return query
        #Nothing found
        return None
    
    def on_search(self, *args):
        self.clear()
        self.entityBeans = []
        query = self.get_search_query()        
        if query and query != self.last_search_query:    
            self.last_search_query = query
            unicode(query, "utf-8")
            artist = self.network.get_artist(query)
            print "Artist: ", artist            
            print "BIO: ", artist.get_bio_summary()
            
            albums = artist.get_top_albums()
            
            print "Albums: ", albums  
            
            for album in albums:    
                album_txt = album['item']
                tracks = album_txt.get_tracks()
                bean = PlaylistBean(name="===[" + album_txt.get_title() + "]===", path="", type=EntityBean.TYPE_FOLDER);
                self.append(bean)
                
                
                
                
                for track in tracks:
                    bean = PlaylistBean(name=track, path="", type=EntityBean.TYPE_MUSIC_URL);
                    self.append(bean)
                    
        pass
    
    def append(self, bean):
        self.entityBeans.append(bean)
        self.repopulate(self.entityBeans, 0)
        

    def clear(self):
        self.model.clear()
        
    def onPlaySong(self, w, e):
        if is_double_click(e):            
            playlistBean = self.model.getSelectedBean()
            print "play", playlistBean
            print "type", playlistBean.type            
            if playlistBean.type == EntityBean.TYPE_MUSIC_URL:
                playlistBean.path = find_song_urls(playlistBean.name)[0]
                print "Find path", playlistBean.path                                           
                self.playerCntr.playSong(playlistBean)
                
                self.index = playlistBean.index
                self.repopulate(self.entityBeans, self.index)
                
            
    def getNextSong(self):
        self.index += 1
        if self.index >= len(self.entityBeans):
            self.index = 0
            
        playlistBean = self.model.getBeenByPosition(self.index)           
        self.repopulate(self.entityBeans, playlistBean.index);        
        return playlistBean
    
    def getPrevSong(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.entityBeans) - 1
            
        playlistBean = self.model.getBeenByPosition(self.index)           
        self.repopulate(self.entityBeans, playlistBean.index);        
        return playlistBean
            
     
    def setPlaylist(self, entityBeans):
        self.entityBeans = entityBeans    
        index = 0
        if entityBeans:
            self.playerCntr.playSong(entityBeans[index])
            self.repopulate(entityBeans, index);
        
    def repopulate(self, entityBeans, index):
        self.model.clear()        
        for i in range(len(entityBeans)):
            songBean = entityBeans[i]            
            color = self.getBackgroundColour(i)
            if i == index:                
                self.model.append(PlaylistBean(gtk.STOCK_GO_FORWARD, songBean.tracknumber, songBean.getPlayListDescription(), songBean.path, color, i, songBean.type))
            else:
                if songBean.type == EntityBean.TYPE_FOLDER:
                    self.model.append(PlaylistBean(None, songBean.tracknumber, songBean.getPlayListDescription(), songBean.path, "green", i, songBean.type))
                else:
                    self.model.append(PlaylistBean(None, songBean.tracknumber, songBean.getPlayListDescription(), songBean.path, color, i, songBean.type))
            
            
                
                
                   
    def getBackgroundColour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"
