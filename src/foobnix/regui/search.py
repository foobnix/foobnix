import gtk
class SearchControls():
    def __init__(self):
        frame = gtk.Frame("Online Music Search")
        frame.set_border_width(0)
        
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.search_line(), False, False, 0)
        vbox.pack_start(self.search_buttons(), False, False, 0)
        
        frame.add(vbox)
        
        frame.show_all()
        self.widget = frame
    
    def search_buttons(self):
        h_line_box = gtk.HBox(False, 0)
        
        
        """Top searches"""
        top_frame = gtk.Frame("Top by Artist")
        hbox = gtk.HBox(False, 0)
        
        songs = gtk.ToggleButton("Songs")        
        albums = gtk.ToggleButton("Albums")
        similars = gtk.ToggleButton("Similars")
        
        hbox.pack_start(songs, True, True, 0)
        hbox.pack_start(albums, True, True, 0)
        hbox.pack_start(similars, True, True, 0)
        
        top_frame.add(hbox)
        
        """Other searches"""
        other_frame = gtk.Frame("Other")
        hbox = gtk.HBox(False, 0)
        
        tags = gtk.ToggleButton("Tag")        
        all = gtk.ToggleButton("All")
        
        hbox.pack_start(tags, True, True, 0)
        hbox.pack_start(all, True, True, 0)
        
        
        other_frame.add(hbox)
        
        
        h_line_box.pack_start(top_frame, True, True, 0)
        h_line_box.pack_start(other_frame, True, True, 0)
        
        h_line_box.show_all()
        return h_line_box
                  
     
    def search_line(self):
        hbox = gtk.HBox(False,0)
        
        entry = gtk.Entry()
        button = gtk.Button("Search")
        
        hbox = gtk.HBox(False,0)
        
        hbox.pack_start(entry, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        
        hbox.show_all()
        
        return hbox
            
        
        
        
        
        
        