'''
Created on Feb 26, 2010

@author: ivan
'''
import gtk
from file_utils import getSongPosition

class PlayList:
    """ Define positions in the model"""
    POS_ICON = 0
    POS_TRACK_NUMBER = 1
    POS_DESCRIPTIOPN = 2
    POS_PATH = 3
    POS_COLOR = 4
    
    def __init__(self, playListWidget):
        
        self.playListModel = gtk.ListStore(str, str, str, str, str)
        
        cellpb = gtk.CellRendererPixbuf()
        cellpb.set_property('cell-background', 'yellow')
        iconColumn = gtk.TreeViewColumn('Icon', cellpb, stock_id=0, cell_background=4)
        numbetColumn = gtk.TreeViewColumn('N', gtk.CellRendererText(), text=1, background=4)
        descriptionColumn = gtk.TreeViewColumn('PlayList', gtk.CellRendererText(), text=2, background=4)
                
        playListWidget.append_column(iconColumn)
        playListWidget.append_column(numbetColumn)
        playListWidget.append_column(descriptionColumn)
        
        playListWidget.set_model(self.playListModel)
        
        self.songs = None;

    def get_icon(self, name):
        theme = gtk.icon_theme_get_default()
        return theme.load_icon(name, 48, 0)     
    
    def clear(self):
        self.songs = []
        self.playListModel.clear()
    
    def setCursorToSong(self, song):
        active_pos = getSongPosition(song, self.songs)                             
        self.setSongs(self.songs, active_pos)
        print "active", song
    
    def getAllSongs(self):
        return self.songs
    
    def removeSong(self, song):
        
        if self.songs:
            for i in range(len(self.songs)):
                tempSong = self.songs[i]
                if song.path == tempSong.path:
                    break
            self.songs.remove(tempSong)
            
            
    def addSong(self, song):
        if self.songs:
            self.songs.append(song)
        else:
            self.songs = [song]
        
        self.setSongs(self.songs)
    
    def addSongs(self, songs):        
        
        for i in range(len(songs)):
            song = songs[i]
            self.songs.append(song)
            color = self.getBackgroundColour(i)
            self.playListModel.append([None, song.tracknumber, song.getShorDescription(), song.path, color])

    def setSongs(self, songs, active=0):
        self.clear()
        self.songs = songs;
        
        for i in range(len(songs)):
            song = songs[i]
            color = self.getBackgroundColour(i)
            if i == active:                
                self.playListModel.append([gtk.STOCK_GO_FORWARD, song.tracknumber, song.getShorDescription(), song.path, color])
            else:
                self.playListModel.append([None, song.tracknumber, song.getShorDescription(), song.path, color])
                   
    def getBackgroundColour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"
        
                
