import gtk
from foobnix.helpers.toggled import OneActiveToggledButton
class SearchControls():
    def __init__(self):
        frame = gtk.Frame()
        label = gtk.Label()
        label.set_markup("<b>Search music online:</b>")
        frame.set_label_widget(label)
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
        top_frame = gtk.Frame()
        label = gtk.Label()
        label.set_markup("<b>Top by artist</b>")
        top_frame.set_label_widget(label)                                
        top_frame.set_shadow_type(gtk.SHADOW_NONE)

        hbox = gtk.HBox(False, 0)
        
        songs = gtk.ToggleButton("Songs")        
        albums = gtk.ToggleButton("Albums")
        similars = gtk.ToggleButton("Similar")
        
        hbox.pack_start(songs, True, True, 0)
        hbox.pack_start(albums, True, True, 0)
        hbox.pack_start(similars, True, True, 0)
        
        top_frame.add(hbox)
        
        """Other searches"""
        other_frame = gtk.Frame()
        label = gtk.Label()
        label.set_markup("<b>Other</b>")
        other_frame.set_label_widget(label)    
        other_frame.set_shadow_type(gtk.SHADOW_NONE)
        hbox = gtk.HBox(False, 0)
        
        tags = gtk.ToggleButton("Tag")        
        all = gtk.ToggleButton("All")
        
        hbox.pack_start(tags, True, True, 0)
        hbox.pack_start(all, True, True, 0)
        
        
        other_frame.add(hbox)
        
        
        h_line_box.pack_start(top_frame, True, True, 0)
        h_line_box.pack_start(other_frame, True, True, 0)
        
        h_line_box.show_all()
        
        OneActiveToggledButton([songs,albums,similars,tags,all])
        
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
            
        
        
        
        
        
        