import gtk
import sys
from foobnix.regui.menu import MenuWidget
class Base():
    
    def menu(self):
               
       
        
        file_item = gtk.MenuItem("File")
        file_item.show()
        
        menu = gtk.Menu()
        menu.show()
        
        sub = gtk.MenuItem("sub")
        sub.show()
        menu.append(sub)
        #menu.append(view_item)
        #menu.append(playback_item)
        #menu.append(help_item)
        
        
        file_item.set_submenu(menu)
        
        view_item = gtk.MenuItem("View")
        view_item.show()
        
        playback_item = gtk.MenuItem("Playback")
        playback_item.show()
        
        help_item = gtk.MenuItem("Help")
        help_item.show()
        
        
        
        
        menu_bar = gtk.MenuBar()
        menu_bar.show()
        
        menu_bar.append (file_item)
        menu_bar.append (view_item)
        menu_bar.append (playback_item)
        menu_bar.append (help_item)
        

        return menu_bar
    
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Foobnix")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.connect("destroy", lambda *a:sys.exit(1))
        
        vbox = gtk.VBox(False, 0)
        vbox.show()
        
        hbox = gtk.HBox(False, 0)
        hbox.show()
        menu = MenuWidget().widget
        hbox.pack_start(menu, False, False)
        
        vbox.pack_start(hbox, False, False)
        
        button = gtk.Button("asdf")
        button.show()
        vbox.pack_start(button, False, False)
        
        self.window.add(vbox)
        self.window.show()
        self.window.set_size_request(400,300)
        
        #self.window.set_size_request(400,250)
        
        gtk.main()


eq = Base()
gtk.main()