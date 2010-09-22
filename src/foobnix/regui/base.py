import gtk
import sys
from foobnix.regui.top import TopWidgets
from foobnix.regui.controls import StatusbarControls
from foobnix.regui.left import LeftWidgets
import time
class Base():
    
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Foobnix")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(True)
        self.window.connect("destroy", lambda * a:sys.exit(1))
        
        vbox = gtk.VBox(False, 0)
        vbox.show()
        
        top = TopWidgets().widget
        
        
        vbox.pack_start(top, False, False)
        
        space = gtk.Button("hi")
        space.show()
        
        
        
        left = LeftWidgets().widget
        
        hpaned = gtk.HPaned()
        #hpaned.add1(left)
        #hpaned.add2(space)
        
        hpaned.pack1(child=left, resize=True, shrink=True)
        hpaned.pack2(child=space, resize=True, shrink=True)
    
        hpaned.show_all()
        
        
        
        statusbar = StatusbarControls().widget
        
        vbox.pack_start(hpaned, True, True)        
        vbox.pack_start(statusbar, False, True)
        
        self.window.add(vbox)
        self.window.show()
        self.window.set_size_request(400, 300)
        
        #self.window.set_size_request(400,250)


init_time = time.time()
eq = Base()
print "******Foobnix run in", time.time() - init_time, " seconds******"
gtk.main()
    
