'''
Created on Feb 26, 2010

@author: ivan
'''
import gtk
import os
import LOG
from file_utils import isDirectory, getExtenstion
from confguration import FConfiguration
from song import Song


class DirectoryList:
    def __init__(self, root_directory, directoryListWidget):
        self.root_directory = root_directory        
        
        column = gtk.TreeViewColumn("Title", gtk.CellRendererText(), text=0)
        column.set_resizable(True)
        directoryListWidget.append_column(column)
        self.direcotryTreeModel = gtk.TreeStore(str, str)                
        directoryListWidget.set_model(self.direcotryTreeModel)

        try:
            os.listdir(root_directory)
            self.addAll()
        except OSError:
            print "No directory", root_directory
            
        
    def updateDirctoryByPath(self, root_direcotry):
        self.root_directory = root_direcotry
        self.direcotryTreeModel.clear()
        self.addAll()
        
    def getAllSongsByDirectory(self, path):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = sorted(list)
        result = []            
        for file_name in list:
            if getExtenstion(file_name) not in FConfiguration().supportTypes:
                    continue
                        
            full_path = path + "/" + file_name
            
            if not isDirectory(full_path):                                
                result.append(Song(file_name, full_path))
                
        LOG.debug(result)
        return result        
    
    def addAll(self):
        level = None;
        self.go_recursive(self.root_directory, level) 
        
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
                LOG.debug("directory", file)
                sub = self.direcotryTreeModel.append(level, [file, full_path])                    
                self.go_recursive(full_path, sub) 
            else:
                if not isDirectory(full_path):
                    self.direcotryTreeModel.append(level, [file, full_path])
                    LOG.debug("file", file)                             
