'''
Created on Oct 21, 2010

@author: ivan
'''
import gtk
KEY_DELETE = 'Delete'
KEY_RETURN = 'Return'

def is_key(event, key_const):
    return gtk.gdk.keyval_name(event.keyval) == key_const

def is_key_control(event): 
    return event.state == gtk.gdk.CONTROL_MASK

def is_key_shift(event): 
    return event.state == gtk.gdk.SHIFT_MASK

def is_key_super(event): 
    return event.state == gtk.gdk.SUPER_MASK

def is_key_alt(event):
    return event.state == gtk.gdk.MOD1_MASK | gtk.gdk.MOD2_MASK

