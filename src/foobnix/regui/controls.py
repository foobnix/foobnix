#-*- coding: utf-8 -*-
'''
Created on 22 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util import LOG

class ToolbarSeparator():
    def __init__(self):
        toolbar = MyToolbar()
        toolbar.add_separator()
        self.widget = toolbar.widget

class PlaybackControls():
    def __init__(self):
        toolbar = MyToolbar()
        toolbar.add_separator()
        toolbar.add_button("Stop", gtk.STOCK_MEDIA_STOP, None, None)   
        toolbar.add_button("Play", gtk.STOCK_MEDIA_PLAY, None, None)
        toolbar.add_button("Pause", gtk.STOCK_MEDIA_PAUSE, None, None)
        toolbar.add_button("Previous", gtk.STOCK_MEDIA_PREVIOUS, None, None)
        toolbar.add_button("Next", gtk.STOCK_MEDIA_NEXT, None, None)
        toolbar.add_separator()
        
        self.widget = toolbar.widget

class VolumeControls():
    def __init__(self):
        vbox = gtk.HBox(False, 0)
        label_m = gtk.Label("-")
        
        adjustment = gtk.Adjustment(value=1, lower=0, upper=100, step_incr=10, page_incr=50, page_size=0)
        scale = gtk.HScale(adjustment)
        scale.set_usize(150, -1)
        scale.set_update_policy(gtk.UPDATE_CONTINUOUS)
        scale.set_digits(1)        
        scale.set_draw_value(False)
        scale.set_value(30)

        label_p = gtk.Label("+")
        
        vbox.pack_start(label_m, False, False)
        vbox.pack_start(scale, False, False)
        vbox.pack_start(label_p, False, False)
        
        vbox.show_all()
        self.widget = vbox         

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


class MyToolbar(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)            
        self.toolbar = gtk.Toolbar()
        self.toolbar.show()
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.toolbar.set_show_arrow(False)
        self.toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
         
        self.i = 0
        
        self.widget = self.toolbar
    
    def add_button(self, tooltip, gtk_stock, func, param):
        button = gtk.ToolButton(gtk_stock)
        button.show()  
        button.set_tooltip_text(tooltip)
        
        LOG.debug("Button-Controls-Clicked", tooltip, gtk_stock, func, param)
        if param:             
            button.connect("clicked", lambda * a: func(param))
        else:
            button.connect("clicked", lambda * a: func())     
                
        self.toolbar.insert(button, self.i)
        self.i += 1        
    
    def add_separator(self):
        sep = gtk.SeparatorToolItem()
        sep.show()        
        self.toolbar.insert(sep, self.i)
        self.i += 1
