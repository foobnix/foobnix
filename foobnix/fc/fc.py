#-*- coding: utf-8 -*-
'''
Created on 23 сент. 2010

@author: ivan
'''

import os

from foobnix.util import const
from foobnix.fc.fc_base import FCBase
from foobnix.fc.fc_cache import FCache
from foobnix.util.singleton import Singleton
from foobnix.util.agent import get_ranmom_agent
from foobnix.fc.fc_helper import FCStates, CONFIG_DIR
from foobnix.util.const import ICON_FOOBNIX, ICON_FOOBNIX_PLAY, \
    ICON_FOOBNIX_PAUSE, ICON_FOOBNIX_STOP, ICON_FOOBNIX_RADIO


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
        self.is_view_video_panel = False
        self.is_order_random = False
        self.repeat_state = const.REPEAT_ALL
        self.playlist_type = const.PLAYLIST_TREE

        """player controls"""
        self.volume = 90
        self.temp_volume = self.volume
        self.is_eq_enable = False
        self.eq_presets = None
        self.eq_presets_default = "CUSTOM"

        """VK"""
        self.access_token =  None
        self.user_id =  None
        self.enable_vk_autocomlete = False

        """LastFM"""
        self.search_limit = 50

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

        """selected tabs"""
        self.nav_selected_tab = 0
        self.pl_selected_tab = 0

        self.agent_line = get_ranmom_agent()

        """main window controls"""
        self.main_window_size = [119, 154, 1024, 479]
        self.window_maximized = False
        self.hpaned_left = -1
        self.hpaned_right = 800
        self.hpaned_right_right_side_width = 174 #self.main_window_size[3] - self.hpaned_right
        self.background_image_themes = ["theme/cat.jpg", "theme/flower.jpg", "theme/winter.jpg"]
        self.background_image = None # "theme/winter.jpg"
        self.window_opacity = 1

        """Check network available"""
        self.net_ping = False

        self.menu_style = "new"

        """main window action"""
        self.on_close_window = const.ON_CLOSE_CLOSE

        """support file formats"""
        audio_containers = [".cue", ".iso.wv", ".m3u", ".m3u8"]
        self.audio_formats = [".mp3", ".ogg", ".ape", ".flac", ".wma", ".mpc", ".aiff", ".raw", ".au", ".aac", ".ac3", ".m4a", ".ra", ".m4p", ".wv", ".shn", ".wav"]
        self.all_support_formats = self.audio_formats + audio_containers
        self.all_support_formats.sort()

        self.enable_music_scrobbler = True
        self.enable_radio_scrobbler = True

        """tray icon"""
        self.show_tray_icon = True
        self.hide_on_start = False
        self.static_tray_icon = True
        self.system_icons_dinamic = False
        self.change_tray_icon = False

        self.all_icons = [ICON_FOOBNIX, ICON_FOOBNIX_PLAY, ICON_FOOBNIX_PAUSE, ICON_FOOBNIX_STOP, ICON_FOOBNIX_RADIO, "images/foobnix-tux.gif"]

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
        self.nosubfolder = False
        self.is_save_online = True

        """info panel"""
        self.info_panel_image_size = 150
        self.tooltip_image_size = 150
        self.is_info_panel_show_tags = False

        self.check_new_version = True

        self.last_dir = None

        """proxy"""
        self.proxy_enable = False
        self.proxy_url = None
        self.proxy_user = None
        self.proxy_password = None

        '''Multimedia and hot keys'''
        self.action_hotkey = {'play_pause': '<SUPER>z', 'state_stop': '<SUPER>x', 'volume_up': '<SUPER>Up', 'volume_down': '<SUPER>Down', 'show_hide': '<SUPER>a', 'prev': '<SUPER>Left', 'next': '<SUPER>Right', 'download' : '<Control><SUPER>z'}
        self.multimedia_keys = {'prev': 'XF86AudioPrev', 'next': 'XF86AudioNext', 'play_pause': 'XF86AudioPlay', 'state_stop': 'XF86AudioStop', 'volume_up': 'XF86AudioRaiseVolume', 'volume_down': 'XF86AudioLowerVolume', 'mute': 'XF86AudioMute'}
        self.media_volume_keys = {'volume_up': 'XF86AudioRaiseVolume', 'volume_down': 'XF86AudioLowerVolume', 'mute': 'XF86AudioMute'}
        self.media_keys_enabled = True
        self.media_volume_keys_enabled = False

        self.left_perspective = "info"

        self.gap_secs = 0
        self.network_buffer_size = 128  # kbytes

        self.tabs_mode = "Multi" # Multi, Single

        self.order_repeat_style = "ToggleButtons"

        self.file_managers = ['nautilus', 'dolphin', 'konqueror', 'thunar', 'pcmanfm', 'krusader', 'explorer']
        self.active_manager = [0, ""]

        #self.numbering_by_order = True

        '''columns configuration'''
        '''for playlists'''
        """translations of key words must match exactly with the translations of column.key names in PlaylistTreeControl"""
        self.columns = {'*': [True, 0, 40], 'N': [True, 1, 35], 'Composer': [False, 2, 80], 'Artist': [False, 3, 90], 'Title': [False, 4, 70], 'Track': [True, 5, 450], 'Time': [True, 6, 50], "Album": [False, 7, 90], 'Year': [False, 8, 50]}

        '''for navigation tree'''
        self.show_full_filename = False

        self.antiscreensaver = False

        self.is_my_radio_active = False

        self.load()

    def delete(self):
        FCStates().delete(CONFIG_FILE)

    def save(self):
        FCStates().save(self, CONFIG_FILE)
        FCBase().save()
        FCache().save()

    def load(self):
        FCStates().load(self, CONFIG_FILE)
