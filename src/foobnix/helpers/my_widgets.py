#-*- coding: utf-8 -*-
'''
Created on 30 авг. 2010

@author: ivan
'''
import gtk

def tab_close_button(func=None, arg=None):
    """button"""
    button = gtk.Button()
    button.set_relief(gtk.RELIEF_NONE)
    img = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
    button.set_image(img)
    if func:           
        button.connect("event", func, arg)
    button.show()
    return button

def notetab_label(func=None, arg=None, angel=0, symbol = "×"):
    """label"""
    label = gtk.Label(symbol)
    label.show()
    label.set_angle(angel)
    
    event = gtk.EventBox()
    event.show()
    event.add(label)    
            
    event.connect("enter-notify-event", lambda w, e:w.get_child().set_markup("<u>" + symbol + "</u>"))
    event.connect("leave-notify-event", lambda w, e:w.get_child().set_markup(symbol))
    if func and arg:                    
        event.connect("button-press-event", lambda *a: func(arg))
    elif func:
        event.connect("button-press-event", lambda *a: func())
    event.show()
    return event
