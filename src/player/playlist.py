'''
Created on Feb 26, 2010

@author: ivan
'''
import gtk
from song import Song

class PlayList:    
    def __init__(self, playListWidget):
        column = gtk.TreeViewColumn("PlayList", gtk.CellRendererText(), text=0)
        column.set_resizable(True)
        
        playListWidget.append_column(column)        
        
        self.playListModel = gtk.TreeStore(str, str)                
        playListWidget.set_model(self.playListModel)
    
    def clear(self):
        self.playListModel.clear()
        
    def addSong(self, Song):
        self.clear()
        self.playListModel.append(None, [Song.name, Song.path])       
    
    def addList(self):
        pass