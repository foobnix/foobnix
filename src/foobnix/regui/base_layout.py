#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.fc.fc import FC
from foobnix.regui.model.signal import FControl
import logging
from foobnix.regui.state import LoadSave
class BaseFoobnixLayout(FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
         
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(controls.top_panel, False, False)
               
        center_box = gtk.VBox(False, 0)
        
        #self.hpaned_right = gtk.HPaned()
        
        bbox = gtk.VBox(False, 0)
        
        bbox.pack_start(controls.notetabs, True, True)        
        bbox.pack_start(controls.movie_window, False, False)
        #self.hpaned_right.pack1(child=bbox, resize=True, shrink=True)
        #self.hpaned_right.pack2(child=controls.info_panel, resize=True, shrink=True)
          
        
        center_box.pack_start(controls.searchPanel, False, False)
        center_box.pack_start(bbox, True, True)
        
        self.hpaned_left = gtk.HPaned()     
        
        self.hpaned_left.pack1(child=controls.perspective, resize=True, shrink=True)
        self.hpaned_left.pack2(child=center_box, resize=True, shrink=True)
    
        self.hpaned_left.show_all()
        
        vbox.pack_start(self.hpaned_left, True, True)        
        vbox.pack_start(controls.statusbar, False, True)
        vbox.show_all()
        
        controls.main_window.add(vbox)        
        
    def set_visible_search_panel(self, flag=True):
        logging.info("set_visible_search_panel" + str(flag))
        if flag:
            self.controls.searchPanel.show_all()
            #self.controls.search_progress.hide()
        else:
            self.controls.searchPanel.hide()   
    
    def set_visible_musictree_panel(self, flag):
        logging.info("set_visible_musictree_panel" + str(flag))
        if flag:
            self.hpaned_left.set_position(FC().hpaned_left)            
        else:
            self.hpaned_left.set_position(0)
        
    

    def on_save(self, *a):
        if FC().is_view_music_tree_panel:
            FC().hpaned_left = self.hpaned_left.get_position()
            
    def on_load(self):  
        #self.controls.search_progress.hide()        
        self.hpaned_left.set_position(FC().hpaned_left)
        self.set_visible_musictree_panel(FC().is_view_music_tree_panel)
        self.set_visible_search_panel(FC().is_view_search_panel)
        
        
                             
