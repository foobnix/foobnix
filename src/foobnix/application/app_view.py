'''
Created on Mar 14, 2010

@author: ivan
'''
import gtk.glade
import sys
from foobnix.util import LOG
import os
class AppView():

    gladeMain = "foobnix/glade/foobnix.glade"
    gladePref = "foobnix/glade/preferences.glade"
    
    
    
    
    def __init__(self):
        self.gxMain = self.glade_XML(self.gladeMain, "foobnixWindow")
        self.gxTrayIcon = self.glade_XML(self.gladeMain, "popUpWindow")
        self.gxPref = self.glade_XML(self.gladePref, "window")
        self.gxAbout = self.glade_XML(self.gladeMain, "aboutdialog")
        self.about_widget = self.gxAbout.get_widget("aboutdialog")
        self.about_widget.connect("response", lambda * a: self.about_widget.hide())
                
        
        self.playlist = self.gxMain.get_widget("playlist_treeview")

    def close_dialog(self):
        pass
        
    def glade_XML(self, main, widget):
        domain = "foobnix"
        try:            
            return gtk.glade.XML(main, widget, domain)
        except:
            pass
        
        for path in sys.path:
            full_path = os.path.join(path, main)
            if os.path.isfile(full_path) and (path.endswith("dist-packages") or path.endswith("site-packages")):
                try:
                    LOG.info("Find glade in", full_path)                    
                    return gtk.glade.XML(os.path.join(path, main), widget, domain)
                except:
                    LOG.warn("Can't find glade file in", path);
                    pass
                
        LOG.error("Can't find glade file!!!");
        
        
  
