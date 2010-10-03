#-*- coding: utf-8 -*-
'''
Created on Oct 3, 2010

@author: anton.komolov
'''
import gtk
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.regui.model import FModel

class DMBean(gtk.ProgressBar):
    def __init__(self, bean):
        gtk.ProgressBar.__init__(self)
        self.set_text(bean.path)

class DownloadManager(gtk.Window, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title("Download Manager")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(True)
        self.connect("delete-event", self.hide_window)
        self.connect("configure-event", self.on_configure_event)
        self.set_icon(self.controls.trayicon.get_pixbuf())

        self.beans = []

        vbox = gtk.VBox(False, 0)
        vbox.show()

        vbox.pack_start(self.line_add(), False, False, 0)
        vbox.pack_start(self.line_control(), False, False, 0)
        vbox.pack_start(self.line_list(), True, True, 0)

        self.add(vbox)

    def line_add(self):
        hbox = gtk.HBox(False, 0)
        hbox.show()

        self.entry = gtk.Entry()
        self.entry.show()

        bt_add = gtk.Button("Add")
        bt_add.show()
        bt_add.connect("clicked", self.add_click)

        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_start(bt_add, False, False, 0)

        return hbox

    def line_control(self):
        hbox = gtk.HBox(True, 0)
        hbox.show()

        bt_start = gtk.Button("Start")
        bt_start.show()
        bt_stop = gtk.Button("Stop All")
        bt_stop.show()
        bt_clear = gtk.Button("Clear list")
        bt_clear.show()
        bt_pref = gtk.Button("Preferences")
        bt_pref.show()

        hbox.pack_start(bt_start, False, True, 0)
        hbox.pack_start(bt_stop, False, True, 0)
        hbox.pack_start(bt_clear, False, True, 0)
        hbox.pack_start(bt_pref, False, True, 0)

        return hbox

    def line_list(self):
        swin = gtk.ScrolledWindow()
        swin.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        swin.show()

        vbox = gtk.VBox(False, 0)
        vbox.show()

        self.dm_list = vbox
        swin.add_with_viewport(vbox)

        return swin

    def add_click(self, *a):
        bean = FModel(path=self.entry.get_text())
        self.add_bean(bean)

    def add_bean(self, bean):
        dmbean = DMBean(bean)
        dmbean.show()
        self.beans.append(dmbean)
        self.dm_list.pack_start(dmbean, False, False, 0)

    def hide_window(self, *a):
        self.hide()
        return True

    def destroy(self):
        self.hide()
        return True

    def on_configure_event(self, w, e):
        FC().dm_window_size = [e.x, e.y, e.width, e.height]

    def on_save(self, *a):
        pass

    def on_load(self):
        cfg = FC().dm_window_size
        if cfg:
            self.set_default_size(cfg[2], cfg[3])
            self.move(cfg[0], cfg[1])
