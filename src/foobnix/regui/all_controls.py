#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util.fc import FC
from foobnix.regui.state import LoadSave

class VolumeControls(LoadSave):
    def __init__(self):
        vbox = gtk.HBox(False, 0)
        label_m = gtk.Label("-")
        
        adjustment = gtk.Adjustment(value=1, lower=0, upper=100, step_incr=10, page_incr=50, page_size=0)
        self.volume_scale = gtk.HScale(adjustment)
        self.volume_scale.set_size_request(150, -1)
        self.volume_scale.set_update_policy(gtk.UPDATE_CONTINUOUS)
        self.volume_scale.set_digits(1)        
        self.volume_scale.set_draw_value(False)
        self.volume_scale.set_value(30)

        label_p = gtk.Label("+")
        
        vbox.pack_start(label_m, False, False)
        vbox.pack_start(self.volume_scale, False, False)
        vbox.pack_start(label_p, False, False)
        
        vbox.show_all()
        self.widget = vbox         
    
    def on_save(self):
        FC().volume = self.volume_scale.get_value()
    
    def on_load(self):
        self.volume_scale.set_value(FC().volume)
        
class StatusbarControls():
    def __init__(self):
        statusbar = gtk.Statusbar()
        statusbar.show()
        
        self.widget = statusbar

