'''
Created on Mar 9, 2010

@author: ivan
'''
from foobnix.bus.BusController import BusController
from foobnix.gui.MainWindowWidget import WindowWiget, SeekProgressBar
import gtk
from foobnix.dirlist import DirectoryList
from foobnix.playlist import PlayList

class FoobNixPlayer():
    def __init__(self):
                
        busController = BusController()
                
        window = WindowWiget(busController)
        SeekProgressBar(busController)
        DirectoryList(busController)
        PlayList(busController)
        
        
        window.show()
        
        
        
        
        
        
        
if __name__ == "__main__":
    player = FoobNixPlayer()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()

    
