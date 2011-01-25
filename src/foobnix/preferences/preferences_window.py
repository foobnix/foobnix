#!/usr/bin/env python

# example packbox.py
import gtk
from foobnix.preferences.configs.music_library import MusicLibraryConfig
from foobnix.preferences.configs.last_fm import LastFmConfig
from foobnix.preferences.configs.vk_conf import VkontakteConfig
from foobnix.preferences.configs.tabs import TabsConfig
from foobnix.preferences.configs.tray_icon import TrayIconConfig
import thread
import os
from foobnix.regui.state import LoadSave
from foobnix.regui.model.signal import FControl
from foobnix.util.fc import FC
from foobnix.helpers.window import ChildTopWindow
from foobnix.regui.model import FDModel
from foobnix.regui.treeview.simple_tree import SimpleListTreeControl
from foobnix.preferences.configs import CONFIG_MUSIC_LIBRARY
import logging
from foobnix.preferences.configs.other_conf import OtherConfig

class PreferencesWindow(ChildTopWindow, FControl, LoadSave):

    configs = []
    POS_NAME = 0
        
    def __init__(self, controls):
        FControl.__init__(self, controls)
        self.number_inits = 0
    
    def lazy_init(self):
        controls = self.controls
        self.configs.append(MusicLibraryConfig(controls))
        #self.configs.append(DMConfig(controls))
        self.configs.append(TabsConfig(controls))
        self.configs.append(LastFmConfig(controls))
        self.configs.append(VkontakteConfig(controls))        
        #self.configs.append(InfoPagenConfig(controls))
        self.configs.append(TrayIconConfig(controls))
        #self.configs.append(NetworkConfig(controls))
        #self.configs.append(NotificationConfig(controls))
        
        
        try:
            """check keybinder installed, debian"""
            import keybinder #@UnresolvedImport @UnusedImport
            from foobnix.preferences.configs.hotkey_conf import HotKeysConfig
            self.configs.append(HotKeysConfig(controls))
        except Exception, e:
            logging.warn("Keybinder not installed" + str(e)) 
        
        
        self.configs.append(OtherConfig(controls))
        
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
            self.navigation.append(FDModel(plugin.name))
                
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
            
    def show(self, current=CONFIG_MUSIC_LIBRARY):
        if not self.number_inits:
            self.lazy_init()
            self.number_inits += 1
        self.show_all()
        self.populate_config_category(current)
        self.on_load()
    
    def on_load(self):
        logging.debug("LOAD PreferencesWindow")
        for plugin in self.configs:            
            plugin.on_load()

    def on_save(self, hide=False):
        for plugin in self.configs:
            plugin.on_save()
        FC().save()
        if hide:
            self.hide_window()
        else:
            bean = self.navigation.get_selected_bean() 
            self.hide()
            if bean:
                self.populate_config_category(bean.text)
            self.show()
                
                
    def hide_window(self, *a):
        self.hide()
        self.navigation.set_cursor_on_cell(0)
        return True
        
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

        button_restore = gtk.Button(_("Restore Defaults Settings"))
        button_restore.connect("clicked", lambda * a:self.restore_defaults())
        button_restore.show()



        button_apply = gtk.Button(_("Apply"))
        button_apply.set_size_request(100, -1)
        button_apply.connect("clicked", lambda * a:self.on_save())
        button_apply.show()
        
        label = gtk.Label("       ")
        
        button_ok = gtk.Button(_("OK"))
        button_ok.set_size_request(100, -1)
        button_ok.connect("clicked", lambda * a:self.on_save(True))
        button_ok.show()

        button_cancel = gtk.Button(_("Cancel"))
        button_cancel.set_size_request(100, -1)
        button_cancel.connect("clicked", self.hide_window)
        button_cancel.show()
        

        empty = gtk.Label("")
        empty.show()

        box.pack_start(button_restore, False, True, 0)
        box.pack_start(empty, True, True, 0)
        box.pack_start(button_apply, False, True, 0)
        box.pack_start(label, False, True, 0)
        box.pack_start(button_ok, False, True, 0)
        box.pack_start(button_cancel, False, True, 0)

        return box

    def restore_defaults(self):
        logging.debug("restore defaults settings")
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
