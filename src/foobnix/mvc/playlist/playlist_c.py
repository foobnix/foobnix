'''
Created on Mar 11, 2010

@author: ivan
'''
from foobnix.mvc.playlist.playlist_m import PlaylistModel, PlaylistBean
import gtk
class PlaylistCntr():
    def __init__(self, widget):
        self.model = PlaylistModel(widget)
        self.model.append(PlaylistBean(gtk.STOCK_GO_FORWARD, "1", "Description", "path", "#F2F2F2"))
        self.model.append(PlaylistBean(None, "12", "Description", "path", "#FFFFE5"))
        
        