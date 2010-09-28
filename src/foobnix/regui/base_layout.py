#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.top import TopWidgets
from foobnix.regui.infopanel import InfoPanelWidget
from foobnix.regui.left import LeftWidgets
from foobnix.regui.all_controls import StatusbarControls
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
class BaseFoobnixLayout(LoadSave, FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
         
        vbox = gtk.VBox(False, 0)
        vbox.show()
        
        self.top = TopWidgets(controls)
                
        vbox.pack_start(self.top.widget, False, False)
        
       
        center_box = gtk.VBox(False, 0)
        
        self.hpaned_right = gtk.HPaned()
        
        self.hpaned_right.pack1(child=controls.notetabs, resize=True, shrink=True)
        self.hpaned_right.pack2(child=controls.info_panel, resize=True, shrink=True)
               
        
        center_box.pack_start(controls.searchPanel, False, False)
        center_box.pack_start(self.hpaned_right, True, True)
        center_box.show_all()
        
        left = LeftWidgets(controls).widget
        
        self.hpaned_left = gtk.HPaned()     
        
        self.hpaned_left.pack1(child=left, resize=True, shrink=True)
        self.hpaned_left.pack2(child=center_box, resize=True, shrink=True)
    
        self.hpaned_left.show_all()
        
        
        
        statusbar = StatusbarControls().widget
        
        vbox.pack_start(self.hpaned_left, True, True)        
        vbox.pack_start(statusbar, False, True)
        
        controls.window.add(vbox)
        
    def on_save(self, *a):
        FC().hpaned_left = self.hpaned_left.get_position()
        FC().hpaned_right = self.hpaned_right.get_position()
        
    
    def on_load(self):
        self.controls.search_progress.hide()
        self.hpaned_left.set_position(FC().hpaned_left)
        self.hpaned_right.set_position(FC().hpaned_right)
                             
