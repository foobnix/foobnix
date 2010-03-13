'''
Created on Mar 10, 2010

@author: ivan
'''
import gtk.glade

import gobject
import os.path
from foobnix.file_utils import getExtenstion, isDirectory
from foobnix.confguration import FConfiguration
from foobnix.song import Song
from foobnix.util import LOG
from foobnix.directory.directory_model import DirectoryModel
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.playlist.playlist_controller import PlaylistCntr
from foobnix.player.player_controller import PlayerController
from foobnix.player.player_widgets_cntr import PlayerWidgetsCntl
from foobnix.tryicon.tryicon_controller import TrayIcon

class AppView():
    glade = "foobnix/glade/foobnix.glade" 

    def __init__(self):
        self.gxMain = gtk.glade.XML(self.glade, "foobnixWindow")
        self.gxTryIcon = gtk.glade.XML(self.glade, "popUpWindow")
                
        self.directory = self.gxMain.get_widget("direcotry_treeview")
        self.playlist = self.gxMain.get_widget("playlist_treeview")

class WindowController():
    def __init__(self, gx):
        self.window = gx.get_widget("foobnixWindow")
        self.window.connect("destroy", self.onDestroy)
    
    def show(self):
        self.window.show()
    
    def hide(self):
        self.window.hide()
    
    def onDestroy(self, *a):
        print "Destroy"
        gtk.main_quit()                   

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


    
    
        
                           