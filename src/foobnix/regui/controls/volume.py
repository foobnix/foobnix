#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.helpers.my_widgets import EventLabel
class VolumeControls(LoadSave, gtk.HBox, FControl):
    MAX_VALUE = 120
    def __init__(self, controls):
        gtk.HBox.__init__(self, False, 0)
        FControl.__init__(self, controls)
        
        label_m = EventLabel(text="‒", func=self.volume_down)
        
        adjustment = gtk.Adjustment(value=1, lower=0, upper=self.MAX_VALUE, step_incr=0, page_incr=0, page_size=0)
        self.volume_scale = gtk.HScale(adjustment)
        self.volume_scale.connect("value-changed", self.on_value_changed)
        self.volume_scale.connect("scroll-event", self.on_scroll_event)
        self.volume_scale.connect("button-press-event", self.on_volume_change)
        #self.volume_scale.connect("motion-notify-event", self.on_volume_change1)
        self.volume_scale.set_size_request(200, -1)
        self.volume_scale.set_update_policy(gtk.UPDATE_CONTINUOUS)
        self.volume_scale.set_digits(1)        
        self.volume_scale.set_draw_value(False)

        label_p = EventLabel(text="+", func=self.volume_up)
        
        self.pack_start(label_m, False, False)
        self.pack_start(self.volume_scale, False, False)
        self.pack_start(label_p, False, False)
        
        self.show_all()
    
    def on_volume_change(self, w, event):
        max_x, max_y = w.size_request()
        x, y = event.x, event.y
        value = x / max_x * self.MAX_VALUE
        if value > self.MAX_VALUE * 0.75:
            value += self.MAX_VALUE / 20
        elif value < self.MAX_VALUE * 0.25:
            value -= self.MAX_VALUE / 20
            
        self.set_value(value);
        self.on_save()
    
    def get_value(self):
        self.volume_scale.get_value() 
    
    def set_value(self, value):
        self.volume_scale.set_value(value)
    
    def volume_up(self):
        value = self.volume_scale.get_value()
        self.volume_scale.set_value(value + 3)
    
    def volume_down(self):
        value = self.volume_scale.get_value()
        self.volume_scale.set_value(value - 3)
    
    
    def on_scroll_event(self, button, event):
        value = self.volume_scale.get_value()
        if event.direction == gtk.gdk.SCROLL_UP: #@UndefinedVariable
            self.volume_scale.set_value(value + 3)
        else:
            self.volume_scale.set_value(value - 3)
        self.controls.player_volue(value)
        return True

    
    def on_value_changed(self, widget):        
        percent = widget.get_value()
        self.controls.player_volue(percent)
        FC().volume = percent
    
    def on_save(self):
        pass
    
    def on_load(self):        
        self.volume_scale.set_value(FC().volume)
