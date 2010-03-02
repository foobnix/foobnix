'''
Created on Feb 26, 2010

@author: ivan
'''
import gtk
import gtk.glade
class GUI:
    def __init__(self):
        self.wTree = gtk.glade.XML("foobnix.glade", "foobnixWindow")
        dic = {
                   "on_mainWindow_destroy" : gtk.main_quit
                   
                   }
        self.wTree.signal_autoconnect(dic)
        

wine = GUI()
gtk.main()