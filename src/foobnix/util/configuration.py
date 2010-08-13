# -*- coding: utf-8 -*-
'''
Created on Feb 27, 2010

@author: ivan
'''
from __future__ import with_statement
import pickle
import os
import tempfile
import ConfigParser
from foobnix.util.singleton import Singleton
from foobnix.util import LOG

FOOBNIX_TMP = "/opt/foobnix"
FOOBNIX_TMP_RADIO = os.path.join(FOOBNIX_TMP, "radio")
FOOBNIX_VERSION_FILE_NAME = "version"


"""get last version from file"""
def get_version():
    result = "A"
    version_file = None
    if os.path.exists(os.path.join(FOOBNIX_TMP, FOOBNIX_VERSION_FILE_NAME)):
        version_file = os.path.join(FOOBNIX_TMP, FOOBNIX_VERSION_FILE_NAME)
    elif os.path.exists(FOOBNIX_VERSION_FILE_NAME):
        version_file = os.path.join(FOOBNIX_VERSION_FILE_NAME)
     
    with file(version_file, 'r') as v_file:
        
        for line in v_file:      
            line = str(line).strip()     
            if line.find("VERSION=") >= 0:             
                result = line[len("VERSION="):]
            elif line.find("RELEASE=") >= 0:  
                result += "-" + line[len("RELEASE="):]  
    return result

VERSION = get_version()        


class FConfiguration:
    
    
    
    FOOBNIX = "foobnix"
    SUPPORTED_AUDIO_FORMATS = 'supported_audio_formats'
    
    __metaclass__ = Singleton
    USER_DIR = os.getenv("HOME") or os.getenv('USERPROFILE')
    CFG_FILE = USER_DIR + "/foobnix_conf.pkl"
    
    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(USER_DIR, "foobnix.cfg"))
    
    
    def get(self, type):
        return self.config.get(self.FOOBNIX, self.SUPPORTED_AUDIO_FORMATS)
    
    def __init__(self, is_load_file=True):
        
        self.mediaLibraryPath = tempfile.gettempdir()
        self.onlineMusicPath = tempfile.gettempdir()
        self.supportTypes = [".mp3", ".ogg", ".ape", ".flac", ".wma", ".cue", ".mpc", ".aiff", ".raw", ".au", ".aac", ".mp4", ".ra", ".m4p", ".3gp" ]
        
        self.isRandom = False
        self.isRepeat = True
        self.isPlayOnStart = False
        self.savedPlayList = []
        self.savedRadioList = []
        self.savedSongIndex = 0
        self.volumeValue = 50.0
        self.vpanelPostition = 234
        self.hpanelPostition = 370
        self.hpanel2Postition = 521
        
        self.playlistState = None
        self.radiolistState = None
        self.virtualListState = {"Default list" : []}
        
        
        self.is_save_online = False
        self.song_source_relevance_algorithm = 0
        self.online_tab_show_by = 0
        
        self.vk_login = "qax@bigmir.net"
        self.vk_password = "foobnix"
        
        self.lfm_login = "foobnix"
        self.lfm_password = "foobnix"
        
        self.API_KEY = "bca6866edc9bdcec8d5e8c32f709bea1"
        self.API_SECRET = "800adaf46e237805a4ec2a81404b3ff2"
    
        self.cookie = None 
        
        self.count_of_tabs = 2
   
        instance = self._loadCfgFromFile(is_load_file)
        if instance:
            try:
                self.virtualListState = instance.virtualListState
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
                self.hpanel2Postition = instance.hpanel2Postition
                
                self.savedRadioList = instance.savedRadioList
                
                self.is_save_online = instance.is_save_online
                self.onlineMusicPath = instance.onlineMusicPath
                
                self.vk_login = instance.vk_login
                self.vk_password = instance.vk_password
                
                self.lfm_login = instance.lfm_login
                self.lfm_password = instance.lfm_password
                
                self.count_of_tabs = instance.count_of_tabs
                
                self.cookie = instance.cookie
            except AttributeError:
                LOG.debug("Configuraton attributes are changed")
                os.remove(self.CFG_FILE)
 
        LOG.info("LOAD CONFIGS")
        self.printArttibutes()

    def save(self):
        LOG.info("SAVE CONFIGS")
        self.printArttibutes()
        FConfiguration()._saveCfgToFile()
        
    def printArttibutes(self):
        for i in dir(self):
            if not i.startswith("__"):
                LOG.info(i, getattr(self, i))
        
    def _saveCfgToFile(self):
        #conf = FConfiguration()
        
        save_file = file(self.CFG_FILE, 'w')
        pickle.dump(self, save_file)
        save_file.close()
        LOG.debug("Save configuration")
            
    def _loadCfgFromFile(self, is_load_file):
        if not is_load_file:
            return

        try:
            with file(self.CFG_FILE, 'r') as load_file:
                load_file = file(self.CFG_FILE, 'r') 
                pickled = load_file.read()
                # fixing mistyped 'configuration' package name
                if 'confguration' in pickled:
                    pickled = pickled.replace('confguration', 'configuration')
                return pickle.loads(pickled)
        
        except IOError:
            LOG.debug('Configuration file does not exist.')
        except ImportError, ex:            
            LOG.error('Configuration file is corrupted. Removing it...')
            os.remove(self.CFG_FILE)
        except BaseException, ex:
            LOG.error('Unexpected exception of type %s: "%s".' % (ex.__class__.__name__, ex))

