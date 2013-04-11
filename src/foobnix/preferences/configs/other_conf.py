#-*- coding: utf-8 -*-
'''
Created on 23 дек. 2010

@author: ivan
'''

from gi.repository import Gtk
import logging

from foobnix.preferences.config_plugin import ConfigPlugin
from foobnix.fc.fc import FC
from foobnix.helpers.dialog_entry import info_dialog_with_link_and_donate
from foobnix.helpers.pref_widgets import IconBlock
from foobnix.preferences.configs import CONFIG_OTHER
from foobnix.util.antiscreensaver import antiscreensaver

class OtherConfig(ConfigPlugin):
    
    name = CONFIG_OTHER
    
    def __init__(self, controls):
        self.controls = controls
                
        box = Gtk.VBox(False, 0)
        box.hide()        

        """save to"""
        hbox = Gtk.HBox(False, 5)
        
        self.online_dir = Gtk.FileChooserButton("set place")
        self.online_dir.set_action(Gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.online_dir.connect("current-folder-changed", self.on_change_folder)        
        self.online_dir.show()
        
        hbox.pack_start(Gtk.Label(_("Save online music to folder:")), False, True, 0)
        hbox.pack_start(self.online_dir, True, True, 0)
        
        """automatic save"""                
        self.automatic_save_checkbutton = Gtk.CheckButton(label=_("Automatic online music save"), use_underline=True)

        self.nosubfolder_checkbutton = Gtk.CheckButton(label=_("Save to one folder (no subfolders)"), use_underline=True)

        """download threads"""
        thbox = Gtk.HBox(False, 5)
                
        tab_label = Gtk.Label(_("Download in threads"))
        tab_label.show()
        
        adjustment = Gtk.Adjustment(value=1, lower=1, upper=10, step_incr=1, page_incr=1, page_size=0)
        self.threads_count = Gtk.SpinButton(adjustment=adjustment)
        self.threads_count.show()
        
        thbox.pack_start(tab_label, False, False, 0)
        thbox.pack_start(self.threads_count, False, True, 0)
              
        """disc cover size"""
        cbox = Gtk.HBox(False, 5)
        cbox.show()
        
        tab_label = Gtk.Label(_("Disc cover size:"))
        tab_label.show()
        
        adjustment = Gtk.Adjustment(value=1, lower=100, upper=350, step_incr=20, page_incr=50, page_size=0)
        self.image_size_spin = Gtk.SpinButton(adjustment=adjustment)
        self.image_size_spin.show()
        
        cbox.pack_start(tab_label, False, False, 0)
        cbox.pack_start(self.image_size_spin, False, True, 0)
                
        """notification"""
        self.check_new_version = Gtk.CheckButton(label=_("Check for new foobnix release on start"), use_underline=True)
        self.check_new_version.show()

        demo = Gtk.Button(_("Show new foobnix release avaliable demo dialog"))
        demo.connect("clicked", lambda * a: info_dialog_with_link_and_donate("foobnix [version]"))
        demo.show()
        
        """background image"""
        
        catbox = Gtk.HBox(False, 5)
        
        self.bg_image = IconBlock("", controls, FC().background_image, FC().background_image_themes)
        
        self.is_show = Gtk.CheckButton(label=_("Enable theme image"), use_underline=True)
        
        catbox.pack_start(self.is_show, False, True, 0)
        catbox.pack_start(self.bg_image, True, True, 0)
        
        """menu position"""
        pbox = Gtk.HBox(False, 5)
        pbox.show()
        
        label = Gtk.Label(_("Menu type: "))
        
        self.old_style = Gtk.RadioButton(None, _("Old Style (Menu Bar)"))
                
        self.new_style = Gtk.RadioButton(self.old_style, _("New Style (Button)"))
        
        pbox.pack_start(label, False, False, 0)
        pbox.pack_start(self.new_style, False, True, 0)
        pbox.pack_start(self.old_style, False, False, 0)
        
        o_r_box = Gtk.HBox(False, 5)
        o_r_box.show()
        
        o_r_label = Gtk.Label(_("Order-Repeat Switcher Style:"))
        
        self.buttons = Gtk.RadioButton(None, _("Toggle Buttons"))
        
        self.labels = Gtk.RadioButton(self.buttons, _("Text Labels"))
        
        o_r_box.pack_start(o_r_label, False, False, 0)
        o_r_box.pack_start(self.buttons, False, True, 0)
        o_r_box.pack_start(self.labels, False, False, 0)
        
        """opacity"""
        obox = Gtk.HBox(False, 5)
        obox.show()
        
        tab_label = Gtk.Label(_("Opacity:"))
        tab_label.show()
          
        adjustment = Gtk.Adjustment(value=1, lower=20, upper=100, step_incr=1, page_incr=1, page_size=0)
        self.opacity_size = Gtk.SpinButton(adjustment=adjustment)
        self.opacity_size.connect("value-changed", self.on_chage_opacity)
        self.opacity_size.show()
        
        obox.pack_start(tab_label, False, False, 0)
        obox.pack_start(self.opacity_size, False, True, 0)
        
        self.fmgrs_combo = self.fmgr_combobox()
        hcombobox = Gtk.HBox(False, 5)
        hcombobox.pack_start(Gtk.Label(_('Choose your preferred file manager:')), False, False, 0)
        hcombobox.pack_start(self.fmgrs_combo, False, False, 0)
        
        self.disable_screensaver = Gtk.CheckButton(label=_("Disable Xscreensaver"), use_underline=True)
                
        """packaging"""        
        box.pack_start(hbox, False, True, 0)
        box.pack_start(self.automatic_save_checkbutton, False, True, 0)
        box.pack_start(self.nosubfolder_checkbutton, False, True, 0)
        box.pack_start(thbox, False, True, 0)
        box.pack_start(cbox, False, True, 0)
        box.pack_start(self.check_new_version, False, True, 0)
        box.pack_start(demo, False, False, 0)
        box.pack_start(catbox, False, False, 0)
        box.pack_start(pbox, False, False, 0)
        box.pack_start(o_r_box, False, False, 0)
        box.pack_start(obox, False, False, 0)
        box.pack_start(hcombobox, False, False, 0)
        box.pack_start(self.disable_screensaver, False, False, 0)
        
        self.widget = box
    
    def on_chage_opacity(self, *a):
        opacity = self.opacity_size.get_value() / 100
        self.controls.main_window.set_opacity(opacity)
        self.controls.preferences.set_opacity(opacity)
    
    def on_change_menu_type(self, *a):
        if self.old_style.get_active():
            FC().menu_style = "old"
        elif self.new_style.get_active():
            FC().menu_style = "new"
                
        self.controls.top_panel.update_menu_style()
    
    def on_change_folder(self, *a):
        path = self.online_dir.get_filename()       
        FC().online_save_to_folder = path        
        logging.info("Change music online folder: " + path)  
                
    def on_load(self):
        self.online_dir.set_current_folder(FC().online_save_to_folder)
        self.online_dir.set_sensitive(FC().is_save_online)
        
        """disc"""
        self.image_size_spin.set_value(FC().info_panel_image_size)
        self.threads_count.set_value(FC().amount_dm_threads)
        
        
        self.opacity_size.set_value(int(FC().window_opacity * 100))
        
        self.check_new_version.set_active(FC().check_new_version)
        if FC().background_image:
            self.is_show.set_active(True)   
        
        if FC().automatic_online_save:
            self.automatic_save_checkbutton.set_active(True)

        if FC().nosubfolder:
            self.nosubfolder_checkbutton.set_active(True)

        """menu style"""
        if  FC().menu_style == "new":
            self.new_style.set_active(True)        
        else: 
            self.old_style.set_active(True)
        
        if FC().order_repeat_style == "TextLabels":
            self.labels.set_active(True)
        
        self.fmgrs_combo.set_active(FC().active_manager[0])
        
        if FC().antiscreensaver == True:
            self.disable_screensaver.set_active(True)
            antiscreensaver()
            
    def on_save(self):
        self.is_background_image = FC().background_image
        if self.is_show.get_active():    
            FC().background_image = self.bg_image.get_active_path()
        else:
            FC().background_image = None
                
        if self.buttons.get_active():
            FC().order_repeat_style = "ToggleButtons"
        else:
            FC().order_repeat_style = "TextLabels"
        self.controls.os.on_load()
        
        FC().info_panel_image_size = self.image_size_spin.get_value_as_int()
        FC().amount_dm_threads = self.threads_count.get_value_as_int()
        
        FC().window_opacity = self.opacity_size.get_value() / 100
        FC().check_new_version = self.check_new_version.get_active()
        
        FC().automatic_online_save = self.automatic_save_checkbutton.get_active()
        FC().nosubfolder = self.nosubfolder_checkbutton.get_active()
        
        if self.is_background_image != FC().background_image:
            self.controls.change_backgound()
            self.controls.preferences.hide()            
            self.controls.preferences.show()        
        FC().active_manager = [self.fmgrs_combo.get_active(), self.fmgrs_combo.get_active_text().lower()]
        
        if self.disable_screensaver.get_active():
            FC().antiscreensaver = True
            antiscreensaver()
        else:
            FC().antiscreensaver = False
            
        self.on_change_menu_type()
        
    def fmgr_combobox(self):
        combobox = Gtk.combo_box_new_text()
        combobox.append_text('--- Auto ---')
        combobox.append_text('Nautilus')
        combobox.append_text('Dolphin')
        combobox.append_text('Konqueror')
        combobox.append_text('Thunar')
        combobox.append_text('PCManFM')
        combobox.append_text('Krusader')
        combobox.append_text('Explorer')
        
        combobox.set_active(0)
        
        return combobox
        
