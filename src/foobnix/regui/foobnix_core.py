import gtk
import time

from foobnix.regui.notetab import NoteTabControl
from foobnix.regui.base_layout import BaseFoobnixLayout
from foobnix.regui.base_controls import BaseFoobnixControls
from foobnix.regui.treeview.musictree import MusicTreeControl
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
from foobnix.regui.treeview.radiotree import RadioTreeControl
from foobnix.regui.treeview.virtualtree import VirtualTreeControl
from foobnix.regui.controls.tray_icon import TrayIconControls
from foobnix.preferences.preferences_window import PreferencesWindow
from foobnix.regui import controls
from foobnix.regui.top import TopWidgets
class FoobnixCore(BaseFoobnixControls):

    def __init__(self):
        BaseFoobnixControls.__init__(self)

        """elements"""
        self.preferences = PreferencesWindow(self)
        self.statusbar = StatusbarControls(self)
        self.volume = VolumeControls(self)
        self.seek_bar = SeekProgressBarControls(self)

        self.media_engine = GStreamerEngine(self)
        self.search_progress = SearchProgressBar(self)

        self.info_panel = InfoPanelWidget(self)

        self.trayicon = TrayIconControls(self)
        self.trayicon.show()

        self.searchPanel = SearchControls(self)
        self.playback = PlaybackControls(self)
        self.main_window = MainWindow(self)
        self.notetabs = NoteTabControl(self)

        self.filter = FilterControl(self)

        self.tree = MusicTreeControl(self)
        self.radio = RadioTreeControl(self)
        self.virtual = VirtualTreeControl(self)

        """layout panels"""
        self.top_panel = TopWidgets(self)

        """layout"""
        self.layout = BaseFoobnixLayout(self)

        self.on_load()
