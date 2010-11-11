'''
Created on Nov 5, 2010

@author: ivan
'''
import gtk
import gobject
from foobnix.helpers.dialog_entry import file_chooser_dialog
from foobnix.util.pix_buffer import create_pixbuf_from_resource

class IconBlock(gtk.HBox):
    ICON_SIZE = 24
    ICON_LIST = ["foobnix_icon.svg", "foobnix.png", "foobnix-pause.jpg", "foobnix-stop.jpg", "foobnix-radio.jpg"]
    
    def __init__(self, text):
        gtk.HBox.__init__(self, False, 0)
        
        self.combobox = gtk.ComboBox()
        self.entry = gtk.Entry()
        self.entry.set_size_request(350, -1)
        
        self.combobox.connect("changed", self.on_change_icon)
        self.model = gtk.ListStore(gobject.TYPE_OBJECT, str)
        
        for icon_name in self.ICON_LIST:
            self.apeend_icon(icon_name)
            
        self.combobox.set_model(self.model)
        
        self.combobox.set_active(0)
                
        pix_render = gtk.CellRendererPixbuf()
        self.combobox.pack_start(pix_render)        
        self.combobox.add_attribute(pix_render, 'pixbuf', 0)
        
        button = gtk.Button("Choose")
        button.connect("clicked",self.on_file_choose)
        
        label = gtk.Label(text)
        label.set_size_request(80, -1)
        
        self.pack_start(label, False, False)
        self.pack_start(self.combobox, False, False)
        self.pack_start(self.entry, True, True)
        self.pack_start(button, False, False)
    
    def apeend_icon(self, icon_name, active=False):
        pixbuf = create_pixbuf_from_resource(icon_name, self.ICON_SIZE)
        if pixbuf:        
            self.model.append([pixbuf, icon_name])
            if active:
                self.combobox.set_active(len(self.model)-1)
    
    def on_file_choose(self, *a):
        file = file_chooser_dialog("Choose icon")
        self.entry.set_text(file[0])
        self.apeend_icon(file[0],True)
    
    def on_change_icon(self, *a):        
        active_id = self.combobox.get_active()
        icon_name = self.combobox.get_model()[active_id][1]
        self.entry.set_text(icon_name)
        
class FrameDecorator(gtk.Frame):
    def __init__(self, text, widget):
        gtk.Frame.__init__(self, text)
        self.add(widget)
        
class ChooseDecorator(gtk.HBox):
    def __init__(self, parent, widget):
        gtk.HBox.__init__(self,False,0)
        self.widget = widget
        self.button = gtk.RadioButton(parent)
        self.button.connect("toggled", self.on_toggle)
        box = HBoxDecorator(self.button, self.widget)
        self.pack_start(box, False, True)
    
    def on_toggle(self, *a):
        if self.button.get_active():
            self.widget.set_sensitive(True)
        else:
            self.widget.set_sensitive(False)
    
    def get_radio_button(self): 
        return self.button       

class VBoxDecorator(gtk.VBox):
    def __init__(self, *args):
        gtk.VBox.__init__(self, False, 0)
        for widget in args:
            self.pack_start(widget, False, False) 
        self.show_all()

class HBoxDecorator(gtk.HBox):
    def __init__(self, *args):
        gtk.HBox.__init__(self, False, 0)
        for widget in args:
            self.pack_start(widget, False, False)             
