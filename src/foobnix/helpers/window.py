#-*- coding: utf-8 -*-
'''
Created on 27 окт. 2010

@author: ivan
'''

import os
import gtk
import time
import logging
import threading

from foobnix.fc.fc import FC
from foobnix.util.key_utils import is_key
from foobnix.util.const import ICON_FOOBNIX
from foobnix.util.text_utils import split_string
from foobnix.util.file_utils import get_full_size
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name


class ChildTopWindow(gtk.Window):
    def __init__(self, title=None, width=None, height=None):         
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        if title:
            self.set_title(title)
        
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)
        self.set_border_width(5)
        try:
            self.set_icon_from_file (self.get_fobnix_logo())
        except TypeError: pass
        if width and height:
            self.set_size_request(width, height)
        self.connect("delete-event", self.hide_window)
        self.connect("key-press-event", self.on_key_press)
        
        self.hide_on_escape = True
        self.set_opacity(FC().window_opacity)
        self.is_rendered = True
        
    def set_hide_on_escape(self, hide_on_escape=True):
        self.hide_on_escape = hide_on_escape
        
    def get_fobnix_logo(self):
        return get_foobnix_resourse_path_by_name(ICON_FOOBNIX)
    
    def on_key_press(self, w, e):
        if self.hide_on_escape and is_key(e, 'Escape'):
            self.hide()
    
    def hide_window(self, *a):
        self.hide()
        return True
    
    def show(self):
        self.show_all()

class CopyProgressWindow(gtk.Dialog):
    def __init__(self, title, file_list, width=None, hight=None):
        gtk.Dialog.__init__(self, title)
        if width and hight:
            self.set_default_size(width, hight)
        
        self.set_icon_from_file (get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        self.set_resizable(True)
        self.set_border_width(5)
        self.total_size = get_full_size(file_list)
        
        self.label_from = gtk.Label()
        self.label_to = gtk.Label()
        self.pr_label = gtk.Label(_("Total progress"))
        
        self.pr_bar = gtk.ProgressBar()
        self.total_pr_bar = gtk.ProgressBar()
        
        self.add_button(_("Stop"), gtk.RESPONSE_REJECT)
        
        self.vbox.pack_start(self.label_from, False)
        self.vbox.pack_start(self.label_to, False)
        self.vbox.pack_start(self.pr_bar, False)
        self.vbox.pack_start(self.pr_label, False)
        self.vbox.pack_start(self.total_pr_bar, False)
        self.exit = False        
        self.show_all()
    
    def progress(self, file, dest_folder):
        size = os.path.getsize(file)
        new_file = os.path.join(dest_folder, os.path.basename(file))
        counter = 0
        got_store = 0
        while True:
            if not os.path.exists(new_file):
                counter += 1
                time.sleep(0.1)
                if counter > 100:
                    logging.error("Can't create file %s" % new_file)
                    return
                continue
                
            got = os.path.getsize(new_file)
            definite = got - got_store
            got_store = got
            
            fraction = (got+0.0)/size
            self.pr_bar.set_fraction(fraction)
            self.pr_bar.set_text("%.0f%%" % (100 * fraction))
            
            fraction = (definite+0.0)/self.total_size + self.total_pr_bar.get_fraction()
            self.total_pr_bar.set_fraction(fraction)
            self.total_pr_bar.set_text("%.0f%%" % (100 * fraction))
            time.sleep(0.1)
            if self.exit:
                raise threading.ThreadError("the thread is stopped")
            if got == size:
                break

class MessageWindow(gtk.MessageDialog):
    def __init__(self, title, type=gtk.MESSAGE_INFO, text=None, parent=None,
                 buttons=None, flags=0, func=None, args=(), func1=None, args1=()):
        text = split_string(text, 40)
        gtk.MessageDialog.__init__(self, parent, flags, type, buttons, text)
        
        self.set_title(title)
        self.show_all()
        id = self.run()
        if id != gtk.RESPONSE_NONE:
            if func and id in [gtk.RESPONSE_OK, gtk.RESPONSE_APPLY, gtk.RESPONSE_ACCEPT, gtk.RESPONSE_YES]:
                func(args) if args else func()
            if func1 and id in [gtk.RESPONSE_NO, gtk.RESPONSE_CLOSE, gtk.RESPONSE_CANCEL, gtk.RESPONSE_REJECT]:
                func1(args1) if args else func1()
        time.sleep(0.1) #otherwise can be freezes
        self.destroy()
        #gobject.timeout_add(100, self.destroy)
        
        
    def delete_event(self, widget, event, data=None):
        self.response(gtk.RESPONSE_NONE)
        return True