'''
Created on Mar 14, 2010

@author: ivan
'''
from foobnix.window.window_controller import WindowController
from foobnix.player.player_controller import PlayerController
from foobnix.playlist.playlist_controller import PlaylistCntr
from foobnix.player.player_widgets_cntr import PlayerWidgetsCntl
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.tryicon.tryicon_controller import TrayIcon
from foobnix.application.app_load_exit_controller import OnLoadExitAppCntr
from foobnix.application.app_configuration_controller import AppConfigurationCntrl
from foobnix.preferences.pref_controller import PrefController
from foobnix.radio.radio_controller import RadioListCntr
from foobnix.online.online_controller import OnlineListCntr
from foobnix.directory.virtuallist_controller import VirturalLIstCntr


class AppController():   

    def __init__(self, v):
        
        
        
        playerCntr = PlayerController()
        playlistCntr = PlaylistCntr(v.playlist, playerCntr)
        
        virtualListCntr = VirturalLIstCntr()
        

       
        
        radioListCntr = RadioListCntr(v.gxMain, playerCntr)
        
        playerWidgets = PlayerWidgetsCntl(v.gxMain, playerCntr)
        playerCntr.registerWidgets(playerWidgets)
        playerCntr.registerPlaylistCntr(playlistCntr)
        
                
        directoryCntr = DirectoryCntr(v.gxMain, playlistCntr, radioListCntr, virtualListCntr)
        appConfCntr = AppConfigurationCntrl(v.gxMain, directoryCntr)
        
        onlineCntr = OnlineListCntr(v.gxMain, playerCntr, directoryCntr)
        playerCntr.registerOnlineCntr(onlineCntr)
        
        prefCntr = PrefController(v.gxPref)
        
        windowController = WindowController(v.gxMain, prefCntr)
        playerCntr.registerWindowController(windowController)
        
        TrayIcon(v.gxTryIcon, windowController, playerCntr)
        
        loadExit = OnLoadExitAppCntr(playlistCntr, playerWidgets, playerCntr, directoryCntr, appConfCntr, radioListCntr)
        windowController.registerOnExitCnrt(loadExit)
        
    
    pass #end of class   
