'''
Created on Mar 16, 2010

@author: ivan
'''
from foobnix.radio.radio_model import RadioListModel
from foobnix.util.plsparser import getStationPath, getPlsName
'''
Created on Mar 11, 2010

@author: ivan
'''

import gtk

from foobnix.playlist.playlist_model import PlaylistModel
from foobnix.model.entity import  CommonBean
from foobnix.util.mouse_utils import is_double_click


class RadioListCntr():
    def __init__(self, gxMain, playerCntr):
        self.widget = gxMain.get_widget("radio_list_treeview")
        
        addButton = gxMain.get_widget("add_radio_toolbutton")        
        removeButton = gxMain.get_widget("remove_radio_toolbuton")
        self.urlText = gxMain.get_widget("radio_url_entry")
        
        
        self.widget.connect("button-press-event", self.onPlaySong)
        addButton.connect("clicked", self.onAddRadio)
        removeButton.connect("clicked", self.onRemoveRadio)
        
        self.model = RadioListModel(self.widget)
        
        self.playerCntr = playerCntr
        self.widget.connect("button-press-event", self.onPlaySong)
        
        self.entityBeans = []
        self.index = self.model.getSize();
                
    
    def onAddRadio(self, *args):
        urlStation = self.urlText.get_text()
        if urlStation:
            nameDef = urlStation
            if urlStation.endswith(".pls"):                
                getUrl = getStationPath(urlStation)
                if getUrl:                
                    urlStation = getUrl         
                    nameDef = getPlsName(nameDef) + " [" + urlStation + " ]"
            
            entity = CommonBean(name=nameDef, path=urlStation, type=CommonBean.TYPE_RADIO_URL, index=self.index + 1);
            self.entityBeans.append(entity)
            self.repopulate(self.entityBeans, (self.model.getSize()))
            self.urlText.set_text("")                        
        
        pass
    
    def onRemoveRadio(self, *args):
            model, iter = self.widget.get_selection().get_selected()
            if iter:              
                playlistBean = self.model.getSelectedBean()
                for i, entity in enumerate(self.entityBeans):
                    if entity.path == playlistBean.path: 
                        self.index = 0                       
                        del self.entityBeans[i]  
                model.remove(iter)
                
                
    def getState(self):
        return [self.entityBeans, self.index]
        
    def setState(self, state):
        self.entityBeans = state[0]
        self.index = state[1]
        if self.entityBeans and self.index < len(self.entityBeans):
            self.repopulate(self.entityBeans, self.index);
            self.playerCntr.playSong(self.entityBeans[self.index])
              
        
    
    def clear(self):
        self.model.clear()
        
    def onPlaySong(self, w, e):
        if is_double_click(e):
            print w
            print e
            playlistBean = self.model.getSelectedBean()
            playlistBean.type = CommonBean.TYPE_RADIO_URL  
                     
            #self.repopulate(self.entityBeans, playlistBean.index);
            self.index = playlistBean.index
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
            songBean.color = self.getBackgroundColour(i)
            songBean.name = songBean.getPlayListDescription()
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
