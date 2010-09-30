#!/usr/bin/env python

# example packbox.py
import gtk
from foobnix.preferences.configs.music_library import MusicLibraryConfig
from foobnix.util.configuration import FConfiguration, get_version
from foobnix.preferences.configs.save_online import SaveOnlineConfig
from foobnix.preferences.configs.last_fm import LastFmConfig
from foobnix.preferences.configs.vk_conf import VkontakteConfig
from foobnix.preferences.configs.tabs import TabsConfig
from foobnix.preferences.configs.info_panel_conf import InfoPagenConfig
from foobnix.preferences.configs.network_conf import NetworkConfig
from foobnix.preferences.configs.notification_conf import NotificationConfig
from foobnix.preferences.configs.tray_icon import TrayIconConfig
from foobnix.preferences.configs.hotkey_conf import HotKeysConfig
import thread
import os
from foobnix.regui.state import LoadSave
from foobnix.regui.model.signal import FControl
from foobnix.util.fc import FC

class PreferencesWindow(FControl, LoadSave):
    
    configs = []
    
    
    
    POS_NAME = 0
    
    def __init__(self, controls):
        FControl.__init__(self, controls)
        
        self.configs.append(MusicLibraryConfig(controls))
        self.configs.append(SaveOnlineConfig(controls))
        self.configs.append(TabsConfig(controls))
        self.configs.append(LastFmConfig(controls))
        self.configs.append(VkontakteConfig(controls))
        self.configs.append(InfoPagenConfig(controls))        
        self.configs.append(TrayIconConfig(controls))
        self.configs.append(NetworkConfig(controls))
        self.configs.append(NotificationConfig(controls))
        self.configs.append(HotKeysConfig(controls))
        
        
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
        self.on_load()
    
    def show(self):
        self.on_load()
        self.window.show() 
        
    def hide(self):
        print "hide preferences"
        self.window.hide()
        #TEMP
        #gtk.main_quit()    
        return True    
    
    def on_load(self):
        for plugin in self.configs:
            plugin.on_load()
    
    def on_save(self):
        for plugin in self.configs:
            plugin.on_save()
        FC().save()
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
        
        button_restore = gtk.Button(_("Restore Defaults"))        
        button_restore.connect("clicked", lambda * a:self.restore_defaults())
        button_restore.show()
        
        
        
        button_save = gtk.Button(_("Save"))
        button_save.set_size_request(100, -1)
        button_save.connect("clicked", lambda * a:self.on_save())
        button_save.show()
        
        button_cancel = gtk.Button(_("Cancel"))
        button_cancel.set_size_request(100, -1)
        button_cancel.connect("clicked", lambda * a:self.hide())
        button_cancel.show()
        
        
        empty = gtk.Label("")
        empty.show()
        
        box.pack_start(button_restore, False, True, 0)
        box.pack_start(empty, True, True, 0)
        box.pack_start(button_save, False, True, 0)        
        box.pack_start(button_cancel, False, True, 0)        
        
        return box

    def restore_defaults(self):
        print "restore defaults"
        gtk.main_quit()
        FConfiguration().remove_cfg_file()        
        thread.start_new_thread(os.system, ("foobnix",))
        
    
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
