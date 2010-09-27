'''
Created on Sep 27, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
from foobnix.helpers.toolbar import MyToolbar
import gtk
class PlaybackControls(MyToolbar,LoadSave):
    def __init__(self):     
        MyToolbar.__init__(self)   
        self.add_separator()
        self.add_button("Stop", gtk.STOCK_MEDIA_STOP, None, None)   
        self.add_button("Play", gtk.STOCK_MEDIA_PLAY, None, None)
        self.add_button("Pause", gtk.STOCK_MEDIA_PAUSE, None, None)
        self.add_button("Previous", gtk.STOCK_MEDIA_PREVIOUS, None, None)
        self.add_button("Next", gtk.STOCK_MEDIA_NEXT, None, None)
        self.add_separator()
        
    def on_load(self): pass
    def on_save(self): pass