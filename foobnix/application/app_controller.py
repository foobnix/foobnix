'''
Created on Mar 14, 2010

@author: ivan
'''
from foobnix.window.window_controller import WindowController
from foobnix.player.player_controller import PlayerController
from foobnix.playlist.playlist_controller import PlaylistCntr
from foobnix.player.player_widgets_cntr import PlayerWidgetsCntl
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.trayicon import TrayIcon
from foobnix.application.app_load_exit_controller import OnLoadExitAppCntr
from foobnix.application.app_configuration_controller import AppConfigurationCntrl
from foobnix.preferences.pref_controller import PrefController
from foobnix.radio.radio_controller import RadioListCntr
from foobnix.online.online_controller import OnlineListCntr
from foobnix.directory.virtuallist_controller import VirturalLIstCntr
from foobnix.base import BaseController


class AppController(BaseController):   

    def __init__(self, v):
        BaseController.__init__(self)
                
        player_controller = PlayerController()
        playlistCntr = PlaylistCntr(v.playlist, player_controller)
        
        virtualListCntr = VirturalLIstCntr()
        

       
        
        radioListCntr = RadioListCntr(v.gxMain, player_controller)
        
        playerWidgets = PlayerWidgetsCntl(v.gxMain, player_controller)
        player_controller.registerWidgets(playerWidgets)
        player_controller.registerPlaylistCntr(playlistCntr)
        
                
        directoryCntr = DirectoryCntr(v.gxMain, playlistCntr, radioListCntr, virtualListCntr)
        playlistCntr.registerDirectoryCntr(directoryCntr)
        appConfCntr = AppConfigurationCntrl(v.gxMain, directoryCntr)
        
        onlineCntr = OnlineListCntr(v.gxMain, player_controller, directoryCntr, playerWidgets)
        player_controller.registerOnlineCntr(onlineCntr)
        
        prefCntr = PrefController(v.gxPref)
        
        window_controller = WindowController(v.gxMain,v.gxAbout, prefCntr)
        player_controller.registerWindowController(window_controller)
        
        tray_icon = TrayIcon(v.gxTrayIcon)
        tray_icon.connect('toggle_window_visibility', window_controller.toggle_visibility)
        tray_icon.connect('exit',  window_controller.onDestroy)
        tray_icon.connect('play',  player_controller.play)
        tray_icon.connect('pause', player_controller.pause)
        tray_icon.connect('prev',  player_controller.prev)
        tray_icon.connect('next',  player_controller.next)
        tray_icon.connect('volume_up',    player_controller.volume_up)
        tray_icon.connect('volume_down',  player_controller.volume_down)
        player_controller.registerTrayIcon(tray_icon)
        
        loadExit = OnLoadExitAppCntr(playlistCntr, playerWidgets, player_controller, directoryCntr, appConfCntr, radioListCntr, virtualListCntr)
        window_controller.registerOnExitCnrt(loadExit)
        
    
    pass #end of class   
