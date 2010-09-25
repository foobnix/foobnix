import gtk
import time

from foobnix.regui.notetab import NoteTabControl
from foobnix.regui.base_layout import BaseFoobnixLayout
from foobnix.regui.base_controls import BaseFoobnixControls
from foobnix.regui.treeview.musictree import MusicTreeControl
from foobnix.regui.window import MainWindow
class FoobnixCore(BaseFoobnixControls):
    
    def __init__(self):       
        BaseFoobnixControls.__init__(self)

        """elements"""
        self.window = MainWindow(self)
        self.notetabs = NoteTabControl(self)
        self.tree = MusicTreeControl(self)
        
        """layout"""        
        self.layout = BaseFoobnixLayout(self.window,
                                        self.notetabs,
                                        self.tree)
        
init_time = time.time()
eq = FoobnixCore()
print "******Foobnix run in", time.time() - init_time, " seconds******"
gtk.main()
    
