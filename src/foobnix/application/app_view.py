'''
Created on Mar 14, 2010

@author: ivan
'''
import gtk.glade
import sys
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
            try:
                return gtk.glade.XML('/usr/local/lib/python' + sys.version[:3] + '/dist-packages/' + main, widget, domain)
            except:
                return gtk.glade.XML('/usr/lib/python' + sys.version[:3] + '/site-packages/' + main, widget, domain)
            
        
  
