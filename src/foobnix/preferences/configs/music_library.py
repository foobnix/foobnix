#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
from foobnix.preferences.config_plugin import ConfigPlugin
import gtk
from foobnix.base.base_list_controller import BaseListController
from deluge.log import LOG
from foobnix.util.configuration import FConfiguration
class MusicLibraryConfig(ConfigPlugin):
    name = "Music Library"
    enable = True
       
    def __init__(self, directory_controller):
        self.directory_controller = directory_controller
        print self.name
        
        box = gtk.VBox(False, 0)
        box.hide()
 
        box.pack_start(self.dirs(), False, True, 0)
        box.pack_start(self.formats(), False, True, 0)
        
        self.widget = box
    
    
    def dirs(self):
        frame = gtk.Frame(label="Music dirs")
        frame.set_border_width(0)
        frame.show()
        
        frame_box = gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
                
        dir_tree = gtk.TreeView()
        dir_tree.set_size_request(-1, 150)
        dir_tree.show()
        self.tree_controller = BaseListController(dir_tree)
        self.tree_controller.set_title("Path")
        
        
        """reload button"""
        reload_button = gtk.Button("Reload")
        reload_button.show()
        
        
        
        """buttons"""
        button_box = gtk.VBox(False, 0)
        button_box.show()
        
        bt_add = gtk.Button("Add")
        bt_add.connect("clicked", self.add_dir)
        bt_add.set_size_request(80, -1)
        bt_add.show()
        
        bt_remove = gtk.Button("Remove")
        bt_remove.connect("clicked", self.remove_dir)
        bt_remove.set_size_request(80, -1)
        bt_remove.show()
        
        empty = gtk.Label("")        
        empty.show()
        
        bt_reload = gtk.Button(label="Reload")
        bt_reload.connect("clicked", self.reload_dir)
        bt_reload.set_size_request(80, -1)
        bt_reload.show()
        
        
        button_box.pack_start(bt_add, False, False, 0)
        button_box.pack_start(bt_remove, False, False, 0)
        button_box.pack_start(empty, True, True, 0)
        button_box.pack_start(bt_reload, False, False, 0)
        
        
        """
        scrool_tree = gtk.ScrolledWindow()
        scrool_tree.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrool_tree.add_with_viewport(dir_tree)
        scrool_tree.show()
        """
        
        frame_box.pack_start(dir_tree, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)
        
           
                
        
        frame.add(frame_box)
        
        
        
        
        return frame
   
    def reload_dir(self, *a):
        FConfiguration().mediaLibraryPath = self.tree_controller.get_all_items()
        self.directory_controller.updateDirectoryByPath()
   
    def on_load(self):
        for path  in FConfiguration().mediaLibraryPath:
            self.tree_controller.add_item(path)
            
        for ext in FConfiguration().supportTypes:
            self.files_controller.add_item(ext)
   
    def on_save(self):             
        FConfiguration().mediaLibraryPath = self.tree_controller.get_all_items() 
    
    def add_dir(self, *a):
        chooser = gtk.FileChooserDialog(title="Choose directory with music", action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()            
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
        frame = gtk.Frame(label="File Types")
        frame.set_border_width(0)
        frame.show()
        
        frame_box = gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
        dir_tree = gtk.TreeView()
        dir_tree.show()
        self.files_controller = BaseListController(dir_tree)
        self.files_controller.set_title("Extension")
        
        
        """buttons"""
        button_box = gtk.VBox(False, 0)
        button_box.show()
        
        bt_add = gtk.Button("Add")
        bt_add.set_size_request(80, -1)
        bt_add.show()
        
        bt_remove = gtk.Button("Remove")
        bt_remove.set_size_request(80, -1)
        bt_remove.show()
        button_box.pack_start(bt_add, False, False, 0)
        button_box.pack_start(bt_remove, False, False, 0)
        
        
          
        
        scrool_tree = gtk.ScrolledWindow()
        scrool_tree.set_size_request(-1, 200)
        scrool_tree.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrool_tree.add_with_viewport(dir_tree)
        scrool_tree.show()
        
        
        
        frame_box.pack_start(scrool_tree, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)
                
        
        frame.add(frame_box)
        return frame
        
