#-*- coding: utf-8 -*-
'''
Created on 23 сент. 2010

@author: ivan
'''

import os

from foobnix.util import const
from foobnix.fc.fc_base import FCBase
from foobnix.util.singleton import Singleton
from foobnix.util.agent import get_ranmom_agent
from foobnix.fc.fc_helper import FCStates, CONFIG_DIR
from foobnix.util.const import ICON_FOOBNIX, ICON_FOOBNIX_PLAY, \
    ICON_FOOBNIX_PAUSE, ICON_FOOBNIX_STOP, ICON_FOOBNIX_RADIO
from foobnix.fc.fc_cache import FCache

CONFIG_FILE = os.path.join(CONFIG_DIR , "foobnix.pkl")
#CONFIG_FILE = os.path.join(CONFIG_DIR , "foobnix_winter.pkl")

"""Foobnix player configuration"""
class FC():
    __metaclass__ = Singleton
    
    def __init__(self):
        """init default values"""
        self.is_view_info_panel = True
        self.is_view_search_panel = True
        self.is_view_music_tree_panel = True
        self.is_view_coverlyrics_panel = False
        self.is_view_lyric_panel = True
        self.is_view_video_panel = True
        self.is_order_random = False
        self.repeat_state = const.REPEAT_ALL
        self.playlist_type = const.PLAYLIST_TREE

        """player controls"""
        self.volume = 10
        self.temp_volume = self.volume
        self.is_eq_enable = False
        self.eq_presets = None
        self.eq_presets_default = "CUSTOM"
        #VK
        self.access_token =  None
        self.user_id =  None
        self.vk_user =  None
        self.vk_pass =  None

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
        self.main_window_size = [119, 154, 1024, 479]
        self.hpaned_left = 280;
        self.hpaned_right = 850;
        self.hpaned_right_right_side_width = 174 #self.main_window_size[3] - self.hpaned_right
        self.vpaned_small = 100;
        self.background_image_themes = ["theme/cat.jpg", "theme/flower.jpg", "theme/winter.jpg"]
        self.background_image = None #"theme/winter.jpg"
        self.window_opacity = 1
        
        """Check network available"""
        self.net_ping = False
        
        self.menu_style = "new"

        """main window action"""
        if os.name == 'nt':
            self.on_close_window = const.ON_CLOSE_MINIMIZE
        else:
            self.on_close_window = const.ON_CLOSE_HIDE

        """support file formats"""
                
        audio_container = [".cue", ".iso.wv"]
        self.video_formats = [".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".mov", ".mpg", ".rm", ".swf", ".vob", ".wmv",".mkv",".m4v", ".mp4"] 
        self.audio_formats = [".mp3", ".m3u", ".ogg", ".ape", ".flac", ".wma", ".mpc", ".aiff", ".raw", ".au", ".aac", ".ac3", ".m4a", ".ra", ".m4p", ".wv", ".shn", ".wav"]        
        self.all_support_formats = self.audio_formats + self.video_formats + audio_container
        self.all_support_formats.sort()
        
        self.enable_music_scrobbler = True
        self.enable_radio_scrobbler = True
        """proxy"""
        self.proxy_enable = False
        self.proxy_url = None
        
        self.hide_on_start = False
        
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
        self.amount_dm_threads = 3
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
        
        '''Multimedia and hot keys'''
        self.action_hotkey = {'foobnix --volume-up': '<SUPER>Up', 'foobnix --volume-down': '<SUPER>Down', 'foobnix --show-hide': '<SUPER>a', 'foobnix --prev': '<SUPER>Left', 'foobnix --play': '<SUPER>x', 'foobnix --play-pause': '<SUPER>z', 'foobnix --next': '<SUPER>Right'}
        self.multimedia_keys = {'foobnix --prev': 'XF86AudioPrev', 'foobnix --next': 'XF86AudioNext', 'foobnix --play-pause': 'XF86AudioPlay', 'foobnix --stop': 'XF86AudioStop', 'foobnix --volume-up': 'XF86AudioRaiseVolume', 'foobnix --volume-down': 'XF86AudioLowerVolume', 'foobnix --mute': 'XF86AudioMute'}
        self.media_volume_keys = {'foobnix --volume-up': 'XF86AudioRaiseVolume', 'foobnix --volume-down': 'XF86AudioLowerVolume', 'foobnix --mute': 'XF86AudioMute'}
        
        self.media_keys_enabled = True
        self.media_volume_keys_enabled = True
        
        self.left_perspective = "info" 
        
        self.gap_secs = 0
        
        self.tabs_mode = "Multi"#Multi, Single
        
        self.order_repeat_style = "ToggleButtons"
        
        self.file_managers = ['nautilus', 'dolphin', 'konqueror', 'thunar', 'pcmanfm', 'krusader', 'explorer']
        self.active_manager = [0, ""]
        
        self.numbering_by_order = True
        
        '''columns configuration'''        
        '''for playlists'''
        """translations of key words must match exactly with the translations of column.key names in PlaylistTreeControl"""
        self.columns = {'*': [True, 0, 40], '№': [True, 1, 30], 'Composer': [False, 2, 80], 'Artist': [False, 3, 90], 'Title': [False, 4, 70], 'Track': [True, 5, 450], 'Time': [True, 6, 50], "Album": [False, 7, 90]}         
        
        '''for navigation tree'''
        self.show_full_filename = False
        
        self.antiscreensaver = False
        
        self.is_my_radio_active = False
        
        self.load();
    
    def delete(self):
        FCStates().delete(CONFIG_FILE)
    
    def save(self):
        FCStates().save(self, CONFIG_FILE)
        FCBase().save()
        FCache().save()
    
    def load(self):
        FCStates().load(self, CONFIG_FILE)
