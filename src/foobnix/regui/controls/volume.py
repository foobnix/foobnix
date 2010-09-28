#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
class VolumeControls(LoadSave, gtk.HBox, FControl):
    MAX_VALUE = 120
    def __init__(self, controls):
        gtk.HBox.__init__(self, False, 0)
        FControl.__init__(self, controls)
        
        label_m = gtk.Label("-")
        
        adjustment = gtk.Adjustment(value=1, lower=0, upper=self.MAX_VALUE, step_incr=10, page_incr=50, page_size=0)
        self.volume_scale = gtk.HScale(adjustment)
        self.volume_scale.connect("value-changed", self.on_value_changed)
        self.volume_scale.connect("scroll-event", self.on_scroll_event)
        self.volume_scale.set_size_request(150, -1)
        self.volume_scale.set_update_policy(gtk.UPDATE_CONTINUOUS)
        self.volume_scale.set_digits(1)        
        self.volume_scale.set_draw_value(False)
        self.volume_scale.set_value(30)

        label_p = gtk.Label("+")
        
        self.pack_start(label_m, False, False)
        self.pack_start(self.volume_scale, False, False)
        self.pack_start(label_p, False, False)
        
        self.show_all()
    
    def on_scroll_event(self, button, event):
        value = self.volume_scale.get_value()
        if event.direction == gtk.gdk.SCROLL_UP:
            self.volume_scale.set_value(value + 5)
        else:
            self.volume_scale.set_value(value - 5)
        self.controls.player_volue(value)
        return True

    
    def on_value_changed(self, widget):        
        percent = widget.get_value()
        self.controls.player_volue(percent)
    
    def on_save(self):
        FC().volume = self.volume_scale.get_value()
    
    def on_load(self):
        self.volume_scale.set_value(FC().volume)
