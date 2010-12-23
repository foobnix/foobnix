#-*- coding: utf-8 -*-
'''
Created on 23 дек. 2010

@author: ivan
'''
import gtk
from foobnix.preferences.config_plugin import ConfigPlugin
from deluge.log import LOG
from foobnix.util.fc import FC
from foobnix.helpers.dialog_entry import info_dialog_with_link_and_donate
from foobnix.helpers.pref_widgets import IconBlock
class OtherConfig(ConfigPlugin):
    
    name = _("Other configs")
    
    def __init__(self, controls):
        self.controls = controls
        box = gtk.VBox(False, 0)
        box.hide()        

        """save to"""
        hbox = gtk.HBox(False, 0)
        
        self.online_dir = gtk.FileChooserButton("set place")
        self.online_dir.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.online_dir.connect("current-folder-changed", self.on_change_folder)        
        self.online_dir.show()
        
        hbox.pack_start(gtk.Label(_("Save music to folder")), False, True, 0)
        hbox.pack_start(self.online_dir, True, True, 0)
        
        """disc cover size"""
        cbox = gtk.HBox(False, 0)
        cbox.show()
        
        tab_label = gtk.Label(_("Disc cover size"))
        tab_label.show()
        
        adjustment = gtk.Adjustment(value=1, lower=100, upper=350, step_incr=20, page_incr=50, page_size=0)
        self.image_size_spin = gtk.SpinButton(adjustment)
        self.image_size_spin.show()
        
        cbox.pack_start(tab_label, False, False, 0)
        cbox.pack_start(self.image_size_spin, False, True, 0)
                
        """notification"""
        self.check_new_version = gtk.CheckButton(label=_("Check for new foobnix release on start"), use_underline=True)
        self.check_new_version.show()
        
        demo = gtk.Button(_("Show new foobnix release avaliable demo dialog"))
        demo.connect("clicked", lambda * a:info_dialog_with_link_and_donate("foobnix [version]"))
        demo.show()
        
        """background image"""
        
        catbox = gtk.HBox(False, 0)
        
        self.bg_image = IconBlock("", controls, FC().background_image, FC().background_image_themes)
        
        self.is_show = gtk.CheckButton(label=_("Enable theme image"), use_underline=True)
        
        def on_change(*a):            
            active = self.is_show.get_active()
            if not active:       
                FC().background_image = None
                print "deactive" 
        
        
        self.is_show.connect("clicked", on_change)
        
        catbox.pack_start(self.is_show, False, True, 0)
        catbox.pack_start(self.bg_image, True, True, 0)
        
        """menu position"""
        pbox = gtk.HBox(False, 0)
        pbox.show()
        
        label = gtk.Label(_("Menu type"))
        
        self.old_style = gtk.RadioButton(None, _("Old Style (Menu Bar)"))
        self.old_style.connect("toggled", self.on_change_menu_type)
        
        self.new_style = gtk.RadioButton(self.old_style, _("New Style (Button)"))
        self.new_style.connect("toggled", self.on_change_menu_type)
        
        
        pbox.pack_start(label, False, False, 0)
        pbox.pack_start(self.new_style, False, True, 0)
        pbox.pack_start(self.old_style, False, False, 0)
        
        
        """packaging"""        
        box.pack_start(hbox, False, True, 0)
        box.pack_start(cbox, False, True, 0)
        box.pack_start(self.check_new_version, False, True, 0)
        box.pack_start(demo, False, False, 0)
        box.pack_start(catbox, False, False, 0)
        box.pack_start(pbox, False, False, 0)
        
        self.widget = box
    
    def on_change_menu_type(self, *a):
        if self.old_style.get_active():
            FC().menu_style = "old"
            
        elif self.new_style.get_active():
            FC().menu_style = "new"
        
        self.controls.top_panel.update_menu_style()
        
        
    def on_change_folder(self, *a):
        path = self.online_dir.get_filename()       
        FC().online_save_to_folder = path        
        LOG.info("Change music online folder", path)  
                
    
    def on_load(self):
        self.online_dir.set_current_folder(FC().online_save_to_folder)
        self.online_dir.set_sensitive(FC().is_save_online)
        
        """disc"""
        self.image_size_spin.set_value(FC().info_panel_image_size)
        
        self.check_new_version.set_active(FC().check_new_version)
        if FC().background_image:
            self.is_show.set_active(True)   
        
        """menu style"""
        if  FC().menu_style == "new":
            self.new_style.set_active(True)        
        else: 
            self.old_style.set_active(True)
    
    def on_save(self):
        if self.is_show.get_active():    
            FC().background_image = self.bg_image.get_active_path()    
        FC().info_panel_image_size = self.image_size_spin.get_value_as_int()
        FC().check_new_version = self.check_new_version.get_active()
        self.controls.change_backgound()
                    
