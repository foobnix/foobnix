#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: ivan
'''

from gi.repository import Gtk
from gi.repository import Gdk
from foobnix.fc.fc import FC
from foobnix.regui.state import LoadSave
from foobnix.regui.model.signal import FControl


class VolumeControls(LoadSave, Gtk.HBox, FControl):
    MAX_VALUE = 100

    def __init__(self, controls):
        Gtk.HBox.__init__(self, False, 0)
        FControl.__init__(self, controls)

        adjustment = Gtk.Adjustment(value=1, lower=0, upper=self.MAX_VALUE, step_incr=0, page_incr=0, page_size=0)
        self.volume_scale = Gtk.HScale(adjustment=adjustment)
        self.volume_scale.connect("value-changed", self.on_value_changed)
        self.volume_scale.connect("scroll-event", self.on_scroll_event)
        self.volume_scale.connect("button-press-event", self.on_volume_change)
        self.volume_scale.set_size_request(200, -1)
        self.volume_scale.set_digits(1)        
        self.volume_scale.set_draw_value(False)

        self.pack_start(self.volume_scale, False, False, 0)
        
        self.show_all()
    
    def on_volume_change(self, w, event):
        max_x, max_y = w.size_request()
        x, y = event.x, event.y
        value = x / max_x * self.MAX_VALUE
        if value > self.MAX_VALUE * 0.75:
            value += self.MAX_VALUE / 20
        elif value < self.MAX_VALUE * 0.25:
            value -= self.MAX_VALUE / 20
            
        self.set_value(value)
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
    
    def mute(self):
        value = self.volume_scale.get_value()
        if value == 0:
            self.volume_scale.set_value(FC().temp_volume)
        else:
            FC().temp_volume = value
            self.volume_scale.set_value(0)
        
    def on_scroll_event(self, button, event):
        value = self.volume_scale.get_value()
        if event.direction == Gdk.ScrollDirection.UP: #@UndefinedVariable
            self.volume_scale.set_value(value + 15)
        else:
            self.volume_scale.set_value(value - 15)
        self.controls.player_volume(value)
        return True
    
    def on_value_changed(self, widget): 
        percent = widget.get_value()
        self.controls.player_volume(percent)
        FC().volume = percent
        self.controls.trayicon.popup_volume_contol.avc.set_volume(percent)
    
    def on_save(self):
        pass
    
    def on_load(self):        
        self.volume_scale.set_value(FC().volume)
