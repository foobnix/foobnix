#-*- coding: utf-8 -*-
'''
Created on Oct 4, 2010

@author: anton.komolov
'''
import gtk
import random
import thread
import time

class DMBean(gtk.HBox):
    STATE_READY = 0
    STATE_DOWNLOAD = 1
    STATE_COMPLITE = 2
    STATE_STOP_THREAD = 3
    def __init__(self, bean, on_clear):
        gtk.HBox.__init__(self, False, 0)
        self._on_clear = on_clear
        self.bean = bean

        """for test doenload"""
        self.total_size = random.randrange(5*1024*1024, 15*10124*1024, 1024)
        self.speed = random.randrange(500, 1024)*1024
        self.ping = random.random()*2
        self.cur_size = 0

        self.label = gtk.Label(bean.text)
        self.label.show()

        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_text(bean.path)
        self.progressbar.hide()

        toolbar = gtk.Toolbar()
        toolbar.show()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_show_arrow(False)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)

        self._state = self.STATE_READY
        self.start_stop = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
        self.start_stop.show()
        self.start_stop.set_tooltip_text('Start download')
        self.start_stop.connect("clicked", self.on_start_stop)
        self.toolbutton_clear = gtk.ToolButton(gtk.STOCK_CLOSE)
        self.toolbutton_clear.show()
        self.toolbutton_clear.set_tooltip_text('Delete download')
        self.toolbutton_clear.connect("clicked", self.on_clear)
        toolbar.insert(self.toolbutton_clear, 0)
        toolbar.insert(self.start_stop, 1)

        self.pack_start(self.label, True, False, 0)
        self.pack_start(self.progressbar, True, True, 0)
        self.pack_start(toolbar, False, False, 0)

    def set_state(self, state):
        stocks = [gtk.STOCK_MEDIA_PLAY, gtk.STOCK_MEDIA_STOP, gtk.STOCK_OK, gtk.STOCK_CANCEL]
        tooltips = ['Start download', 'Stop download', 'Clear download', 'Stopping']
        label_vis = [self.label.show, self.label.hide, self.label.show, self.label.hide]
        progr_vis = [self.progressbar.hide, self.progressbar.show, self.progressbar.hide, self.progressbar.show]
        if self._state != state:
            if state == self.STATE_READY:
                self.toolbutton_clear.show()
            else:
                self.toolbutton_clear.hide()
            self.start_stop.set_stock_id(stocks[state])
            self.start_stop.set_tooltip_text(tooltips[state])
            label_vis[state]()
            progr_vis[state]()
            self._state = state

    def on_start_stop(self, *a):
        if self._state == self.STATE_READY:
            """Start download"""
            self.start()
        elif self._state == self.STATE_DOWNLOAD:
            """Stop download"""
            self.stop()
        elif self._state == self.STATE_COMPLITE:
            """Clear download"""
            self.clear()

    def start(self):
        if self._state == self.STATE_READY:
            self.dm_thread_id = thread.start_new_thread(self.download_thread, ())
            self.set_state(self.STATE_DOWNLOAD)

    def stop(self):
        if self._state == self.STATE_DOWNLOAD:
            self.set_state(self.STATE_STOP_THREAD)

    def clear(self):
        if self._state == self.STATE_COMPLITE:
            self.hide()
            if self._on_clear:
                self._on_clear(self)

    def on_clear(self, *a):
        if self._state == self.STATE_READY:
            self.hide()
            if self._on_clear:
                self._on_clear(self)

    def download_thread(self):
        i = 0
        cur_size = 0
        while cur_size < self.total_size:
            self.url_report(i, self.speed, self.total_size)
            i += 1
            cur_size += self.speed
            time.sleep(self.ping)
            if self._state == self.STATE_STOP_THREAD:
                self.set_state(self.STATE_READY)
                return
        self.set_state(self.STATE_COMPLITE)

    def url_report(self, block_count, block_size, total_size):
        """Hook function for urllib.urlretrieve()"""

        """stop download
        if self._state == self.STATE_STOP_THREAD:
            thread.exit()
            self.set_state(self.STATE_READY)
            return"""

        """update info"""
        if total_size<=0:
            persent = 0.5
            total_size = "NaN"
        else:
            persent = block_count * block_size * 1.0 / total_size 
        self.progressbar.set_text("%s | %s / %s (%.2f%%)" % (self.bean.text, block_count * block_size ,
                                                           total_size, persent * 100))
        self.progressbar.set_fraction(persent)
