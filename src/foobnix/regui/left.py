#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.radio.radios import RadioFolder
from foobnix.regui.model import FModel
class LeftWidgets(FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        vbox = gtk.VBox(False, 0)
        
        scan = DirectoryScanner("/home/ivan/Music")
        #scan = DirectoryScanner("/home/ivan/Музыка")
        #thread.start_new_thread(self.tree.populate_from_scanner, scan.get_music_results())
        self.controls.tree.populate_from_scanner(scan.get_music_results())

        controls.tree.set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        controls.radio.set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        controls.virtual.set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
               
        
                
        buttons = PerspectiveButtonControlls(controls).widget
        
        vbox.pack_start(controls.tree.scroll, True, True)
        vbox.pack_start(controls.radio.scroll, True, True)
        vbox.pack_start(controls.virtual.scroll, True, True)
        
        vbox.pack_start(controls.filter, False, False)
        vbox.pack_start(buttons, False, False)
        
        vbox.show_all()
                
        self.widget = vbox
    
    def on_load(self):            
        pass
   
    def on_save(self):
        pass

class PerspectiveButtonControlls(FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        hbox = gtk.HBox(False, 0)
               
        musics = self.custom_button("Music", gtk.STOCK_HARDDISK)
        musics.connect("clicked", self.on_change_perspective, controls.tree)
        musics.set_active(True)
        
        
        radios = self.custom_button("Radio", gtk.STOCK_NETWORK)
        radios.connect("clicked", self.on_change_perspective, controls.radio)
        
        self.radio_folder = RadioFolder()          
        files = self.radio_folder.get_radio_FPLs()
        for fpl in files:
            parent = FModel(fpl.name).add_font("bold")
            parentIter = controls.radio.append(parent)            
            for radio, urls in fpl.urls_dict.iteritems():
                child = FModel(radio, urls[0]).add_font("").add_level(parentIter)
                controls.radio.append(child)
        
        
        virtuals = self.custom_button("Lists", gtk.STOCK_INDEX)
        virtuals.connect("clicked", self.on_change_perspective, controls.virtual)
        
        list = [musics, radios, virtuals]
        OneActiveToggledButton(list)
        
        hbox.pack_start(musics, False, False)
        hbox.pack_start(radios, False, False)
        hbox.pack_start(virtuals, False, False)
        
        hbox.show_all()
        
        self.widget = hbox
    
   
    def on_change_perspective(self, w, perspective):
        self.controls.tree.scroll.hide()
        self.controls.radio.scroll.hide()
        self.controls.virtual.scroll.hide()
        perspective.scroll.show()
                    
        
    def custom_button(self, title, gtk_stock, func=None, param=None):
        button = gtk.ToggleButton(title)

        if param and func:             
            button.connect("toggled", lambda * a: func(param))
        elif func:
            button.connect("toggled", lambda * a: func())         
                
        button.set_relief(gtk.RELIEF_NONE)
        label = button.get_child()
        button.remove(label)
        
        vbox = gtk.VBox(False, 0)
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        vbox.add(img)
        vbox.add(gtk.Label(title))
        vbox.show_all()
        
        button.add(vbox)
        return button
