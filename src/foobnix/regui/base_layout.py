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
        
        self.controls = controls  
        bbox = gtk.VBox(False, 0)
        bbox.pack_start(controls.notetabs, True, True)        
        bbox.pack_start(controls.movie_window, False, False)
        
        center_box = gtk.VBox(False, 0)        
        center_box.pack_start(controls.searchPanel, False, False)
        center_box.pack_start(bbox, True, True)
        
        self.hpaned_left = gtk.HPaned()
        self.hpaned_left.connect("motion-notify-event", self.on_motion)
        
        self.hpaned_left.pack1(child=controls.perspective, resize=True, shrink=True)
        self.hpaned_left.pack2(child=center_box, resize=True, shrink=True)
        
        self.hpaned_right = gtk.HPaned()
        self.hpaned_right.connect("motion-notify-event", self.on_motion)
        self.hpaned_right.pack1(child=self.hpaned_left, resize=True, shrink=True)
        self.hpaned_right.pack2(child=controls.coverlyrics, shrink=False)
        
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(controls.top_panel, False, False)
        vbox.pack_start(self.hpaned_right, True, True)        
        vbox.pack_start(controls.statusbar, False, True)
        vbox.show_all()
                
        self.hpaned_left.connect("button-release-event", self.save_panels)
        self.hpaned_right.connect("button-release-event", self.save_panels)
        self.hpaned_left.connect("size-allocate", self.on_configure_hl_event)
        self.hpaned_right.connect("size-allocate", self.on_configure_hr_event)
        controls.main_window.connect("configure-event", self.on_configure_event)
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
            self.hpaned_right.set_position(self.hpaned_right.allocation.width - FC().hpaned_right_right_side_width)
            self.controls.coverlyrics.show()
            gobject.idle_add(self.controls.coverlyrics.adapt_image)
        else:
            self.controls.coverlyrics.hide()
        
        FC().is_view_coverlyrics_panel = flag
    
    def on_motion(self, *a):
        return
    
    def save_panels(self, *a):
        left_position = self.hpaned_left.get_position()
        if left_position != FC().hpaned_left and left_position > 0:   
            FC().hpaned_left = left_position
            self.normalize_columns()
        if self.hpaned_right.get_property("visible"):
            right_position = self.hpaned_right.get_position()
            if right_position != FC().hpaned_right and right_position > 0:   
                FC().hpaned_right = right_position
            FC().hpaned_right_right_side_width = self.hpaned_right.allocation.width - right_position
            self.controls.coverlyrics.adapt_image()  

    def normalize_columns(self):
        for page in xrange(self.controls.tabhelper.get_n_pages()):
            tab_content = self.controls.tabhelper.get_nth_page(page)
            tree = tab_content.get_child()
            tree.normalize_columns_width()
    
    def on_configure_event(self, w, e):
        FC().main_window_size = [e.x, e.y, e.width, e.height]
    
    def on_configure_hl_event(self, *a):
        def task():
            if FC().is_view_music_tree_panel and self.hpaned_left.get_position() != FC().hpaned_left:
                self.hpaned_left.set_position(FC().hpaned_left)
        gobject.idle_add(task)

    def on_configure_hr_event(self, *a):
        def task():
            if self.controls.coverlyrics.get_property("visible"):
                hrw = self.hpaned_right.allocation.width
                if (hrw - self.hpaned_right.get_position()) != FC().hpaned_right_right_side_width:
                    self.hpaned_right.set_position(hrw - FC().hpaned_right_right_side_width)
        gobject.idle_add(task)

    def on_load(self):
        self.set_visible_search_panel(FC().is_view_search_panel)
        gobject.idle_add(self.set_visible_musictree_panel, FC().is_view_music_tree_panel, 
                         priority = gobject.PRIORITY_DEFAULT_IDLE - 10)
        self.set_visible_coverlyrics_panel(FC().is_view_coverlyrics_panel)
                                
