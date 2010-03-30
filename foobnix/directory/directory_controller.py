'''
Created on Mar 11, 2010

@author: ivan
'''
import os

from foobnix.util import LOG



from foobnix.directory.directory_model import DirectoryModel
from foobnix.model.entity import CommonBean
from foobnix.util.confguration import FConfiguration
from foobnix.util.file_utils import isDirectory, getExtenstion
from foobnix.util.mouse_utils import is_double_click
import gtk
from foobnix.directory.virtuallist_controller import VirturalLIstCntr
import copy
from foobnix.directory.pref_list_model import PrefListModel
import thread
class DirectoryCntr():
    
    VIEW_ARTIST_ALBUM = 0
    VIEW_RADIO_STATION = 1
    VIEW_VIRTUAL_LISTS = 2
    
    DEFAULT_LIST = _("Default")
    
    
    def __init__(self, gxMain, playlistCntr, radioListCntr, virtualListCntr):
        
        self.playlistCntr = playlistCntr
        self.radioListCntr = radioListCntr
        self.virtualListCntr = virtualListCntr
        
        
        
        widget = gxMain.get_widget("direcotry_treeview")
        self.model = DirectoryModel(widget)
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
        
        
        
                
        
        self.filter = gxMain.get_widget("filter-combobox-entry")
        self.filter.connect("key-release-event", self.onFiltering)
        
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
        
        self.saved_model = None
        
        
        
    
    def getState(self):
        return self.prefListMap
    
    def setState(self, preflists):
        self.prefListMap = preflists
        self.prefModel.prefListMap = preflists
        for key in self.prefListMap: 
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
        self.currentListMap = self.prefModel.getSelected()
        
        if self.currentListMap in self.prefListMap:
            beans = self.prefListMap[self.currentListMap]
            self.display_virtual(beans) 
        else:
            self.clear()          
            
    
    def onPreflListMouseClick(self, w, event):
        if event.button == 3 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
            print "Create new"
            unknownListName = "Unknown play list"
            if not self.prefModel.isContain(unknownListName):
                self.prefModel.append(unknownListName)           
       
    def onPreflListDeleteItem(self, w, event):
        print event
        if event.type == gtk.gdk.KEY_RELEASE: #@UndefinedVariable
            #Enter pressed
            print event.keyval
            print event.hardware_keycode
            if event.hardware_keycode == 119 or event.hardware_keycode == 107:
                if self.prefModel.getSelectedIndex() > 0:
                    self.prefModel.removeSelected()               
    
    def all(self, *args):
        for arg in args:
            print args
    
    
    def getModel(self):
        return self.model
    
    def on_drag_get(self, *args):    
        self.populate_playlist(append=True)
    
    def set_active_view(self, view_type):
        self.view_list.set_active(view_type)

    def onChangeView(self, *args):
        active_index = self.view_list.get_active()  
        if active_index == self.VIEW_ARTIST_ALBUM:
            self.clear()
            self.addAll()                
                
                
        elif active_index == self.VIEW_RADIO_STATION:
            self.clear()
            beans = self.radioListCntr.getState()[0]
            print beans
            for bean in beans:
                self.model.append(None, CommonBean(bean.name, bean.path, "normal", True, CommonBean.TYPE_MUSIC_URL))
        elif active_index == self.VIEW_VIRTUAL_LISTS:                      
            items = self.getPrefListBeans(self.DEFAULT_LIST)
            self.display_virtual(items)
                        
    def append_virtual(self, beans=None):
        self.appendToPrefListBeans(beans, self.currentListMap)       
        items = self.getPrefListBeans(self.currentListMap)
        self.display_virtual(items)
   
    def display_virtual(self, items):
        self.clear()
        
        "Displya list title"
        self.model.append(None, CommonBean(name="[" + self.currentListMap + "] play list", path=None, font="bold", is_visible=True, type=CommonBean.TYPE_LABEL, parent=None, index=0))
        
        if not items:
            return None
                
        
        parent = None
        
        i = 1
        for item in items:
            print item
            if item.parent == None:
                parent = self.model.append(None, CommonBean(name=item.name, path=item.path, font="normal", is_visible=True, type=item.type, parent=item.parent, index=i))
            else:
                self.model.append(parent, CommonBean(name=item.name, path=item.path, font="normal", is_visible=True, type=item.type, parent=item.parent, index=i))
            i += 1
       
        
    
    def onTreeViewDeleteItem(self, w, event):
        if self.view_list.get_active() != self.VIEW_VIRTUAL_LISTS:
            return
        
        print event
        if event.type == gtk.gdk.KEY_RELEASE: #@UndefinedVariable
            #Enter pressed
            print event.keyval
            print event.hardware_keycode
            if event.hardware_keycode == 119 or event.hardware_keycode == 107:
                print "Delete"
                bean = self.model.getSelectedBean()
                self.virtualListCntr.remove_with_childrens(bean.index, bean.parent)                
                self.append_virtual()
            
    
    def onFiltering(self, *args):   
        text = self.filter.get_children()[0].get_text()
        if text : 
            self.model.filterByName(text)
    
    def onMouseClick(self, w, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
            self.populate_playlist()
        if event.button == 3 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
            print "Create new"
            #self.append_virtual([CommonBean(name="New Artist", type=CommonBean.TYPE_FOLDER, parent=None)])
    
    def populate_playlist(self, append=False):
        print "Drug begin"
        directoryBean = self.model.getSelectedBean()
        if not directoryBean:
            return 
        
        print "Select: ", directoryBean.name, directoryBean.type 
        print "Drug type", directoryBean.type
        
        
        
        if directoryBean.type == CommonBean.TYPE_FOLDER:
            songs = self.model.getChildSongBySelected()
            print "Select songs", songs
            if not songs:
                return
            if append:                                                                            
                self.playlistCntr.appendPlaylist(songs)
            else:
                self.playlistCntr.setPlaylist(songs)
        elif directoryBean.type == CommonBean.TYPE_LABEL:
            songs = self.model.getAllSongs()
            if append:                                                                            
                self.playlistCntr.appendPlaylist(songs)
            else:
                self.playlistCntr.setPlaylist(songs)
        else:
            if append:                                      
                self.playlistCntr.appendPlaylist([directoryBean])
            else:
                self.playlistCntr.setPlaylist([directoryBean])
            
    
    
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
        self.model.clear()
        self.addAll()
    
    def clear(self):
        self.model.clear()
        
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
    
    def addAllThread(self):
        level = None;                
        self.go_recursive(self.musicFolder, level)
    
    def addAll(self):                
        thread.start_new_thread(self.addAllThread(), ())
        
        
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
            list = os.listdir(dir)
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
                sub = self.model.append(level, CommonBean(name=file, path=full_path, font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER))                    
                self.go_recursive(full_path, sub) 
            else:
                if not isDirectory(full_path):
                    self.model.append(level, CommonBean(name=file, path=full_path, font="normal", is_visible=True, type=CommonBean.TYPE_MUSIC_FILE))
                    #LOG.debug("file", file)                             

