# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2010

@author: ivan
'''
import os

from foobnix.util import LOG



from foobnix.directory.directory_model import DirectoryModel
from foobnix.model.entity import CommonBean
from foobnix.util.configuration import FConfiguration
from foobnix.util.file_utils import isDirectory, get_file_extenstion
import gtk
from foobnix.directory.pref_list_model import PrefListModel
import gettext
from foobnix.util.mouse_utils import  is_double_left_click
from mutagen.mp3 import MP3
from foobnix.util.time_utils import normilize_time
from foobnix.radio.radios import  RadioFolder
from foobnix.cue.cue_reader import CueReader


gettext.install("foobnix", unicode=True)

class DirectoryCntr():
    
    VIEW_LOCAL_MUSIC = 0
    VIEW_RADIO_STATION = 1
    VIEW_VIRTUAL_LISTS = 2
    VIEW_CHARTS_LISTS = 2
    
    DEFAULT_LIST = "Default list";
    #DEFAULT_LIST_NAME = _("Default list");
    
    
    def __init__(self, gxMain, playlistCntr, virtualListCntr):
        
        self.playlistCntr = playlistCntr
        self.virtualListCntr = virtualListCntr
        
        
        
        widget = gxMain.get_widget("direcotry_treeview")
        self.current_list_model = DirectoryModel(widget)
        widget.connect("button-press-event", self.onMouseClick)
        widget.connect("key-release-event", self.onTreeViewDeleteItem)
        
        widget.connect("drag-end", self.on_drag_get)
        
        "Pref lists "
        self.prefListMap = {self.DEFAULT_LIST : []}
        self.currentListMap = self.DEFAULT_LIST
        
        
        prefList = gxMain.get_widget("treeview3")
        prefList.connect("button-press-event", self.onPreflListMouseClick)
        prefList.connect("key-release-event", self.onPreflListDeleteItem)
        prefList.connect("cursor-changed", self.onPreflListSelect)
        self.prefModel = PrefListModel(prefList, self.prefListMap)
        
        
        self.mainNoteBook = gxMain.get_widget("main_notebook")
        self.mainNoteBook.set_current_page(0)
        
        self.leftNoteBook = gxMain.get_widget("left_notebook")
        
        
        self.filter = gxMain.get_widget("filter-entry")
        self.filter.connect("key-release-event", self.onFiltering)
        
        show_local = gxMain.get_widget("show_local_music_button")
        show_local.connect("clicked", self.onChangeView, self.VIEW_LOCAL_MUSIC)
        self.active_view = self.VIEW_LOCAL_MUSIC
                
        show_radio = gxMain.get_widget("show_radio_button")
        show_radio.connect("clicked", self.onChangeView, self.VIEW_RADIO_STATION)
        
        show_play_list = gxMain.get_widget("show_lists_button")
        show_play_list.connect("clicked", self.onChangeView, self.VIEW_VIRTUAL_LISTS)
        
        #show_charts_ = gxMain.get_widget("show_charts_button")
        #show_charts_.connect("clicked", self.onChangeView, self.VIEW_CHARTS_LISTS)
        
        self.onChangeView
        
        
        self.saved_model = None
        
        self.radio_folder = RadioFolder()
        
    
    def getState(self):        
        return self.prefListMap
    
    def setState(self, preflists):
        self.prefListMap = preflists
        self.prefModel.prefListMap = preflists
        for key in self.prefListMap:
            LOG.info("add key to virtual list", unicode(key))             
            self.prefModel.append(key)
            
    
    
    def getPrefListBeans(self, preflist=DEFAULT_LIST):
        
        
        if preflist in self.prefListMap:
            return self.prefListMap[preflist]
        return None
    
    def appendToPrefListBeans(self, beans, preflist=DEFAULT_LIST):
        if not preflist in self.prefListMap:
            LOG.info("Key not found")
            self.prefListMap[preflist] = []
        
        if beans:                    
            for bean in beans:
                self.prefListMap[preflist].append(bean)
    
    def clearPrefList(self, listName):
        if listName in self.prefListMap:
            self.prefListMap[listName] = []
            
    
    def onPreflListSelect(self, *args):
        #self.view_list.set_active(self.VIEW_VIRTUAL_LISTS)        
        self.currentListMap = self.prefModel.getSelected()
        
        if self.currentListMap in self.prefListMap:
            beans = self.prefListMap[self.currentListMap]
            self.display_virtual(beans) 
        else:
            self.clear()          
            
    
    def onPreflListMouseClick(self, w, event):
        if event.button == 3 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
            LOG.debug("Create new paly list")
            unknownListName = _("New play list")
            if not self.prefModel.isContain(unknownListName):
                self.prefModel.append(unknownListName) 
                self.prefListMap[unknownListName] = []          
       
    def onPreflListDeleteItem(self, w, event):
        
        if event.type == gtk.gdk.KEY_RELEASE: #@UndefinedVariable
            #Enter pressed
            LOG.info(event.keyval)
            LOG.info(event.hardware_keycode)
            if event.hardware_keycode == 119 or event.hardware_keycode == 107:
                if self.prefModel.getSelectedIndex() > 0:
                    del self.prefListMap[unicode(self.prefModel.getSelected())]
                    self.prefModel.removeSelected()
                                        
                    self.clear()                     
                                   
    
    def all(self, *args):
        for arg in args:
            LOG.info(arg)
    
    
    def getModel(self):
        return self.current_list_model
    
    def on_drag_get(self, *args):    
        self.populate_playlist(append=True)
    
    "TODO: set active button state"
    def set_active_view(self, view_type):
        #self.view_list.set_active(view_type)
        pass

    def onChangeView(self, w, active_view):
        self.active_view = active_view
        self.leftNoteBook.set_current_page(0)
        
        if active_view == self.VIEW_LOCAL_MUSIC:
            self.clear()
            self.addAll()                
                
                
        elif active_view == self.VIEW_RADIO_STATION:
            self.clear()
            files = self.radio_folder.get_radio_FPLs()
            for fpl in files:
                parent = self.current_list_model.append(None, CommonBean(name=fpl.name, path=None, font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER))
                for radio, urls in fpl.urls_dict.iteritems():
                    self.current_list_model.append(parent, CommonBean(name=radio, path=urls[0], font="normal", is_visible=True, type=CommonBean.TYPE_RADIO_URL, parent=fpl.name))
                    
                
                
        elif active_view == self.VIEW_VIRTUAL_LISTS:                      
            items = self.getPrefListBeans(self.DEFAULT_LIST)
            self.display_virtual(items)
            
        
                        
    def append_virtual(self, beans=None):
        LOG.debug("Current virtual list", self.currentListMap)
        if not self.currentListMap:
            self.currentListMap = self.DEFAULT_LIST 
            
        self.appendToPrefListBeans(beans, self.currentListMap)       
        items = self.getPrefListBeans(self.currentListMap)
        self.display_virtual(items)
   
    def display_virtual(self, items):
        self.clear()
        
        "Displya list title"
        self.current_list_model.append(None, CommonBean(name="[" + self.currentListMap + "]", path=None, font="bold", is_visible=True, type=CommonBean.TYPE_LABEL, parent=None, index=0))
        
        if not items:
            return None
                
        
        parent = None
        
        i = 1
        for item in items:
            LOG.info(item)
            if item.parent == None:
                parent = self.current_list_model.append(None, CommonBean(name=item.name, path=item.path, font="normal", is_visible=True, type=item.type, parent=item.parent, index=i))
            else:
                self.current_list_model.append(parent, CommonBean(name=item.name, path=item.path, font="normal", is_visible=True, type=item.type, parent=item.parent, index=i))
            i += 1
       
        
    
    def onTreeViewDeleteItem(self, w, event):
        if self.active_view != self.VIEW_VIRTUAL_LISTS:
            return
        
        LOG.info(event)
        if event.type == gtk.gdk.KEY_RELEASE: #@UndefinedVariable
            #Enter pressed
            LOG.info(event.keyval)
            LOG.info(event.hardware_keycode)
            if event.hardware_keycode == 119 or event.hardware_keycode == 107:
                LOG.info("Delete")
                bean = self.current_list_model.get_selected_bean()
                LOG.info(bean.index)
                if bean.index > 0:
                    self.virtualListCntr.items = self.prefListMap[self.currentListMap]
                    self.virtualListCntr.remove_with_childrens(bean.index - 1, bean.parent)                
                    self.append_virtual()
            
    
    def onFiltering(self, *args):   
        text = self.filter.get_text()
        LOG.info("filtering by text", text)
        self.current_list_model.filterByName(text)
        
    
    def onMouseClick(self, w, event):
        if is_double_left_click(event):
            self.populate_playlist()
    
    def update_songs_time(self, songs):
        for song in songs:
            if song.path and song.path.endswith("3") and not song.time:
                try:
                    audio = MP3(song.path)
                    song.time = normilize_time(audio.info.length)
                except:
                    pass
                
                #audio = EasyID3(song.path)
                #song.title = str(audio["title"][0])                 
                #song.artist =str( audio["artist"][0])
                #song.album = str(audio["album"][0])
                #song.tracknumber= str(audio["tracknumber"][0])
                #LOG.info(song.title, song.artist, song.album
                
                
    
    
    def populate_playlist(self, append=False):
        LOG.info("Drug begin")
        directoryBean = self.current_list_model.get_selected_bean()
        if not directoryBean:
            return 
        
        LOG.info("Select: ", directoryBean.name, directoryBean.type) 
        LOG.info("Drug type", directoryBean.type)
        
        if directoryBean.type in [CommonBean.TYPE_FOLDER, CommonBean.TYPE_GOOGLE_HELP] :
            songs = self.current_list_model.getChildSongBySelected()
            
            self.update_songs_time(songs)
            LOG.info("Select songs", songs)
            if not songs:
                return
            if append:                  
                self.playlistCntr.append(songs)
            else:
                self.playlistCntr.append_notebook_page(directoryBean.name)
                self.playlistCntr.append_and_play(songs)
                
        elif directoryBean.type == CommonBean.TYPE_LABEL:
            songs = self.current_list_model.getAllSongs()
            
            if append:                                                                            
                self.playlistCntr.append(songs)
            else:
                self.playlistCntr.append_notebook_page(directoryBean.name)
                self.playlistCntr.append_and_play(songs)
        else:
            if append:                                      
                self.playlistCntr.append([directoryBean])
            else:
                self.playlistCntr.append_notebook_page(directoryBean.name)
                self.playlistCntr.append_and_play([directoryBean])
        
        #LOG.info("PAGE", self.leftNoteBook.get_current_page() 
        #LOG.info("SET PAGE", self.mainNoteBook.set_current_page(0)
        
            
    
    
    def getALLChildren(self, row, string):        
        for child in row.iterchildren():
            name = child[self.POS_NAME].lower()            
            if name.find(string) >= 0:
                LOG.info("FIND SUB :", name, string)
                child[self.POS_VISIBLE] = True        
            else:               
                child[self.POS_VISIBLE] = False
        
                    
        
    def updateDirectoryByPath(self, path):
        LOG.info("Update path", path)
        self.musicFolder = path
        self.current_list_model.clear()
        self.addAll()
    
    def clear(self):
        self.current_list_model.clear()
        
    def getAllSongsByPath(self, path):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = sorted(list)
        result = []            
        for file_name in list:
            if get_file_extenstion(file_name) not in FConfiguration().supportTypes:
                    continue
                        
            full_path = path + "/" + file_name
            
            if not isDirectory(full_path):                                
                bean = CommonBean(name=file_name, path=full_path, type=CommonBean.TYPE_MUSIC_FILE)
                result.append(bean)
                
        LOG.debug(result)
        return result 
    
    cachModel = []
    
    def addAllThread(self):
        """
        if self.cachModel:            
            for bean in self.cachModel:                    
                    self.current_list_model.append(None, bean)  
            return True
      """
      
        level = None;
        self.go_recursive(self.musicFolder, level)
        if not  len(self.current_list_model.getModel()):
            self.current_list_model.append(level, CommonBean(name=_("Music not found in ") + FConfiguration().mediaLibraryPath, path=None, font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER, parent=level))
        else:                
            """
            for i in xrange(len(self.current_list_model.getModel())):   
                bean = self.current_list_model.getBeenByPosition(i)
                self.cachModel.append(bean)
           """ 
        
        
        
    
    def addAll(self):                
        #thread.start_new_thread(self.addAllThread, ())
        self.addAllThread()
        
    def sortedDirsAndFiles(self, path, list):        
        files = []
        directories = []
        #First add dirs
        for file in list:            
            full_path = path + "/" + file
            if isDirectory(full_path):
                directories.append(file)
            else:    
                files.append(file)
                
        return sorted(directories) + sorted(files)
    
    def isDirectoryWithMusic(self, path):
        if isDirectory(path):
            dir = os.path.abspath(path)
            list = None
            try:
                list = os.listdir(dir)
            except OSError, e:
                LOG.info("Can'r get list of dir", e)
            
            if not list:
                return False
                 
            for file in list:
                full_path = path + "/" + file
                if isDirectory(full_path):                              
                    if self.isDirectoryWithMusic(full_path):
                        return True                    
                else:
                    if get_file_extenstion(file) in FConfiguration().supportTypes:
                        return True
                    
        return False            
    
    def go_recursive(self, path, level):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = self.sortedDirsAndFiles(path, list)
                
        for file in list:
            
            full_path = path + "/" + file
            
            if not isDirectory(full_path) and get_file_extenstion(file) not in FConfiguration().supportTypes:
                continue
      
            """check cue is valid"""
            if full_path.endswith(".cue") and not CueReader(full_path).is_cue_valid():
                continue
            
            if self.isDirectoryWithMusic(full_path):
                #LOG.debug("directory", file)                
                sub = self.current_list_model.append(level, CommonBean(name=file, path=full_path, font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER, parent=level))                    
                self.go_recursive(full_path, sub) 
            else:
                if not isDirectory(full_path):
                    self.current_list_model.append(level, CommonBean(name=file, path=full_path, font="normal", is_visible=True, type=CommonBean.TYPE_MUSIC_FILE, parent=level))
                    #LOG.debug("file", file)                             

