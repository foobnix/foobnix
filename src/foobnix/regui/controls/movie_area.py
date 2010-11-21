from foobnix.regui.model.signal import FControl
import gtk
from foobnix.helpers.my_widgets import notetab_label
from foobnix.helpers.window import ChildTopWindow
from foobnix.util.mouse_utils import is_double_left_click

class EventDecorator(gtk.EventBox):
    def __init__(self, widget, func=None, arg=None):
        gtk.EventBox.__init__(self)
        self.add(widget)   
       
        def task(w, e):
            if is_double_left_click(e):
                if func and arg: func(arg)
                elif func: func()
                    
        self.connect("button-press-event", task)
        

class FullScreanArea(ChildTopWindow):
        def __init__(self, on_hide_callback):
            ChildTopWindow.__init__(self, "movie")
            self.on_hide_callback = on_hide_callback
            
            self.drow = gtk.DrawingArea()
            self.set_resizable(True)
            self.set_border_width(0)
            
            event = EventDecorator(self.drow, self.on_hide_callback)
            
            self.add(event)

        def get_draw(self):
            return self.drow
            
        def hide_window(self, *a):
            self.hide()            
            return True
        
        def show_window(self):
            self.show_all()
            self.fullscreen()

class MovieDrawingArea(FControl, gtk.Frame):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Frame.__init__(self)
              
        self.set_label_widget(notetab_label(self.hide))
        self.set_label_align(1.0, 0.0)
        self.set_border_width(0)
        
        
        self.smallscree_area = gtk.DrawingArea()
        event = EventDecorator(self.smallscree_area, self.on_full_screen)
        self.add(event)
        
        self.fullscrean_area = FullScreanArea(self.on_small_screen)
        
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
            
            

