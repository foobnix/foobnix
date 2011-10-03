#-*- coding: utf-8 -*-
'''
Created on 30 авг. 2010

@author: ivan
'''
import gtk
from foobnix.helpers.pref_widgets import HBoxDecorator
from foobnix.fc.fc import FC
#from desktopcouch.replication_services.example import is_active

def open_link_in_browser(uri):
    link = gtk.LinkButton(uri)
    link.clicked()
    
class PespectiveToogledButton(gtk.ToggleButton):
    def __init__(self, title, gtk_stock, tooltip=None):
        gtk.ToggleButton.__init__(self, title)
        if not tooltip:
            tooltip = title
        
        self.set_tooltip_text(tooltip)
                
        self.set_relief(gtk.RELIEF_NONE)
        label = self.get_child()
        self.remove(label)
        
        vbox = gtk.VBox(False, 0)
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        vbox.add(img)
        vbox.add(gtk.Label(title))
        vbox.show_all()
        
        self.add(vbox)

class ButtonStockText(gtk.Button):
    def __init__(self, title, gtk_stock, tooltip=None):
        gtk.Button.__init__(self, "")
        if not tooltip:
            tooltip = title
        
        self.set_tooltip_text(tooltip)
        
        label = self.get_child()
        self.remove(label)
        
        box = gtk.HBox(False, 0)
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        box.add(img)
        box.add(gtk.Label(title))
        box.show_all()
        
        self.add(box)        
        
class InsensetiveImageButton(gtk.EventBox):
    def __init__(self, stock_image, size=gtk.ICON_SIZE_LARGE_TOOLBAR):
        gtk.EventBox.__init__(self)
        self.button = gtk.Button()
        #self.button.set_sensitive(False)
        self.button.set_focus_on_click(False)
        self.button.set_relief(gtk.RELIEF_NONE)
        img = gtk.image_new_from_stock(stock_image, size)
        self.button.set_image(img)
        self.add(HBoxDecorator(self.button, gtk.Label("R")))
        
        #self.button.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))
        
        self.connect("button-press-event", self.on_click)
        self.button.connect("button-press-event", self.on_click1)
        
        self.insensetive = False
    
    def on_click1(self, *a):
        pass
        
    def on_click(self, *a):
        self.insensetive = not self.insensetive
        #self.button.set_sensitive(self.insensetive)
    
     
        
                

class ImageButton(gtk.Button):
    def __init__(self, stock_image, func=None, tooltip_text=None, size=gtk.ICON_SIZE_LARGE_TOOLBAR):
        gtk.Button.__init__(self)
        self.set_relief(gtk.RELIEF_NONE)
        self.set_focus_on_click(False)
        if tooltip_text:
            self.set_tooltip_text(tooltip_text)
        img = gtk.image_new_from_stock(stock_image, size)
        self.set_image(img)
        if func:
            self.connect("clicked", lambda * a: func())
        

class ToggleImageButton(gtk.ToggleButton):
    def __init__(self, gtk_stock, func=None, param=None):
        gtk.ToggleButton.__init__(self)
        self.set_relief(gtk.RELIEF_NONE)
        self.set_focus_on_click(False)
        if param and func:             
            self.connect("toggled", lambda * a: func(param))
        elif func:
            self.connect("toggled", lambda * a: func())         
                
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        self.add(img)
        
class ToggleWidgetButton(gtk.ToggleButton):
    def __init__(self, widget, func=None, param=None):
        gtk.ToggleButton.__init__(self)

        if param and func:             
            self.connect("toggled", lambda * a: func(param))
        elif func:
            self.connect("toggled", lambda * a: func())         
                
        self.set_relief(gtk.RELIEF_NONE)        
        self.add(widget)        

