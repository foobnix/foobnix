#-*- coding: utf-8 -*-
'''
Created on Oct 4, 2010

@author: anton.komolov
'''
import gtk
import random
import threading
import time
import urllib
import os

class DMThread(threading.Thread):
    def __init__(self, dmbean):
        threading.Thread.__init__(self)
        self.dmbean = dmbean
        self._stop = threading.Event()

    def run(self):
        block_size = 4096
        block_count = 0
        try:
            remote_size = -1
            self.loader = Range_url_opener(self.dmbean, self)
            if not os.path.exists(self.dmbean.save_path):
                os.makedirs(self.dmbean.save_path)
            fname = os.path.join(self.dmbean.save_path, self.dmbean.save_name)
            file_handler = open(fname + '.tmp',"wb")
            local_size = 0
            self.remote_handler = self.loader.open(self.dmbean.get_url())
            if "Content-Length" in self.remote_handler.headers:
                remote_size = int(self.remote_handler.headers["Content-Length"])
            data = True
            while data and not self._stop.isSet():
                data = self.remote_handler.read(block_size)
                if data:
                    block_count += 1
                    file_handler.write(data)
                    self.dmbean.url_report(block_count, block_size, remote_size)
            self.remote_handler.close()
            file_handler.close()
        except Exception, e:
            self.dmbean.state_ready()
        else:
            if not self._stop.isSet():
                os.rename(fname + '.tmp', fname)
                self.dmbean.state_complite()
            else:
                self.dmbean.state_ready()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

class DMBean(gtk.HBox):
    STATE_READY = 0
    STATE_DOWNLOAD = 1
    STATE_COMPLITE = 2
    STATE_STOP_THREAD = 3
    def __init__(self, bean, save_path, on_clear, vk_search):
        gtk.HBox.__init__(self, False, 0)
        self._on_clear = on_clear
        self._vk_search = vk_search
        self.bean = bean
        self.save_path = os.path.join(save_path, bean.artist if bean.artist else '',
            bean.album if bean.album else '')
        self.save_name = None
        self.thread = None
        self.label = gtk.Label(bean.text)
        self.label.show()

        self.progressbar = gtk.ProgressBar()
        if bean.path:
            self.progressbar.set_text(bean.path)
        else:
            self.progressbar.set_text(bean.text)
        self.progressbar.hide()

        toolbar = gtk.Toolbar()
        toolbar.show()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_show_arrow(False)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)

        self._state = None
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
        self.state_ready()

        self.pack_start(self.label, True, False, 0)
        self.pack_start(self.progressbar, True, True, 0)
        self.pack_start(toolbar, False, False, 0)

    def state_ready(self):
        if self.thread and not self.thread.stopped():
            self.thread.stop()
        self.thread = DMThread(self)
        self.set_state(self.STATE_READY)

    def state_download(self):
        self.set_state(self.STATE_DOWNLOAD)
        self.thread.start()

    def state_complite(self):
        self.set_state(self.STATE_COMPLITE)
        self.thread = None

    def state_stop_thread(self):
        self.set_state(self.STATE_STOP_THREAD)
        self.thread.stop()

    def set_state(self, state):
        stocks = [gtk.STOCK_MEDIA_PLAY, gtk.STOCK_MEDIA_STOP, gtk.STOCK_OK, gtk.STOCK_CANCEL]
        tooltips = ['Start download', 'Stop download', 'Clear download', 'Stopping']
        label_vis = [self.label.show, self.label.hide, self.label.show, self.label.hide]
        progr_vis = [self.progressbar.hide, self.progressbar.show, self.progressbar.hide, self.progressbar.show]
        if self._state != state:
            gtk.gdk.threads_enter()
            if state == self.STATE_READY:
                self.toolbutton_clear.show()
            else:
                self.toolbutton_clear.hide()
            self.start_stop.set_stock_id(stocks[state])
            self.start_stop.set_tooltip_text(tooltips[state])
            label_vis[state]()
            progr_vis[state]()
            self._state = state
            gtk.gdk.threads_leave()

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
            if not self.bean.path:
                if not self._vk_search(self.bean):
                    self.label.set_text(self.bean.text + ' (Error: VK search failed)')
                    return False
            if (not self.bean.path.lower().startswith('http://')
                or not self.bean.path.lower().endswith('.mp3')):
                self.label.set_text(self.bean.text + ' (Error: wrong URL)')
                return False
            if self.bean.title:
                self.save_name = self.bean.title + '.mp3'
            else:
                self.save_name = os.path.basename(urllib.url2pathname(url))
            self.state_download()

    def get_url(self):
        return self.bean.path

    def stop(self):
        if self._state == self.STATE_DOWNLOAD:
            self.state_stop_thread()

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

    def url_report(self, block_count, block_size, total_size):
        """Hook function for urllib.urlretrieve()"""

        """stop download
        if self._state == self.STATE_STOP_THREAD:
            thread.exit()
            self.set_state(self.STATE_READY)
            return"""

        """update info"""
        gtk.gdk.threads_enter()
        if total_size<=0:
            persent = 0.5
            total_size = "NaN"
        else:
            persent = block_count * block_size * 1.0 / total_size
            if persent > 1.0: persent = 1.0
        self.progressbar.set_text("%s | %s / %s (%.2f%%)" % (self.bean.text, size2text(block_count * block_size),
                                                             size2text(total_size), persent * 100))
        self.progressbar.set_fraction(persent)
        gtk.gdk.threads_leave()

    def set_http_error(self, id):
        gtk.gdk.threads_enter()
        self.label.set_text(self.bean.text + ' (HTTP Error: %s)' % id)
        gtk.gdk.threads_leave()

def size2text(size):
    if size > 1024*1024*1024:
        return "%.2f Gb" % (size / (1024*1024*1024.0))
    if size > 1024*1024:
        return "%.2f Mb" % (size / (1024*1024.0))
    if size > 1024:
        return "%.2f Kb" % (size / 1024.0)
    return size

class Range_url_opener(urllib.FancyURLopener):
	def __init__(self, dmbean, thread):
		urllib.FancyURLopener.__init__(self)
		self.dmbean = dmbean
		self.thread = thread

	def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
		pass

	def http_error_401(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		self.dmbean.set_http_error(401)

	def http_error_403(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		self.dmbean.set_http_error(403)

	def http_error_404(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		self.dmbean.set_http_error(404)

	def http_error_405(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		self.dmbean.set_http_error(405)

	def http_error_408(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		self.dmbean.set_http_error(408)

	def http_error_500(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		self.dmbean.set_http_error(500)

	def http_error_503(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		self.dmbean.set_http_error(503)
