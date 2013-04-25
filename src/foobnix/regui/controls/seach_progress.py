#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''

import time
import threading

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject


class SearchProgress(Gtk.Spinner):
    def __init__(self, controls):
        Gtk.Spinner.__init__(self)
        self.controls = controls
        self.set_no_show_all(True)
        self.main_window = self.controls.main_window
        self.set_size_request(30, 30)
        self.label = Gtk.Label()
        self.label.show()
        self.set_halign(Gtk.Align.END)
        self.set_valign(Gtk.Align.END)
    
    def start(self, text=None):
        if not text:
            text = _("Process...")

        def safe_task():
            self.label.set_text(text)
            self.show()
            super(SearchProgress, self).start()
        GObject.idle_add(safe_task, priority=GObject.PRIORITY_DEFAULT_IDLE - 10)

    def stop(self):
        def safe_task():
            super(SearchProgress, self).stop()
            self.hide()
        GObject.idle_add(safe_task)
        
    def background_spinner_wrapper(self, task, in_graphic_thread, *args):
        self.start()

        def thread_task(*args):
            def safe_task(*args):
                try:
                    task(*args)
                finally:
                    self.stop()
            if in_graphic_thread:
                GObject.idle_add(safe_task, *args)
            else:
                Gdk.threads_init()
                Gdk.threads_enter()
                safe_task(*args)
                Gdk.threads_leave()
      
        t = threading.Thread(target=thread_task, args=(args))
        t.start()

    def move_to_coord(self, *a):
        pl_tree = self.controls.notetabs.get_current_tree()
        pl_tree_alloc = pl_tree.get_allocation()
        scrolled_pl_tree_alloc = pl_tree.scroll.get_allocation()
        try:
            pl_tree_width = pl_tree_alloc.width
            scrolled_pl_tree_width = scrolled_pl_tree_alloc.width
        except:
            pl_tree_width = 0
            scrolled_pl_tree_width = 0
        try:
            pl_tree_height = pl_tree_alloc.height
            scrolled_pl_tree_height = scrolled_pl_tree_alloc.height
        except:
            pl_tree_height = 0
            scrolled_pl_tree_height = 0

        self.set_margin_bottom(scrolled_pl_tree_height - pl_tree_height + 5)
        self.set_margin_right(scrolled_pl_tree_width - pl_tree_width + 5)

    def show(self):
        super(SearchProgress, self).show()
        self.move_to_coord() 