def tab_close_button(func=None, arg=None, stock=gtk.STOCK_CLOSE):
    """button"""
    button = gtk.Button()
    button.set_relief(gtk.RELIEF_NONE)
    img = gtk.image_new_from_stock(stock, gtk.ICON_SIZE_MENU)
    button.set_image(img)
    if func and arg:           
        button.connect("button-press-event", lambda * a: func(arg))
    elif func:
        button.connect("button-press-event", lambda * a: func())
    button.show()
    return button



class EventLabel(gtk.EventBox):
    def __init__(self, text="×", angle=0, func=None, arg=None, func1=None):        
        gtk.EventBox.__init__(self)
        self.text = text
        self.set_visible_window(False)
        self.selected = False
        
        self.label = gtk.Label()
        self.set_not_underline()
        
        self.label.set_angle(angle)
        
        self.connect("enter-notify-event", lambda * a : self.set_underline())
        self.connect("leave-notify-event", lambda * a: self.set_not_underline())
        if func and arg:                    
            self.connect("button-press-event", lambda * a: func(arg))
        elif func:
            self.connect("button-press-event", lambda * a: func())
        
        self.func1 = func1

        self.add(self.label)
        self.show_all()
     
    def set_markup(self, text):
        self.text = text
        self.label.set_markup(text)
        
    def set_underline(self):
        if self.selected:
            self.label.set_markup("<b><u>" + self.text + "</u></b>")
        else:           
            self.label.set_markup("<u>" + self.text + "</u>")
    
    def set_not_underline(self):
        if self.selected:              
            self.label.set_markup("<b>" + self.text + "</b>")
        else:
            self.label.set_markup(self.text)
        
    def set_active(self):
        self.selected = True
        self.set_underline()
    
    def set_not_active(self):
        self.selected = False
        self.set_not_underline()
    
def notetab_label(func=None, arg=None, angle=0, symbol="×"):
    """label"""
    label = gtk.Label(symbol)
    label.show()
    label.set_angle(angle)
    
    event = gtk.EventBox()
    event.show()
    event.add(label)    
    event.set_visible_window(False)
    
    event.connect("enter-notify-event", lambda w, e:w.get_child().set_markup("<u>" + symbol + "</u>"))
    event.connect("leave-notify-event", lambda w, e:w.get_child().set_markup(symbol))
    if func and arg:                    
        event.connect("button-press-event", lambda * a: func(arg))
    elif func:
        event.connect("button-press-event", lambda * a: func())
    event.show()
    return event

class AlternateVolumeControl (gtk.DrawingArea):
    def __init__(self, levels, h_border=None, v_border=None):
        gtk.DrawingArea.__init__(self)
        self.show ()
        self.volume = FC().volume
        self.connect("expose-event", self.expose_handler, levels, h_border, v_border)
       
    def set_volume (self, vol):
        self.volume = vol
        self.queue_draw()
        
    def expose_handler(self, area, event, levels, h_border, v_border) :
        gc = self.window.new_gc ()
        area_width = area.get_allocation().width
        area_height = area.get_allocation().height
        if not h_border:
            h_border = area_width/100
        if not v_border:
            v_border = area_height/100 
        width = area_width - 2*h_border
        height = area_height - 2*v_border
        
        '''to get the height times the number levels of volume 
           (for the smooth growth of the height)'''
        height = height - height%levels if height >= levels else levels
        
        step = width/(levels - 1)
        gc.line_width = step/2
        x = h_border
        y = height + v_border
        label = width * self.volume/100.0 + h_border
        
        i = 1
        while i < levels:
            if x < label:
                gc.set_rgb_fg_color(gtk.gdk.color_parse("orange red"))#@UndefinedVariable
            else:
                gc.set_rgb_fg_color(gtk.gdk.color_parse("white"))#@UndefinedVariable
            if x != h_border:
                area.window.draw_line (gc, x, y, x, 
                    (int) (round (y - height / (width *1.0 / (x - h_border))))) 
            i += 1
            x += step
        
        
        
        
        
        
        
        