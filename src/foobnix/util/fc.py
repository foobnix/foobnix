#-*- coding: utf-8 -*-
'''
Created on 23 сент. 2010

@author: ivan
'''
import pickle
from foobnix.util import LOG, const
import os
from foobnix.util.singleton import Singleton
import uuid
import random
from foobnix.util.const import ICON_FOOBNIX, ICON_FOOBNIX_PLAY, \
    ICON_FOOBNIX_PAUSE, ICON_FOOBNIX_STOP, ICON_FOOBNIX_RADIO
import thread

CONFIG_DIR = os.path.expanduser("~") + "/.config/foobnix/"
if not os.path.exists(CONFIG_DIR):
    os.mkdir(CONFIG_DIR)
CONFIG_FILE = CONFIG_DIR + "foobnix.pkl"


def get_random_vk():
    vks = {
       "c891888@bofthew.com":"c891888",
       "c892009@bofthew.com":"c892009",
       "c892406@bofthew.com":"c892406",
       "c892588@bofthew.com":"c892588"       
       }

    rand = random.randint(0, len(vks) - 1)
    key = vks.keys()[rand]
    value = vks[key]
    return key, value


"""Foobnix configuration"""
class FC:
    __metaclass__ = Singleton

    API_KEY = "bca6866edc9bdcec8d5e8c32f709bea1"
    API_SECRET = "800adaf46e237805a4ec2a81404b3ff2"
    LASTFM_USER = "l_user_"
    LASTFM_PASSWORD = "l_pass_"

    def __init__(self):
        """init default values"""
        self.is_view_info_panel = True
        self.is_view_search_panel = True
        self.is_view_music_tree_panel = True
        self.is_view_lyric_panel = True
        self.is_view_video_panel = True
        self.is_order_random = False
        self.repeat_state = const.REPEAT_ALL
        self.playlist_type = const.PLAYLIST_TREE

        """player controls"""
        self.volume = 10
        self.is_eq_enable = False
        self.eq_presets = None
        self.eq_presets_default = "CUSTOM"

        """tabs"""
        self.len_of_tab = 30
        self.tab_close_element = "label"
        self.count_of_tabs = 5
        self.tab_position = "top"
        

        """main window controls"""
        self.main_window_size = [119, 154, 884, 479]
        self.hpaned_left = 248;
        self.hpaned_right = 320;
        self.vpaned_small = 100;

        """main window action"""
        self.on_close_window = const.ON_CLOSE_HIDE

        """support file formats"""
        self.last_music_path = None
        self.music_paths = ["/tmp"]
        audio = [".mp3", ".ogg", ".ape", ".flac", ".wma", ".cue", ".mpc", ".aiff", ".raw", ".au", ".aac", ".mp4", ".ra", ".m4p", ".3gp"]
        video = [".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".mov", ".mp4", ".mpg", ".rm", ".swf", ".vob", ".wmv"]
        self.support_formats = audio + video
        
        self.cache_music_tree_beans = []
        self.cache_virtual_tree_beans = []
        self.cache_radio_tree_beans = []

        """last fm"""
        self.lfm_login = self.LASTFM_USER
        self.lfm_password = self.LASTFM_PASSWORD
        """vk"""
        vk = get_random_vk()
        self.vk_login = vk[0]
        self.vk_password = vk[1]
        self.vk_cookie = None
        
        self.enable_music_srobbler = True
        self.enable_radio_srobbler = True

        """proxy"""
        self.proxy_enable = False
        self.proxy_url = None
        
        """tray icon"""
        self.show_tray_icon = True
        self.tray_icon_auto_hide = True
        self.static_tray_icon = True
        self.system_icons_dinamic = False
        self.change_tray_icon = False
        

        self.all_icons = [ICON_FOOBNIX, ICON_FOOBNIX_PLAY, ICON_FOOBNIX_PAUSE, ICON_FOOBNIX_STOP, ICON_FOOBNIX_RADIO, "standart_icons/foobnix-tux.gif"]
                
        self.static_icon_entry = ICON_FOOBNIX
        
        self.play_icon_entry = ICON_FOOBNIX_PLAY
        self.pause_icon_entry = ICON_FOOBNIX_PAUSE
        self.stop_icon_entry = ICON_FOOBNIX_STOP
        self.radio_icon_entry = ICON_FOOBNIX_RADIO
                
        """download manager controls"""
        self.auto_start_donwload = True
        self.max_active_count = 3
        self.online_save_to_folder = "/tmp"
        self.is_save_online = True
        
        """info panel"""
        self.info_panel_image_size = 150
        self.tooltip_image_size = 150
        self.is_info_panel_show_tags = False
        
        self.uuid = uuid.uuid4().hex
        self.check_new_version = True

        self.last_dir = None
        
        self.proxy_enable = False
        self.proxy_url = None
        self.proxy_user = None
        self.proxy_password = None
        
        self.action_hotkey = {'foobnix --volume-up': '<SUPER>Up', 'foobnix --volume-down': '<SUPER>Down', 'foobnix --show-hide': '<SUPER>a', 'foobnix --prev': '<SUPER>Left', 'foobnix --play': '<SUPER>x', 'foobnix --pause': '<SUPER>z', 'foobnix --next': '<SUPER>Right'}

        self.left_perspective = "info"        
        self = self._load();
        
        

    def save(self, in_thread=True):
        if in_thread:
            thread.start_new_thread(FCHelper().save, (self,))
        else:
            FCHelper().save(self)
        
    def _load(self):
        """restore from file"""
        object = FCHelper().load()
        if object:
            dict = object.__dict__
            keys = self.__dict__.keys()
            for i in dict:
                try:
                    if i in keys:
                        setattr(self, i, dict[i])
                except Exception, e:
                    LOG.warn("Value not found", e)
                    return False
        return True

    def info(self):
        FCHelper().print_info(self)

    def delete(self):
        FCHelper().delete()

class FCHelper():
    def __init__(self):
        pass

    def save(self, object):
        save_file = file(CONFIG_FILE, 'w')
        try:
            pickle.dump(object, save_file)
        except Exception, e:
            LOG.error("Erorr dumping pickle conf", e)
        save_file.close()
        LOG.debug("Config save")
        self.print_info(object);


    def load(self):
        if not os.path.exists(CONFIG_FILE):
            LOG.warn("Config file not found", CONFIG_FILE)
            return None

        with file(CONFIG_FILE, 'r') as load_file:
            try:
                load_file = file(CONFIG_FILE, 'r')
                pickled = load_file.read()

                object = pickle.loads(pickled)
                LOG.debug("Config loaded")
                self.print_info(object);
                return object
            except Exception, e:
                LOG.error("Error laod config", e)
        return None


    def delete(self):
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

    def print_info(self, object):
        dict = object.__dict__
        for i in object.__dict__:
            LOG.debug(i, str(dict[i])[:500]);
