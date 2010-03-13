'''
Created on Mar 14, 2010

@author: ivan
'''
from foobnix.util.confguration import FConfiguration
class OnLoadExitAppCntr():
    def __init__(self, playlistCntr):
        self.playlistCntr = playlistCntr
        
        self.onStart()

    def onStart(self):
        print "Init configs"
        print FConfiguration().playlistState
        if FConfiguration().playlistState:
            self.playlistCntr.setState(FConfiguration().playlistState)
            
    def onExit(self):
        print "Save configs"        
        FConfiguration().playlistState = self.playlistCntr.getState()
        FConfiguration().save()
    