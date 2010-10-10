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
        self.bean = dmbean.bean
        self._stop = threading.Event()

    def run(self):
        block_size = 4096
        block_count = 0
        try:
            gtk.gdk.threads_enter()
            self.dmbean.pb_text = _('VK search...')
            self.dmbean.update()
            gtk.gdk.threads_leave()
            if not self.bean.path and not self.dmbean.do_fill_from_vk():
                raise DMThreadVKException()
            gtk.gdk.threads_leave()
            if (not self.bean.path.lower().startswith('http://')
                or not self.bean.path.lower().endswith('.mp3')):
                raise DMThreadURLException()
            if self.bean.title:
                save_name = self.bean.title + '.mp3'
            else:
                save_name = os.path.basename(urllib.url2pathname(self.bean.path))
            remote_size = -1
            self.loader = Range_url_opener(self.dmbean, self)
            if not os.path.exists(self.dmbean.save_path):
                os.makedirs(self.dmbean.save_path)
            fname = os.path.join(self.dmbean.save_path, save_name)
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
                    gtk.gdk.threads_enter()
                    self.dmbean.url_report(block_count, block_size, remote_size)
                    gtk.gdk.threads_leave()
            self.remote_handler.close()
            file_handler.close()
        except IOError, e:
            if os.path.isfile(fname + '.tmp'):
                os.unlink(fname + '.tmp')
            gtk.gdk.threads_enter()
            self.dmbean.set_error(e.strerror)
            self.dmbean.state_ready()
            gtk.gdk.threads_leave()
        except DMThreadException, e:
            if os.path.isfile(fname + '.tmp'):
                os.unlink(fname + '.tmp')
            gtk.gdk.threads_enter()
            self.dmbean.set_error(e.message)
            self.dmbean.state_ready()
            gtk.gdk.threads_leave()
        else:
            if not self._stop.isSet():
                os.rename(fname + '.tmp', fname)
                gtk.gdk.threads_enter()
                self.dmbean.state_complite()
                gtk.gdk.threads_leave()
            else:
                os.unlink(fname + '.tmp')
                gtk.gdk.threads_enter()
                self.dmbean.state_ready()
                gtk.gdk.threads_leave()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

