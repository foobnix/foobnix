import gtk
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.regui.model.signal import FControl
import logging
from foobnix.util.text_utils import capitalize_query
from foobnix.util.key_utils import is_key_enter

class SearchControls(FControl, gtk.VBox):
    def __init__(self, controls):        
        gtk.VBox.__init__(self, False, 0)
        FControl.__init__(self, controls)
        self.controls = controls
        
        label = gtk.Label()
        label.set_markup("<b>%s:</b>" % _("Search music online"))
        #self.set_label_widget(label)
        #self.set_border_width(0)
        
        """default search function"""
        self.search_function = self.controls.search_top_tracks
        self.buttons = []
                
        
        self.pack_start(self.search_line(), False, False, 0)
                
        #self.pack_start(controls.search_progress, False, False, 0)
        
        self.show_all()
        """search on enter"""
        for button in self.buttons:
            button.connect("key-press-event", self.on_search_key_press)
        
        """only one button active"""    
        OneActiveToggledButton(self.buttons)
        
    
    def set_search_function(self, search_function):
        logging.info("Set search function" + str(search_function))
        self.search_function = search_function    
        
    
    def on_search(self, *w):
        if self.get_query():
            if self.get_query().startswith("http://vk"):
                self.controls.search_vk_page_tracks(self.get_query())                
            else:
                self.search_function(self.get_query())
    
    def get_query(self):
        query = self.entry.get_text()
        return capitalize_query(query)
        
    def search_line(self):
        self.entry = gtk.Entry()
        online_text = _("Online Music Search, Play, Download")        
        
        def on_activate():
            logging.debug("on_activate" + self.entry.get_text())
            if online_text == self.entry.get_text():
                self.entry.set_text("")
            
        self.entry.connect("button-press-event", lambda * a:on_activate())
        self.entry.connect("key-press-event", self.on_search_key_press)
        
        self.entry.set_text(online_text)
               
        combobox = self.combobox_creator()
        
        search_button = gtk.Button(_("Search"))
        search_button.connect("clicked", self.on_search)
        
        hbox = gtk.HBox(False, 0)
        searchLable = gtk.Label()
        searchLable.set_markup("<b>%s</b>" % _("Online Search"))
        
        hbox.pack_start(self.controls.search_progress, False, False)
        
        hbox.pack_start(combobox, False, False)        
        hbox.pack_start(self.entry, True, True)
        hbox.pack_start(search_button, False, False)
        hbox.show_all()
        
        return hbox 
    
    def set_search_text(self, text):
        self.entry.set_text(text)
    
    def on_search_key_press(self, w, e):
        if is_key_enter(e):
            self.on_search();
            self.entry.grab_focus()
    
    def combobox_creator(self):
        list_func = []
        liststore = gtk.ListStore(str)
        
        
        liststore.append([_("Tracks")])
        list_func.append(self.controls.search_top_tracks)
        

        liststore.append([_("Albums")])
        list_func.append(self.controls.search_top_albums)
        
        liststore.append([_("Similar")])
        list_func.append(self.controls.search_top_similar)
        
        liststore.append([_("Genre")])
        list_func.append(self.controls.search_top_tags)
        
        
        liststore.append([_("Audio")])
        list_func.append(self.controls.search_all_tracks)
        
        #liststore.append([_("Video")])
        #list_func.append(self.controls.search_all_videos)
               
        combobox = gtk.ComboBox(liststore)
        cell = gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 0)
        combobox.set_active(0)
        self.set_search_function(list_func[0])
        
        def on_changed(combobox):
            n = combobox.get_active()
            self.set_search_function(list_func[n])
            self.entry.grab_focus()
        
        combobox.connect("changed", on_changed)     
        return combobox
        
    def show_menu(self, w, event, menu):
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)  
        
        
