#-*- coding: utf-8 -*-
'''
Created on 31 may 2011

@author: zavlab1
'''

import base64
import socket
import threading
import logging

from gi.repository import Gtk

from foobnix.fc.fc import FC
from foobnix.helpers.window import MessageWindow
from foobnix.gui.service.lastfm_service import LastFmService
from foobnix.gui.state import Quitable
from foobnix.util import idle_task


class NetWrapper(Quitable):
    def __init__(self, contorls, is_ping=True):
        self.controls = contorls
        self.stopped_flag = threading.Event()
        self.stopped_flag.set()
        self.counter = 0 #to count how many times in row was disconnect
        self.dd_count = 0
        self.is_ping = None
        self.set_ping(is_ping)
        self.timeout = 7
        self.pause = 10
        self.is_connected = False
        "only for self.execute() method"
        self.previous_connect = True #show the message only if a connection existed and then there was a disconnect
        self.start_ping()

    def set_ping(self, is_ping=True):
        FC().net_ping = is_ping
        if not self.is_ping and is_ping:
            logging.info("ping enabled")
        elif self.is_ping and not is_ping:
            logging.info("ping disabled")
        self.is_ping = is_ping

    def start_ping(self):
        if not self.stopped_flag.is_set(): #means there is already one active ping process
            logging.warning("You may not have more one ping process simultaneously")
            return
        self.stopped_flag.clear()
        threading.Thread(target=self.ping).start()

    def stop_ping(self):
        self.stopped_flag.set()

    def on_quit(self):
        self.stop_ping()

    def ping(self):
        while not self.stopped_flag.is_set():
            if FC().proxy_enable and FC().proxy_url:
                try:
                    self.ping_with_proxy()
                except Exception as e:
                    logging.error(str(e))
                return
            s = socket.socket()
            s.settimeout(self.timeout)
            port = 80 #port number is a number, not string
            try:
                s.connect(('google.com', port))
                self.is_connected = True
                if not self.previous_connect:
                    self.restore_connection()
                self.previous_connect = True
                if self.is_ping:
                    logging.info("Success Internet connection")
                self.counter = 0
            except Exception as e:

                self.is_connected = False
                if self.is_ping:
                    logging.warning("Can\'t connect to Internet. Reason - " + str(e))
                self.counter += 1
                if self.counter == 2: #if disconnect was two times in row, show message
                    if self.previous_connect:
                        self.previous_connect = False
                        if self.is_ping:
                            self.disconnect_dialog()
                    self.counter = 0
            finally:
                s.close()

            self.stopped_flag.wait(self.pause)

    def ping_with_proxy(self):
        while not self.stopped_flag.is_set():
            if not FC().proxy_enable:
                self.ping()
                return
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            url="http://www.google.com:80/"
            index = FC().proxy_url.find(":")
            host = FC().proxy_url[:index]
            port = FC().proxy_url[index + 1:]
            auth = None
            if FC().proxy_user and FC().proxy_password:
                auth = base64.b64encode(FC().proxy_user + ":" + FC().proxy_password).strip()
            try:
                s.connect((host, int(port)))
                if auth:
                    s.send('GET %s HTTP/1.1' % url + '\r\n' + 'Proxy-Authorization: Basic %s' % auth + '\r\n\r\n')
                else:
                    s.send('GET %s HTTP/1.1' % url + '\r\n\r\n')
                data = s.recv(1024)
                s.close()
                if not data:
                    raise Exception("Can't get reply from " + url)
                if "407" in data:
                    raise Exception("Proxy Authentication Required")
                self.is_connected = True
                if not self.previous_connect:
                    self.restore_connection()
                self.previous_connect = True
                if self.is_ping:
                    logging.info("Success Internet connection")
                self.counter = 0
            except Exception as e:
                s.close()
                self.is_connected = False
                if self.is_ping:
                    logging.warning("Can\'t connect to Internet. Reason - " + str(e))
                self.counter += 1
                if self.counter == 2: #if disconnect was two times in row, show message
                    if self.previous_connect:
                        self.previous_connect = False
                        if self.is_ping:
                            self.disconnect_dialog()
                    self.counter = 0
            finally:
                s.close()

            self.stopped_flag.wait(self.pause)

    @idle_task
    def disconnect_dialog(self):
        # only one dialog must be shown
        if self.dd_count:
                logging.debug("one disconnect dialog is showing yet")
                return

        logging.info("Disconnect dialog is shown")
        self.dd_count += 1
        MessageWindow(title=_("Internet Connection"),
                      text=_("Foobnix not connected or Internet not available. Please try again a little bit later."),
                      parent=self.controls.main_window, buttons=Gtk.ButtonsType.OK)
        self.dd_count -= 1


    def is_internet(self):
        return True if self.is_connected else False

    def break_connection(self):
        self.stop_ping()
        self.is_connect = False

    def restore_connection(self):
        self.start_ping()
        logging.info("Try to restore connection")
        def task_restore_connection():
            #logging.info("Try to restore vk_service")
            #self.controls.vk_service = VKService(FC().access_token, FC().user_id)
            logging.info("Try to restore lastfm_service")
            self.controls.lastfm_service = LastFmService(self.controls)
        threading.Thread(target = task_restore_connection, args = ()).start()


    "wrapper for Internet function"
    def execute(self,func, *args):
        if not self.is_ping:
            return func(*args) if args else func()
        if self.is_connected:
            #self.previous_connect = True
            logging.info("In execute. Success internet connection")
            return func(*args) if args else func()
        else:
            logging.warning("In execute. No internet connection")
            return None

