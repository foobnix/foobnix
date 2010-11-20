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

class MusicLibraryConfig(ConfigPlugin, FControl):
    name = CONFIG_MUSIC_LIBRARY
    enable = True
       
    def __init__(self, controls):
        FControl.__init__(self, controls)
        
        box = gtk.VBox(False, 0)
        box.hide()
        
        
        #self.child_button = gtk.CheckButton(label=_("Get music from child folders"), use_underline=True)
        #$self.child_button.show()
        
 
        box.pack_start(self.dirs(), False, True, 0)
        #box.pack_start(self.child_button, False, True, 0)
        box.pack_start(self.formats(), False, True, 0)
        
        self.widget = box
    
    
    def dirs(self):
        frame = gtk.Frame(label=_("Music dirs"))
        frame.set_border_width(0)
        frame.show()
        
        frame_box = gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
        
        self.tree_controller = SimpleListTreeControl("Paths", None)
        
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
        
        
        
        
        frame_box.pack_start(self.tree_controller.scroll, True, True, 0)
        frame_box.pack_start(button_box, False, False, 0)
                
        
        frame.add(frame_box)
        
        
        
        
        return frame
   
    def reload_dir(self, *a):
        FC().music_paths = self.tree_controller.get_all_beans_text()
        self.controls.update_music_tree()
   
    def on_load(self):
        self.tree_controller.clear()
        for path in FC().music_paths:
            self.tree_controller.append(FDModel(path))
            
        self.files_controller.clear()
        for ext in FC().support_formats:
            self.files_controller.append(FDModel(ext))
            
    def on_save(self):             
        FC().music_paths = self.tree_controller.get_all_beans_text()
        FC().support_formats = self.files_controller.get_all_beans_text()
        
         
    
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
            
        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()
        print "add folder(s)"
    
    def remove_dir(self, *a):
        self.tree_controller.delete_selected()
    
    def formats(self):
        frame = gtk.Frame(label=_("File Types"))
        frame.set_border_width(0)
        frame.show()
        
        frame_box = gtk.HBox(False, 0)
        frame_box.set_border_width(5)
        frame_box.show()
        
        self.files_controller = SimpleListTreeControl("Extensions", None)
        
        
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
        
