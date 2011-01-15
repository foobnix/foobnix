#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
from foobnix.preferences.config_plugin import ConfigPlugin
import gtk
from foobnix.helpers.dialog_entry import show_entry_dialog
from foobnix.util import LOG
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.preferences.configs import CONFIG_MUSIC_LIBRARY
from foobnix.regui.treeview.simple_tree import  SimpleListTreeControl
from foobnix.regui.model import FDModel
import time
import gobject


class MusicLibraryConfig(ConfigPlugin, FControl):
    name = CONFIG_MUSIC_LIBRARY
    enable = True
       
    def __init__(self, controls):
        FControl.__init__(self, controls)
        
        box = gtk.VBox(False, 0)
        box.hide()
        box.pack_start(self.tabs_mode(), False, True, 0)
        box.pack_start(self.dirs(), False, True, 0)
        box.pack_start(self.formats(), False, True, 0)
        box.pack_start(self.gap(), False, True, 0)
        self.widget = box
    
    
    def dirs(self):
        self.frame = gtk.Frame(label=_("Music dirs"))
        self.frame.set_border_width(0)
        self.frame.show()
        self.frame.set_no_show_all(True)
        frame_box = gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
        
        self.tree_controller = SimpleListTreeControl(_("Paths"), None)
        
        """reload button"""
        reload_button = gtk.Button(_("Reload"))
        reload_button.show()
        
        
        
        """buttons"""
        button_box = gtk.VBox(False, 0)
        button_box.show()
        
        bt_add = gtk.Button(_("Add"))
        bt_add.connect("clicked", self.add_dir)
        bt_add.set_size_request(80, -1)
        bt_add.show()
        
        bt_remove = gtk.Button(_("Remove"))
        bt_remove.connect("clicked", self.remove_dir)
        bt_remove.set_size_request(80, -1)
        bt_remove.show()
        
        empty = gtk.Label("")        
        empty.show()
        
        #bt_reload = gtk.Button(label=_("Reload"))
        #bt_reload.connect("clicked", self.reload_dir)
        #bt_reload.set_size_request(80, -1)
        #bt_reload.show()
                
        button_box.pack_start(bt_add, False, False, 0)
        button_box.pack_start(bt_remove, False, False, 0)
        button_box.pack_start(empty, True, True, 0)
        #button_box.pack_start(bt_reload, False, False, 0)
        
        self.tree_controller.scroll.show_all()
        frame_box.pack_start(self.tree_controller.scroll, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)
                
        self.frame.add(frame_box)
        
        if FC().tabs_mode == "Multi":
            self.frame.hide()       
        return self.frame
   
    def reload_dir(self, *a):
        FC().music_paths[0] = self.tree_controller.get_all_beans_text()
        tree = self.controls.tablib.get_current_tree()
        self.controls.update_music_tree(tree)
   
    def on_load(self):
        self.tree_controller.clear_tree()
        for path in FC().music_paths[0]:
            self.tree_controller.append(FDModel(path))
            
        self.files_controller.clear_tree()
        for ext in FC().all_support_formats:
            self.files_controller.append(FDModel(ext))
            
        self.adjustment.set_value(FC().gap_secs)
        if FC().tabs_mode == "Single":
            self.singletab_button.set_active(True)
            self.controls.tablib.set_show_tabs(False)
                
    def on_save(self):             
        FC().music_paths[0] = self.tree_controller.get_all_beans_text()
        FC().all_support_formats = self.files_controller.get_all_beans_text()
        FC().gap_secs = self.adjustment.get_value()
        if self.singletab_button.get_active():
            for i in xrange(len(FC().music_paths)-1, 0, -1):
                del FC().music_paths[i]
                del FC().cache_music_tree_beans[i]
                del FC().tab_names[i]
                self.controls.tablib.remove_page(i)
            FC().tabs_mode = "Single"
            self.controls.tablib.set_show_tabs(False)
        else:
            FC().tabs_mode = "Multi"
            self.controls.tablib.set_show_tabs(True)
        
    def add_dir(self, *a):
        chooser = gtk.FileChooserDialog(title=_("Choose directory with music"), action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        if FC().last_music_path:
            chooser.set_current_folder(FC().last_music_path)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()
            path = paths[0]  
            FC().last_music_path = path[:path.rfind("/")]          
            for path in paths:            
                if path not in self.tree_controller.get_all_beans_text():
                    self.tree_controller.append(FDModel(path))
            gobject.idle_add(self.reload_dir)
        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()
        
         
    def remove_dir(self, *a):
        self.tree_controller.delete_selected()
    
    def formats(self):
        frame = gtk.Frame(label=_("File Types"))
        frame.set_border_width(0)
        frame.show()
        
        frame_box = gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
        self.files_controller = SimpleListTreeControl(_("Extensions"), None)
                
        """buttons"""
        button_box = gtk.VBox(False, 0)
        button_box.show()
        
        bt_add = gtk.Button(_("Add"))
        bt_add.connect("clicked", self.on_add_file)
        bt_add.set_size_request(80, -1)
        bt_add.show()
        
        bt_remove = gtk.Button(_("Remove"))
        bt_remove.connect("clicked", lambda * a:self.files_controller.remove_selected())
        bt_remove.set_size_request(80, -1)
        bt_remove.show()
        button_box.pack_start(bt_add, False, False, 0)
        button_box.pack_start(bt_remove, False, False, 0)
                
        scrool_tree = gtk.ScrolledWindow()
        scrool_tree.set_size_request(-1, 160)
        scrool_tree.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrool_tree.add_with_viewport(self.files_controller.scroll)
        scrool_tree.show()
          
        frame_box.pack_start(scrool_tree, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)
                        
        frame.add(frame_box)
        
        return frame
    
    def on_add_file(self, *a):
        val = show_entry_dialog(_("Please add audio extension"), _("Extension should be like '.mp3'"))
        if val and val.find(".") >= 0 and len(val) <= 5 and val not in self.files_controller.get_all_beans_text():
            self.files_controller.append(FDModel(val))
        else:
            LOG.info("Can't add your value", val)
            
    def gap(self):
        label = gtk.Label(_("Gap between tracks: "))
                
        self.adjustment = gtk.Adjustment(value=0, lower=0, upper=5, step_incr=0.5)
        
        gap_len = gtk.SpinButton(self.adjustment, climb_rate=0.0, digits=1)
        gap_len.show()
        
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(label, False, False)
        hbox.pack_start(gap_len, False, False)
        hbox.show_all()
        
        return hbox
        
    def tabs_mode(self):
        hbox = gtk.HBox()
        self.multitabs_button = gtk.RadioButton(None, _("Multi tab mode"))
        def on_toggle_multitab(widget, data=None):
            self.frame.hide()
        self.multitabs_button.connect("toggled", on_toggle_multitab)
        hbox.pack_start(self.multitabs_button, True, False)
        
        self.singletab_button = gtk.RadioButton(self.multitabs_button, _("Single tab mode"))
        def on_toggle_singletab(widget, data=None):
            self.frame.show()
        self.singletab_button.connect("toggled", on_toggle_singletab)
        hbox.pack_end(self.singletab_button, True, False)
        return hbox
        
            
        
        
