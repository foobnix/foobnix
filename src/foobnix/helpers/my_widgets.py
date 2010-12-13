#-*- coding: utf-8 -*-
'''
Created on 30 авг. 2010

@author: ivan
'''
import gtk
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
        

class ImageButton(gtk.Button):
    def __init__(self, stock_image, func=None, tooltip_text=None):
        gtk.Button.__init__(self)
        self.set_relief(gtk.RELIEF_NONE)
        if tooltip_text:
            self.set_tooltip_text(tooltip_text)
        img = gtk.image_new_from_stock(stock_image, gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.set_image(img)
        if func:
            self.connect("clicked", lambda * a: func())
        

class ToggleImageButton(gtk.ToggleButton):
    def __init__(self, gtk_stock, func=None, param=None):
        gtk.ToggleButton.__init__(self)

        if param and func:             
            self.connect("toggled", lambda * a: func(param))
        elif func:
            self.connect("toggled", lambda * a: func())         
                
        self.set_relief(gtk.RELIEF_NONE)
        img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
        self.add(img)

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
    def __init__(self, text="×", angel=0, func=None, arg=None, func1=None):        
        gtk.EventBox.__init__(self)
        self.text = text
        
        self.selected = False
        
        self.label = gtk.Label()
        self.set_not_underline()
        
        self.label.set_angle(angel)
        
        self.connect("enter-notify-event", lambda * a : self.set_underline())
        self.connect("leave-notify-event", lambda * a: self.set_not_underline())
        if func and arg:                    
            self.connect("button-press-event", lambda * a: func(arg))
        elif func:
            self.connect("button-press-event", lambda * a: func())
        
        self.func1 = func1

        self.add(self.label)
        self.show_all()
        
        
        
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
    
    
        

def notetab_label(func=None, arg=None, angel=0, symbol="×"):
    """label"""
    label = gtk.Label(symbol)
    label.show()
    label.set_angle(angel)
    
    event = gtk.EventBox()
    event.show()
    event.add(label)    
    
    """change style of event"""
    style = event.get_style().copy()
    colour = style.bg[gtk.STATE_NORMAL]
    style.bg[gtk.STATE_ACTIVE] = colour
    event.set_style(style)
            
    event.connect("enter-notify-event", lambda w, e:w.get_child().set_markup("<u>" + symbol + "</u>"))
    event.connect("leave-notify-event", lambda w, e:w.get_child().set_markup(symbol))
    if func and arg:                    
        event.connect("button-press-event", lambda * a: func(arg))
    elif func:
        event.connect("button-press-event", lambda * a: func())
    event.show()
    return event
