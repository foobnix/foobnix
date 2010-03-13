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
class AppController():   

    def __init__(self, v):
        self.windowController = WindowController(v.gxMain)
        
        playerCntr = PlayerController()
        playlistCntr = PlaylistCntr(v.playlist, playerCntr)
        
        playerWidgets = PlayerWidgetsCntl(v.gxMain, playerCntr)
        playerCntr.registerWidgets(playerWidgets)
        playerCntr.registerPlaylistCntr(playlistCntr)
                
        DirectoryCntr(v.directory, playlistCntr)
        
        TrayIcon(v.gxTryIcon, self.windowController,playerCntr)
        
   
    
    pass #end of class   