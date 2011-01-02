import gtk
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.regui.model.signal import FControl
from foobnix.util import LOG
from foobnix.util.text_utils import capitilize_query
from foobnix.util.key_utils import is_key

class SearchControls(FControl, gtk.Frame):
    def __init__(self, controls):        
        gtk.Frame.__init__(self)
        FControl.__init__(self, controls)
        self.controls = controls
        
        label = gtk.Label()
        label.set_markup("<b>%s:</b>" % _("Search music online"))
        self.set_label_widget(label)
        self.set_border_width(0)
        
        """default search function"""
        self.search_function = self.controls.search_top_tracks
        self.buttons = []
                
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.search_line(), False, False, 0)
                
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
        self.entry = gtk.Entry()
        self.entry.connect("key-press-event", self.on_search_key_press)
        
        self.entry.set_text("")
        #button = gtk.Button(_("_Search"))
        #button.connect("clicked", self.on_search)
        
        menu_button = gtk.Button(_("Kinds of search"))
        menu = self.menu_creator()
        #g.set_tooltip_text(_("Set focus on search line (Alt+G) Google :)"))
        menu_button.connect("button-press-event", self.show_menu, menu)
        
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(menu_button, False, False, 0)        
        hbox.pack_start(self.entry, True, True, 0)
        #hbox.pack_start(button, False, False, 0)
        hbox.show_all()
        
        return hbox 
    
    def set_search_text(self, text):
        self.entry.set_text(text)
    
    def on_search_key_press(self, w, e):        
        if is_key(e, 'Return'):
            self.on_search();
            self.entry.grab_focus()
    
    def menu_creator(self):
        menu = gtk.Menu()
        item = gtk.CheckMenuItem(_("Tracks"))
        item.connect("toggled", self.set_search_function, self.controls.search_top_tracks)
        menu.append(item)
        item = gtk.CheckMenuItem(_("_Albums"))
        item.connect("toggled", self.set_search_function, self.controls.search_top_albums)
        menu.append(item)
        item = gtk.CheckMenuItem(_("Similar"))
        item.connect("toggled", self.set_search_function, self.controls.search_top_similar)
        menu.append(item)
        item = gtk.CheckMenuItem(_("Genre"))
        item.connect("toggled", self.set_search_function, self.controls.search_top_tags)
        menu.append(item)
        item = gtk.CheckMenuItem(_("All"))
        item.connect("toggled", self.set_search_function , self.controls.search_all_tracks)
        menu.append(item)
        item = gtk.CheckMenuItem(_("Video"))
        item.connect("toggled", self.set_search_function , self.controls.search_all_videos)
        menu.append(item)
        
        def on_select(selected_item, *a):
            for item in menu:
                item.set_active(False)
             
        for item in menu:
            item.connect("button-press-event", on_select)
        return menu
         
    def show_menu(self, w, event, menu):
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)  
        
        