#!/usr/bin/env python

# example packbox.py

from foobnix.preferences.configs.try_icon import TryIconConfig
from foobnix.preferences.configs.category_info import CategoryInfoConfig
import gtk
from foobnix.preferences.configs.music_library import MusicLibraryConfig
from foobnix.util.configuration import FConfiguration, get_version
from foobnix.preferences.configs.save_online import SaveOnlineConfig
from foobnix.preferences.configs.last_fm import LastFmConfig
from foobnix.preferences.configs.vk_conf import VkontakteConfig
from foobnix.preferences.configs.tabs import TabsConfig

class PreferencesWindow:
    configs = []
    
    
    
    POS_NAME = 0
    
    def __init__(self, directory_controller, online_controller):
        
        self.configs.append(MusicLibraryConfig(directory_controller))
        self.configs.append(SaveOnlineConfig())
        self.configs.append(TabsConfig(online_controller))
        self.configs.append(LastFmConfig())
        self.configs.append(VkontakteConfig())
        
        #self.configs.append(TryIconConfig())
        #self.configs.append(CategoryInfoConfig())
        
        self.label = None
        
        mainVBox = gtk.VBox(False, 0)
        
        
        self.window = self.craete_window()        
        
        paned = gtk.HPaned()
        paned.set_position(200)
        paned.show()
        
        paned.add1(self.create_left_menu())
        
        cbox = gtk.VBox(False, 0)
        cbox.show()
        for plugin in self.configs:
            cbox.pack_start(plugin.widget, False, True, 0)
        
        cbox.show()
                
        self.container = self.create_container(cbox)
        paned.add2(self.container)
                
                
        
        mainVBox.pack_start(paned, True, True, 0)        
        mainVBox.pack_start(self.create_save_cancel_buttons(), False, False, 0)
        
        mainVBox.show()
        
        self.window.add(mainVBox)        
        #self.show()
        
        self.populate_config_category(self.configs[0].name)
        self.load()
    
    def show(self):
        self.load()
        self.window.show() 
        
    def hide(self):
        print "hide preferences"
        self.window.hide()
        #TEMP
        #gtk.main_quit()    
        return True    
    
    def load(self):
        for plugin in self.configs:
            plugin.on_load()
    
    def save(self):
        for plugin in self.configs:
            plugin.on_save()
        FConfiguration().save()
        self.hide()
        
        
    
    def craete_window(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        
        window.connect("delete-event", lambda * a: self.hide())
        window.connect("destroy", lambda * a: self.hide())
        
        window.set_border_width(10)

        window.set_title("Foobnix " + get_version() + " - " + _  ("Preferences"))
        window.set_resizable(False)
        window.set_position(gtk.WIN_POS_CENTER_ALWAYS)  
        
        window.set_size_request(800, 500)
        return window

    
    def create_left_menu(self):
        model = gtk.ListStore(str)
        
        for plugin in self.configs:
            model.append([plugin.name])
        
        treeview = gtk.TreeView()
        
        column_name = gtk.TreeViewColumn(_("Categories"), gtk.CellRendererText(), text=self.POS_NAME)
        treeview.append_column(column_name)
        
        treeview.set_model(model)
        treeview.connect("cursor-changed", self.on_change_category)
        
        treeview.show()
        return treeview
    
    def populate_config_category(self, name):
        for plugin in self.configs:
            if plugin.name == name:
                plugin.show()
                self.update_label(name)
            else:
                plugin.hide()
    
    def on_change_category(self, w):
        selection = w.get_selection()
        model, selected = selection.get_selected()
        if selected:
            name = model.get_value(selected, self.POS_NAME)
            self.populate_config_category(name)
            
    
    def create_save_cancel_buttons(self):
        box = gtk.HBox(False, 0)
        box.show()
        
        button_save = gtk.Button(_("Save"))
        button_save.set_size_request(100, -1)
        button_save.connect("clicked", lambda * a:self.save())
        button_save.show()
        
        button_cancel = gtk.Button(_("Cancel"))
        button_cancel.set_size_request(100, -1)
        button_cancel.connect("clicked", lambda * a:self.hide())
        button_cancel.show()
        
        
        empty = gtk.Label("")
        empty.show()
        
        box.pack_start(empty, True, True, 0)
        box.pack_start(button_save, False, True, 0)        
        box.pack_start(button_cancel, False, True, 0)        
        
        return box   
    
    def update_label(self, title):
        self.label.set_markup('<b><i><span  size="x-large" >' + title + '</span></i></b>');
    
    def create_container(self, widget):
        box = gtk.VBox(False, 0)
        box.show()
        
        self.label = gtk.Label()        
        self.label.show()
        
        separator = gtk.HSeparator()
        separator.show()
        
        box.pack_start(self.label, False, True, 0)
        box.pack_start(separator, False, True, 0)
        box.pack_start(widget, False, True, 0)        
        
        return box
        
def main():   
    gtk.main()   
    return 0         

if __name__ == "__main__":    
    w = PreferencesWindow(None, None)
    w.show()    
    main()
