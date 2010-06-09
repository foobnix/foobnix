'''
Created on Mar 11, 2010

@author: ivan
'''


from foobnix.playlist.playlist_model import PlaylistModel
from foobnix.model.entity import CommonBean
from foobnix.util.mouse_utils import is_double_click
from foobnix.player.player_controller import PlayerController
from random import randint
from foobnix.util.configuration import FConfiguration
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.util import LOG


class PlaylistCntr():
    def __init__(self, widget, playerCntr):
        self.current_list_model = PlaylistModel(widget)
        self.playerCntr = playerCntr
        widget.connect("button-press-event", self.onPlaySong)
                
        self.index = 0;
        widget.connect("drag-end", self.onDrugBean)
        
    def registerDirectoryCntr(self, directoryCntr):
        self.directoryCntr=directoryCntr
                                             
    
        
    def onDrugBean(self, *ars):
        selected = self.current_list_model.getSelectedBean()
        LOG.info("Drug song", selected, selected.type)
        self.directoryCntr.set_active_view(DirectoryCntr.VIEW_VIRTUAL_LISTS)
        if selected.type in [CommonBean.TYPE_MUSIC_URL, CommonBean.TYPE_MUSIC_FILE]:
            selected.parent = None                            
            self.directoryCntr.append_virtual([selected])
            
        self.directoryCntr.leftNoteBook.set_current_page(0)
    
    def getState(self):
        return [self.get_playlist_beans(), self.index]
    
    def get_playlist_beans(self):
        return self.current_list_model.get_all_beans()
    
    def set_playlist_beans(self, beans):
        return self.current_list_model.set_all_beans(beans)    
        
        
    def setState(self, state):
        self.set_playlist_beans(state[0])
        self.index = state[1]
        if self.get_playlist_beans():
            self.repopulate(self.get_playlist_beans(), self.index);
            #self.playerCntr.playSong(self.get_playlist_beans()[self.index])
              
    def clear(self):
        self.current_list_model.clear()
        
    def onPlaySong(self, w, e):
        if is_double_click(e):
            playlistBean = self.current_list_model.getSelectedBean()           
            self.repopulate(self.get_playlist_beans(), playlistBean.index);
            self.index = playlistBean.index
            self.playerCntr.set_mode(PlayerController.MODE_PLAY_LIST)            
            self.playerCntr.playSong(playlistBean)
            
    def getNextSong(self):
        if FConfiguration().isRandom:            
            self.index = randint(0,len(self.get_playlist_beans()))   
        else:
            self.index += 1
        
        if self.index >= len(self.get_playlist_beans()):
                self.index = 0
                if not FConfiguration().isRepeat:
                    self.index = len(self.get_playlist_beans()) 
                    return None
            
        playlistBean = self.current_list_model.getBeenByPosition(self.index)
        if not playlistBean:
            return None           
        self.repopulate(self.get_playlist_beans(), playlistBean.index);        
        return playlistBean
    
    def getPrevSong(self):
        
        if FConfiguration().isRandom:            
            self.index = randint(0,len(self.get_playlist_beans()))
        else:
            self.index -= 1
        
        if self.index < 0:
            self.index = len(self.get_playlist_beans()) - 1
        
            
        playlistBean = self.current_list_model.getBeenByPosition(self.index)           
        self.repopulate(self.get_playlist_beans(), playlistBean.index);        
        return playlistBean
            
     
    def setPlaylist(self, entityBeans):
        print "Set play list"
        self.clear()
        self.set_playlist_beans(entityBeans)    
        self.index = 0
        if entityBeans:
            self.playerCntr.playSong(entityBeans[0])
            self.repopulate(entityBeans, self.index);
            
    def appendPlaylist(self, entityBeans):
        print "Append play list"        
        
        self.current_list_model.append_all_beans(entityBeans)
        
        #if self.get_playlist_beans():
            #self.playerCntr.playSong(self.get_playlist_beans()[index])
        self.repopulate(self.get_playlist_beans(), self.index);
            
                
        
    def repopulate(self, entityBeans, index):
        self.current_list_model.clear()        
        for i in range(len(entityBeans)):
            songBean = entityBeans[i]    
            songBean.name = songBean.getPlayListDescription()        
            songBean.color = self.getBackgroundColour(i)
            songBean.index = i
            if i == index:  
                songBean.setIconPlaying()               
                self.current_list_model.append(songBean)
            else:
                songBean.setIconNone() 
                self.current_list_model.append(songBean)
                   
    def getBackgroundColour(self, i):
        if i % 2 :
            return "#F2F2F2"
        else:
            return "#FFFFE5"
