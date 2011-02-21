#-*- coding: utf-8 -*-
'''
Created on 23 сент. 2010

@author: ivan
'''
from __future__ import with_statement
from foobnix.util import const
from foobnix.util.singleton import Singleton
from foobnix.util.const import ICON_FOOBNIX, ICON_FOOBNIX_PLAY, \
    ICON_FOOBNIX_PAUSE, ICON_FOOBNIX_STOP, ICON_FOOBNIX_RADIO

from foobnix.util.agent import get_ranmom_agent
from foobnix.fc.fc_helper import FCStates, CONFIG_DIR
from foobnix.version import VERSION
from foobnix.fc.fc_base import FCBase
import os

CONFIG_FILE = os.path.join(CONFIG_DIR , "foobnix_%s.pkl" % VERSION)

"""Foobnix player configuration"""
class FC():
    __metaclass__ = Singleton
    
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
        
        self.update_tree_on_start = False
        
        """expand tree paths"""
        self.nav_expand_paths = []
        self.radio_expand_paths = []
        self.virtual_expand_paths = []
        
        """selected tree paths"""
        self.nav_selected_paths = []
        self.radio_selected_paths = []
        self.virtual_selected_paths = []
        
        
        self.agent_line = get_ranmom_agent()

        """main window controls"""
        self.main_window_size = [119, 154, 884, 479]
        self.hpaned_left = 248;
        self.hpaned_right = 320;
        self.vpaned_small = 100;
        self.background_image_themes = ["theme/cat.jpg", "theme/flower.jpg"]
        self.background_image = None
        self.window_opacity = 1
        
        self.menu_style = "new"

        """main window action"""
        self.on_close_window = const.ON_CLOSE_HIDE

        """support file formats"""
                
        audio_container = [".cue", ".iso.wv"]
        video_formats = [".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".mov", ".mpg", ".rm", ".swf", ".vob", ".wmv"] 
        self.audio_formats = [".mp3", ".m3u", ".ogg", ".ape", ".flac", ".wma", ".mpc", ".aiff", ".raw", ".au", ".aac", ".mp4", ".m4a", ".ra", ".m4p", ".wv"]        
        self.all_support_formats = self.audio_formats + video_formats + audio_container
        self.all_support_formats.sort()
        
        """music library"""
        self.tab_names = [_("Empty tab"), ]
        self.last_music_path = None
        self.music_paths = [[], ]
        self.cache_music_tree_beans = [[], ]
        
        self.cache_virtual_tree_beans = []
        self.cache_radio_tree_beans = []

        self.enable_music_scrobbler = True
        self.enable_radio_scrobbler = True
        """proxy"""
        self.proxy_enable = False
        self.proxy_url = None
        
        """tray icon"""
        self.show_tray_icon = True
        self.tray_icon_auto_hide = True
        self.static_tray_icon = True
        self.system_icons_dinamic = False
        self.change_tray_icon = False
        
        self.all_icons = [ICON_FOOBNIX, ICON_FOOBNIX_PLAY, ICON_FOOBNIX_PAUSE, ICON_FOOBNIX_STOP, ICON_FOOBNIX_RADIO, "foobnix-tux.gif"]
                
        self.static_icon_entry = ICON_FOOBNIX
        
        self.play_icon_entry = ICON_FOOBNIX_PLAY
        self.pause_icon_entry = ICON_FOOBNIX_PAUSE
        self.stop_icon_entry = ICON_FOOBNIX_STOP
        self.radio_icon_entry = ICON_FOOBNIX_RADIO
        
        """Notification"""
        self.notifier = True
        self.notify_time = 3000
               
        """download manager controls"""
        self.auto_start_donwload = True
        self.max_active_count = 3
        self.online_save_to_folder = "/tmp"
        self.automatic_online_save = False
        self.is_save_online = True
        
        """info panel"""
        self.info_panel_image_size = 150
        self.tooltip_image_size = 150
        self.is_info_panel_show_tags = False
        
        self.check_new_version = True

        self.last_dir = None
        
        self.proxy_enable = False
        self.proxy_url = None
        self.proxy_user = None
        self.proxy_password = None
        
        self.action_hotkey = {'foobnix --volume-up': '<SUPER>Up', 'foobnix --volume-down': '<SUPER>Down', 'foobnix --show-hide': '<SUPER>a', 'foobnix --prev': '<SUPER>Left', 'foobnix --play': '<SUPER>x', 'foobnix --pause': '<SUPER>z', 'foobnix --next': '<SUPER>Right'}

        self.left_perspective = "info"        
        
        self.gap_secs = 0
        
        self.tabs_mode = "Multi"#Multi, Single
        
        self.tab_pl_names = [_("Empty tab"), ]
        self.cache_pl_tab_contents = []
        
        self.order_repeat_style = "ToggleButtons"
        
        self.file_managers = ['nautilus', 'dolphin', 'konqueror', 'thunar', 'pcmanfm']
        self.active_manager = [0, ""]
        
        self.covers = {}
         
        self.load();
    
    def save(self):
        FCStates().save(self, CONFIG_FILE)
        FCBase().save()
    
    def load(self):
        FCStates().load(self, CONFIG_FILE)
