# -*- coding: utf-8 -*-
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong
'''
Created on Mar 16, 2010

@author: ivanf
'''
from foobnix.online import pylast
import time
from foobnix.online.online_model import OnlineListModel
from foobnix.player.player_controller import PlayerController
from foobnix.online.vk import Vkontakte
from foobnix.online.search_controller import search_top_albums, \
    search_top_tracks, search_top_similar, search_tags_genre
import thread
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.util.configuration import FConfiguration
from foobnix.online.google.search import GoogleSearch
import os
import urllib

import threading
from foobnix.util import LOG
#from foobnix.online.google.translate import translate



import gtk

from foobnix.model.entity import  CommonBean
from foobnix.util.mouse_utils import is_double_click
from foobnix.online.information_controller import InfortaionController


API_KEY = FConfiguration().API_KEY
API_SECRET = FConfiguration().API_SECRET

username = FConfiguration().lfm_login
password_hash = pylast.md5(FConfiguration().lfm_password)
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

try:
    lastfm = pylast.get_lastfm_network(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
except:
    lastfm = None
    LOG.error("lasf.fm connection error")

try:
    vkontakte = Vkontakte(FConfiguration().vk_login, FConfiguration().vk_password)
except:
    vkontakte = None
    LOG.error("Vkontakte connection error")
    

def is_ascii(s):    # TODO: search for python function doing this
    return all(ord(c) < 128 for c in s)

def convertVKstoBeans(vkSongs):
    beans = []
    for vkSong in vkSongs:
        bean = CommonBean(name=vkSong.getFullDescription(), path=vkSong.path, type=CommonBean.TYPE_MUSIC_URL);
        beans.append(bean)
    return beans


def search_artist_top_tracks(query, on_success, on_fail=None):
    def _perform_search():
        try:
            beans = search_top_tracks(lastfm, query)
            on_success(query, beans)
        except:
            if on_fail:
                on_fail(query)
    return thread.start_new_thread(_perform_search, ())

def search_artist_top_albums(query, on_success, on_fail=None):
    def _perform_search():
        try:
            beans = search_top_albums(lastfm, query)
            on_success(query, beans)
        except:
            if on_fail:
                on_fail(query)

    return thread.start_new_thread(_perform_search, ())

def search_artist_similar_artists(query, on_success, on_fail=None):
    def _perform_search():
        try:
            beans = search_top_similar(lastfm, query)
            on_success(query, beans)
        except:
            if on_fail:
                on_fail(query)

    return thread.start_new_thread(_perform_search, ())

def search_tracks_by_name(query, on_success, on_fail=None):
    def _perform_search():
        try:
            vkSongs = vkontakte.find_song_urls(query)
            beans = convertVKstoBeans(vkSongs)
            on_success(query, beans)
        except:
            if on_fail:
                on_fail(query)

    return thread.start_new_thread(_perform_search, ())

def search_tracks_by_tags(query, on_success, on_fail=None):
    def _perform_search():
        try:
#            if not is_ascii(query):
#                query = translate(query, src="ru", to="en")
#                self.append([self.TextBeen("Translated: " + query, color="LIGHT GREEN")])
            beans = search_tags_genre(lastfm, query)
            on_success(query, beans)
        except:
            if on_fail:
                on_fail(query)

    return thread.start_new_thread(_perform_search, ())


def spermophile_search(query):
    return None
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

class OnlineListCntr():

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

        self.searchType = search_artist_top_tracks
        self.create_search_mode_buttons(gxMain)

        self.treeview = gxMain.get_widget("online_treeview")
        self.treeview.connect("drag-end", self.on_drag_end)
        self.treeview .connect("button-press-event", self.onPlaySong)

        self.similar_songs_model = OnlineListModel(self.treeview)

        self.entityBeans = []
        self.index = self.similar_songs_model.getSize();
        
        if not lastfm:
            self.playerWidgets.setStatusText(_("lasf.fm connection error"))

        if not vkontakte or not vkontakte.isLive():
            self.playerWidgets.setStatusText(_("Vkontakte connection error"))


        self.play_attempt = 0
        self.count = 0

        self.playerThreadId = None

        self.info = InfortaionController(gxMain, lastfm, self.playerCntr, self.directoryCntr)

        pass #end of init
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def create_search_mode_buttons(self, gxMain):
        mode_to_button_map = {search_artist_top_tracks: 'top_songs_togglebutton',
                              search_artist_top_albums: 'top_albums_togglebutton',
                              search_artist_similar_artists: 'top_similar_togglebutton',
                              search_tracks_by_name: 'all_search_togglebutton',
                              search_tracks_by_tags: 'tags_togglebutton',
                              spermophile_search: 'tracks_togglebutton' }
        self.search_mode_buttons = {}
        for mode, name in mode_to_button_map.items():
            button = gxMain.get_widget(name)
            button.connect('toggled', self.on_search_mode_selected, mode)
            self.search_mode_buttons[mode] = button


    def on_search_mode_selected(self, button, selected_mode=None):
        if selected_mode==None:
            return
        #button.set_active(True)
        #TODO kostul' to set button in toggled state by double click, set_active do not draw it enable.
        #errors in console, how to fix it?
        button.clicked()
        
        for mode, button in self.search_mode_buttons.items():
            if mode != selected_mode:
                button.set_active(False)

        self.searchType = selected_mode
        LOG.info("Selected Search type", selected_mode)




    def report_now_playing(self, song):
        if song.getArtist() and song.getTitle():
            print "Reporting about ... ARTIST: " + song.getArtist(), "TITLE: ", song.getTitle()
            #self.scrobler.report_now_playing(song.getArtist(), song.getTitle())
        else:
            print _("Artist and title not correct")
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def scrobble(self, artist, title, time_started, source, mode, duration, album="", track_number="", mbid=""):
        self.scrobler.scrobble(artist, title, time_started, source, mode, duration, album, track_number, mbid)

    def on_drag_end(self, *ars):
        selected = self.similar_songs_model.getSelectedBean()
        print "SELECTED", selected
        self.directoryCntr.set_active_view(DirectoryCntr.VIEW_VIRTUAL_LISTS)
        if selected.type == CommonBean.TYPE_MUSIC_URL:
            selected.parent = None
            self.directoryCntr.append_virtual([selected])
        elif selected.type in [CommonBean.TYPE_FOLDER, CommonBean.TYPE_GOOGLE_HELP]:
            selected.type = CommonBean.TYPE_FOLDER
            results = []
            for i in xrange(self.similar_songs_model.getSize()):
                searchBean = self.similar_songs_model.getBeenByPosition(i)
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

    def get_search_query(self):
        query = self.search_text.get_text()
        if query and len(query.strip()) > 0:
            print query
            return query
        #Nothing found
        return None

    lock = threading.Lock()

#TODO: This file is under heavy refactoring, don't touch anything you think is wrong
    def on_search(self, *args):
        if self.playerThreadId:
            return None

        if not vkontakte or not vkontakte.isLive():
            LOG.error("VK is not availiable")
            LOG.error("Vkontakte connection error")
            return None

        self.lock.acquire()
        self.clear()

        query = self.get_search_query()
        if query:
            query = self.capitilize_query(u"" + query)

            self.append([self.TextBeen("Searching... " + query + " please wait", color="GREEN")])
            if self.searchType == search_artist_top_albums:
                self.playerThreadId = search_artist_top_albums(query, self.show_results)

            elif self.searchType == search_artist_top_tracks:
                self.playerThreadId = search_artist_top_tracks(query, self.show_results)

            elif self.searchType == search_artist_similar_artists:
                self.playerThreadId = search_artist_similar_artists(query, self.show_results, self.googleHelp)

            elif self.searchType == search_tracks_by_name:
                self.playerThreadId = search_tracks_by_name(query, self.show_results)

            elif self.searchType == search_tracks_by_tags:
                self.playerThreadId = search_tracks_by_tags(query, self.show_results)


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

#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def search_vk_engine(self, query):
        vkSongs = vkontakte.find_song_urls(query)
        beans = convertVKstoBeans(vkSongs)
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


#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

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
        self.similar_songs_model.clear()

    def onPlaySong(self, w, e):
        if is_double_click(e):
            playlistBean = self.similar_songs_model.getSelectedBean()
            print "play", playlistBean
            print "type", playlistBean.type
            if playlistBean.type == CommonBean.TYPE_MUSIC_URL:
                #thread.start_new_thread(self.playBean, (playlistBean,))
                self.playBean(playlistBean)
            elif playlistBean.type == CommonBean.TYPE_GOOGLE_HELP:
                self.search_text.set_text(playlistBean.name)
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def playBean(self, playlistBean):
        if playlistBean.type == CommonBean.TYPE_MUSIC_URL:
            self.setSongResource(playlistBean)

            LOG.info("Song source path", playlistBean.path)

            if not playlistBean.path:
                self.count += 1
                print self.count
                playlistBean.setIconErorr()
                if self.count < 5   :
                    return self.playBean(self.getNextSong())
                return

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
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def setSongResource(self, playlistBean, update_song_info=True):
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

                #Seach by vk engine
                vkSong = vkontakte.find_most_relative_song(playlistBean.name)
                if vkSong:
                    LOG.info("Find song on VK", vkSong, vkSong.path)
                    playlistBean.path = vkSong.path
                else:
                    playlistBean.path = None

        if update_song_info:
            """retrive images and other info"""
            self.info.show_song_info(playlistBean)

    def dowloadThread(self, bean):
        thread.start_new_thread(self.downloadSong, (bean,))


    def nextBean(self):
        self.index += 1
        if self.index >= len(self.entityBeans):
            self.index = 0

        playlistBean = self.similar_songs_model.getBeenByPosition(self.index)
        return playlistBean
    def prevBean(self):
        self.index -= 1
        if self.index <= 0:
            self.index = len(self.entityBeans)

        playlistBean = self.similar_songs_model.getBeenByPosition(self.index)
        return playlistBean

#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

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
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def repopulate(self, entityBeans, index):
        self.similar_songs_model.clear()
        for i in range(len(entityBeans)):
            songBean = entityBeans[i]

            if not songBean.color:
                songBean.color = self.getBackgroundColour(i)

            songBean.name = songBean.getPlayListDescription()
            songBean.index = i

            if i == index:
                songBean.setIconPlaying()
                self.similar_songs_model.append(songBean)
            else:
                songBean.setIconNone()
                self.similar_songs_model.append(songBean)

    def getBackgroundColour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"
