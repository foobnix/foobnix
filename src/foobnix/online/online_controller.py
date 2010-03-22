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
from foobnix.player.player_controller import PlayerController
from foobnix.online.vk import Vkontakte
from foobnix.online.search_controller import search_top_albums, \
    search_top_tracks, search_top_similar
import thread
from foobnix.directory.directory_controller import DirectoryCntr

'''
Created on Mar 11, 2010

@author: ivan
'''

import gtk

from foobnix.playlist.playlist_model import PlaylistModel
from foobnix.model.entity import  CommonBean
from foobnix.util.mouse_utils import is_double_click


class OnlineListCntr():
    
    API_KEY = "cd461af0871de8509abee1e982cae29e"
    API_SECRET = "0d25b8eedef9bf50108646b14d504463"
    
    username = "foobnix"
    password_hash = pylast.md5("foobnix")    
    
    TOP_SONGS = "TOP_SONG"
    TOP_ALBUMS = "TOP_ALBUMS"
    TOP_SIMILAR = "TOP_SIMILAR"
    TOP_SEARCH = "TOP_SEARCH"
    
    def __init__(self, gxMain, playerCntr, directoryCntr):
        self.playerCntr = playerCntr
        self.directoryCntr = directoryCntr
        
        self.search_text = gxMain.get_widget("search_entry")
        self.search_text.connect("key-press-event", self.on_key_pressed)
        search_button = gxMain.get_widget("search_button")
        search_button.connect("clicked", self.on_search)
        
        
        self.radio_song = gxMain.get_widget("radiobutton_song")        
        self.radio_album = gxMain.get_widget("radiobutton_album")
        self.radio_similar = gxMain.get_widget("radiobutton_similar")
        self.radio_search = gxMain.get_widget("radiobutton_search")
        
        self.treeview = gxMain.get_widget("online_treeview")
        
        self.treeview.connect("drag-end", self.on_drag_end)
        
        self.treeview .connect("button-press-event", self.onPlaySong)
        
        self.model = OnlineListModel(self.treeview)
                
        self.entityBeans = []
        self.index = self.model.getSize();
        
        self.network = pylast.get_lastfm_network(api_key=self.API_KEY, api_secret=self.API_SECRET, username=self.username, password_hash=self.password_hash)
        
        
        
        self.vk = Vkontakte('qax@bigmir.net', 'foobnix')
        
        pass #end of init

    
    def on_drag_end(self, *ars):
        selected = self.model.getSelectedBean()
        print "SELECTED", selected
        self.directoryCntr.set_active_view(DirectoryCntr.VIEW_VIRTUAL_LISTS)
        if selected.type == CommonBean.TYPE_MUSIC_URL:
            selected.parent = None                            
            self.directoryCntr.append_virtual([selected])
        elif selected.type == CommonBean.TYPE_FOLDER:
            results = []       
            for i in xrange(self.model.getSize()):            
                searchBean = self.model.getBeenByPosition(i)
                #print "Search", searchBean 
                if str(searchBean.name) == str(selected.name):
                    searchBean.parent = None
                    results.append(searchBean)
                    
                elif str(searchBean.parent) == str(selected.name):
                    results.append(searchBean)
                else:
                    print str(searchBean.parent) + " != " + str(selected.name) 
                    
            self.directoryCntr.append_virtual(results)
        print "drug"
    
    
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
        if self.radio_search.get_active(): return self.TOP_SEARCH
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
      
        query = self.get_search_query()        
        if query:  
            
            if self.get_search_by() == self.TOP_ALBUMS:
                self.playerThreadId = thread.start_new_thread(self.search_top_albums, (query,))
                thread.start_new_thread(self.search_dots, (query,))                

            elif self.get_search_by() == self.TOP_SONGS:                
                self.playerThreadId = thread.start_new_thread(self.search_top_tracks, (query,))
                thread.start_new_thread(self.search_dots, (query,))          
            
            elif self.get_search_by() == self.TOP_SIMILAR:
                self.playerThreadId = thread.start_new_thread(self.search_top_similar, (query,))
                thread.start_new_thread(self.search_dots, (query,))          
            
            else:
                self.playerThreadId = thread.start_new_thread(self.search_vk_engine, (query,))
                thread.start_new_thread(self.search_dots, (query,))          
            
            #self.show_results(query, beans) 
            
        pass
    
    
    def search_dots(self, query):
        dots = "..."        
        while self.playerThreadId != None:            
            dots += "."
            self.clear()
            self.append([self.SearchingCriteriaBean(query + dots)])
            time.sleep(1)
        
    def search_top_albums(self, query):
        beans = search_top_albums(self.network, query)
        self.show_results(query, beans) 
       
    
    def search_top_tracks(self, query):
        beans = search_top_tracks(self.network, query)        
        self.show_results(query, beans)      
    
    def search_top_similar(self, query):
        beans = search_top_similar(self.network, query)
        self.show_results(query, beans)  
    def search_vk_engine(self, query):
        vkSongs = self.vk.find_song_urls(query)
        beans = self.convertVKstoBeans(vkSongs)
        self.show_results(query, beans)
    
    def show_results(self, query, beans):
        self.playerThreadId = None
        self.clear()
        
        if beans:                
            self.append([self.SearchCriteriaBeen(query)])
            self.append(beans)
        else:
            self.append([self.NotFoundBeen()])
    
    def convertVKstoBeans(self, vkSongs):
        beans = []
        for vkSong in vkSongs:
            bean = CommonBean(name=vkSong.getFullDescription(), path=vkSong.path, type=CommonBean.TYPE_MUSIC_URL);
            beans.append(bean)
        return beans
    
    def NotFoundBeen(self):
        return CommonBean(name="Not found ", path=None, color="RED", type=CommonBean.TYPE_FOLDER)
    
    def SearchCriteriaBeen(self, name):
        return CommonBean(name=name, path=None, color="#4DCC33", type=CommonBean.TYPE_FOLDER)
    
    def SearchingCriteriaBean(self, name):
        return CommonBean(name="Searching: " + name, path=None, color="GREEN", type=CommonBean.TYPE_FOLDER)
    
    def append(self, beans):  
        for bean in beans:                  
            self.entityBeans.append(bean)
        self.repopulate(self.entityBeans, -1)
        

    def clear(self):
        self.entityBeans = []
        self.model.clear()
        
    def onPlaySong(self, w, e):
        if is_double_click(e):            
            playlistBean = self.model.getSelectedBean()
            print "play", playlistBean
            print "type", playlistBean.type            
            if playlistBean.type == CommonBean.TYPE_MUSIC_URL:
                
                self.setSongResource(playlistBean)

                print "Find path", playlistBean.path   
                
                self.playerCntr.set_mode(PlayerController.MODE_ONLINE_LIST)                                  
                self.playerCntr.playSong(playlistBean)
                
                self.index = playlistBean.index
                self.repopulate(self.entityBeans, self.index)
    
    def setSongResource(self, playlistBean):
        if not playlistBean.path:
            if playlistBean.type == CommonBean.TYPE_MUSIC_URL:
                #Seach by pvleer engine
                #playlistBean.path = find_song_urls(playlistBean.name)[0]
                
                #Seach by vk engine                
                vkSong = self.vk.find_most_relative_song(playlistBean.name)
                #print vkSongs
                if vkSong:
                     
                    print "GET PATH", vkSong.path
                    #playlistBean.name = playlistBean.name + " vk[" + str(vk.album) + " " + str(vk.track) + " " + str(vk.time) + "]"
                    
                    playlistBean.path = vkSong.path                    
                else:
                    playlistBean.path = None
                
                
                
       
    
    def nextBean(self):
        self.index += 1
        if self.index >= len(self.entityBeans):
            self.index = 0
            
        playlistBean = self.model.getBeenByPosition(self.index)
        return playlistBean
    def prevBean(self):
        self.index += 1
        if self.index >= len(self.entityBeans):
            self.index = 0
            
        playlistBean = self.model.getBeenByPosition(self.index)
        return playlistBean
    
    def getNextSong(self):
        playlistBean = self.nextBean() 
        
        if(playlistBean.type == CommonBean.TYPE_FOLDER):
            playlistBean = self.nextBean()
        
        self.setSongResource(playlistBean)
        print "PATH", playlistBean.path
                      
        self.repopulate(self.entityBeans, playlistBean.index);        
        return playlistBean
    
    def getPrevSong(self):
        playlistBean = self.prevBean()
        
        if(playlistBean.type == CommonBean.TYPE_FOLDER):
            self.getPrevSong()
               
        self.setSongResource(playlistBean)       
                                   
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
            
            if not songBean.color:            
                songBean.color = self.getBackgroundColour(i)
            
            songBean.name = songBean.getPlayListDescription()
            songBean.index = i
            
            if i == index:
                songBean.setIconPlaying()               
                self.model.append(songBean)
            else:
                songBean.setIconNone()  
                self.model.append(songBean)
                   
    def getBackgroundColour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"
