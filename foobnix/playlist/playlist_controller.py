'''
Created on Mar 11, 2010

@author: ivan
'''

import gtk

from foobnix.playlist.playlist_model import PlaylistModel
from foobnix.model.entity import CommonBean
from foobnix.util.mouse_utils import is_double_click
from foobnix.player.player_controller import PlayerController


class PlaylistCntr():
    def __init__(self, widget, playerCntr):
        self.model = PlaylistModel(widget)
        self.playerCntr = playerCntr
        widget.connect("button-press-event", self.onPlaySong)
                
        self.index = 0;
    
    def getState(self):
        return [self.get_playlist_beans(), self.index]
    
    def get_playlist_beans(self):
        return self.model.get_all_beans()
    
    def set_playlist_beans(self, beans):
        return self.model.set_all_beans(beans)    
        
        
    def setState(self, state):
        self.set_playlist_beans(state[0])
        self.index = state[1]
        if self.get_playlist_beans():
            self.repopulate(self.get_playlist_beans(), self.index);
           #self.playerCntr.playSong(self.get_playlist_beans()[self.index])
              
    def clear(self):
        self.model.clear()
        
    def onPlaySong(self, w, e):
        if is_double_click(e):
            playlistBean = self.model.getSelectedBean()           
            self.repopulate(self.get_playlist_beans(), playlistBean.index);
            self.index = playlistBean.index
            self.playerCntr.set_mode(PlayerController.MODE_PLAY_LIST)            
            self.playerCntr.playSong(playlistBean)
            
    def getNextSong(self):
        self.index += 1
        if self.index >= len(self.get_playlist_beans()):
            self.index = 0
            
        playlistBean = self.model.getBeenByPosition(self.index)           
        self.repopulate(self.get_playlist_beans(), playlistBean.index);        
        return playlistBean
    
    def getPrevSong(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.get_playlist_beans()) - 1
            
        playlistBean = self.model.getBeenByPosition(self.index)           
        self.repopulate(self.get_playlist_beans(), playlistBean.index);        
        return playlistBean
            
     
    def setPlaylist(self, entityBeans):
        self.clear()
        self.set_playlist_beans(entityBeans)    
        self.index = 0
        if entityBeans:
            self.playerCntr.playSong(entityBeans[self.index])
            self.repopulate(entityBeans, self.index);
            
    def appendPlaylist(self, entityBeans):        
        for entity in entityBeans:
            self.get_playlist_beans().append(entity)
        
        if self.get_playlist_beans():
            #self.playerCntr.playSong(self.get_playlist_beans()[index])
            self.repopulate(self.get_playlist_beans(), self.index);        
        
    def repopulate(self, entityBeans, index):
        self.model.clear()        
        for i in range(len(entityBeans)):
            songBean = entityBeans[i]    
            songBean.name = songBean.getPlayListDescription()        
            songBean.color = self.getBackgroundColour(i)
            songBean.index = i
            if i == index:  
                songBean.setIconPlaying()               
                self.model.append(songBean)
            else:
                songBean.setIconNone() 
                self.model.append(songBean)
                   
    def getBackgroundColour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"
