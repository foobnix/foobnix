import gtk
import sys
from foobnix.regui.top import TopWidgets
from foobnix.regui.controls import StatusbarControls
from foobnix.regui.left import LeftWidgets
import time
from foobnix.regui.search import SearchControls
from foobnix.regui.infopanel import InfoPanelWidget
from foobnix.regui.notebook import NotebookControls
from foobnix.util.fc import FC
from foobnix.regui.state import LoadSave
class Base(LoadSave):
    
    def __init__(self):
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
        
        leftPaned = gtk.HPaned()
        
        leftPaned.pack1(child=NotebookControls().widget, resize=True, shrink=True)
        leftPaned.pack2(child=InfoPanelWidget().widget, resize=True, shrink=True)
               
        
        searchPanel = SearchControls().widget
        
        
        center_box.pack_start(searchPanel, False, False)
        center_box.pack_start(leftPaned, True, True)
        center_box.show_all()
        
        left = LeftWidgets().widget
        
        hpaned = gtk.HPaned()
        #hpaned.add1(left)
        #hpaned.add2(space)
        
        hpaned.pack1(child=left, resize=True, shrink=True)
        hpaned.pack2(child=center_box, resize=True, shrink=True)
    
        hpaned.show_all()
        
        
        
        statusbar = StatusbarControls().widget
        
        vbox.pack_start(hpaned, True, True)        
        vbox.pack_start(statusbar, False, True)
        
        self.window.add(vbox)
        self.window.show()
        
        self.main_window_size = None
        
    
    def on_configure_event(self, w, e):
        self.main_window_size = [e.x, e.y, e.width, e.height]
    
    def on_save(self, *a):
        self.top.on_save()
        FC().main_window_size = self.main_window_size
                        
        gtk.main_quit()
        FC().save()
    
    def on_load(self):
        cfg = FC().main_window_size
        print "CFG", cfg
        FC().info()        
        if cfg:
            self.window.move(cfg[0], cfg[1])
            self.window.set_default_size(cfg[2], cfg[3])
            
        self.top.on_load()
        
        

init_time = time.time()
eq = Base()
eq.on_load()
print "******Foobnix run in", time.time() - init_time, " seconds******"
gtk.main()
    
