#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.helpers.toggled import OneActiveToggledButton
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.model.signal import FControl
class LeftWidgets(FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        vbox = gtk.VBox(False, 0)
        
        self.tree = controls.tree      

        scan = DirectoryScanner("/home/ivan/Музыка")
        self.tree.populate_from_scanner(scan.get_music_results())
        
        scrool_tree = gtk.ScrolledWindow()        
        scrool_tree.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrool_tree.add_with_viewport(self.tree)
        scrool_tree.show()    
                
        
        
        buttons = PerspectiveButtonControlls().widget
        
        vbox.pack_start(scrool_tree, True, True)
        vbox.pack_start(controls.filter, False, False)
        vbox.pack_start(buttons, False, False)
        
        vbox.show_all()
                
        self.widget = vbox
   

class PerspectiveButtonControlls():
    def __init__(self):
        hbox = gtk.HBox(False, 0)
               
        music = self.custom_button("Music", gtk.STOCK_HARDDISK)
        radio = self.custom_button("Radio", gtk.STOCK_NETWORK)
        lists = self.custom_button("Lists", gtk.STOCK_INDEX)
        OneActiveToggledButton([music, radio, lists])
        
        hbox.pack_start(music, False, False)
        hbox.pack_start(radio, False, False)
        hbox.pack_start(lists, False, False)
        
        hbox.show_all()
        
        self.widget = hbox
    
   
                    
        
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
