#-*- coding: utf-8 -*-
'''
Created on 30 авг. 2010

@author: ivan
'''

from gi.repository import Gtk
from gi.repository import Gdk

from foobnix.fc.fc import FC
from foobnix.helpers.pref_widgets import HBoxDecorator


def open_link_in_browser(uri):
    link = Gtk.LinkButton(uri)
    link.clicked()
    
class PespectiveToogledButton(Gtk.ToggleButton):
    def __init__(self, title, gtk_stock, tooltip=None):
        Gtk.ToggleButton.__init__(self, title)
        if not tooltip:
            tooltip = title
        
        self.set_tooltip_text(tooltip)
                
        self.set_relief(Gtk.ReliefStyle.NONE)
        label = self.get_child()
        self.remove(label)
        
        vbox = Gtk.VBox(False, 0)
        img = Gtk.Image.new_from_stock(gtk_stock, Gtk.IconSize.MENU)
        vbox.add(img)
        vbox.add(Gtk.Label(title))
        vbox.show_all()
        
        self.add(vbox)

class ButtonStockText(Gtk.Button):
    def __init__(self, title, gtk_stock, tooltip=None):
        Gtk.Button.__init__(self, "")
        if not tooltip:
            tooltip = title
        
        self.set_tooltip_text(tooltip)
        
        label = self.get_child()
        self.remove(label)
        
        box = Gtk.HBox(False, 0)
        img = Gtk.Image.new_from_stock(gtk_stock, Gtk.IconSize.MENU)
        box.add(img)
        box.add(Gtk.Label(title))
        box.show_all()
        
        alignment = Gtk.Alignment(xalign=0.5)
        #alignment.set_padding(padding_top=0, padding_bottom=0, padding_left=10, padding_right=10)
        alignment.add(box)
        
        self.add(alignment)    
        
class InsensetiveImageButton(Gtk.EventBox):
    def __init__(self, stock_image, size=Gtk.IconSize.LARGE_TOOLBAR):
        Gtk.EventBox.__init__(self)
        self.button = Gtk.Button()
        #self.button.set_sensitive(False)
        self.button.set_focus_on_click(False)
        self.button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_stock(stock_image, size)
        self.button.set_image(img)
        self.add(HBoxDecorator(self.button, Gtk.Label("R")))
        
        #self.button.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("red"))
        
        self.connect("button-press-event", self.on_click)
        self.button.connect("button-press-event", self.on_click1)
        
        self.insensetive = False
    
    def on_click1(self, *a):
        pass
        
    def on_click(self, *a):
        self.insensetive = not self.insensetive
        #self.button.set_sensitive(self.insensetive)

class ImageButton(Gtk.Button):
    def __init__(self, stock_image, func=None, tooltip_text=None, size=Gtk.IconSize.LARGE_TOOLBAR):
        Gtk.Button.__init__(self)
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_focus_on_click(False)
        if tooltip_text:
            self.set_tooltip_text(tooltip_text)
        img = Gtk.Image.new_from_stock(stock_image, size)
        self.set_image(img)
        if func:
            self.connect("clicked", lambda * a: func())
        

class ToggleImageButton(Gtk.ToggleButton):
    def __init__(self, gtk_stock, func=None, param=None):
        Gtk.ToggleButton.__init__(self)
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_focus_on_click(False)
        if param and func:             
            self.connect("toggled", lambda * a: func(param))
        elif func:
            self.connect("toggled", lambda * a: func())         
                
        img = Gtk.Image.new_from_stock(gtk_stock, Gtk.IconSize.MENU)
        self.add(img)
        
class ToggleWidgetButton(Gtk.ToggleButton):
    def __init__(self, widget, func=None, param=None):
        Gtk.ToggleButton.__init__(self)

        if param and func:             
            self.connect("toggled", lambda * a: func(param))
        elif func:
            self.connect("toggled", lambda * a: func())         
                
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.add(widget)        


def tab_close_button(func=None, arg=None, stock=Gtk.STOCK_CLOSE):
    """button"""
    button = Gtk.Button()
    button.set_relief(Gtk.ReliefStyle.NONE)
    img = Gtk.Image.new_from_stock(stock, Gtk.IconSize.MENU)
    button.set_image(img)
    if func and arg:           
        button.connect("button-press-event", lambda * a: func(arg))
    elif func:
        button.connect("button-press-event", lambda * a: func())
    button.show()
    return button



class EventLabel(Gtk.EventBox):
    def __init__(self, text="×", angle=0, func=None, arg=None, func1=None):        
        Gtk.EventBox.__init__(self)
        self.text = text
        self.set_visible_window(False)
        self.selected = False
        
        self.label = Gtk.Label()
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
    label = Gtk.Label(symbol)
    label.show()
    label.set_angle(angle)
    
    event = Gtk.EventBox()
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

class AlternateVolumeControl (Gtk.DrawingArea):
    def __init__(self, levels, s_width, interval, v_step):
        Gtk.DrawingArea.__init__(self)
        self.show()
        self.volume = FC().volume
        self.connect("draw", self.draw_callback, levels, s_width, interval, v_step)
       
    def set_volume (self, vol):
        self.volume = vol
        self.queue_draw()
    
    def draw_callback(self, w, cr, levels, s_width, interval, v_step):
        #levels = a number of volume levels (a number of sticks equals level-1)
        #s_width - width of stick
        #interval - interval between sticks
        #v_step - increase the height of the stick
        #all parameters must be integer type
        
        area_width = w.get_allocation().width
        area_height = w.get_allocation().height
        
        h_step = s_width + interval
        width = levels * (s_width + interval) - interval
        height = v_step * (levels - 1)
        
        if width < area_width:
            start_x = (area_width-width)/2
        else:
            start_x = 1

        if height < area_height:
            start_y = area_height - (area_height - height)/2
        else:
            start_y = 0
        
        x = start_x
        y = start_y - 1

        label = FC().volume * width/100.0 + start_x

        i = 0
        while i < levels:
            color = Gdk.color_parse("orange red") if x  < label else Gdk.color_parse("white")
            Gdk.cairo_set_source_color(cr, color)

            cr.move_to(x, start_y)
            cr.line_to(x+s_width, start_y)
            cr.line_to(x+s_width, y)
            cr.line_to(x, y)
            #cr.close_path()
            cr.fill()
            
            i += 1
            x += h_step
            y -= v_step
            
        
        
