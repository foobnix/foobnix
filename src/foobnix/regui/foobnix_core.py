import gtk
import time

from foobnix.regui.notetab import NoteTabControl
from foobnix.regui.base_layout import BaseFoobnixLayout
from foobnix.regui.base_controls import BaseFoobnixControls
from foobnix.regui.treeview.musictree import MusicTreeControl
from foobnix.regui.window import MainWindow
from foobnix.regui.controls.filter import FilterControl
from foobnix.regui.controls.playback import PlaybackControls
import gobject
from foobnix.regui.search import SearchControls
from foobnix.regui.controls.seach_progress import SearchProgressBar
class FoobnixCore(BaseFoobnixControls):
    
    def __init__(self):       
        BaseFoobnixControls.__init__(self)

        """elements"""
        
        self.search_progress = SearchProgressBar(self)
        
        self.searchPanel = SearchControls(self)   
        self.playback = PlaybackControls(self)     
        self.window = MainWindow(self)
        self.notetabs = NoteTabControl(self)
          
        self.filter = FilterControl(self)
        self.tree = MusicTreeControl(self)
        
        
        
        """layout"""        
        self.layout = BaseFoobnixLayout(self)
        
        self.on_load()
        
init_time = time.time()
gobject.threads_init()
#gtk.gdk.threads_enter()
eq = FoobnixCore()
print "******Foobnix run in", time.time() - init_time, " seconds******"
gtk.main()
    
