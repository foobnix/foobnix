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
    
    def __init__(self):
        self.gxMain = self.glade_XML(self.gladeMain, "foobnixWindow")
        self.gxTrayIcon = self.glade_XML(self.gladeMain, "popUpWindow")
        self.gxAbout = self.glade_XML(self.gladeMain, "aboutdialog")
        self.about_widget = self.gxAbout.get_widget("aboutdialog")
        self.about_widget.connect("response", lambda * a: self.about_widget.hide())
        self.playlist = self.gxMain.get_widget("playlist_treeview")

    def close_dialog(self):
        pass
        
    def glade_XML(self, main, widget):
        for path in sys.path:
            full_path = os.path.join(path, main)
            if os.path.isfile(full_path):                                    
                return gtk.glade.XML(os.path.join(path, main), widget, "foobnix")
                
        LOG.error("Can't find glade file!!!");
        
        
  
