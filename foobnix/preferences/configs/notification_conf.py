#-*- coding: utf-8 -*-
'''
Created on 3 сент. 2010

@author: ivan
'''
from foobnix.preferences.config_plugin import ConfigPlugin
from gi.repository import Gtk
from foobnix.fc.fc import FC
from foobnix.helpers.dialog_entry import info_dialog_with_link_and_donate
class NotificationConfig(ConfigPlugin):
    
    name = _("Notifications")
    
    def __init__(self, controls):
        box = Gtk.VBox(False, 0)
        box.hide()
        
        self.check_new_version = Gtk.CheckButton(label=_("Check for new foobnix release on start"), use_underline=True)
        self.check_new_version.show()
        
        demo = Gtk.Button(_("Show new foobnix release avaliable demo dialog"))
        demo.connect("clicked", lambda * a:info_dialog_with_link_and_donate("foobnix [version]"))
        demo.show()
        
        
        box.pack_start(self.check_new_version, False, True, 0)
        box.pack_start(demo, False, False, 0)
        
        self.widget = box
    
    def on_load(self):
        self.check_new_version.set_active(FC().check_new_version)
    
    def on_save(self):        
        FC().check_new_version = self.check_new_version.get_active()
        
        
    
    
