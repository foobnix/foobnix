#-*- coding: utf-8 -*-
'''
Created on 31 may 2011

@author: zavlab1
'''

import os
import time
import thread
import logging

from threading import Thread
from subprocess import Popen, PIPE
from foobnix.helpers import dialog_entry

class NetWrapper():
    def __init__(self, is_ping=True):
        self.flag = True
        self.is_connected = True
        
        if not is_ping:
            logging.debug("Ping functional is disabled")
            """disable net wrapper functional"""
            return
        
        """in win ping successfully works, but console with ping appears and hide periodically"""
        if os.name != 'nt':
            thread.start_new_thread(self.ping, ())
            
    def ping(self):
        def task(sp):
            i = 0
            while i < 10:
                if sp.poll():
                    return
                else:
                    i += 1
                    time.sleep(0.5)
            #if sp.returncode == None: #mistake 'if not sp.returncode:'
            if not self.out:
                self.is_connected = False
                logging.debug("internet is not connected \"not self.out\" ")            
                sp.kill()
        
        if os.name == 'nt':
            cmd = ['ping', 'google.com', '-n 2']
        else:
            cmd = ['ping', 'google.com', '-c 2']
         
        while self.flag:
            sp = Popen(cmd, stdout=PIPE, stderr=PIPE)
            timer = Thread(target=task, args=(sp,))    
            timer.start()
            self.out, self.error = sp.communicate()
            if self.error:
                self.is_connected = False
                logging.debug("internet is not connected - error")
            elif self.out:
                self.is_connected = True
            time.sleep(2)
    
    def _dialog(self):
        logging.warning("No internet connection")
        dialog_entry.info_dialog(_("Internet Connection"), _("Foobnix not connected \n or internet not available. \n Please try again a little bit later."))
    
    def is_internet(self):
        if self.is_connected:
            return True
        else:
            return False
            
    def execute(self,func, *args):
        if self.is_connected:
            logging.info("Success internet connection")
            return func(*args) if args else func()
        else:
            self._dialog()
            return None
