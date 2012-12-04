#-*- coding: utf-8 -*-
from foobnix.fc.fc import FC
from foobnix.regui.notetab import NoteTabControl
from foobnix.regui.base_layout import BaseFoobnixLayout
from foobnix.regui.base_controls import BaseFoobnixControls
from foobnix.regui.window import MainWindow
from foobnix.regui.controls.filter import FilterControl
from foobnix.regui.controls.playback import PlaybackControls, \
    OrderShuffleControls
from foobnix.regui.search import SearchControls
from foobnix.regui.controls.seach_progress import SearchProgressBar
from foobnix.regui.infopanel import InfoPanelWidget
from foobnix.regui.engine.gstreamer import GStreamerEngine
from foobnix.regui.controls.seekbar import SeekProgressBarControls
from foobnix.regui.controls.volume import VolumeControls
from foobnix.regui.controls.status_bar import StatusbarControls
from foobnix.regui.controls.tray_icon import TrayIconControls
from foobnix.preferences.preferences_window import PreferencesWindow
from foobnix.regui.top import TopWidgets
from foobnix.regui.treeview.radio_tree import RadioTreeControl,\
    MyRadioTreeControl
from foobnix.regui.treeview.virtual_tree import VirtualTreeControl
from foobnix.eq.eq_controller import EqController
from foobnix.dm.dm import DM
from foobnix.regui.controls.movie_area import MovieDrawingArea
from foobnix.util.single_thread import SingleThread
from foobnix.regui.perspectives import PerspectiveControls
from foobnix.util.localization import foobnix_localization
from foobnix.regui.notetab.tab_library import TabHelperControl
from foobnix.regui.service.lastfm_service import LastFmService
from foobnix.regui.treeview.lastfm_integration_tree import LastFmIntegrationControls
from foobnix.regui.treeview.vk_integration_tree import VKIntegrationControls
from foobnix.regui.controls.record import RadioRecord
from foobnix.regui.coverlyrics import CoverLyricsPanel
from foobnix.util.net_wrapper import NetWrapper


foobnix_localization()

class FoobnixCore(BaseFoobnixControls):
    def __init__(self, with_dbus=False):
        BaseFoobnixControls.__init__(self)
        self.layout = None
        
        self.net_wrapper = NetWrapper(self, FC().net_ping)
        
        self.statusbar = StatusbarControls(self)
                
        self.lastfm_service = LastFmService(self)
                
        self.media_engine = GStreamerEngine(self)
        
        """elements"""
        
        self.tabhelper = TabHelperControl(self)
                
        self.volume = VolumeControls(self)
        
        self.record = RadioRecord(self)
        self.seek_bar_movie = SeekProgressBarControls(self)
        self.seek_bar = SeekProgressBarControls(self, self.seek_bar_movie)
        
        self.trayicon = TrayIconControls(self)
        self.main_window = MainWindow(self)
        self.search_progress = SearchProgressBar(self)
        self.in_thread = SingleThread(self.search_progress)
        
        self.info_panel = InfoPanelWidget(self)
                
        self.movie_window = MovieDrawingArea(self)

        self.searchPanel = SearchControls(self)
        self.os = OrderShuffleControls(self)
        self.playback = PlaybackControls(self)
        
        
        
        self.coverlyrics = CoverLyricsPanel(self)
        self.notetabs = NoteTabControl(self)
        
        self.filter = FilterControl(self)

        self.radio = RadioTreeControl(self)
        self.my_radio = MyRadioTreeControl(self)
        self.virtual = VirtualTreeControl(self)
        self.lastfm_integration = LastFmIntegrationControls(self)
        self.vk_integration = VKIntegrationControls(self)
                
        self.perspective = PerspectiveControls(self)
        
        """preferences"""
        self.preferences = PreferencesWindow(self)
        
        self.eq = EqController(self)
        self.dm = DM(self)

        """layout panels"""
        self.top_panel = TopWidgets(self)
                
        """layout"""
        self.layout = BaseFoobnixLayout(self)
        
        if with_dbus:
            from foobnix.regui.controls.dbus_manager import DBusManager
            self.dbus = DBusManager(self)
            try:            
                import keybinder #@UnresolvedImport @UnusedImport
                from foobnix.preferences.configs.hotkey_conf import load_foobnix_hotkeys
                load_foobnix_hotkeys()
            except:
                pass
        
    def run(self):    
        self.on_load()
        if FC().hide_on_start:
            self.main_window.hide()

        