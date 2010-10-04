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
from foobnix.dm.dm_bean import DMBean

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

    def _add_button(self, text='Ok', stock=None, func=None, param=None):
        bt = gtk.Button(text)
        if stock:
            image = gtk.Image()
            image.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
            bt.set_image(image)
        if func:
            if param:
                bt.connect("clicked", lambda * a: func(param))
            else:
                bt.connect("clicked", lambda * a: func())
        bt.show()
        return bt


    def line_add(self):
        hbox = gtk.HBox(False, 0)
        hbox.show()

        self.entry = gtk.Entry()
        self.entry.show()

        bt_add = self._add_button("Add", gtk.STOCK_ADD, self.add_click)

        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_start(bt_add, False, False, 0)

        return hbox

    def line_control(self):
        hbox = gtk.HBox(True, 0)
        hbox.show()

        _buttons = [["Start All", gtk.STOCK_MEDIA_PLAY, self.start_all],
                   ["Stop All", gtk.STOCK_MEDIA_STOP, self.stop_all],
                   ["Clear list", gtk.STOCK_OK, self.clear_all],
                   ["Preferences", gtk.STOCK_PREFERENCES, self.controls.show_preferences]]
        for b in _buttons:
            bt = self._add_button(*b)
            hbox.pack_start(bt, False, True, 0)

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

    def start_all(self):
        for dmbean in self.beans:
            dmbean.start()

    def stop_all(self):
        for dmbean in self.beans:
            dmbean.stop()

    def clear_all(self):
        beans = self.beans[:]
        for dmbean in beans:
            dmbean.clear()

    def add_click(self):
        bean = FModel(text = self.entry.get_text(), path = self.entry.get_text())
        self.add_bean(bean)

    def add_bean(self, bean):
        dmbean = DMBean(bean, self.on_clear_dmbean)
        dmbean.show()
        self.beans.append(dmbean)
        self.dm_list.pack_start(dmbean, False, False, 0)

    def on_clear_dmbean(self, dmbean):
        self.beans.remove(dmbean)
        print 'ACTIVE BEANS', self.beans
        dmbean.destroy()

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
