'''
Created on Mar 14, 2010

@author: ivan
'''
from foobnix.util.configuration import FConfiguration
from foobnix.util import LOG
class AppConfigurationCntrl():
    def __init__(self, gxMain, directoryCntr):
        self.directoryCntr = directoryCntr
        '''''        
        """Random button"""
        self.randomCheckButton = gxMain.get_widget("random_checkbutton")
        self.randomCheckButton.set_active(FConfiguration().isRandom)
        self.randomCheckButton.connect("clicked", self.onRandomClicked)
        
        """Repeat button"""
        self.repeatCheckButton = gxMain.get_widget("repeat_checkbutton")
        self.repeatCheckButton.set_active(FConfiguration().isRepeat)
        self.repeatCheckButton.connect("clicked", self.onRepeatClicked)
        
        """Play on Start"""
        self.playOnStartCheckButton = gxMain.get_widget("playonstart_checkbutton")
        self.playOnStartCheckButton.set_active(FConfiguration().isPlayOnStart)
        self.playOnStartCheckButton.connect("clicked", self.onPlayOnStartClicked)
        '''''               
        
    
    def onPlayOnStartClicked(self, *args):
        FConfiguration().isPlayOnStart = self.playOnStartCheckButton.get_active()
        
    def onRepeatClicked(self, *args):
        FConfiguration().isRepeat = self.repeatCheckButton.get_active()
        
    def onRandomClicked(self, *args):
        FConfiguration().isRandom = self.randomCheckButton.get_active()
        

