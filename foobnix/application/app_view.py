'''
Created on Mar 14, 2010

@author: ivan
'''
import gtk
class AppView():
    glade = "foobnix/glade/foobnix.glade" 

    def __init__(self):
        self.gxMain = gtk.glade.XML(self.glade, "foobnixWindow")
        self.gxTryIcon = gtk.glade.XML(self.glade, "popUpWindow")
                
        self.directory = self.gxMain.get_widget("direcotry_treeview")
        self.playlist = self.gxMain.get_widget("playlist_treeview")