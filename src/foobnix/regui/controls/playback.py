'''
Created on Sep 27, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
from foobnix.helpers.toolbar import MyToolbar
from foobnix.regui.model.signal import FControl
import gtk
from foobnix.helpers.my_widgets import ImageButton

class PlaybackControlsNotUser(FControl, MyToolbar, LoadSave):
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
    
class PlaybackControls(FControl, gtk.HBox, LoadSave):
    def __init__(self, controls): 
        gtk.HBox.__init__(self, False)
        self.pack_start(gtk.SeparatorToolItem())
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_STOP, controls.state_stop, _("Stop")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PLAY, controls.state_play, _("Play")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PAUSE, controls.state_pause, _("Pause")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PREVIOUS, controls.prev, _("Previous")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_NEXT, controls.next, _("Next")))
        self.pack_start(gtk.SeparatorToolItem())
    def on_load(self): pass
    def on_save(self): pass    
