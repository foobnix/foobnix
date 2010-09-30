'''
Created on Sep 7, 2010

@author: ivan
'''
from foobnix.preferences.config_plugin import ConfigPlugin
import gtk
from foobnix.helpers.menu import Popup
from foobnix.util.configuration import FConfiguration
import keybinder
import os
from foobnix.util import LOG
import thread
from foobnix.util.mouse_utils import is_double_left_click
class HotKeysConfig(ConfigPlugin):
    
    name = _("Global Hotkeys")
    
    def __init__(self, controls):
        print "Create try icon conf"
        box = gtk.VBox(False, 0)        
        box.hide()
        
        self.tree_widget = gtk.TreeView()
        self.tree_widget.connect("button-press-event", self.on_populate_click)
        
        self.tree_widget.show()
        self.model = gtk.ListStore(str,str)
        
        self.title = None
        self.column1 = gtk.TreeViewColumn(_("Action"), gtk.CellRendererText(), text=0)
        self.column2 = gtk.TreeViewColumn(_("Hotkey"), gtk.CellRendererText(), text=1)
        self.tree_widget.append_column(self.column1)
        self.tree_widget.append_column(self.column2)        
        self.tree_widget.set_model(self.model)
        
        hbox = gtk.HBox(False, 0)
        hbox.show()
        
        add_button = gtk.Button(_("Add"))      
        add_button.set_size_request(80, -1)
        add_button.connect("clicked", self.on_add_row) 
        add_button.show()
        
        remove_button = gtk.Button(_("Remove"))
        remove_button.connect("clicked", self.on_remove_row)
        remove_button.set_size_request(80, -1)
        remove_button.show()
        
        hbox.pack_start(add_button, False, True, 0)
        hbox.pack_start(remove_button, False, True, 0)
        
        
        
        
        hotbox = gtk.HBox(False, 0)
        hotbox.show()
        
        self.action_text = gtk.Entry()      
        self.action_text.set_size_request(150, -1)
        self.action_text.connect("button-press-event", self.on_mouse_click) 
        self.action_text.show()
        
        self.hotkey_text = gtk.Entry()
        self.hotkey_text.set_editable(False)
        self.hotkey_text.connect("key-press-event", self.on_key_press)
        #self.hotkey_text.connect("key-release-event", self.on_key_release)
        self.hotkey_text.set_size_request(150, -1)
        self.hotkey_text.show()
        
        hotbox.pack_start(self.action_text, False, True, 0)
        hotbox.pack_start(self.hotkey_text, False, True, 0)
        
        
        box.pack_start(self.tree_widget, False, True, 0)
        box.pack_start(hotbox, False, True, 0)
        box.pack_start(hbox, False, True, 0)
        self.widget = box
    
    def set_action_text(self, text):
        self.action_text.set_text("foobnix " + text)
        
    def set_hotkey_text(self, text):
        self.hotkey_text.set_text(text) 
        
    def on_add_row(self, *args):
        command = self.action_text.get_text()
        hotkey = self.hotkey_text.get_text()
        if command and hotkey: 
            if command not in self.get_all_items():
                self.model.append([command, hotkey])
                self.add_key_binder(command, hotkey);
            
        self.action_text.set_text("")
        self.hotkey_text.set_text("")
    
        
    def on_remove_row(self, *args):
        selection = self.tree_widget.get_selection()
        model, selected = selection.get_selected()
        model.remove(selected)   
        keystring = self.model.get_value(selected, 1)
        try:
            keybinder.unbind(keystring)
        except:
            pass 
    
    def on_populate_click(self,w,event):
        if is_double_left_click(event):            
            selection = self.tree_widget.get_selection()
            model, selected = selection.get_selected()
            
            command = self.model.get_value(selected, 0)
            keystring = self.model.get_value(selected, 1)
            self.action_text.set_text(command)
            self.hotkey_text.set_text(keystring)
        
    def on_mouse_click(self,w, event):
        menu = Popup()
        menu.add_item(_("Play"), gtk.STOCK_MEDIA_PLAY, self.set_action_text, "--play")
        menu.add_item(_("Pause"), gtk.STOCK_MEDIA_PAUSE, self.set_action_text, "--pause")
        menu.add_item(_("Stop"), gtk.STOCK_MEDIA_STOP, self.set_action_text, "--stop")
        menu.add_item(_("Next song"), gtk.STOCK_MEDIA_NEXT, self.set_action_text, "--next")
        menu.add_item(_("Previous song"), gtk.STOCK_MEDIA_PREVIOUS, self.set_action_text, "--prev")
        menu.add_item(_("Voulume up"), gtk.STOCK_GO_UP, self.set_action_text, "--volume-up")
        menu.add_item(_("Voulume down"), gtk.STOCK_GO_DOWN, self.set_action_text, "--volume-down")
        menu.add_item(_("Show-Hide"), gtk.STOCK_FULLSCREEN, self.set_action_text, "--show-hide")
        menu.show(event)     
   
    def on_load(self):
        items = FConfiguration().action_hotkey
        self.model.clear()
        for key in items:
            command = key
            hotkey = items[key]            
            self.model.append([command,hotkey])  
            
        self.bind_all(items)
       
    
    def add_key_binder(self, command, hotkey):
        try:                      
            keybinder.bind(hotkey, self.activate_hot_key, command)
        except Exception, e:
            print hotkey, e
    
    def activate_hot_key(self, command):
        LOG.debug("Run command: "+command)         
        thread.start_new_thread(os.system,(command,))
        
    def on_save(self):
        FConfiguration().action_hotkey = self.get_all_items()
        self.bind_all(self.get_all_items())
    
    def unbind_all(self):
        print "unbin all"
        items = self.get_all_items()
        for keystring in items: 
            try:          
                keybinder.unbind(items[keystring])
            except:
                pass
                              
    def bind_all(self,items):
        for key in items:
            command = key
            hotkey = items[key]
            self.add_key_binder(command, hotkey);                
   
    def get_all_items(self):
        items = {}
        for item in self.model:              
            action = item[0]
            hotkey = item[1]
            items[action]=hotkey       
        return items      
        
    def on_key_press(self,w,event):
        self.unbind_all() 
        keyname = gtk.gdk.keyval_name(event.keyval)
        print "Key %s (%d) was pressed" % (keyname, event.keyval), event.state
        if event.state & gtk.gdk.CONTROL_MASK:           
            self.set_hotkey_text("<Control>"+keyname)
        elif event.state & gtk.gdk.SHIFT_MASK :
            self.set_hotkey_text("<Shift>"+keyname)
        elif event.state & gtk.gdk.SUPER_MASK:            
            self.set_hotkey_text("<SUPER>"+keyname)
        elif event.state & (gtk.gdk.MOD1_MASK | gtk.gdk.MOD2_MASK):
            self.set_hotkey_text("<Alt>"+keyname)    
        else:            
            self.set_hotkey_text(keyname)       
            
    def on_key_release(self,w,event): 
        keyname = gtk.gdk.keyval_name(event.keyval)
        print "Key release %s (%d) was pressed" % (keyname, event.keyval)        