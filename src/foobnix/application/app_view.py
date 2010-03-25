'''
Created on Mar 14, 2010

@author: ivan
'''
import gtk.glade
class AppView():

    gladeMain = "foobnix/glade/foobnix.glade"
    gladePref = "foobnix/glade/preferences.glade"
    
    def __init__(self):
        self.gxMain = self.glade_XML(self.gladeMain, "foobnixWindow")
        self.gxTryIcon = self.glade_XML(self.gladeMain, "popUpWindow")
        self.gxPref = self.glade_XML(self.gladePref, "window")
                
        
        self.playlist = self.gxMain.get_widget("playlist_treeview")

    def glade_XML(self, main, widget):
        try:
            return gtk.glade.XML(main, widget)
        except:
            try:
                return gtk.glade.XML("/usr/local/lib/python2.6/dist-packages/" + main, widget)
            except:
                return gtk.glade.XML("/usr/lib/python2.5/site-packages/" + main, widget)
            
        
  
