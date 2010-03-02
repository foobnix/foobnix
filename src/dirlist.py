'''
Created on Feb 26, 2010

@author: ivan
'''
import gtk
import os
import LOG
from file_utils import isDirectory, getExtenstion
from confguration import FoobNixConf

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
    
    def addAll(self):
        level = None;
        self.go_recursive(self.root_directory, level) 
    
    def getSongsInCatalog(self, catalogPath):        
        return []       
              
    def go_recursive(self, path, level):
            
        dir = os.path.abspath(path)
        list = os.listdir(dir)
                
        for file in list:
            
            full_path = path + "/" + file
            
            if not isDirectory(full_path) and getExtenstion(file) not in FoobNixConf().supportTypes:
                continue
                    
            sub = self.direcotryTreeModel.append(level, [file, full_path])              
            
            if isDirectory(full_path):
                LOG.debug("directory", file)                    
                self.go_recursive(full_path, sub) 
            else:
                LOG.debug("file", file)                             