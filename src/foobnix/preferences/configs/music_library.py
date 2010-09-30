#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
from foobnix.preferences.config_plugin import ConfigPlugin
import gtk
from foobnix.base.base_list_controller import BaseListController
from foobnix.util.configuration import FConfiguration
from foobnix.helpers.dialog_entry import show_entry_dialog
import foobnix.util.localization 
from foobnix.util import LOG

class MusicLibraryConfig(ConfigPlugin):
    name = _("Music Library")
    enable = True
       
    def __init__(self, controls):
        
        box = gtk.VBox(False, 0)
        box.hide()
        
        
        self.child_button = gtk.CheckButton(label=_("Get music from child folders"), use_underline=True)
        self.child_button.show()
        
 
        box.pack_start(self.dirs(), False, True, 0)
        box.pack_start(self.child_button, False, True, 0)
        box.pack_start(self.formats(), False, True, 0)
        
        self.widget = box
    
    
    def dirs(self):
        frame = gtk.Frame(label=_("Music dirs"))
        frame.set_border_width(0)
        frame.show()
        
        frame_box = gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
                
        dir_tree = gtk.TreeView()
        dir_tree.show()
        self.tree_controller = BaseListController(dir_tree)
        self.tree_controller.set_title(_("Path"))
        
        
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
        
        bt_reload = gtk.Button(label=_("Reload"))
        bt_reload.connect("clicked", self.reload_dir)
        bt_reload.set_size_request(80, -1)
        bt_reload.show()
        
        
        button_box.pack_start(bt_add, False, False, 0)
        button_box.pack_start(bt_remove, False, False, 0)
        button_box.pack_start(empty, True, True, 0)
        button_box.pack_start(bt_reload, False, False, 0)
        
        
        
        scrool_tree = gtk.ScrolledWindow()
        scrool_tree.set_size_request(-1, 170)
        scrool_tree.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrool_tree.add_with_viewport(dir_tree)
        scrool_tree.show()
        
        
        frame_box.pack_start(scrool_tree, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)
                
        
        frame.add(frame_box)
        
        
        
        
        return frame
   
    def reload_dir(self, *a):
        FConfiguration().media_library_path = self.tree_controller.get_all_items()
        self.directory_controller.updateDirectoryByPath()
   
    def on_load(self):
        self.tree_controller.clear()
        for path in FConfiguration().media_library_path:
            self.tree_controller.add_item(path)
            
        self.files_controller.clear()
        for ext in FConfiguration().supportTypes:
            self.files_controller.add_item(ext)
            
        self.child_button.set_active(FConfiguration().add_child_folders)
   
    def on_save(self):             
        FConfiguration().media_library_path = self.tree_controller.get_all_items()
        FConfiguration().supportTypes = self.files_controller.get_all_items()
        FConfiguration().add_child_folders = self.child_button.get_active()
         
    
    def add_dir(self, *a):
        chooser = gtk.FileChooserDialog(title=_("Choose directory with music"), action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        if FConfiguration().last_dir:
                chooser.set_current_folder(FConfiguration().last_dir)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()
            path = paths[0]  
            FConfiguration().last_dir = path[:path.rfind("/")]          
            for path in paths:            
                if path not in self.tree_controller.get_all_items():
                    self.tree_controller.add_item(path)
            
        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()
        print "add folder(s)"
    
    def remove_dir(self, *a):
        self.tree_controller.remove_selected()
    
    def formats(self):
        frame = gtk.Frame(label=_("File Types"))
        frame.set_border_width(0)
        frame.show()
        
        frame_box = gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
        dir_tree = gtk.TreeView()
        dir_tree.show()
        self.files_controller = BaseListController(dir_tree)
        self.files_controller.set_title(_("Extension"))
        
        
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
        scrool_tree.add_with_viewport(dir_tree)
        scrool_tree.show()
        
        
        
        frame_box.pack_start(scrool_tree, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)
                
        
        frame.add(frame_box)
        return frame
    
    def on_add_file(self, *a):
        val = show_entry_dialog(_("Please add audio extension"), _("Extension should be like '.mp3'"))
        if val and val.find(".") >= 0 and len(val) <= 5 and val not in self.files_controller.get_all_items():
            self.files_controller.add_item(val)
        else:
            LOG.info("Can't add your value", val)
        
