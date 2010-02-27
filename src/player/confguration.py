'''
Created on Feb 27, 2010

@author: ivan
'''
import pickle
import LOG

class FNConfiguration:
    __single = None
    
    def __init__(self):
        
        self.mediaLibraryPath = "/home/ivan/Music"
        self.currentSong = None
        self.currentSongIndex = None
        self.currentPlayListSongs = None
            
        self.load()
    

        
    @staticmethod
    def getMediaLibraryPath():        
        return FNConfiguration().mediaLibraryPath
   
    def load(self):     
        cfg = self._loadCfgFromFile()
        if cfg:
            self.mediaLibraryPath = cfg.mediaLibraryPath
            self.currentSong = cfg.currentSong
            self.currentPlayListSongs = cfg.currentPlayListSongs 
    
    @staticmethod
    def save():
        FNConfiguration()._saveCfgToFile()               
        
    def _saveCfgToFile(self):
        #conf = FNConfiguration()
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
                
        conf = pickle.load(load_file)
        load_file.close()
        LOG.debug("Load configuration")
        return conf
