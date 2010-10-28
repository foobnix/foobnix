import gtk
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.regui.model.signal import FControl
from foobnix.util import LOG
from foobnix.util.text_utils import capitilize_query
class SearchControls(FControl, gtk.Frame):
    def __init__(self, controls):        
        gtk.Frame.__init__(self)
        FControl.__init__(self, controls)
        self.controls = controls
        
        label = gtk.Label()
        label.set_markup("<b>Search music online:</b>")
        self.set_label_widget(label)
        self.set_border_width(0)
        
        """default search function"""
        self.search_function = self.controls.search_top_tracks
        self.buttons = []
        
        
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.search_line(), False, False, 0)
        vbox.pack_start(self.search_buttons(), False, False, 0)
        
        vbox.pack_start(controls.search_progress, False, False, 0)
           
        self.add(vbox)
        
        self.show_all()
        """search on enter"""
        for button in self.buttons:
            button.connect("key-press-event", self.on_search_key_press)
        
        """only one button active"""    
        OneActiveToggledButton(self.buttons)
        
    
    def set_search_function(self, w, search_function):
        LOG.info("Set search fucntion", search_function)
        self.search_function = search_function    
        
    
    def on_search(self, *w):
        if self.get_query():
            if self.get_query().startswith("http://vk"):
                self.controls.search_vk_page_tracks(self.get_query())                
            else:
                self.search_function(self.get_query())
    
    def get_query(self):
        query = self.entry.get_text()
        return capitilize_query(query)
        
    def search_line(self):
        hbox = gtk.HBox(False, 0)
        
        self.entry = gtk.Entry()
        self.entry.connect("key-press-event", self.on_search_key_press)
        
        self.entry.set_text("Madonna")
        button = gtk.Button("Search")
        button.connect("clicked", self.on_search)
        
        hbox = gtk.HBox(False, 0)
        
        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_start(button, False, False, 0)
        
        hbox.show_all()
        
        return hbox 
    
    def set_search_text(self, text):
        self.entry.set_text(text)
    
    def on_search_key_press(self, w, e):        
        if gtk.gdk.keyval_name(e.keyval) == 'Return':
            self.on_search();
    
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
        songs.set_active(True)
        songs.connect("toggled", self.set_search_function, self.controls.search_top_tracks)
        
        albums = gtk.ToggleButton("Albums")
        albums.connect("toggled", self.set_search_function, self.controls.search_top_albums)        
        
        similars = gtk.ToggleButton("Similar")
        similars.connect("toggled", self.set_search_function, self.controls.search_top_similar)
        
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
        
        tags = gtk.ToggleButton("Genre")        
        tags.connect("toggled", self.set_search_function, self.controls.search_top_tags)
        
        all = gtk.ToggleButton("All")
        all.connect("toggled", self.set_search_function , self.controls.search_all_tracks)
        
        video = gtk.ToggleButton("Video")
        video.connect("toggled", self.set_search_function , self.controls.search_all_videos)
        
        hbox.pack_start(tags, True, True, 0)
        hbox.pack_start(all, True, True, 0)
        hbox.pack_start(video, True, True, 0)
        
        
        other_frame.add(hbox)
        
        
        h_line_box.pack_start(top_frame, True, True, 0)
        h_line_box.pack_start(other_frame, True, True, 0)
        
        h_line_box.show_all()
        
        self.buttons = [songs, albums, similars, tags, all, video]
        return h_line_box
                  
     
   
            
        
        
        
        
        
        
