#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.top import TopWidgets
from foobnix.regui.infopanel import InfoPanelWidget
from foobnix.regui.search import SearchControls
from foobnix.regui.left import LeftWidgets
from foobnix.regui.controls import StatusbarControls
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
class BaseFoobnixLayout(LoadSave):
    def __init__(self, window, notetabs, tree):        
        vbox = gtk.VBox(False, 0)
        vbox.show()
        
        self.top = TopWidgets()
                
        vbox.pack_start(self.top.widget, False, False)
        
       
        center_box = gtk.VBox(False, 0)
        
        self.hpaned_right = gtk.HPaned()
        
        self.info_panel = InfoPanelWidget()
        
        self.hpaned_right.pack1(child=notetabs, resize=True, shrink=True)
        self.hpaned_right.pack2(child=self.info_panel.widget, resize=True, shrink=True)
               
        
        searchPanel = SearchControls().widget
        
        
        center_box.pack_start(searchPanel, False, False)
        center_box.pack_start(self.hpaned_right, True, True)
        center_box.show_all()
        
        left = LeftWidgets(tree).widget
        
        self.hpaned_left = gtk.HPaned()     
        
        self.hpaned_left.pack1(child=left, resize=True, shrink=True)
        self.hpaned_left.pack2(child=center_box, resize=True, shrink=True)
    
        self.hpaned_left.show_all()
        
        
        
        statusbar = StatusbarControls().widget
        
        vbox.pack_start(self.hpaned_left, True, True)        
        vbox.pack_start(statusbar, False, True)
        
        window.add(vbox)
        window.show()
        
    def on_save(self, *a):
        FC().hpaned_left = self.hpaned_left.get_position()
        FC().hpaned_right = self.hpaned_right.get_position()
        
    
    def on_load(self):
        self.hpaned_left.set_position(FC().hpaned_left)
        self.hpaned_right.set_position(FC().hpaned_right)
                             
