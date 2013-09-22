#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from foobnix.util import idle_task


class SearchProgress(Gtk.Spinner):
    def __init__(self, controls):
        Gtk.Spinner.__init__(self)
        self.controls = controls
        self.set_no_show_all(True)
        self.main_window = self.controls.main_window
        self.set_size_request(30, 30)
        self.set_halign(Gtk.Align.END)
        self.set_valign(Gtk.Align.END)

        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(255, 255, 255))

    @idle_task
    def start(self, text=None):
        self.show()
        super(SearchProgress, self).start()

    @idle_task
    def stop(self):
        super(SearchProgress, self).stop()
        self.hide()

    def background_spinner_wrapper(self, task, *args):
        self.start()
        while Gtk.events_pending():
            Gtk.main_iteration()
        try:
            task(*args)
        finally:
            self.stop()

    '''def background_spinner_wrapper(self, task, in_graphic_thread, *args):
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
                safe_task(*args)

        t = threading.Thread(target=thread_task, args=(args))
        t.start()'''

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