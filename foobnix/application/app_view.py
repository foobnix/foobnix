'''
Created on Mar 14, 2010

@author: ivan
'''
import gtk
class AppView():
    gladeMain = "foobnix/glade/foobnix.glade" 
    gladePref = "foobnix/glade/preferences.glade"

    def __init__(self):
        self.gxMain = gtk.glade.XML(self.gladeMain, "foobnixWindow")
        self.gxTryIcon = gtk.glade.XML(self.gladeMain, "popUpWindow")
        self.gxPref = gtk.glade.XML(self.gladePref,"window")
                
        self.directory = self.gxMain.get_widget("direcotry_treeview")
        self.playlist = self.gxMain.get_widget("playlist_treeview")