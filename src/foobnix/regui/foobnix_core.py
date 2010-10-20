#-*- coding: utf-8 -*-

from foobnix.regui.notetab import NoteTabControl
from foobnix.regui.base_layout import BaseFoobnixLayout
from foobnix.regui.base_controls import BaseFoobnixControls
from foobnix.regui.window import MainWindow
from foobnix.regui.controls.filter import FilterControl
from foobnix.regui.controls.playback import PlaybackControls
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
from foobnix.eq.eq_gui import EQContols
from foobnix.regui.controls.dbus_manager import DBusManager
from foobnix.dm.dm_gui import DownloadManager
from foobnix.regui.about.about import AboutWindow
from foobnix.regui.treeview.radio_tree import RadioTreeControl
from foobnix.regui.treeview.virtual_tree import VirtualTreeControl
from foobnix.regui.treeview.navigation_tree import NavigationTreeControl

class FoobnixCore(BaseFoobnixControls):

    def __init__(self):
        BaseFoobnixControls.__init__(self)

        self.media_engine = GStreamerEngine(self)

        """elements"""
        self.preferences = PreferencesWindow(self)
        self.statusbar = StatusbarControls(self)
        self.volume = VolumeControls(self)
        self.seek_bar = SeekProgressBarControls(self)

        self.search_progress = SearchProgressBar(self)

        self.info_panel = InfoPanelWidget(self)

        self.trayicon = TrayIconControls(self)
        self.trayicon.show()

        self.searchPanel = SearchControls(self)
        self.playback = PlaybackControls(self)
        self.main_window = MainWindow(self)
        self.notetabs = NoteTabControl(self)

        self.filter = FilterControl(self)

        self.tree = NavigationTreeControl(self)
        self.radio = RadioTreeControl(self)
        self.virtual = VirtualTreeControl(self)

        self.eq = EQContols(self)
        self.dm = DownloadManager(self)
        self.about = AboutWindow()

        """layout panels"""
        self.top_panel = TopWidgets(self)

        """layout"""
        self.layout = BaseFoobnixLayout(self)

        """D-Bus"""
        self.dbus = DBusManager(self)

        self.on_load()
