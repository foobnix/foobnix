#-*- coding: utf-8 -*-
'''
Created on 31 may 2011

@author: zavlab1
'''

import os
import gtk
import time
import thread
import logging

from threading import Thread
from subprocess import Popen, PIPE
from foobnix.helpers.window import MessageWindow

class NetWrapper():
    def __init__(self, contorls, is_ping=True):
        self.controls = contorls
        self.flag = True
        self.is_connected = True
        
        "only for self.execute() method"
        self.previous_connect = True
        
        if not is_ping:
            logging.debug("Ping functional is disabled")
            """disable net wrapper functional"""
            return
        
        """in win ping successfully works, but console with ping appears and hide periodically"""
        if os.name != 'nt':
            thread.start_new_thread(self.ping, ())
        else:
            self.is_connected = True
                        
    def ping(self):
        def task(sp):
            i = 0
            while i < 20:
                if sp.poll() != None:
                    return
                else:
                    i += 1
                    time.sleep(0.5)
            
            if not self.out:
                self.is_connected = False
                logging.debug("internet is not connected \"not self.out\" ")            
                sp.kill()
        
        if os.name == 'nt':
            cmd = ['ping', 'google.com', '-n 2']
        else:
            cmd = ['ping', 'google.com', '-c 2']
         
        while self.flag:
            self.out = None
            self.error = None
            sp = Popen(cmd, stdout=PIPE, stderr=PIPE)
            timer = Thread(target=task, args=(sp,))    
            timer.start()
            self.out, self.error = sp.communicate()
            if self.error:
                self.is_connected = False
                logging.debug("internet is not connected - error")
            elif self.out:
                if "100%" in self.out:
                    self.is_connected = False
                    logging.debug("internet is not connected - error")
                self.is_connected = True
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
            logging.info("Success internet connection")
            return func(*args) if args else func()
        else:
            if self.previous_connect:
                self.previous_connect = False
                self.disconnect_dialog()
            logging.warning("No internet connection")
            return None
