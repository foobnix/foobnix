'''
Created on Feb 26, 2010

@author: ivan
'''
import gtk
from song import Song
import gobject

class PlayList:    
    def __init__(self, playListWidget):
        
        self.playListModel = gtk.ListStore(str, str,str)
        
        self.tvcolumn = gtk.TreeViewColumn('Icon')
        self.tvcolumn1 = gtk.TreeViewColumn('PlayList')
        
        playListWidget.append_column(self.tvcolumn)
        playListWidget.append_column(self.tvcolumn1)
        
        self.cellpb = gtk.CellRendererPixbuf()
        self.cell = gtk.CellRendererText()
        
        self.tvcolumn.pack_start(self.cellpb, False)
        self.tvcolumn1.pack_start(self.cell, True)
        
        self.tvcolumn.set_attributes(self.cellpb, stock_id=1)
        self.tvcolumn1.set_attributes(self.cell, text=0)
                           
                        
        playListWidget.set_model(self.playListModel)
        
        

    def get_icon(self, name):
        theme = gtk.icon_theme_get_default()
        return theme.load_icon(name, 48, 0)     
    
    def clear(self):
        self.playListModel.clear()
        
    def addSong(self, Song):
        self.clear()
        self.playListModel.append([Song.name,gtk.STOCK_GO_FORWARD, Song.path])       
    
    def addSongs(self, songs, active = 0):
        self.clear()
        for i in range(len(songs)):
            song = songs[i]
            if i == active:
                self.playListModel.append([song.name,gtk.STOCK_GO_FORWARD, song.path])
            else:
                self.playListModel.append([song.name,None, song.path])   
   

     
