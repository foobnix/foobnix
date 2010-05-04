'''
Created on Mar 14, 2010

@author: ivan
'''
import gtk

from foobnix.window.window_controller import WindowController
from foobnix.player.player_controller import PlayerController
from foobnix.playlist.playlist_controller import PlaylistCntr
from foobnix.player.player_widgets_cntr import PlayerWidgetsCntl
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.trayicon import TrayIcon
from foobnix.application.app_configuration_controller import AppConfigurationCntrl
from foobnix.preferences.pref_controller import PrefController
from foobnix.radio.radio_controller import RadioListCntr
from foobnix.online.online_controller import OnlineListCntr
from foobnix.directory.virtuallist_controller import VirturalLIstCntr
from foobnix.base import BaseController

from foobnix.util.configuration import FConfiguration
from foobnix.online.search_panel import SearchPanel

class AppController(BaseController):

    def __init__(self, v):
        BaseController.__init__(self)
                
        self.player_controller = PlayerController()
        self.playlistCntr = PlaylistCntr(v.playlist, self.player_controller)
        
        self.virtualListCntr = VirturalLIstCntr()
        
        self.radioListCntr = RadioListCntr(v.gxMain, self.player_controller)
        
        self.playerWidgets = PlayerWidgetsCntl(v.gxMain, self.player_controller)
        self.player_controller.registerWidgets(self.playerWidgets)
        self.player_controller.registerPlaylistCntr(self.playlistCntr)
        
        
        self.directoryCntr = DirectoryCntr(v.gxMain, self.playlistCntr, self.radioListCntr, self.virtualListCntr)
        self.playlistCntr.registerDirectoryCntr(self.directoryCntr)
        self.appConfCntr = AppConfigurationCntrl(v.gxMain, self.directoryCntr)
        
        onlineCntr = OnlineListCntr(v.gxMain, self.player_controller, self.directoryCntr)
        self.player_controller.registerOnlineCntr(onlineCntr)
        
        self.preferences_window_controller = PrefController(v.gxPref)
        
        self.main_window_controller = WindowController(v.gxMain, v.gxAbout)
        self.main_window_controller.connect('show_preferences', self.preferences_window_controller.show)
        
        self.tray_icon = TrayIcon(v.gxTrayIcon)
        self.tray_icon.connect('toggle_window_visibility', self.main_window_controller.toggle_visibility)
        self.tray_icon.connect('exit',  self.exit)
        self.tray_icon.connect('play',  self.player_controller.play)
        self.tray_icon.connect('pause', self.player_controller.pause)
        self.tray_icon.connect('prev',  self.player_controller.prev)
        self.tray_icon.connect('next',  self.player_controller.next)
        self.tray_icon.connect('volume_up',    self.player_controller.volume_up)
        self.tray_icon.connect('volume_down',  self.player_controller.volume_down)
        
        self.player_controller.connect('song_playback_started', self.tray_icon.on_song_started)
        self.player_controller.connect('song_playback_started', self.main_window_controller.on_song_started)

        self.main_window_controller.connect('exit', self.exit)
        
        self.search_panel = SearchPanel(v.gxMain)
        self.search_panel.connect('show_search_results', onlineCntr.show_results)
        #self.search_panel.connect('starting_search', onlineCntr.clear)
        
        self.restore_state()
    
    def exit(self, sender):
        self.save_state()
        self.tray_icon.icon.set_visible(False)
        gtk.main_quit()

    def restore_state(self):
        if FConfiguration().playlistState:
            self.playlistCntr.setState(FConfiguration().playlistState)
        
        if FConfiguration().virtualListState:
            self.directoryCntr.setState(FConfiguration().virtualListState)
        
        if FConfiguration().volumeValue:
            self.playerWidgets.volume.set_value(FConfiguration().volumeValue)
            self.player_controller.setVolume(FConfiguration().volumeValue / 100)
        
        if FConfiguration().hpanelPostition:
            self.playerWidgets.hpanel.set_position(FConfiguration().hpanelPostition)
        
        if FConfiguration().hpanel2Postition:
            self.playerWidgets.hpanel2.set_position(FConfiguration().hpanel2Postition)
        
        
        if FConfiguration().vpanelPostition:
            self.playerWidgets.vpanel.set_position(FConfiguration().vpanelPostition)
        
        if FConfiguration().mediaLibraryPath:
            self.appConfCntr.setMusicFolder(FConfiguration().mediaLibraryPath)
        
        if FConfiguration().radiolistState:
            self.radioListCntr.setState(FConfiguration().radiolistState)
        
        self.appConfCntr.setVkLoginPass(FConfiguration().vk_login, FConfiguration().vk_password)
        self.appConfCntr.setLfmLoginPass(FConfiguration().lfm_login, FConfiguration().lfm_password)
        
        if FConfiguration().isPlayOnStart:
            self.player_controller.next()
    
    def save_state(self):
        FConfiguration().playlistState = self.playlistCntr.getState()
        FConfiguration().virtualListState = self.directoryCntr.getState()
        
        FConfiguration().radiolistState = self.radioListCntr.getState()
        
        FConfiguration().volumeValue = self.playerWidgets.volume.get_value()
        FConfiguration().vpanelPostition = self.playerWidgets.vpanel.get_position()
        FConfiguration().hpanelPostition = self.playerWidgets.hpanel.get_position()
        FConfiguration().hpanel2Postition = self.playerWidgets.hpanel2.get_position()
        FConfiguration().mediaLibraryPath = self.appConfCntr.getMusicFolder()
        
        FConfiguration().vk_login = self.appConfCntr.getVkLogin()
        FConfiguration().vk_password = self.appConfCntr.getVkPassword()
        
        FConfiguration().lfm_login = self.appConfCntr.getLfmLogin()
        FConfiguration().lfm_password = self.appConfCntr.getLfmPassword()
        
        FConfiguration().save()

