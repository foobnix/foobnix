'''
Created on Mar 14, 2010

@author: ivan
'''
from foobnix.util.confguration import FConfiguration
class OnLoadExitAppCntr():
    def __init__(self, playlistCntr, playerWidgets, playerCntr, directoryCntr, appConfCntr, radioListCntr, virtualListCntr):
        self.directoryCntr = directoryCntr
        self.playlistCntr = playlistCntr
        self.playerWidgets = playerWidgets
        self.playerCntr = playerCntr
        self.appConfCntr = appConfCntr
        self.radioListCntr = radioListCntr
        self.virtualListCntr = virtualListCntr
        
        self.onStart()

    def onStart(self):
        print "Init configs"
        print FConfiguration().playlistState
        
        if FConfiguration().playlistState:
            self.playlistCntr.setState(FConfiguration().playlistState)
        
        if FConfiguration().virtualListState:
            self.directoryCntr.setState(FConfiguration().virtualListState)
        
        if FConfiguration().volumeValue:
            self.playerWidgets.volume.set_value(FConfiguration().volumeValue)
            self.playerCntr.setVolume(FConfiguration().volumeValue / 100)
        
        if FConfiguration().hpanelPostition:
            self.playerWidgets.hpanel.set_position(FConfiguration().hpanelPostition)
        
        if FConfiguration().vpanelPostition:
            self.playerWidgets.vpanel.set_position(FConfiguration().vpanelPostition)
            
        if FConfiguration().mediaLibraryPath:            
            self.appConfCntr.setMusicFolder(FConfiguration().mediaLibraryPath)
            
        if FConfiguration().radiolistState:
            self.radioListCntr.setState(FConfiguration().radiolistState)
        
        self.appConfCntr.setVkLoginPass(FConfiguration().vk_login, FConfiguration().vk_password)
        self.appConfCntr.setLfmLoginPass(FConfiguration().lfm_login, FConfiguration().lfm_password)
            
            
            
    def onExit(self):
        print "Save configs"        
        FConfiguration().playlistState = self.playlistCntr.getState()
        FConfiguration().virtualListState = self.directoryCntr.getState()
        
        FConfiguration().radiolistState = self.radioListCntr.getState()
        
        FConfiguration().volumeValue = self.playerWidgets.volume.get_value()
        FConfiguration().vpanelPostition = self.playerWidgets.vpanel.get_position()
        FConfiguration().hpanelPostition = self.playerWidgets.hpanel.get_position()
        FConfiguration().mediaLibraryPath = self.appConfCntr.getMusicFolder()
        
        FConfiguration().vk_login = self.appConfCntr.getVkLogin()
        FConfiguration().vk_password = self.appConfCntr.getVkPassword()
        
        FConfiguration().lfm_login = self.appConfCntr.getLfmLogin()
        FConfiguration().lfm_password = self.appConfCntr.getLfmPassword()
          
        FConfiguration().save()
    
    
