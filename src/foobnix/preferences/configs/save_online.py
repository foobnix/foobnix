#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.util.configuration import FConfiguration
from foobnix.util import LOG

class SaveOnlineConfig(ConfigPlugin):
    
    name = _("Online Music")
    
    def __init__(self):
        print "Create try icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        
        hbox = gtk.HBox(False, 0)
        hbox.show()
        
        self.is_save = gtk.CheckButton(label=_("Save online music"), use_underline=True)
        self.is_save.connect("clicked", self.on_save_online)
        self.is_save.show()
        
        self.online_dir = gtk.FileChooserButton("set place")
        self.online_dir.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.online_dir.connect("current-folder-changed", self.on_change_folder)        
        self.online_dir.show()
        
        hbox.pack_start(self.is_save, False, True, 0)
        hbox.pack_start(self.online_dir, True, True, 0)
        
                
        box.pack_start(hbox, False, True, 0)
        
        self.widget = box
        
        
    def on_save_online(self, *a):
        value = self.is_save.get_active()
        if  value:
            self.online_dir.set_sensitive(True)
        else:
            self.online_dir.set_sensitive(False)
                
        FConfiguration().is_save_online = value              
        
    def on_change_folder(self, *a):
        path = self.online_dir.get_filename()       
        FConfiguration().onlineMusicPath = path
        
        LOG.info("Change music online folder", path)  
                
    
    def on_load(self):
        self.is_save.set_active(FConfiguration().is_save_online)
        
        self.online_dir.set_current_folder(FConfiguration().onlineMusicPath)
        self.online_dir.set_sensitive(FConfiguration().is_save_online)
