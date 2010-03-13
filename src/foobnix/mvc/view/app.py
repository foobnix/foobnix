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
from foobnix.mvc.directory.directory_model import DirectoryModel
from foobnix.mvc.directory.directory_controller import DirectoryCntr
from foobnix.mvc.playlist.playlist_c import PlaylistCntr
from foobnix.mvc.player.player_controller import PlayerController
from foobnix.mvc.player.player_widgets_cntr import PlayerWidgetsCntl

class AppView():
    glade = "foobnix/glade/foobnix.glade"  
    top = "foobnixWindow"

    def __init__(self):
        self.gx = gtk.glade.XML(self.glade, self.top)
        self.window = self.gx.get_widget("foobnixWindow")        
        self.directory = self.gx.get_widget("direcotry_treeview")
        self.playlist = self.gx.get_widget("playlist_treeview")
                

class AppController():   

    def __init__(self, v):
        v.window.connect("destroy", self.onDestroy)
        playerCntr = PlayerController()
        playlistCntr = PlaylistCntr(v.playlist, playerCntr)
        
        playerWidgets = PlayerWidgetsCntl(v.gx, playerCntr)
        playerCntr.registerWidgets(playerWidgets)
        playerCntr.registerPlaylistCntr(playlistCntr)
                
        DirectoryCntr(v.directory, playlistCntr)
        
    def onDestroy(self, *a):
        print "Destroy"
        gtk.main_quit()
    
    pass #end of class                 


    
    
        
                           