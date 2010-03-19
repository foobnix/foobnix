'''
Created on Mar 11, 2010

@author: ivan
'''

import gtk

from foobnix.playlist.playlist_model import PlaylistModel
from foobnix.model.entity import PlaylistBean, EntityBean
from foobnix.util.mouse_utils import is_double_click
from foobnix.player.player_controller import PlayerController


class PlaylistCntr():
    def __init__(self, widget, playerCntr):
        self.model = PlaylistModel(widget)
        self.playerCntr = playerCntr
        widget.connect("button-press-event", self.onPlaySong)
        
        self.entityBeans = []
        self.index = 0;
    
    def getState(self):
        return [self.entityBeans, self.index]
        
    def setState(self, state):
        self.entityBeans = state[0]
        self.index = state[1]
        if self.entityBeans:
            self.repopulate(self.entityBeans, self.index);
           #self.playerCntr.playSong(self.entityBeans[self.index])
              
        
    
    def clear(self):
        self.model.clear()
        
    def onPlaySong(self, w, e):
        if is_double_click(e):
            playlistBean = self.model.getSelectedBean()           
            self.repopulate(self.entityBeans, playlistBean.index);
            self.index = playlistBean.index
            self.playerCntr.set_mode(PlayerController.MODE_PLAY_LIST)
            playlistBean.type = EntityBean.TYPE_MUSIC_FILE
            self.playerCntr.playSong(playlistBean)
            
    def getNextSong(self):
        self.index += 1
        if self.index >= len(self.entityBeans):
            self.index = 0
            
        playlistBean = self.model.getBeenByPosition(self.index)           
        self.repopulate(self.entityBeans, playlistBean.index);        
        return playlistBean
    
    def getPrevSong(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.entityBeans) - 1
            
        playlistBean = self.model.getBeenByPosition(self.index)           
        self.repopulate(self.entityBeans, playlistBean.index);        
        return playlistBean
            
     
    def setPlaylist(self, entityBeans):
        self.entityBeans = entityBeans    
        index = 0
        if entityBeans:
            self.playerCntr.playSong(entityBeans[index])
            self.repopulate(entityBeans, index);
        
    def repopulate(self, entityBeans, index):
        self.model.clear()        
        for i in range(len(entityBeans)):
            songBean = entityBeans[i]            
            color = self.getBackgroundColour(i)
            if i == index:                
                self.model.append(PlaylistBean(gtk.STOCK_GO_FORWARD, songBean.tracknumber, songBean.getPlayListDescription(), songBean.path, color, i))
            else:
                self.model.append(PlaylistBean(None, songBean.tracknumber, songBean.getPlayListDescription(), songBean.path, color, i))
                   
    def getBackgroundColour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"