class DMBean(gtk.HBox):
    STATE_READY = 0
    STATE_DOWNLOAD = 1
    STATE_COMPLITE = 2
    STATE_STOP_THREAD = 3
    def __init__(self, bean, save_path):
        gtk.HBox.__init__(self, False, 0)
        self.bean = bean
        self.save_path = os.path.join(save_path,
            bean.artist if bean.artist else '',
            bean.album if bean.album else '')
        self.save_name = None
        self.thread = None
        self.label = gtk.Label(bean.text)
        self.label.show()
        self.error = ''
        self.enable = True

        self.progressbar = gtk.ProgressBar()
        self.pb_text = ''
        self.pb_fraction = 0.0
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
        self.start_stop.set_tooltip_text(_('Start download'))
        self.start_stop.connect("clicked", self.on_start_stop)
        self.toolbutton_clear = gtk.ToolButton(gtk.STOCK_CLOSE)
        self.toolbutton_clear.show()
        self.toolbutton_clear.set_tooltip_text(_('Delete download'))
        self.toolbutton_clear.connect("clicked", self.on_clear_click)
        toolbar.insert(self.toolbutton_clear, 0)
        toolbar.insert(self.start_stop, 1)
        self.state_ready()

        self.pack_start(self.label, True, False, 0)
        self.pack_start(self.progressbar, True, True, 0)
        self.pack_start(toolbar, False, False, 0)

    def state_ready(self):
        if self.thread and not self.thread.stopped():
            self.thread.stop()
        if self.thread:
            self.on_stopped(self)
        self.thread = DMThread(self)
        self.set_state(self.STATE_READY)

    def state_download(self):
        self.set_state(self.STATE_DOWNLOAD)
        self.on_start(self)
        self.thread.start()

    def state_complite(self):
        self.set_state(self.STATE_COMPLITE)
        self.thread = None
        self.on_complite(self)

    def state_stop_thread(self):
        self.set_state(self.STATE_STOP_THREAD)
        self.thread.stop()

    def set_state(self, state):
        if self._state != state:
            self._state = state
        self.update()

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
        if self._state == self.STATE_READY and self.enable:
            self.state_download()

    def get_url(self):
        return self.bean.path

    def stop(self):
        if self._state == self.STATE_DOWNLOAD:
            self.state_stop_thread()

    def clear(self):
        if self._state == self.STATE_COMPLITE:
            self.on_clear(self, False)

    def on_clear_click(self, *a):
        if self._state == self.STATE_READY:
            self.on_clear(self, True)

    def on_clear(self, dmbean, wait):
        pass

    def on_complite(self, dmbean):
        pass

    def on_stopped(self, dmbean):
        pass

    def on_start(self, dmbean):
        pass

    def fill_bean_from_vk(self, bean):
        return False

    def do_fill_from_vk(self):
        return self.fill_bean_from_vk(self.bean)

    def is_ready(self):
        return self._state == self.STATE_READY

    def is_download(self):
        return self._state == self.STATE_DOWNLOAD

    def is_complite(self):
        return self._state == self.STATE_COMPLITE

    def url_report(self, block_count, block_size, total_size):
        """Hook function for urllib.urlretrieve()"""
        if total_size<=0:
            persent = 0.5
            total_size = "NaN"
        else:
            persent = block_count * block_size * 1.0 / total_size
            if persent > 1.0: persent = 1.0
        self.pb_text = "%s | %s / %s (%.2f%%)" % (self.bean.text, size2text(block_count * block_size),
                                                  size2text(total_size), persent * 100)
        self.pb_fraction = persent
        self.update()

    def update(self):
        """update info"""
        stocks = [gtk.STOCK_MEDIA_PLAY, gtk.STOCK_MEDIA_STOP, gtk.STOCK_OK, gtk.STOCK_CANCEL]
        tooltips = [_('Start download'), _('Stop download'), _('Clear download'), _('Stopping')]
        label_vis = [self.label.show, self.label.hide, self.label.show, self.label.hide]
        progr_vis = [self.progressbar.hide, self.progressbar.show, self.progressbar.hide, self.progressbar.show]
        if self._state == self.STATE_READY:
            self.toolbutton_clear.show()
        else:
            self.toolbutton_clear.hide()
        self.start_stop.set_stock_id(stocks[self._state])
        self.start_stop.set_tooltip_text(tooltips[self._state])
        if self._state == self.STATE_READY:
            if self.enable:
                self.start_stop.show()
            else:
                self.start_stop.hide()
        else:
            self.start_stop.show()
        label_vis[self._state]()
        progr_vis[self._state]()
        self.progressbar.set_text(self.pb_text)
        self.progressbar.set_fraction(self.pb_fraction)
        self.label.set_text(self.bean.text + self.error)

    def set_error(self, error):
        if error:
            self.error = ' (%s)' % error
        else:
            self.error = ''

def size2text(size):
    if size > 1024*1024*1024:
        return _("%.2f Gb") % (size / (1024*1024*1024.0))
    if size > 1024*1024:
        return _("%.2f Mb") % (size / (1024*1024.0))
    if size > 1024:
        return _("%.2f Kb") % (size / 1024.0)
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
		raise DMThreadHTTPException(401)

	def http_error_403(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		raise DMThreadHTTPException(403)

	def http_error_404(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		raise DMThreadHTTPException(404)

	def http_error_405(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		raise DMThreadHTTPException(405)

	def http_error_408(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		raise DMThreadHTTPException(408)

	def http_error_500(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		raise DMThreadHTTPException(500)

	def http_error_503(self, url, fp, errcode, errmsg, headers, data=None):
		self.thread.stop()
		raise DMThreadHTTPException(503)

class DMThreadException(Exception):
    def _get_message(self):
        return self._message

    def _set_message(self, message):
        self._message = message

    message = property(_get_message, _set_message)

class DMThreadHTTPException(DMThreadException):
    def __init__(self, id):
        DMThreadError.__init__(self)
        self.id = id
        errors = {401: _("[401] Unauthorized"),
                  403: _("[403] Forbidden"),
                  404: _("[404] Not found"),
                  405: _("[405] Method not allowed"),
                  408: _("[408] Request time-out"),
                  500: _("[500] Internal Server Error"),
                  503: _("[503] Service unavailable")}
        if id in errors:
            self._set_message(errors[id])
        else:
            self._set_message(_('[%d] HTTP Error') % id)

class DMThreadVKException(DMThreadException):
    def __init__(self):
        self._set_message(_('Error: VK search failed'))

class DMThreadURLException(DMThreadException):
    def __init__(self):
        self._set_message(_('Error: wrong URL'))
