import gtk
import sys
from foobnix.regui.menu import MenuWidget
from foobnix.regui.controls import PlaybackControls, VolumeControls, \
    ToolbarSeparator, SeekProgressBarControls, StatusbarControls
class Base():
    
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Foobnix")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(True)
        self.window.connect("destroy", lambda * a:sys.exit(1))
        
        vbox = gtk.VBox(False, 0)
        vbox.show()
        
        hbox = gtk.HBox(False, 0)
        hbox.show()
        
        menu = MenuWidget().widget
        buttons = PlaybackControls().widget
        volume = VolumeControls().widget
        sep = ToolbarSeparator().widget
        seek = SeekProgressBarControls().widget
        
        hbox.pack_start(menu, False, False)
        hbox.pack_start(buttons, False, False)
        hbox.pack_start(volume, False, False)
        hbox.pack_start(sep, False, False)
        hbox.pack_start(seek, True, True)
        
        vbox.pack_start(hbox, False, False)
        
        space = gtk.Label("")
        space.show()
        
        statusbar = StatusbarControls().widget
        
        vbox.pack_start(space, True, True)        
        vbox.pack_start(statusbar, False, True)
        
        self.window.add(vbox)
        self.window.show()
        self.window.set_size_request(400, 300)
        
        #self.window.set_size_request(400,250)
        
        gtk.main()


eq = Base()
gtk.main()
