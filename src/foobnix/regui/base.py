import gtk
from foobnix.regui.top import TopWidgets
from foobnix.regui.controls import StatusbarControls
from foobnix.regui.left import LeftWidgets
import time
from foobnix.regui.search import SearchControls
from foobnix.regui.infopanel import InfoPanelWidget
from foobnix.util.fc import FC
from foobnix.regui.state import LoadSave
from foobnix.regui.notetab import NoteTabControl
from foobnix.regui.base_layout import BaseFoobnixLayout
from foobnix.regui.base_controls import BaseFoobnixControls
from foobnix.regui.treeview.musictree import MusicTreeControl
class Base(LoadSave):
    
    def __init__(self):
        
        controls = BaseFoobnixControls()
        
        notetabs = NoteTabControl(controls)
        tree = MusicTreeControl(controls)
        
        controls.notetabs = notetabs
        controls.tree = tree
        
        
        layout = BaseFoobnixLayout()
        layout.notetabs = notetabs
        layout.tree = tree
                                
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Foobnix Music Player")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(True)
        self.window.connect("destroy", self.on_save)
        self.window.connect("configure-event", self.on_configure_event)
        
        vbox = gtk.VBox(False, 0)
        vbox.show()
        
        self.top = TopWidgets()
        
        
        vbox.pack_start(self.top.widget, False, False)
        
       
        center_box = gtk.VBox(False, 0)
        
        self.hpaned_right = gtk.HPaned()
        
        self.info_panel = InfoPanelWidget()
        
        self.hpaned_right.pack1(child=notetabs, resize=True, shrink=True)
        self.hpaned_right.pack2(child=self.info_panel.widget, resize=True, shrink=True)
               
        
        searchPanel = SearchControls().widget
        
        
        center_box.pack_start(searchPanel, False, False)
        center_box.pack_start(self.hpaned_right, True, True)
        center_box.show_all()
        
        left = LeftWidgets(tree).widget
        
        self.hpaned_left = gtk.HPaned()     
        
        self.hpaned_left.pack1(child=left, resize=True, shrink=True)
        self.hpaned_left.pack2(child=center_box, resize=True, shrink=True)
    
        self.hpaned_left.show_all()
        
        
        
        statusbar = StatusbarControls().widget
        
        vbox.pack_start(self.hpaned_left, True, True)        
        vbox.pack_start(statusbar, False, True)
        self.window.add(vbox)
        
        
        
    
    def on_configure_event(self, w, e):
        FC().main_window_size = [e.x, e.y, e.width, e.height]

    def on_save(self, *a):
        self.top.on_save()
        self.info_panel.on_save()
        
        FC().hpaned_left = self.hpaned_left.get_position()
        FC().hpaned_right = self.hpaned_right.get_position()
        gtk.main_quit()
        FC().save()
    
    def on_load(self):
        self.hpaned_left.set_position(FC().hpaned_left)
        self.hpaned_right.set_position(FC().hpaned_right)
         
        cfg = FC().main_window_size
        if cfg:
            self.window.set_default_size(cfg[2], cfg[3])            
            self.window.move(cfg[0], cfg[1])
            self.window.show()
            
        self.top.on_load()
        self.info_panel.on_load()
        
        

init_time = time.time()
eq = Base()
eq.on_load()
print "******Foobnix run in", time.time() - init_time, " seconds******"
gtk.main()
    
