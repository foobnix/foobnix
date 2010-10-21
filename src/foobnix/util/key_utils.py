'''
Created on Oct 21, 2010

@author: ivan
'''
import gtk
KEY_DELETE =  'Delete'
KEY_RETURN =  'Return'

def is_key(event, key_const):
    return gtk.gdk.keyval_name(event.keyval) == key_const
    

