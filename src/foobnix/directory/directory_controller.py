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
from foobnix.util.file_utils import isDirectory, getExtenstion
import gtk
from foobnix.directory.pref_list_model import PrefListModel
import gettext


gettext.install("foobnix", unicode=True)

class DirectoryCntr():
    
    VIEW_LOCAL_MUSIC = 0
    VIEW_RADIO_STATION = 1
    VIEW_VIRTUAL_LISTS = 2
    VIEW_CHARTS_LISTS = 2
    
    DEFAULT_LIST = "Default list";
    #DEFAULT_LIST_NAME = _("Default list");
    
    
    def __init__(self, gxMain, playlistCntr, radioListCntr, virtualListCntr):
        
        self.playlistCntr = playlistCntr
        self.radioListCntr = radioListCntr
        self.virtualListCntr = virtualListCntr
        
        
        
        widget = gxMain.get_widget("direcotry_treeview")
        self.similar_songs_model = DirectoryModel(widget)
        widget.connect("button-press-event", self.onMouseClick)
        widget.connect("key-release-event", self.onTreeViewDeleteItem)
        
        #widget.connect("drag-begin", self.all)
        #widget.connect("drag-data-get", self.all)
        #widget.connect("drag-data-received", self.all)
        #widget.connect("drag-drop", self.all)
        widget.connect("drag-end", self.on_drag_get)
        #widget.connect("drag-failed", self.all)
        #widget.connect("drag-leave", self.all)
        
        "Pref lists "
        self.prefListMap = {self.DEFAULT_LIST : []}
        self.currentListMap = self.DEFAULT_LIST
        
        
        prefList = gxMain.get_widget("treeview3")
        prefList.connect("button-press-event", self.onPreflListMouseClick)
        prefList.connect("key-release-event", self.onPreflListDeleteItem)
        prefList.connect("cursor-changed", self.onPreflListSelect)
        self.prefModel = PrefListModel(prefList, self.prefListMap)
        
        
        self.mainNoteBook = gxMain.get_widget("main_notebook")
        self.mainNoteBook.set_current_page(1)
        self.leftNoteBook = gxMain.get_widget("left_notebook")
                
        
        self.filter = gxMain.get_widget("filter-entry")
        #self.filter.connect("key-press-event", self.onFiltering)
        self.filter.connect("key-release-event", self.onFiltering)
        
        """
        self.view_list = gxMain.get_widget("view_list_combobox")
        cell = gtk.CellRendererText()
        self.view_list.pack_start(cell, True)
        self.view_list.add_attribute(cell, 'text', 0)  
        liststore = gtk.ListStore(str)
        self.view_list.set_model(liststore)
        self.view_list.append_text(_("by artist/album"))
        self.view_list.append_text(_("by radio/stations"))
        self.view_list.append_text(_("by play lists"))
        self.view_list.set_active(0)
        
        self.view_list.connect("changed", self.onChangeView)
        """
        
        show_local = gxMain.get_widget("show_local_music_button")
        show_local.connect("clicked",self.onChangeView, self.VIEW_LOCAL_MUSIC)
        self.active_view=self.VIEW_LOCAL_MUSIC
                
        show_radio = gxMain.get_widget("show_radio_button")
        show_radio.connect("clicked",self.onChangeView, self.VIEW_RADIO_STATION)
        
        show_play_list = gxMain.get_widget("show_lists_button")
        show_play_list.connect("clicked",self.onChangeView, self.VIEW_VIRTUAL_LISTS)
        
        show_charts_ = gxMain.get_widget("show_charts_button")
        show_charts_.connect("clicked",self.onChangeView, self.VIEW_CHARTS_LISTS)
        
        self.onChangeView
        
        
        self.saved_model = None
        
        
        
    
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
            print "Key not found"
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
            print event.keyval
            print event.hardware_keycode
            if event.hardware_keycode == 119 or event.hardware_keycode == 107:
                if self.prefModel.getSelectedIndex() > 0:
                    del self.prefListMap[unicode(self.prefModel.getSelected())]
                    self.prefModel.removeSelected()
                                        
                    self.clear()                     
                                   
    
    def all(self, *args):
        for arg in args:
            print arg
    
    
    def getModel(self):
        return self.similar_songs_model
    
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
            beans = self.radioListCntr.getState()[0]
            print beans
            for bean in beans:
                self.similar_songs_model.append(None, CommonBean(bean.name, bean.path, "normal", True, CommonBean.TYPE_MUSIC_URL))
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
        self.similar_songs_model.append(None, CommonBean(name="[" + self.currentListMap + "]", path=None, font="bold", is_visible=True, type=CommonBean.TYPE_LABEL, parent=None, index=0))
        
        if not items:
            return None
                
        
        parent = None
        
        i = 1
        for item in items:
            print item
            if item.parent == None:
                parent = self.similar_songs_model.append(None, CommonBean(name=item.name, path=item.path, font="normal", is_visible=True, type=item.type, parent=item.parent, index=i))
            else:
                self.similar_songs_model.append(parent, CommonBean(name=item.name, path=item.path, font="normal", is_visible=True, type=item.type, parent=item.parent, index=i))
            i += 1
       
        
    
    def onTreeViewDeleteItem(self, w, event):
        if self.active_view != self.VIEW_VIRTUAL_LISTS:
            return
        
        print event
        if event.type == gtk.gdk.KEY_RELEASE: #@UndefinedVariable
            #Enter pressed
            print event.keyval
            print event.hardware_keycode
            if event.hardware_keycode == 119 or event.hardware_keycode == 107:
                print "Delete"
                bean = self.similar_songs_model.getSelectedBean()
                print bean.index
                if bean.index > 0:
                    self.virtualListCntr.items = self.prefListMap[self.currentListMap]
                    self.virtualListCntr.remove_with_childrens(bean.index - 1, bean.parent)                
                    self.append_virtual()
            
    
    def onFiltering(self, *args):   
        text = self.filter.get_text()
        print "filtering by text", text
        self.similar_songs_model.filterByName(text)
        
    
    def onMouseClick(self, w, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
            self.populate_playlist()
        if event.button == 3 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
            print "Create new"
            #self.append_virtual([CommonBean(name="New Artist", type=CommonBean.TYPE_FOLDER, parent=None)])
    
    def populate_playlist(self, append=False):
        print "Drug begin"
        directoryBean = self.similar_songs_model.getSelectedBean()
        if not directoryBean:
            return 
        
        print "Select: ", directoryBean.name, directoryBean.type 
        print "Drug type", directoryBean.type
        
        if directoryBean.type in [CommonBean.TYPE_FOLDER, CommonBean.TYPE_GOOGLE_HELP] :
            songs = self.similar_songs_model.getChildSongBySelected()
            print "Select songs", songs
            if not songs:
                return
            if append:                                                                            
                self.playlistCntr.appendPlaylist(songs)
            else:
                self.playlistCntr.setPlaylist(songs)
        elif directoryBean.type == CommonBean.TYPE_LABEL:
            songs = self.similar_songs_model.getAllSongs()
            if append:                                                                            
                self.playlistCntr.appendPlaylist(songs)
            else:
                self.playlistCntr.setPlaylist(songs)
        else:
            if append:                                      
                self.playlistCntr.appendPlaylist([directoryBean])
            else:
                self.playlistCntr.setPlaylist([directoryBean])
        
        #print "PAGE", self.leftNoteBook.get_current_page() 
        print "SET PAGE", self.mainNoteBook.set_current_page(0)
        
            
    
    
    def getALLChildren(self, row, string):        
        for child in row.iterchildren():
            name = child[self.POS_NAME].lower()            
            if name.find(string) >= 0:
                print "FIND SUB :", name, string
                child[self.POS_VISIBLE] = True        
            else:               
                child[self.POS_VISIBLE] = False
        
                    
        
    def updateDirectoryByPath(self, path):
        print "Update path", path
        self.musicFolder = path
        self.similar_songs_model.clear()
        self.addAll()
    
    def clear(self):
        self.similar_songs_model.clear()
        
    def getAllSongsByPath(self, path):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = sorted(list)
        result = []            
        for file_name in list:
            if getExtenstion(file_name) not in FConfiguration().supportTypes:
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
                    self.similar_songs_model.append(None, bean)  
            return True
      """
      
        level = None;
        self.go_recursive(self.musicFolder, level)
        if not  len(self.similar_songs_model.getModel()):
            self.similar_songs_model.append(level, CommonBean(name=_("Music not found in ") + FConfiguration().mediaLibraryPath, path=None, font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER, parent=level))
        else:                
            """
            for i in xrange(len(self.similar_songs_model.getModel())):   
                bean = self.similar_songs_model.getBeenByPosition(i)
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
                print "Can'r get list of dir", e
            
            if not list:
                return False
                 
            for file in list:
                full_path = path + "/" + file
                if isDirectory(full_path):                              
                    if self.isDirectoryWithMusic(full_path):
                        return True                    
                else:
                    if getExtenstion(file) in FConfiguration().supportTypes:
                        return True
                    
        return False            
    
    def go_recursive(self, path, level):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = self.sortedDirsAndFiles(path, list)
                
        for file in list:
            
            full_path = path + "/" + file
            
            if not isDirectory(full_path) and getExtenstion(file) not in FConfiguration().supportTypes:
                continue
      
            
            if self.isDirectoryWithMusic(full_path):
                #LOG.debug("directory", file)                
                sub = self.similar_songs_model.append(level, CommonBean(name=file, path=full_path, font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER, parent=level))                    
                self.go_recursive(full_path, sub) 
            else:
                if not isDirectory(full_path):
                    self.similar_songs_model.append(level, CommonBean(name=file, path=full_path, font="normal", is_visible=True, type=CommonBean.TYPE_MUSIC_FILE, parent=level))
                    #LOG.debug("file", file)                             

