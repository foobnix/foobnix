'''
Created on Mar 11, 2010

@author: ivan
'''
import os

from foobnix.util import LOG



from foobnix.directory.directory_model import DirectoryModel
from foobnix.model.entity import DirectoryBean, PlaylistBean, SongBean, \
    EntityBean
from foobnix.util.confguration import FConfiguration
from foobnix.util.file_utils import isDirectory, getExtenstion
from foobnix.util.mouse_utils import is_double_click
import gtk
class DirectoryCntr():
    
    def __init__(self, gxMain, widget, playlistCntr, radioListCntr):
        self.playlistCntr = playlistCntr
        self.radioListCntr = radioListCntr
        self.model = DirectoryModel(widget)

        widget.connect("button-press-event", self.onMouseClick)
        
        self.filter = gxMain.get_widget("filter-combobox-entry")
        self.filter.connect("key-release-event", self.onFiltering)
        
        self.view_list = gxMain.get_widget("view_list_combobox")
        cell = gtk.CellRendererText()
        self.view_list.pack_start(cell, True)
        self.view_list.add_attribute(cell, 'text', 0)  
        liststore = gtk.ListStore(str)
        self.view_list.set_model(liststore)
        self.view_list.append_text("by artist/album")
        self.view_list.append_text("by radio/stations")
        self.view_list.append_text("by play lists")
        self.view_list.set_active(0)
        
        self.view_list.connect("changed", self.onChangeView)

    def onChangeView(self, *args):
        active_index = self.view_list.get_active()  
        if active_index == 0:
            self.clear()
            self.addAll()
        elif active_index == 1:
            self.clear()
            beans = self.radioListCntr.getState()[0]
            print beans
            for bean in beans:
                self.model.append(None, DirectoryBean(bean.name, bean.path, "normal", True, DirectoryBean.TYPE_MUSIC_URL))
        else:
            pass
    
    
    def onFiltering(self, *args):   
        text = self.filter.get_children()[0].get_text()
        if text : 
            self.model.filterByName(text)
    
    def onMouseClick(self, w, e):
        if is_double_click(e): 
            directoryBean = self.model.getSelectedBean()
            if directoryBean.type == DirectoryBean.TYPE_MUSIC_FILE:
                self.playlistCntr.clear()                                                                           
                self.playlistCntr.setPlaylist([SongBean().init(directoryBean)])
            elif directoryBean.type == DirectoryBean.TYPE_FOLDER:
                songs = self.getAllSongsByPath(directoryBean.path)
                if songs:
                    self.playlistCntr.clear()
                    self.playlistCntr.setPlaylist(songs)
            else:
                self.playlistCntr.setPlaylist([SongBean(type=EntityBean.TYPE_MUSIC_URL).init(directoryBean)])

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
                result.append(SongBean(file_name, full_path))
                
        LOG.debug(result)
        return result 
    
    def addSong(self, song): 
        self.direcotryTreeModel.append(None, [song.name, song.path, "normal", True, self.TYPE_URL])
    
    def addAll(self):
        level = None;
        self.go_recursive(self.musicFolder, level) 
        
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
                sub = self.model.append(level, DirectoryBean(file, full_path, "bold", True, DirectoryBean.TYPE_FOLDER))                    
                self.go_recursive(full_path, sub) 
            else:
                if not isDirectory(full_path):
                    self.model.append(level, DirectoryBean(file, full_path, "normal", True, DirectoryBean.TYPE_MUSIC_FILE))
                    #LOG.debug("file", file)                             

