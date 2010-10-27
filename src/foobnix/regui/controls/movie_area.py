from foobnix.regui.model.signal import FControl
import gtk
from foobnix.helpers.my_widgets import notetab_label

class MovieDrawingArea(FControl, gtk.Frame):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Frame.__init__(self)
        
        label = notetab_label(self.hide)
        
        self.set_label_widget(label)
        self.set_label_align(1.0, 0.0)

        self.set_border_width(0)
        self.drow = gtk.DrawingArea()
        self.add(self.drow)
    
    def draw_video(self, message):
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            self.show_all()
            self.drow.set_size_request(-1, 400)
            imagesink.set_xwindow_id(self.drow.window.xid)
