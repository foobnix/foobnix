'''
Created on Sep 27, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
from foobnix.helpers.toolbar import MyToolbar
from foobnix.regui.model.signal import FControl
import gtk
from foobnix.helpers.my_widgets import ImageButton, EventLabel
from foobnix.util.fc import FC
from foobnix.util import const

class PlaybackControlsNotUsedOld(FControl, MyToolbar, LoadSave):
    def __init__(self, controls): 
        FControl.__init__(self, controls)    
        MyToolbar.__init__(self)   
        self.add_separator()
        self.add_button("Stop", gtk.STOCK_MEDIA_STOP, controls.state_stop, None)   
        self.add_button("Play", gtk.STOCK_MEDIA_PLAY, controls.state_play, None)
        self.add_button("Pause", gtk.STOCK_MEDIA_PAUSE, controls.state_pause, None)
        self.add_button("Previous", gtk.STOCK_MEDIA_PREVIOUS, controls.prev, None)
        self.add_button("Next", gtk.STOCK_MEDIA_NEXT, controls.next, None)
        self.add_separator()
        
    def on_load(self): pass
    def on_save(self): pass
    
class OrderShuffleControls(FControl, gtk.HBox, LoadSave):
    def __init__(self, controls): 
        gtk.HBox.__init__(self, False)
        
        self.rlabel = EventLabel(text="S", func=lambda * a: self.on_random())
        self.olabel = EventLabel(text="R", func=lambda * a: self.on_order())
        
        self.pack_start(self.rlabel)
        self.pack_start(gtk.Label(" "))
        self.pack_start(self.olabel)
        
        self.pack_start(gtk.SeparatorToolItem())
    
    def update(self):
        if FC().is_order_random:
            self.rlabel.set_markup("<b>S</b>")
            self.rlabel.set_tooltip_text("Shuffle on")
            
        else:
            self.rlabel.set_markup("S")
            self.rlabel.set_tooltip_text("Shuffle off")
            
        if FC().repeat_state == const.REPEAT_ALL:
            self.olabel.set_markup("<b>R</b>")
            self.olabel.set_tooltip_text("Repeat all")            
        elif FC().repeat_state == const.REPEAT_SINGLE:
            self.olabel.set_markup("<b>R1</b>")
            self.olabel.set_tooltip_text("Repeat single")
        else:
            self.olabel.set_markup("R")
            self.olabel.set_tooltip_text("Repeat off")
        
    def on_random(self, *a):
        FC().is_order_random = not FC().is_order_random
        self.update()
    
    def on_order(self):
        if FC().repeat_state == const.REPEAT_ALL:
            FC().repeat_state = const.REPEAT_SINGLE
        elif FC().repeat_state == const.REPEAT_SINGLE:
            FC().repeat_state = const.REPEAT_NO
        elif FC().repeat_state == const.REPEAT_NO:
            FC().repeat_state = const.REPEAT_ALL
        self.update()
            
    def on_load(self): 
        self.update()
        
    def on_save(self): pass    
    
class PlaybackControls(FControl, gtk.HBox, LoadSave):
    def __init__(self, controls): 
        gtk.HBox.__init__(self, False)
        self.pack_start(gtk.SeparatorToolItem())
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_STOP, controls.state_stop, _("Stop")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PLAY, controls.state_play, _("Play")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PAUSE, controls.state_play_pause, _("Pause")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PREVIOUS, controls.prev, _("Previous")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_NEXT, controls.next, _("Next")))
        self.pack_start(gtk.SeparatorToolItem())
        
        
    def on_load(self): pass
    def on_save(self): pass    
