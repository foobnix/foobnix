#-*- coding: utf-8 -*-

from foobnix.regui.model.signal import FControl

import gtk
import gobject
import logging

from foobnix.helpers.window import ChildTopWindow
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.regui.controls.playback import PlaybackControls
from foobnix.util.key_utils import is_key, is_key_alt, get_key
from foobnix.helpers.my_widgets import notetab_label, ImageButton
import threading
from foobnix.util import analytics


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
            self.set_property("skip-taskbar-hint", True)
            self.set_keep_above(True)
            self.draw = AdvancedDrawingArea(controls)
            self.draw.action_function = on_hide_callback 
            self.set_resizable(True)
            self.set_border_width(0)
            
            self.layout.pack_start(self.draw, True)
                        
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
            line.show_all()
            
            control_panel = gtk.Window(gtk.WINDOW_POPUP)
            control_panel.set_size_request(800, -1)
            control_panel.add(line)
            
            self.add(self.layout)
                       
            self.draw.connect("enter-notify-event", lambda *a: gobject.idle_add(control_panel.hide))
            
            def my_event(w, e):
                if e.y > gtk.gdk.screen_height() - 5: #@UndefinedVariable
                    def safe_task():
                        control_panel.show()
                        control_panel.set_size_request(gtk.gdk.screen_width(), -1)#@UndefinedVariable
                        control_panel.move(0, gtk.gdk.screen_height() - control_panel.get_allocation().height)#@UndefinedVariable
                    gobject.idle_add(safe_task)
                    
            self.connect("motion-notify-event", my_event)
                      
        def volume_changed(self, volumebutton, value):
            self.controls.volume.set_value(float(value * 100))
        
        def set_text(self, text):
            gobject.idle_add(self.text_label.set_text, text)
        
        def get_draw(self):
            return self.draw
            
        def hide_window(self, *a):
            gobject.idle_add(self.hide)         
                    
        def show_window(self):
            def safe_task():
                self.fullscreen()
                self.volume_button.set_value(float(self.controls.volume.volume_scale.get_value()/ 100))
                self.show_all()
            gobject.idle_add(safe_task)
            

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
        
        def modyfy_background():
            for state in (gtk.STATE_NORMAL, gtk.STATE_PRELIGHT, gtk.STATE_ACTIVE, gtk.STATE_SELECTED, gtk.STATE_INSENSITIVE):
                self.smallscree_area.modify_bg(state, self.smallscree_area.get_colormap().alloc_color("black"))
                self.fullscrean_area.draw.modify_bg(state, self.fullscrean_area.get_colormap().alloc_color("black"))
        gobject.idle_add(modyfy_background)
        
        self.output = None
        self.set_output(self.smallscree_area)
    
    def set_output(self, area):
        self.output = area
        
    
    def get_output(self):
        return self.output
    
    def get_draw(self):
        return self.smallscree_area
     
    def on_full_screen(self):
        self.controls.state_stop(True)
        self.fullscrean_area.show_window()        
        self.set_output(self.fullscrean_area.get_draw())      
        self.controls.state_play(under_pointer_icon=True)
        analytics.action("FullScreanArea");
                
    def set_text(self, text):
        gobject.idle_add(self.fullscrean_area.set_text, text)
        
    def on_small_screen(self):
        self.controls.state_stop(True)
        self.set_output(self.smallscree_area)
        self.fullscrean_area.hide_window()
        self.controls.state_play(under_pointer_icon=True)
            
    def draw_video(self, message):
        message_name = message.structure.get_name()
        
        if message_name == "prepare-xwindow-id":
            imagesink = message.src
            
            def safe_task():
                imagesink.set_property("force-aspect-ratio", True)
                self.show_all()
                imagesink.set_xwindow_id(self.get_output().window.xid)
                
                '''trick to amoid possible black screen in movie_area'''
                threading.Timer(0.5, lambda: self.get_output().set_size_request(-1, 400)).start()
                
            gobject.idle_add(safe_task)
            

                  
            
            

