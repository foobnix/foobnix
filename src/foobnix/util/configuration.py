# -*- coding: utf-8 -*-
'''
Created on Feb 27, 2010

@author: ivan
'''
from __future__ import with_statement
import os
from foobnix.util.singleton import Singleton
import tempfile
from foobnix.util import const, LOG
import gtk
import pickle
import uuid

FOOBNIX_TMP = "/usr/share/foobnix"
FOOBNIX_TMP_RADIO = os.path.join(FOOBNIX_TMP, "radio")
FOOBNIX_VERSION_FILE_NAME = "version"

USER_DIR = os.getenv("HOME") or os.getenv('USERPROFILE')
CFG_FILE_DIR = os.path.join(USER_DIR, ".config/foobnix")
CFG_FILE = os.path.join(CFG_FILE_DIR, "foobnix_conf.pkl")

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

def check_create_cfg_dir():
    if not os.path.exists(CFG_FILE_DIR):
        os.makedirs(CFG_FILE_DIR)

class FConfiguration:
    
    
    
    FOOBNIX = "foobnix"
    SUPPORTED_AUDIO_FORMATS = 'supported_audio_formats'
    
    __metaclass__ = Singleton
    
    
    #config = ConfigParser.RawConfigParser()    
    #config.read(CFG_FILE)
    
    
    #def get(self, type):
    #    return self.config.get(self.FOOBNIX, self.SUPPORTED_AUDIO_FORMATS)
    check_create_cfg_dir()
    def __init__(self, is_load_file=True):
        
        self.media_library_path = [tempfile.gettempdir()]
        
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
        
        ### view panels ###
        self.view_tree_panel = True
        self.view_search_panel = True
        self.view_info_panel = False
        self.view_lyric_panel = False
        
        self.playlistState = None
        self.radiolistState = None
        self.virtualListState = {"Default list" : []}
        
        
        self.is_save_online = False
        self.song_source_relevance_algorithm = 0
        self.online_tab_show_by = 0
        
        self.vk_login = "qax@bigmir.net"
        self.vk_password = "foobnix"
        
        self.lfm_user_default = "l_user_" 
        self.lfm_login = self.lfm_user_default
        self.lfm_password = "l_pass_"
        
        self.API_KEY = "bca6866edc9bdcec8d5e8c32f709bea1"
        self.API_SECRET = "800adaf46e237805a4ec2a81404b3ff2"
    
        self.cookie = None 
        
        self.count_of_tabs = 3
        self.len_of_tab = 30
        
        self.cache_music_beans = []
        
        self.tab_position = "top"
        
        self.last_dir = None
        
        self.on_close_window = const.ON_CLOSE_HIDE;
        self.show_tray_icon = True
        
        self.proxy_enable = False
        self.proxy_url = None
        self.proxy_user = None
        self.proxy_password = None
        
        """info panel"""
        
        if gtk.gdk.screen_height() < 800:
            self.info_panel_image_size = 150
        else:
            self.info_panel_image_size = 200    
                
        
        self.tab_close_element = "label"
        self.play_ordering = const.ORDER_LINEAR 
        self.play_looping = const.LOPPING_LOOP_ALL
        
        """random uuis of player"""
        self.uuid = uuid.uuid4().hex
        
        self.check_new_version = True
        
        self.add_child_folders = True
        self.lyric_panel_image_size = 250
        
        self.tray_icon_auto_hide = True
        
        self.action_hotkey = {'foobnix --volume-up': '<SUPER>Up', 'foobnix --volume-down': '<SUPER>Down', 'foobnix --show-hide': '<SUPER>a', 'foobnix --prev': '<SUPER>Left', 'foobnix --play': '<SUPER>x', 'foobnix --pause': '<SUPER>z', 'foobnix --next': '<SUPER>Right'}
        
        
        self.last_notebook_page = "Foobnix"
        self.last_notebook_beans = []
        self.last_play_bean = 0
        self.save_tabs = True
        self.play_on_start = True
        self.configure_state = None
   
        instance = self._loadCfgFromFile(is_load_file)
        if instance:
            try:
                self.supportTypes = instance.supportTypes
                self.virtualListState = instance.virtualListState
                self.playlistState = instance.playlistState
                self.radiolistState = instance.radiolistState 
                self.media_library_path = instance.media_library_path
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
                self.len_of_tab = instance.len_of_tab
                
                self.cookie = instance.cookie
                
                self.view_tree_panel = instance.view_tree_panel
                self.view_search_panel = instance.view_search_panel
                self.view_info_panel = instance.view_info_panel
                self.view_lyric_panel = instance.view_lyric_panel
                
                self.cache_music_beans = instance.cache_music_beans
                self.tab_position = instance.tab_position
                
                self.last_dir = instance.last_dir
                self.info_panel_image_size = instance.info_panel_image_size
                self.tab_close_element = instance.tab_close_element
                
                self.play_ordering = instance.play_ordering 
                self.play_looping = instance.play_looping
                
                self.on_close_window = instance.on_close_window;
                self.show_tray_icon = instance.show_tray_icon
                
                "proxy"
                self.proxy_enable = instance.proxy_enable
                self.proxy_url = instance.proxy_url
                self.proxy_user = instance.proxy_user
                self.proxy_password = instance.proxy_password
                
                self.uuid = instance.uuid
                
                self.check_new_version = instance.check_new_version 
                self.add_child_folders = instance.add_child_folders
                self.lyric_panel_image_size = instance.lyric_panel_image_size
                
                self.action_hotkey = instance.action_hotkey
                self.tray_icon_auto_hide = instance.tray_icon_auto_hide
                
                self.last_notebook_page = instance.last_notebook_page
                self.last_notebook_beans = instance.last_notebook_beans
                self.play_on_start = instance.play_on_start
                self.save_tabs = instance.save_tabs
                self.last_play_bean = instance.last_play_bean
                self.configure_state = instance.configure_state
                
            except AttributeError:
                LOG.debug("Configuraton attributes are changed")
                os.remove(CFG_FILE)
 
        LOG.info("LOAD CONFIGS")
        self.printArttibutes()

    def save(self):
        LOG.info("SAVE CONFIGS")
        self.printArttibutes()
        FConfiguration()._saveCfgToFile()
        
    def printArttibutes(self):
        for i in dir(self):
            if not i.startswith("__"):
                value = str(getattr(self, i))[:300]
                LOG.info(i, value)
        
    def _saveCfgToFile(self):
        #conf = FConfiguration()
        
        save_file = file(CFG_FILE, 'w')
        try:
            pickle.dump(self, save_file)
        except:
            LOG.error("Erorr dumping pickle conf")
        save_file.close()
        LOG.debug("Save configuration")
            
    def _loadCfgFromFile(self, is_load_file):
        if not is_load_file:
            return

        try:
            with file(CFG_FILE, 'r') as load_file:
                load_file = file(CFG_FILE, 'r') 
                pickled = load_file.read()
                # fixing mistyped 'configuration' package name
                if 'confguration' in pickled:
                    pickled = pickled.replace('confguration', 'configuration')
                return pickle.loads(pickled)
        
        except IOError:
            LOG.debug('Configuration file does not exist.')
        except ImportError, ex:            
            LOG.error('Configuration file is corrupted. Removing it...')
            os.remove(CFG_FILE)
        except BaseException, ex:
            LOG.error('Unexpected exception of type %s: "%s".' % (ex.__class__.__name__, ex))

