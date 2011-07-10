#-*- coding: utf-8 -*-
'''
Created on 31 may 2011

@author: zavlab1
'''

import os
import gtk
import time
import socket
import thread
import logging

from foobnix.helpers.window import MessageWindow

class NetWrapper():
    def __init__(self, contorls, is_ping=True):
        self.controls = contorls
        self.flag = True
                
        "only for self.execute() method"
        self.previous_connect = False
        
        if os.name != 'nt':
            self.is_connected = False
            thread.start_new_thread(self.ping, ())
        else:
            self.is_connected = True
            thread.start_new_thread(self.ping, ())            
    
    def ping(self):
        while self.flag:
            s = socket.socket()
            s.settimeout(7.0)
            port = 80 # port number is a number, not string
            try:
                s.connect(('google.com', port))
                self.is_connected = True 
                logging.info("Success internet connection")
            except Exception, e:
                self.is_connected = False
                logging.warning("Can\'t connect to internet. Reason - " + str(e))
            time.sleep(3)
                
    def disconnect_dialog(self):
        def task():
            self.disconnect_message = MessageWindow(title=_("Internet Connection"), 
                                                text=_("Foobnix not connected or internet not available. Please try again a little bit later."),
                                                parent=self.controls.main_window, buttons=gtk.BUTTONS_OK)
        thread.start_new_thread(task, ())
        
    def is_internet(self):
        if self.is_connected:
            return True
        else:
            return False
            
    def execute(self,func, *args):
        if self.is_connected:
            self.previous_connect = True
            logging.info("In execute. Success internet connection")
            return func(*args) if args else func()
        else:
            if self.previous_connect:
                self.previous_connect = False
                self.disconnect_dialog()
            logging.warning("In execute. No internet connection")
            return None

