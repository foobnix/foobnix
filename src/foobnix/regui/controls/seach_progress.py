#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
import time
import thread
import logging
import threading


class SearchProgressBarOld(Gtk.ProgressBar):
    def __init__(self):
        Gtk.ProgressBar.__init__(self)
        self.set_size_request(20, -1)
        self.set_pulse_step(0.2)
        self.set_fraction(0)
        self.flag = True
        self.started = False
        self.set_text("...")

    def start(self, text=None):
        if text:
            self.set_text(text)
        if self.started:
            return None
            
        self.show_all()
        
        self.flag = True

        def pulse_thread(): 
            self.started = True
            while self.flag:
                self.pulse()
                time.sleep(0.1)
            self.started = False
        thread.start_new_thread(pulse_thread, ())

    def stop(self):
        self.flag = False
        self.set_fraction(0)
     

if True:    # Gtk.pygtk_version >= (2, 22, 0):
    class SearchProgressBarNew(Gtk.Spinner):
        def __init__(self):
            super(SearchProgressBarNew, self).__init__()
            self.set_no_show_all(True)
             

    class SearchProgressBar(SearchProgressBarNew):
        def __init__(self, controls):
            SearchProgressBarNew.__init__(self)
            self.controls = controls
            self.main_window = self.controls.main_window
            self.set_size_request(30, 30)
            self.show()
            self.label = Gtk.Label()
            self.label.show()
            self.spinner_popup = self.create_spinner_popup()
            self.spinner_popup.hide()
            self.spinner_popup.connect_after('map', self.configure_popup, self.controls.main_window) 
    
        def start(self, text=None):
            if not text:
                text = _("Process...")

            def safe_task():
                try:
                    """to avoid bugs in Unity and GnomeFallback"""
                    if (self.main_window.iconified or not self.main_window.props.is_active):
                        return
                except KeyError, e:
                    logging.info(str(e) + " environment not found")                
                self.label.set_text(text)
                self.spinner_popup.show()
                super(SearchProgressBarNew, self).start()
                self.move_to_coord()
            GObject.idle_add(safe_task, priority=GObject.PRIORITY_DEFAULT_IDLE - 10)

        def stop(self):
            def safe_task():
                super(SearchProgressBarNew, self).stop()
                self.spinner_popup.hide()
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

        def create_spinner_popup(self):
            self.main_window.connect("configure-event", self.move_to_coord)
            hbox = Gtk.HBox()
            hbox.pack_start(self, False, False, 0)
            hbox.pack_start(self.label, False, False, 0)
            hbox.show()
            popup = Gtk.Window()
            popup.set_transient_for(self.main_window)
            popup.set_destroy_with_parent(True)
            popup.set_decorated(False)
            popup.set_accept_focus(False)
            popup.set_skip_pager_hint(True)
            popup.set_skip_taskbar_hint(True)
            popup.set_opacity(0.6)
            popup.add(hbox)
            return popup
        
        def move_to_coord(self, *a):
            rect = self.controls.main_window.window.get_frame_extents()
            window_width = rect.width
            window_height = rect.height
            window_x = rect.x
            window_y = rect.y
            popup_width = self.spinner_popup.get_allocation().width
            popup_height = self.spinner_popup.get_allocation().height
            if self.controls.coverlyrics.get_property("visible"):
                coverlyrics_width = self.controls.coverlyrics.get_allocation().width
            else:
                coverlyrics_width = 0
            statusbar_height = self.controls.statusbar.get_allocation().height
            try:
                pl_tree_width = self.controls.notetabs.get_current_tree().get_allocation().width
            except:
                pl_tree_width = 7
            notetabs_width = self.controls.notetabs.get_allocation().width
            try:
                pl_tree_height = self.controls.notetabs.get_current_tree().get_allocation().height
                notetabs_height = self.controls.notetabs.get_current_tree().scroll.get_allocation().height + 5
            except:
                pl_tree_height = 0
                notetabs_height = 7
            self.spinner_popup.move(window_x + window_width - popup_width - coverlyrics_width - (notetabs_width - pl_tree_width),
                                    window_y + window_height - popup_height - statusbar_height - (notetabs_height - pl_tree_height))
            
        def configure_popup(self, popup, parent):
            popup.window.set_keep_above(False)
            popup.set_transient_for(parent)

        
else:
    class SearchProgressBar(SearchProgressBarOld):
        def __init__(self, controls):
                SearchProgressBarOld.__init__(self)
