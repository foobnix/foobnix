#-*- coding: utf-8 -*-
'''
Created on 31 may 2011

@author: zavlab1
'''

import gtk
import time
import socket
import thread
import logging

from foobnix.helpers.window import MessageWindow

class NetWrapper():
    def __init__(self, contorls, is_ping=True):
        self.controls = contorls
        self.flag = False
        self.counter = 0 #to count how many times in row was disconnect
        self.is_connected = False        
        "only for self.execute() method"
        self.previous_connect = False #show the message only if a connection existed and then there was a disconnect
                       
        self.start_ping()
                  
    def start_ping(self):
        if self.flag: #means there is already one active ping process
            logging.warning("You may not have more one ping process simultaneously")
            return
        self.flag = True
        thread.start_new_thread(self.ping, ())
         
    def stop_ping(self):
        self.flag = False
            
    def ping(self):
        while self.flag:
            s = socket.socket()
            s.settimeout(7.0)
            port = 80 #port number is a number, not string
            try:
                s.connect(('google.com', port))
                self.is_connected = True
                self.previous_connect = True 
                logging.info("Success Internet connection")
                self.counter = 0
            except Exception, e:
                self.is_connected = False
                logging.warning("Can\'t connect to Internet. Reason - " + str(e))
                self.counter += 1
                if self.counter == 2: #if disconnect was two times in row, show message
                    if self.previous_connect:
                        self.previous_connect = False
                        self.disconnect_dialog()
                    self.counter = 0
            time.sleep(3)
               
    def disconnect_dialog(self):
        def task():
            MessageWindow(title=_("Internet Connection"), 
                          text=_("Foobnix not connected or Internet not available. Please try again a little bit later."),
                          parent=self.controls.main_window, buttons=gtk.BUTTONS_OK)
        thread.start_new_thread(task, ())
        
    def is_internet(self):
        return True if self.is_connected else False
    
    def break_connection(self):
        self.stop_ping()
        self.is_connect = False
            
    def restore_connection(self):   
        self.start_ping()
        
    "wrapper for Internet function"        
    def execute(self,func, *args):
        if self.is_connected:
            self.previous_connect = True
            logging.info("In execute. Success internet connection")
            return func(*args) if args else func()
        else:
            logging.warning("In execute. No internet connection")
            return None

