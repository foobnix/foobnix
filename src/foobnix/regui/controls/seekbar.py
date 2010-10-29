#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: ivan
'''
from foobnix.regui.model.signal import FControl
import gtk
from foobnix.util.time_utils import convert_seconds_to_text
import gobject
class SeekProgressBarControls(FControl, gtk.Alignment):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Alignment.__init__(self, xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        
        self.set_padding(padding_top=7, padding_bottom=7, padding_left=0, padding_right=7)
        
        self.progresbar = gtk.ProgressBar()
        self.progresbar.set_text("00:00 / 00:00")
        
        event = gtk.EventBox()
        event.connect("button-press-event", self.on_seek)
        event.add(self.progresbar)
        
        self.add(event)
        
        self.show_all()
    
    def on_seek(self, widget, event):
        width = widget.allocation.width
        x = event.x
        seek_percent = (x + 0.0) / width * 100        
        self.controls.player_seek(seek_percent);
    
    def set_text(self, text):
        if text:
            self.progresbar.set_text(text[:200])    
    
    def clear(self):
        self.progresbar.set_text("00:00 / 00:00")
        self.progresbar.set_fraction(0)
    
    def update_seek_status(self, position_sec, duration_sec):
        def task():        
            duration_str = convert_seconds_to_text(duration_sec)
            position_str = convert_seconds_to_text(position_sec)
            
            seek_text = position_str + " / " + duration_str
            seek_persent = (position_sec + 0.0) / (duration_sec)                
                                  
            self.progresbar.set_text(seek_text)
            if 0 <= seek_persent <= 1: 
                self.progresbar.set_fraction(seek_persent)
        gobject.idle_add(task)
