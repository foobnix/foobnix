# -*- coding: utf-8 -*-
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong
'''
Created on Mar 16, 2010

@author: ivanf
'''
import os
import thread
import time
import urllib
import gtk

from gobject import GObject #@UnresolvedImport

from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.model.entity import CommonBean
from foobnix.online.google.search import GoogleSearch
from foobnix.online.information_controller import InformationController
from foobnix.online.online_model import OnlineListModel
from foobnix.online.search_panel import SearchPanel
from foobnix.online.vk import Vkontakte
from foobnix.player.player_controller import PlayerController
from foobnix.util import LOG
from foobnix.util.configuration import FConfiguration
from foobnix.util.mouse_utils import is_double_click



#from foobnix.online.google.translate import translate

#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

try:
    vkontakte = Vkontakte(FConfiguration().vk_login, FConfiguration().vk_password)
except:
    vkontakte = None
    LOG.error("Vkontakte connection error")

class OnlineListCntr(GObject):
    
    def __init__(self, gxMain, playerCntr, directoryCntr):
        self.playerCntr = playerCntr
        self.directoryCntr = directoryCntr

        self.search_panel = SearchPanel(gxMain)
        
        self.count = 0
        self.info = InformationController(gxMain, self.playerCntr, self.directoryCntr)
        
        self.online_notebook = gxMain.get_widget("notebook1")
    
    def create_notebook_tab(self):
        treeview = gtk.TreeView()
        model = OnlineListModel(treeview)
        self.current_list_model = model
        
        treeview.connect("drag-end", self.on_drag_end)
        treeview.connect("button-press-event", self.onPlaySong, model)

        treeview.show()
        
        window =gtk.ScrolledWindow()
        window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        window.add_with_viewport(treeview)
        window.show()
        return  window    
        
    def append_notebook_page(self, name):
        print "append new tab"
        label = gtk.Label(name)
        
        label.set_angle(90)         
        self.online_notebook.prepend_page(self.create_notebook_tab(), label)
        self.online_notebook.set_current_page(0)
         

#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def on_drag_end(self, *ars):
        selected = self.current_list_model.getSelectedBean()
        print "SELECTED", selected
        self.directoryCntr.set_active_view(DirectoryCntr.VIEW_VIRTUAL_LISTS)
        if selected.type == CommonBean.TYPE_MUSIC_URL:
            selected.parent = None
            self.directoryCntr.append_virtual([selected])
        elif selected.type in [CommonBean.TYPE_FOLDER, CommonBean.TYPE_GOOGLE_HELP]:
            selected.type = CommonBean.TYPE_FOLDER
            results = []
            for i in xrange(self.current_list_model.getSize()):
                searchBean = self.current_list_model.getBeenByPosition(i)
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

#TODO: This file is under heavy refactoring, don't touch anything you think is wrong
    

    def show_results(self, sender, query, beans, criteria=True):
        self.append_notebook_page(query)
        
        print "Show results...."
        if beans:
            if criteria:
                self.append([self.SearchCriteriaBeen(query)])
            self.append(beans)
        else:
            self.googleHelp(query)


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
            self.current_list_model.append(bean)
            
        self.repopulate(-1)

    def onPlaySong(self, w, e, similar_songs_model):        
        self.current_list_model = similar_songs_model
        self.index = similar_songs_model.getSelectedBean().index
        if is_double_click(e):
            playlistBean = similar_songs_model.getSelectedBean()
            print "play", playlistBean
            print "type", playlistBean.type
            if playlistBean.type == CommonBean.TYPE_MUSIC_URL:
                #thread.start_new_thread(self.playBean, (playlistBean,))
                self.playBean(playlistBean)
            elif playlistBean.type == CommonBean.TYPE_GOOGLE_HELP:
                self.search_panel.search_text.set_text(playlistBean.name)
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
            self.repopulate(self.index)


    def downloadSong(self, song):
        if not FConfiguration().is_save_online:
            print "Source not saved ...., please set in configuration"
            return None

        print "===Dowload song start"
        #time.sleep(5)
        file = self.get_file_store_path(song)
        
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
        if self.index >= self.current_list_model.getSize():
            self.index = 0

        playlistBean = self.current_list_model.getBeenByPosition(self.index)
        return playlistBean
    
    def prevBean(self):
        list = self.current_list_model.get_all_beans()
        self.index -= 1
        if self.index <= 0:
            self.index = self.current_list_model.getSize()

        playlistBean = self.current_list_model.getBeenByPosition(self.index)
        return playlistBean

#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def getNextSong(self):

        currentSong = self.nextBean()

        if(currentSong.type == CommonBean.TYPE_FOLDER):
            currentSong = self.nextBean()

        self.setSongResource(currentSong)
        print "PATH", currentSong.path
        
        self.repopulate(currentSong.index);
        return currentSong

    def getPrevSong(self):
        playlistBean = self.prevBean()

        if(playlistBean.type == CommonBean.TYPE_FOLDER):
            self.getPrevSong()

        self.setSongResource(playlistBean)

        self.repopulate(playlistBean.index);
        return playlistBean


    def setPlaylist(self, entityBeans):
        self.entityBeans = entityBeans
        index = 0
        if entityBeans:
            self.playerCntr.playSong(entityBeans[index])
            self.repopulate(index);
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def repopulate(self, index):
        list = self.current_list_model.get_all_beans()
        self.current_list_model.clear()
        for i in xrange(len(list)):
            songBean = list[i]

            if not songBean.color:
                songBean.color = self.getBackgroundColour(i)

            songBean.name = songBean.getPlayListDescription()
            songBean.index = i

            if i == index:
                songBean.setIconPlaying()
                self.current_list_model.append(songBean)
            else:
                songBean.setIconNone()
                self.current_list_model.append(songBean)

    def getBackgroundColour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"

    def make_dirs(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
