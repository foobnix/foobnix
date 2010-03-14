'''
Created on Mar 11, 2010

@author: ivan
'''
import os

from foobnix.util import LOG



from foobnix.directory.directory_model import DirectoryModel
from foobnix.model.entity import DirectoryBean, PlaylistBean, SongBean
from foobnix.util.confguration import FConfiguration
from foobnix.util.file_utils import isDirectory, getExtenstion
from foobnix.util.mouse_utils import is_double_click
class DirectoryCntr():
    
    def __init__(self, widget, playlistCntr):
        self.playlistCntr = playlistCntr
        self.model = DirectoryModel(widget)
               
        #self.musicFolder = FConfiguration().mediaLibraryPath
        #os.listdir(self.musicFolder)
        #self.addAll()
        
        widget.connect("button-press-event", self.onMouseClick)
       
    
    def onMouseClick(self,w,e):
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
                
                
    
    def filterByName(self, string):        
        if len(string.strip()) > 0:
            for line in self.direcotryTreeModel:
                name = line[self.POS_NAME].lower()
                string = string.strip().lower()
                
                if name.find(string) >= 0:
                    print "FIND :", name, string
                    line[self.POS_VISIBLE] = True                    
                else:                   
                    line[self.POS_VISIBLE] = False
        else:
            for line in self.direcotryTreeModel:                
                line[self.POS_VISIBLE] = True

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
        self.directory.clear()
        
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

