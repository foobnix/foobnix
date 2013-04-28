'''
Created on Nov 5, 2010

@author: ivan
'''
from gi.repository import Gtk
from gi.repository import GObject
import logging

from foobnix.fc.fc import FC
from foobnix.helpers.dialog_entry import file_chooser_dialog
from foobnix.util.pix_buffer import create_pixbuf_from_resource
from foobnix.helpers.window import ChildTopWindow


class IconBlock(Gtk.HBox):
    
    temp_list = FC().all_icons[:]
     
    def __init__(self, text, controls, filename, all_icons=temp_list):
        Gtk.HBox.__init__(self, False, 0)
        
        self.controls = controls
        
        self.combobox = Gtk.ComboBox()
        self.entry = Gtk.Entry()
        self.entry.set_size_request(300, -1)
        self.entry.set_property("margin", 0)
        if filename:
            self.entry.set_text(filename)
        else:
            filename = ""
        
        
        self.all_icons = all_icons
        
        self.modconst = ModelConstructor(all_icons)
               
        self.combobox.set_model(self.modconst.model)
        
        if filename in self.all_icons:
            self.combobox.set_active(self.all_icons.index(filename))
        else:
            self.combobox.set_active(0)
            self.on_change_icon()
            logging.warning("Icon " + filename + " is absent in list of icons")
        
        pix_render = Gtk.CellRendererPixbuf()
        self.combobox.pack_start(pix_render, 0)
        self.combobox.add_attribute(pix_render, 'pixbuf', 0)
        
        button = Gtk.Button("Choose", Gtk.STOCK_OPEN)
        button.connect("clicked", self.on_file_choose)
        
        button_2 = Gtk.Button("Delete", Gtk.STOCK_DELETE)
        button_2.connect("clicked", self.on_delete)
        
        label = Gtk.Label(text)
        if text: # if iconblock without label
            label.set_size_request(80, -1)
        
        self.pack_start(label, False, False, 0)
        self.pack_start(self.combobox, False, False, 0)
        self.pack_start(self.entry, True, True, 0)
        self.pack_start(button, False, False, 0)
        self.pack_start(button_2, False, False, 0)
        
        self.combobox.connect("changed", self.on_change_icon)
        
    def on_file_choose(self, *a):
        file = file_chooser_dialog("Choose icon")
        if not file:
            return None
        self.entry.set_text(file[0])
        self.modconst.apeend_icon(self, file[0], True)
        self.all_icons.append(file[0])
    
    def on_change_icon(self, *a):        
        active_id = self.combobox.get_active()
        if active_id >= 0:
            icon_name = self.combobox.get_model()[active_id][1]
            self.entry.set_text(icon_name)
        #FC().static_tray_icon = True
        #self.controls.trayicon.on_dynamic_icons(None)
    
    def get_active_path(self):
        active_id = self.combobox.get_active()
        return self.combobox.get_model()[active_id][1]
            
    def on_delete(self, *a):
        active_id = self.combobox.get_active()
        rem_icon = self.entry.get_text()
        iter = self.modconst.model.get_iter(active_id)
        try:
            if self.all_icons.index(rem_icon) > 4:
                self.all_icons.remove(rem_icon)
                self.modconst.delete_icon(iter)
                self.combobox.set_active(0)
            else:
                error_window = ChildTopWindow("Error")
                label = Gtk.Label("You can not remove a standard icon")
                error_window.add(label)
                error_window.show()
        except ValueError, e:
            logging.error("There is not such icon in the list" + str(e))        
        
class FrameDecorator(Gtk.Frame):
    def __init__(self, text, widget):
        Gtk.Frame.__init__(self, label=text)
        self.add(widget)
        
class ChooseDecorator(Gtk.HBox):
    def __init__(self, parent, widget):
        Gtk.HBox.__init__(self, False, 0)
        self._widget = widget
        self.button = Gtk.RadioButton.new_from_widget(parent)
        
        self.on_toggle()
        self.button.connect("toggled", self.on_toggle)
        box = HBoxDecorator(self.button, self._widget)
        self.pack_start(box, False, True, 0)
    
    def on_toggle(self, *a):
        if self.button.get_active():
            self._widget.set_sensitive(True)
        else:
            self._widget.set_sensitive(False)
    
    def get_radio_button(self): 
        return self.button       

class VBoxDecorator(Gtk.VBox):
    def __init__(self, *args):
        Gtk.VBox.__init__(self, False, 0)
        for widget in args:
            self.pack_start(widget, False, False, 0)
        self.show_all()

class HBoxDecorator(Gtk.HBox):
    def __init__(self, *args):
        Gtk.HBox.__init__(self, False, 0)
        for widget in args:
            self.pack_start(widget, False, False, 0)
        self.show_all()

class HBoxDecoratorTrue(Gtk.HBox):
    def __init__(self, *args):
        Gtk.HBox.__init__(self, False, 0)
        for widget in args:
            self.pack_start(widget, True, True, 0)
        self.show_all()


class HBoxLableEntry(Gtk.HBox):
    def __init__(self, text, entry):
        Gtk.HBox.__init__(self, False, 0)
        self.pack_start(text, False, False, 0)
        self.pack_start(entry, True, True, 0)
        self.show_all()
        
class ModelConstructor():
    
    ICON_SIZE = 24
    
    def __init__(self, all_icons):
        
        self.model = Gtk.ListStore(GObject.TYPE_OBJECT, str)
        
        for icon_name in all_icons:
            self.apeend_icon(None, icon_name)          

    def apeend_icon(self, calling_object, icon_name, active=False):
        pixbuf = create_pixbuf_from_resource(icon_name, self.ICON_SIZE)
        if pixbuf:        
            self.model.append([pixbuf, icon_name])
            if active:
                calling_object.combobox.set_active(len(self.model) - 1)
                
    def delete_icon(self, iter):
        self.model.remove(iter)
