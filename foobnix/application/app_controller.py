'''
Created on Mar 14, 2010

@author: ivan
'''
from foobnix.window.wndow_controller import WindowController
from foobnix.player.player_controller import PlayerController
from foobnix.playlist.playlist_controller import PlaylistCntr
from foobnix.player.player_widgets_cntr import PlayerWidgetsCntl
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.tryicon.tryicon_controller import TrayIcon
from foobnix.application.app_load_exit_controller import OnLoadExitAppCntr
from foobnix.application.app_configuration_controller import AppConfigurationCntrl


class AppController():   

    def __init__(self, v):
        
        
        
        playerCntr = PlayerController()
        playlistCntr = PlaylistCntr(v.playlist, playerCntr)
        
        playerWidgets = PlayerWidgetsCntl(v.gxMain, playerCntr)
        playerCntr.registerWidgets(playerWidgets)
        playerCntr.registerPlaylistCntr(playlistCntr)
                
        directoryCntr = DirectoryCntr(v.directory, playlistCntr)
        appConfCntr = AppConfigurationCntrl(v.gxMain, directoryCntr)
        
        windowController = WindowController(v.gxMain)
        
        TrayIcon(v.gxTryIcon, windowController,playerCntr)
        
        loadExit = OnLoadExitAppCntr(playlistCntr, playerWidgets, playerCntr, directoryCntr, appConfCntr)
        windowController.registerOnExitCnrt(loadExit)
        
    
    pass #end of class   