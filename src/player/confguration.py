'''
Created on Feb 27, 2010

@author: ivan
'''
import pickle
import LOG


class Singleton(type):
    def __call__(self, *args, **kw):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kw)
        return self.instance
    
    def __init__(self, name, bases, dict):
        super(Singleton, self).__init__(name, bases, dict)
        self.instance = None

class FoobNixConf:
    __metaclass__ = Singleton
    
    def __init__(self):
        self.mediaLibraryPath = "/home/ivan/Music"
        self.currentSong = None
        self.currentSongIndex = None
        self.currentPlayListSongs = None
        
        instance = self._loadCfgFromFile()
        if instance:
            self.mediaLibraryPath = instance.mediaLibraryPath
            #self.currentSong = None
            #self.currentSongIndex = None
            #self.currentPlayListSongs = None
        
                        
            

    def get(self):             
        cfg = self._loadCfgFromFile()
        if cfg:
            self.mediaLibraryPath = cfg.mediaLibraryPath
            self.currentSong = cfg.currentSong
            self.currentPlayListSongs = cfg.currentPlayListSongs 
        LOG.debug("Load from Fie")
        return cfg    
    def save(self):
        FoobNixConf()._saveCfgToFile()               
        
    def _saveCfgToFile(self):
        #conf = FoobNixConf()
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
            conf = FoobNixConf()
            return conf
        
        load_file.close()    
        
        LOG.debug("Load configuration")
        return conf