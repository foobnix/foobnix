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
        
class SeekProgressBarControls():
    def __init__(self):
        aligment = gtk.Alignment(xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        aligment.set_padding(padding_top=7, padding_bottom=7, padding_left=0, padding_right=7)
        
        progresbar = gtk.ProgressBar()
        progresbar.set_text("00:00 / 00:00")
        
        event = gtk.EventBox()
        event.add(progresbar)
        
        aligment.add(event)
        
        aligment.show_all()
        
        self.widget = aligment

class StatusbarControls():
    def __init__(self):
        statusbar = gtk.Statusbar()
        statusbar.show()
        
        self.widget = statusbar

