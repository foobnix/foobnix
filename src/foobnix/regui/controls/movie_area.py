#-*- coding: utf-8 -*-

from foobnix.regui.model.signal import FControl

import gtk
import logging

from foobnix.helpers.window import ChildTopWindow
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.regui.controls.playback import PlaybackControls
from foobnix.util.key_utils import is_key, is_key_alt, get_key
from foobnix.helpers.my_widgets import notetab_label, ImageButton


class AdvancedDrawingArea(gtk.DrawingArea):
    def __init__(self, controls):  
        gtk.DrawingArea.__init__(self)
        self.controls = controls
        self.set_events(gtk.gdk.ALL_EVENTS_MASK) #@UndefinedVariable
        self.set_flags(gtk.CAN_FOCUS)
        
        self.connect("key-release-event", self.on_key_press)
        self.connect("button-press-event", self.on_button_press)
        self.connect("scroll-event", self.controls.volume.on_scroll_event)
    
    def action_function(self):
        logging.debug("Template function not defined")    
    
    def on_key_press(self, w, e):   
        if is_key(e, 'Escape') or get_key(e) in ('F', 'f', 'а', 'А'):                
            self.action_function()                
        elif is_key_alt(e) and is_key(e, "Return"):
            self.action_function()
        elif get_key(e) in ('P', 'p', 'з', 'З','space'):
            self.controls.play_pause()
        elif is_key(e, 'Left'):
            self.controls.seek_down()
        elif is_key(e, 'Right'):
            self.controls.seek_up()
        elif is_key(e, 'Up'):
            self.controls.volume_up()
        elif is_key(e, 'Down'):
            self.controls.volume_down()
        
        self.grab_focus()
            
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            self.action_function()
        
        self.grab_focus()

class FullScreanArea(ChildTopWindow):
        def __init__(self, controls, on_hide_callback):
            self.controls = controls
            ChildTopWindow.__init__(self, "movie")
            self.set_hide_on_escape(False)
            self.on_hide_callback = on_hide_callback
            self.set_flags(gtk.CAN_FOCUS)
            self.layout = gtk.VBox(False)
            
            self.drow = AdvancedDrawingArea(controls)
            self.drow.action_function = on_hide_callback 
            self.set_resizable(True)
            self.set_border_width(0)
            
            self.layout.pack_start(self.drow, True)
            
            
            self.text_label = gtk.Label("foobnix")
            self.volume_button= gtk.VolumeButton()
            self.volume_button.connect("value-changed", self.volume_changed)
            
            line = gtk.HBox(False)            
             
            line.pack_start(ImageButton(gtk.STOCK_FULLSCREEN, on_hide_callback, _("Exit Fullscrean")), False)
            line.pack_start(PlaybackControls(controls), False)
            line.pack_start(controls.seek_bar_movie, True)
            line.pack_start(gtk.SeparatorToolItem(),False)
            line.pack_start(self.text_label, False)
            line.pack_start(gtk.SeparatorToolItem(),False)
            line.pack_start(self.volume_button, False)
            
            self.layout.pack_start(line,False)
            
            self.add(self.layout)
            self.set_opacity(1)
            
            self.drow.connect("enter-notify-event", lambda *a: line.hide())
            
            def my_event(w, e):
                if e.y > gtk.gdk.screen_height() - 5: #@UndefinedVariable
                    line.show()
                    
            self.connect("motion-notify-event", my_event)
                      
        def volume_changed(self, volumebutton, value):
            self.controls.volume.set_value(float(value * 100))
        
        def set_text(self, text):
            self.text_label.set_text(text)
        
        def get_draw(self):
            return self.drow
            
        def hide_window(self, *a):
            self.hide()            
            return True
        
        def show_window(self):
            self.show_all()
            self.fullscreen()
            self.volume_button.set_value(float(self.controls.volume.volume_scale.get_value()/ 100))

class MovieDrawingArea(FControl, gtk.Frame):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Frame.__init__(self)
              
        self.set_label_widget(notetab_label(self.hide))
        self.set_label_align(1.0, 0.0)
        self.set_border_width(0)
        
        
        self.smallscree_area = AdvancedDrawingArea(controls)
        self.smallscree_area.action_function = self.on_full_screen
        self.add(self.smallscree_area)
        
        self.fullscrean_area = FullScreanArea(controls, self.on_small_screen)
        
        self.out = None
        self.set_out(self.smallscree_area)
    
    def set_out(self, area):
        self.out = area
    
    def get_out(self):
        return self.out
    
    def get_draw(self):
        return self.smallscree_area
     
    def on_full_screen(self):
        self.controls.state_stop(True)
        self.fullscrean_area.show_window()        
        self.set_out(self.fullscrean_area.get_draw())      
        self.controls.state_play(True)
    
    def set_text(self, text):
        self.fullscrean_area.set_text(text)
        
                                      
    def on_small_screen(self):
        self.controls.state_stop(True)
        self.set_out(self.smallscree_area)
        self.fullscrean_area.hide_window()
        self.controls.state_play(True)
        
    
    def draw_video(self, message):
        
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            self.show_all()
            self.get_out().set_size_request(-1, 400)
            imagesink.set_xwindow_id(self.get_out().window.xid)          
            
            

