'''
Created on Feb 27, 2010

@author: ivan
'''
import pickle
import os
from foobnix.util import LOG


class Singleton(type):
    def __call__(self, *args, **kw):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kw)
        return self.instance
    
    def __init__(self, name, bases, dict):
        super(Singleton, self).__init__(name, bases, dict)
        self.instance = None

class FConfiguration:
    __metaclass__ = Singleton
    
    def __init__(self):
        self.mediaLibraryPath = "/home/ivan/Music"
        self.supportTypes = [".mp3", ".ogg", ".ape", "flac"]
        self.isRandom = False
        self.isRepeat = True
        self.isPlayOnStart = True
        self.savedPlayList = []
        self.savedRadioList = []
        self.savedSongIndex = 0
        self.volumeValue = 0
        self.vpanelPostition = 300
        self.hpanelPostition = 300
        
        self.playlistState = None
        self.radiolistState = None
        
        instance = self._loadCfgFromFile()
        if instance:
            try:
                self.playlistState = instance.playlistState
                self.radiolistState = instance.radiolistState 
                self.mediaLibraryPath = instance.mediaLibraryPath
                self.isRandom = instance.isRandom
                self.isRepeat = instance.isRepeat
                self.isPlayOnStart = instance.isPlayOnStart
                self.savedPlayList = instance.savedPlayList
                self.savedSongIndex = instance.savedSongIndex
                self.volumeValue = instance.volumeValue
                self.vpanelPostition = instance.vpanelPostition
                self.hpanelPostition = instance.hpanelPostition
                self.savedRadioList = instance.savedRadioList
                
            except AttributeError:
                LOG.debug("Configuraton attributes are changed")                
                os.remove("foobnix_conf.pkl")
 
        print "LOAD CONFIGS"
        self.printArttibutes()

    def save(self):
        print "SAVE CONFIGS"
        self.printArttibutes()
        FConfiguration()._saveCfgToFile()      
        
    def printArttibutes(self):
        for i in dir(self):
            if not i.startswith("__"):
                print i, getattr(self,i)         
        
    def _saveCfgToFile(self):
        #conf = FConfiguration()
        save_file = file("foobnix_conf.pkl", 'w')
        pickle.dump(self, save_file)
        save_file.close()
        LOG.debug("Save configuration")
            
    def _loadCfgFromFile(self): 
        try:       
            load_file = file("foobnix_conf.pkl", "r")
        except IOError:
            LOG.debug("file not exists")
            return None
        try:        
            conf = pickle.load(load_file)
        except AttributeError:
            LOG.debug("Error loading configuration")
            conf = FConfiguration()
            return conf
        
        load_file.close()    
        
        LOG.debug("Load configuration")
        return conf
