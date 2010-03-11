'''
Created on Mar 11, 2010

@author: ivan
'''

import gtk
from foobnix.song import Song
from foobnix.mvc.playlist.playlist_m import PlaylistModel
from foobnix.mvc.model.entity import PlaylistBean, SongBean

class PlaylistCntr():
    def __init__(self, widget, playerCntr):
        self.model = PlaylistModel(widget)
        self.playerCntr = playerCntr
        self.model.append(PlaylistBean(gtk.STOCK_GO_FORWARD, "1", "Description", "path", "#F2F2F2"))
        self.model.append(PlaylistBean(None, "12", "Description", "path", "#FFFFE5"))
     
    def append(self, entityBeans):        
        for entityBean in entityBeans:
            self.model.append(PlaylistBean().init(entityBean))
        if entityBeans:
            self.playerCntr.playSong(entityBeans[0])
    
    def clear(self):
        self.model.clear()                  