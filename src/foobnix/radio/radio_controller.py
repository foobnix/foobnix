'''
Created on Mar 16, 2010

@author: ivan
'''
from foobnix.radio.radio_model import RadioListModel
from foobnix.util.plsparser import getStationPath, getPlsName, get_content

from foobnix.model.entity import  CommonBean
from foobnix.util.mouse_utils import is_double_click
import urllib2
from foobnix.util import LOG


class RadioListCntr():
    def __init__(self, gxMain, playerCntr):
        self.widget = gxMain.get_widget("radio_list_treeview")
        
        addButton = gxMain.get_widget("add_radio_toolbutton")        
        removeButton = gxMain.get_widget("remove_radio_toolbuton")
        self.urlText = gxMain.get_widget("radio_url_entry")
        
        
        self.widget.connect("button-press-event", self.onPlaySong)
        addButton.connect("clicked", self.onAddRadio)
        removeButton.connect("clicked", self.onRemoveRadio)
        
        self.current_list_model = RadioListModel(self.widget)
        
        self.playerCntr = playerCntr
        self.widget.connect("button-press-event", self.onPlaySong)
        
        self.entityBeans = []
        self.index = self.current_list_model.get_size();
                
    
    def onAddRadio(self, *args):
        urlStation = self.urlText.get_text()
        if urlStation:
            nameDef = urlStation
            if urlStation.endswith(".pls"):                
                getUrl = getStationPath(urlStation)
                if getUrl:                
                    urlStation = getUrl         
                    nameDef = getPlsName(nameDef) + " [" + urlStation + " ]"
                    print nameDef
            elif urlStation.endswith(".m3u"):
                content = get_content(urlStation)
                for line in content.rsplit():
                    if not line.startswith("#"):
                        urlStation = line         
                        nameDef = line
                        break
                     
            
            
            entity = CommonBean(name=nameDef, path=urlStation, type=CommonBean.TYPE_RADIO_URL, index=self.index + 1);
            self.entityBeans.append(entity)
            self.repopulate(self.entityBeans, (self.current_list_model.get_size()))
            self.urlText.set_text("")                        
        
        pass
    
    def onRemoveRadio(self, *args):
            model, iter = self.widget.get_selection().get_selected()
            if iter:              
                playlistBean = self.current_list_model.get_selected_bean()
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
        self.current_list_model.clear()
        
    def onPlaySong(self, w, e):
        if is_double_click(e):
            print w
            print e
            playlistBean = self.current_list_model.get_selected_bean()
            playlistBean.type = CommonBean.TYPE_RADIO_URL  
                     
            #self.repopulate(self.entityBeans, playlistBean.index);
            self.index = playlistBean.index
            
            if not playlistBean.path.startswith("http"):
                return None
            
            print playlistBean.path
            remotefile = urllib2.urlopen(playlistBean.path)
            print "INFO", remotefile
            if not remotefile.info() or remotefile.info()["Content-Type"].find("text") == -1:
                self.playerCntr.playSong(playlistBean)                
            else:            
                LOG.error("Can't play html page")
                return None
                
            
    def getNextSong(self):
        self.index += 1
        if self.index >= len(self.entityBeans):
            self.index = 0
            
        playlistBean = self.current_list_model.getBeenByPosition(self.index)           
        self.repopulate(self.entityBeans, playlistBean.index);        
        return playlistBean
    
    def getPrevSong(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(self.entityBeans) - 1
            
        playlistBean = self.current_list_model.getBeenByPosition(self.index)           
        self.repopulate(self.entityBeans, playlistBean.index);        
        return playlistBean
            
     
    def setPlaylist(self, entityBeans):
        self.entityBeans = entityBeans    
        index = 0
        if entityBeans:
            self.playerCntr.playSong(entityBeans[index])
            self.repopulate(entityBeans, index);
        
    def repopulate(self, entityBeans, index):
        self.current_list_model.clear()        
        for i in range(len(entityBeans)):
            songBean = entityBeans[i]            
            songBean.color = self.getBackgroundColour(i)
            songBean.name = songBean.getPlayListDescription()
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
