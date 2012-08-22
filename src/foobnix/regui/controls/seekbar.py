#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: ivan
'''

import gtk

from foobnix.regui.model.signal import FControl
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.util.const import FTYPE_RADIO
import gobject


class SeekProgressBarControls(FControl, gtk.Alignment):
    def __init__(self, controls, seek_bar_movie=None):
        FControl.__init__(self, controls)
        self.seek_bar_movie = seek_bar_movie
        gtk.Alignment.__init__(self, xalign=0.5, yalign=0.5, xscale=1.0, yscale=1.0)
        
        self.set_padding(padding_top=7, padding_bottom=7, padding_left=0, padding_right=7)
        
        self.tooltip = gtk.Window(gtk.WINDOW_POPUP)
        self.tooltip.set_position(gtk.WIN_POS_CENTER)
        self.tooltip_label = gtk.Label()
        self.tooltip.add(self.tooltip_label)
        
        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_text("00:00 / 00:00")
        try:
            self.progressbar.set_has_tooltip(True)
        except:
            #fix debian compability
            pass
        
        self.progressbar.connect("leave-notify-event", lambda *a: self.safe_hide_tooltip())
        self.progressbar.connect("motion-notify-event", self.on_pointer_motion)        
        event = gtk.EventBox()
        event.add(self.progressbar)
        event.connect("button-press-event", self.on_seek)
        
        
        self.add(event)
        self.show_all()
        self.tooltip.hide()
        
    def safe_hide_tooltip(self):
        gobject.idle_add(self.tooltip.hide)
    def on_pointer_motion(self, widget, event):
        width = widget.allocation.width
        x = event.x
        duration = self.controls.media_engine.duration_sec
        seek_percent = (x + 0.0) / width
        sec = int(duration * seek_percent)
        sec = convert_seconds_to_text(sec)
        def safe_task():
            self.tooltip_label.set_text(sec)
            self.tooltip.show_all()
            x, y, mask = gtk.gdk.get_default_root_window().get_pointer() #@UndefinedVariable @UnusedVariable
            self.tooltip.move(x+5, y-15)
        gobject.idle_add(safe_task)
    
    def on_seek(self, widget, event):
        bean = self.controls.media_engine.bean
        if bean and bean.type == FTYPE_RADIO:
            return None
        
        width = widget.allocation.width
        x = event.x
        seek_percent = (x + 0.0) / width * 100        
        self.controls.player_seek(seek_percent);
        
        if self.seek_bar_movie:
            self.seek_bar_movie.on_seek(widget, event)
    
    def set_text(self, text):
        if text:
            self.progressbar.set_text(text[:200])    
        
        if self.seek_bar_movie:
            self.seek_bar_movie.set_text(text)
        
        
    def clear(self):
        def task():
            self.progressbar.set_text("00:00 / 00:00")
            gobject.idle_add(self.progressbar.set_fraction, 0)
        
            if self.seek_bar_movie:
                self.seek_bar_movie.clear()
        
    
    def update_seek_status(self, position_sec, duration_sec):
        duration_str = convert_seconds_to_text(duration_sec)
        position_str = convert_seconds_to_text(position_sec)
        seek_persent = (position_sec + 0.0) / (duration_sec)
        seek_text = position_str + " / " + duration_str
        
        if 0 <= seek_persent <= 1: 
            self.progressbar.set_text(seek_text)
            gobject.idle_add(self.progressbar.set_fraction, seek_persent)
        
        if self.seek_bar_movie:
            self.seek_bar_movie.update_seek_status(position_sec, duration_sec)
