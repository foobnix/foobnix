#!/usr/bin/env python

# example packbox.py
import gtk
from foobnix.preferences.configs.music_library import MusicLibraryConfig
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
from foobnix.helpers.window import ChildTopWindow
from foobnix.preferences.configs.dm_config import DMConfig
from foobnix.regui.model import FModel
from foobnix.regui.treeview.simple_tree import SimpleListTreeControl
from foobnix.preferences.configs import CONFIG_MUSIC_LIBRARY

class PreferencesWindow(ChildTopWindow, FControl, LoadSave):

    configs = []
    POS_NAME = 0

    def __init__(self, controls):
        FControl.__init__(self, controls)

        self.configs.append(MusicLibraryConfig(controls))
        self.configs.append(DMConfig(controls))
        self.configs.append(TabsConfig(controls))
        self.configs.append(LastFmConfig(controls))
        self.configs.append(VkontakteConfig(controls))
        self.configs.append(InfoPagenConfig(controls))
        self.configs.append(TrayIconConfig(controls))
        self.configs.append(NetworkConfig(controls))
        self.configs.append(NotificationConfig(controls))
        self.configs.append(HotKeysConfig(controls))
        

        self.label = None

        mainVBox = gtk.VBox(False, 0)

        ChildTopWindow.__init__(self, _("Preferences"), 900, 500)
        

        paned = gtk.HPaned()
        paned.set_position(250)
        
        def func():
            bean = self.navigation.get_selected_bean()            
            if bean:
                self.populate_config_category(bean.text)
        
        self.navigation = SimpleListTreeControl(_("Categories"), controls, True)        
        
        for plugin in self.configs:
            self.navigation.append(FModel(plugin.name))
            
        self.navigation.set_left_click_func(func)

        paned.add1(self.navigation.scroll)

        cbox = gtk.VBox(False, 0)
        for plugin in self.configs:
            cbox.pack_start(plugin.widget, False, True)


        self.container = self.create_container(cbox)
        paned.add2(self.container)

        mainVBox.pack_start(paned, True, True, 0)
        mainVBox.pack_start(self.create_save_cancel_buttons(), False, False, 0)
        
        self.add(mainVBox)
        self.on_load()
        
    
    def show(self, current=CONFIG_MUSIC_LIBRARY):
        self.show_all()
        self.populate_config_category(current)
        self.navigation.set_selected_row()
        
    
    def on_load(self):
        for plugin in self.configs:            
            plugin.on_load()

    def on_save(self):
        for plugin in self.configs:
            plugin.on_save()
        FC().save()
        self.hide()

    def populate_config_category(self, name):
        for plugin in self.configs:
            if plugin.name == name:
                plugin.widget.show()
                self.update_label(name)
            else:
                plugin.widget.hide()

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
        FC().delete()
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

if __name__ == "__main__":
    w = PreferencesWindow(None)    
    w.show()
    gtk.main()
