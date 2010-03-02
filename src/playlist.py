'''
Created on Feb 26, 2010

@author: ivan
'''
import gtk
from file_utils import getSongPosition
from confguration import FConfiguration

class PlayList:    
    def __init__(self, playListWidget):
        
        self.playListModel = gtk.ListStore(str, str, str, str)
        
        iconColumn = gtk.TreeViewColumn('Icon', gtk.CellRendererPixbuf(), stock_id=0)
        numbetColumn = gtk.TreeViewColumn('N', gtk.CellRendererText(), text=1)
        descriptionColumn = gtk.TreeViewColumn('PlayList', gtk.CellRendererText(), text=2)
                
        playListWidget.append_column(iconColumn)
        playListWidget.append_column(numbetColumn)
        playListWidget.append_column(descriptionColumn)
        
        playListWidget.set_model(self.playListModel)
        
        self.songs = None;

    def get_icon(self, name):
        theme = gtk.icon_theme_get_default()
        return theme.load_icon(name, 48, 0)     
    
    def clear(self):
        self.playListModel.clear()
    
    def setCursorToSong(self, song):
        active_pos = getSongPosition(song, self.songs)                             
        self.setSongs(self.songs, active_pos)
        print "active", song
    
    def setSongs(self, songs, active=0):
        self.clear()
        self.songs = songs;
        FConfiguration().savedPlayList = songs
        FConfiguration().savedSongIndex = active
        
        
        for i in range(len(songs)):
            song = songs[i]
            if i == active:
                self.playListModel.append([gtk.STOCK_GO_FORWARD, song.tracknumber, song.getShorDescription(), song.path])
            else:
                self.playListModel.append([None, song.tracknumber, song.getShorDescription(), song.path])   
