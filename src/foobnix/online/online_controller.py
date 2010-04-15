# -*- coding: utf-8 -*-

'''
Created on Mar 16, 2010

@author: ivanf
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
    search_top_tracks, search_top_similar, search_tags_genre
import thread
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.util.confguration import FConfiguration
from foobnix.online.google.search import GoogleSearch, SearchError
import urllib2
import os
import urllib

import threading
from foobnix.online.google.translate import Translator
from foobnix.util import LOG


'''
Created on Mar 11, 2010

@author: ivan
'''

import gtk

from foobnix.playlist.playlist_model import PlaylistModel
from foobnix.model.entity import  CommonBean
from foobnix.util.mouse_utils import is_double_click


class OnlineListCntr():
    
    API_KEY = FConfiguration().API_KEY
    API_SECRET = FConfiguration().API_SECRET
    
    username = FConfiguration().lfm_login
    password_hash = pylast.md5(FConfiguration().lfm_password)    
    
    TOP_SONGS = "TOP_SONG"
    TOP_ALBUMS = "TOP_ALBUMS"
    TOP_SIMILAR = "TOP_SIMILAR"
    TOP_SEARCH = "TOP_SEARCH"
    TOP_TAGS_GENRE = "TOP_TAGS_GENRE"
    
    def make_dirs(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
    
    
    def __init__(self, gxMain, playerCntr, directoryCntr, playerWidgets):
        self.playerCntr = playerCntr
        self.directoryCntr = directoryCntr
        self.playerWidgets = playerWidgets
        
        self.search_text = gxMain.get_widget("search_entry")
        self.search_text.connect("key-press-event", self.on_key_pressed)
        search_button = gxMain.get_widget("search_button")
        search_button.connect("clicked", self.on_search)
        
        
        self.radio_song = gxMain.get_widget("radiobutton_song")        
        self.radio_album = gxMain.get_widget("radiobutton_album")
        self.radio_similar = gxMain.get_widget("radiobutton_similar")
        self.radio_search = gxMain.get_widget("radiobutton_search")
        self.radio_tags_genre = gxMain.get_widget("radiobutton_tags")
        
        self.treeview = gxMain.get_widget("online_treeview")
        
        self.treeview.connect("drag-end", self.on_drag_end)
        
        self.treeview .connect("button-press-event", self.onPlaySong)
        
        self.model = OnlineListModel(self.treeview)
                
        self.entityBeans = []
        self.index = self.model.getSize();
        try:
            self.network = pylast.get_lastfm_network(api_key=self.API_KEY, api_secret=self.API_SECRET, username=self.username, password_hash=self.password_hash)
            #self.scrobler = self.network.get_scrobbler("tst", "1.0")  
        except:
            self.playerWidgets.setStatusText(_("lasf.fm connection error"))
            LOG.error("lasf.fm connection error")
            #return None
        
        self.vk = Vkontakte(FConfiguration().vk_login, FConfiguration().vk_password)
        if not self.vk.isLive():            
            self.playerWidgets.setStatusText(_("Vkontakte connection error"))
            LOG.error("Vkontakte connection error")
            
        
        self.play_attempt = 0
        
        self.playerThreadId = None
        
        pass #end of init

    
    def report_now_playing(self, song):
        if song.getArtist() and song.getTitle():
            print "Reporting about ... ARTIST: " + song.getArtist(), "TITLE: ", song.getTitle()
            #self.scrobler.report_now_playing(song.getArtist(), song.getTitle())
        else:
            print _("Artist and title not correct")
        
    def scrobble(self, artist, title, time_started, source, mode, duration, album="", track_number="", mbid=""):
        self.scrobler.scrobble(artist, title, time_started, source, mode, duration, album, track_number, mbid)
        
    def on_drag_end(self, *ars):
        selected = self.model.getSelectedBean()
        print "SELECTED", selected
        self.directoryCntr.set_active_view(DirectoryCntr.VIEW_VIRTUAL_LISTS)
        if selected.type == CommonBean.TYPE_MUSIC_URL:
            selected.parent = None                            
            self.directoryCntr.append_virtual([selected])
        elif selected.type in [CommonBean.TYPE_FOLDER, CommonBean.TYPE_GOOGLE_HELP]:
            selected.type = CommonBean.TYPE_FOLDER
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
        self.directoryCntr.leftNoteBook.set_current_page(0)
    
    
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
        if self.radio_tags_genre.get_active(): return self.TOP_TAGS_GENRE
        #default is
        return self.TOP_SONGS
    
    def get_search_query(self):
        query = self.search_text.get_text()
        if query and len(query.strip()) > 0:
            print query            
            return query
        #Nothing found
        return None
    
    lock = threading.Lock()

    def on_search(self, *args):
        if self.playerThreadId:
            return None
        
        if not self.vk.isLive():
            LOG.error("VK is not availiable")
            LOG.error("Vkontakte connection error")
            return None
        
        self.lock.acquire()
        self.clear()
        
        query = self.get_search_query()        
        if query:  
            query = self.capitilize_query(u"" + query)
            
            self.append([self.TextBeen("Searching... " + query + " please wait", color="GREEN")])
            if self.get_search_by() == self.TOP_ALBUMS:
                self.playerThreadId = thread.start_new_thread(self.search_top_albums, (query,))
                #thread.start_new_thread(self.search_dots, (query,))                

            elif self.get_search_by() == self.TOP_SONGS:                
                self.playerThreadId = thread.start_new_thread(self.search_top_tracks, (query,))
                #thread.start_new_thread(self.search_dots, (query,))          
            
            elif self.get_search_by() == self.TOP_SIMILAR:
                self.playerThreadId = thread.start_new_thread(self.search_top_similar, (query,))
            
            elif self.get_search_by() == self.TOP_SEARCH:                
                self.playerThreadId = thread.start_new_thread(self.search_vk_engine, (query,))
                #thread.start_new_thread(self.search_dots, (query,))
            elif self.get_search_by() == self.TOP_TAGS_GENRE:
                self.playerThreadId = thread.start_new_thread(self.search_tags_genre, (query,))
                
            
            #self.show_results(query, beans)
        self.lock.release() 
        pass
  
    def capitilize_query(self, line):
        line = line.strip()        
        result = ""
        for l in line.split():
            result += " " + l[0].upper() + l[1:]
        return result
    
    def search_dots(self, query):
        dots = "..."        
        while self.playerThreadId != None:            
            dots += "."
            self.clear()
            self.append([self.SearchingCriteriaBean(query + dots)])
            time.sleep(2)
        
    def search_top_albums(self, query):
        beans = search_top_albums(self.network, query)
        self.show_results(query, beans) 
       
    
    def search_top_tracks(self, query):
        beans = search_top_tracks(self.network, query)        
        self.show_results(query, beans)      
    

    def is_ascii(self, s):
        return all(ord(c) < 128 for c in s)    
    
    def search_tags_genre(self, query):        
        if not self.is_ascii(query):
            translator = Translator()            
            query = translator.translate(query.encode(), lang_from="ru")
            self.append([self.TextBeen("Translated: " + query, color="LIGHT GREEN")])
        
        beans = search_tags_genre(self.network, query)        
        self.show_results(query, beans, False)
    
    def search_top_similar(self, query):
        try:
            beans = search_top_similar(self.network, query)
            self.show_results(query, beans)
        except:
            self.playerThreadId = None
            self.googleHelp(query)
            
            
          
    def search_vk_engine(self, query):
        vkSongs = self.vk.find_song_urls(query)
        beans = self.convertVKstoBeans(vkSongs)
        self.show_results(query, beans)
    
    def show_results(self, query, beans, criteria=True):
    
        self.clear()
        print "Show results...."
        if beans:
            if criteria:                
                self.append([self.SearchCriteriaBeen(query)])
            self.append(beans)
        else:
            self.googleHelp(query)
        self.playerThreadId = None    
        
    
    def googleHelp(self, query):
      
        self.append([self.TextBeen("Not Found, wait for results from google ...")])

        try:
            ask = query.encode('utf-8')
            
            
            gs = GoogleSearch(ask)
            gs.results_per_page = 10
            results = gs.get_results()
            for res in results:
                result = res.title.encode('utf8')   
                time.sleep(0.05)             
                self.append([self.TextBeen(str(result), color="YELLOW", type=CommonBean.TYPE_GOOGLE_HELP)])
        except :
            print "Search failed: %s" 
        
        
        
    def convertVKstoBeans(self, vkSongs):
        beans = []
        for vkSong in vkSongs:
            bean = CommonBean(name=vkSong.getFullDescription(), path=vkSong.path, type=CommonBean.TYPE_MUSIC_URL);
            beans.append(bean)
        return beans
    
    def TextBeen(self, query, color="RED", type=CommonBean.TYPE_FOLDER):
        return CommonBean(name=query, path=None, color=color, type=type)
    
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
                #thread.start_new_thread(self.playBean, (playlistBean,))
                self.playBean(playlistBean)
            elif playlistBean.type == CommonBean.TYPE_GOOGLE_HELP:
                self.search_text.set_text(playlistBean.name)
                
    count = 0
    def playBean(self, playlistBean):            
        if playlistBean.type == CommonBean.TYPE_MUSIC_URL:
            self.setSongResource(playlistBean)
            print "Find path", playlistBean.path 
          
            if not playlistBean.path:
                self.count += 1
                print self.count
                playlistBean.setIconErorr()
                if self.count < 5   :                
                    return self.playBean(self.getNextSong())
                return 
            
            count = 0
            self.playerCntr.set_mode(PlayerController.MODE_ONLINE_LIST)                                  
            self.playerCntr.playSong(playlistBean)
            
            self.index = playlistBean.index
            self.repopulate(self.entityBeans, self.index)

                
    def downloadSong(self, song):
        if not FConfiguration().is_save_online:
            print "Source not saved ...., please set in configuration"
            return None
            
        print "===Dowload song start"
        #time.sleep(5)
        file = self.get_file_store_path(song)
        
        #remotefile = urllib2.urlopen(song.path)
        #f = open(file, 'wb')
        #f.write(remotefile.read())
        #f.close()
        #urllib.file = self.get_file_store_path(song
        if not os.path.exists(file + ".tmp"):
            r = urllib.urlretrieve(song.path, file + ".tmp")
            os.rename(file + ".tmp", file)
            print r        
            print "===Dowload song End ", file
        else:
            print "Exists ..."
        
    def get_file_store_path(self, song):
        dir = FConfiguration().onlineMusicPath
        if song.getArtist():
            dir = dir + "/" + song.getArtist()
        self.make_dirs(dir)
        song = dir + "/" + song.name + ".mp3"
        print "Stored dir: ", song
        return song
    
    def setSongResource(self, playlistBean):
        if not playlistBean.path:
            if playlistBean.type == CommonBean.TYPE_MUSIC_URL:
                
                file = self.get_file_store_path(playlistBean)
                if os.path.isfile(file) and os.path.getsize(file) > 1:
                    print "Find file dowloaded"
                    playlistBean.path = file
                    playlistBean.type = CommonBean.TYPE_MUSIC_FILE
                    return True
                else:
                    print "FILE NOT FOUND IN SYSTEM"
                                    
                
                #Seach by pvleer engine
                #playlistBean.path = find_song_urls(playlistBean.name)[0]
                
                #Seach by vk engine                
                vkSong = self.vk.find_most_relative_song(playlistBean.name)
                #print vkSongs
                if vkSong:
                     
                    print "GET PATH", vkSong.path
                    #playlistBean.name = playlistBean.name + " vk[" + str(vk.album) + " " + str(vk.track) + " " + str(vk.time) + "]"
                    
                    #self.dowloadThread(playlistBean)
                       
                    #self.downloadSong(playlistBean)  
                    
                    playlistBean.path = vkSong.path
                                   
                else:
                    playlistBean.path = None
                
                
    def dowloadThread(self, bean):
        thread.start_new_thread(self.downloadSong, (bean,))                
       
    
    def nextBean(self):
        self.index += 1
        if self.index >= len(self.entityBeans):
            self.index = 0
            
        playlistBean = self.model.getBeenByPosition(self.index)
        return playlistBean
    def prevBean(self):
        self.index -= 1
        if self.index <= 0:
            self.index = len(self.entityBeans)
            
        playlistBean = self.model.getBeenByPosition(self.index)
        return playlistBean
    
        
    def getNextSong(self):
        
        currentSong = self.nextBean() 
        
        if(currentSong.type == CommonBean.TYPE_FOLDER):
            currentSong = self.nextBean()
        
        self.setSongResource(currentSong)
        print "PATH", currentSong.path
                      
        self.repopulate(self.entityBeans, currentSong.index);        
        return currentSong
    
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
