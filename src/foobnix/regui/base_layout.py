#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
import gobject
import logging

from foobnix.fc.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave


class BaseFoobnixLayout(FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
          
        bbox = gtk.VBox(False, 0)
        bbox.pack_start(controls.notetabs, True, True)        
        bbox.pack_start(controls.movie_window, False, False)
        
        center_box = gtk.VBox(False, 0)        
        center_box.pack_start(controls.searchPanel, False, False)
        center_box.pack_start(bbox, True, True)
        
        self.hpaned_left = gtk.HPaned()
        self.hpaned_left.connect("motion-notify-event", self.on_save_and_normilize_columns)
        self.hpaned_left.pack1(child=controls.perspective, resize=True, shrink=True)
        self.hpaned_left.pack2(child=center_box, resize=True, shrink=True)
        
        self.hpaned_right = gtk.HPaned()
        self.hpaned_right.connect("motion-notify-event", self.on_save_and_normilize_columns)
        self.hpaned_right.pack1(child=self.hpaned_left, resize=True, shrink=True)
        self.hpaned_right.pack2(child=controls.coverlyrics, resize=True, shrink=True)
        
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(controls.top_panel, False, False)
        vbox.pack_start(self.hpaned_right, True, True)        
        vbox.pack_start(controls.statusbar, False, True)
        vbox.show_all()
        
        controls.main_window.add(vbox)        
        
    def set_visible_search_panel(self, flag=True):
        logging.info("set_visible_search_panel " + str(flag))
        if flag:
            self.controls.searchPanel.show_all()
        else:
            self.controls.searchPanel.hide()
        
        FC().is_view_search_panel = flag   
    
    def set_visible_musictree_panel(self, flag):
        logging.info("set_visible_musictree_panel " + str(flag))
        if flag:
            self.hpaned_left.set_position(FC().hpaned_left)
        else:
            self.hpaned_left.set_position(0)
            
        FC().is_view_music_tree_panel = flag
        
    def set_visible_coverlyrics_panel(self, flag):
        logging.info("set_visible_coverlyrics_panel " + str(flag))
        if flag:
            self.hpaned_right.set_position(FC().hpaned_right)
            self.controls.coverlyrics.show()
        else:
            self.controls.coverlyrics.hide()
        
        FC().is_view_coverlyrics_panel = flag
            
    def on_save_and_normilize_columns(self, *a): 
        if self.hpaned_left.get_position() > 0:   
            FC().hpaned_left = self.hpaned_left.get_position()
        if self.hpaned_right.get_position() > 0:   
            FC().hpaned_right = self.hpaned_right.get_position()
            image = self.controls.coverlyrics.image
            image.size = self.controls.coverlyrics.lyrics.get_allocation().width
            image.set_from_pixbuf(self.controls.coverlyrics.get_pixbuf())
               
        for page in xrange(self.controls.tabhelper.get_n_pages()):
            tab_content = self.controls.tabhelper.get_nth_page(page)
            tree = tab_content.get_child()
            tree.normalize_columns_width()
            
    def on_load(self):
        self.set_visible_search_panel(FC().is_view_search_panel)
        gobject.idle_add(self.set_visible_musictree_panel, FC().is_view_music_tree_panel, 
                         priority = gobject.PRIORITY_DEFAULT_IDLE - 10)
        self.set_visible_coverlyrics_panel(FC().is_view_coverlyrics_panel)
        
        
                
        
                             
