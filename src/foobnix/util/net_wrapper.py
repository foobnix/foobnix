#-*- coding: utf-8 -*-
'''
Created on 31 may 2011

@author: zavlab1
'''
import time
import thread
import logging

from threading import Thread
from subprocess import Popen, PIPE
from foobnix.helpers import dialog_entry

class NetWrapper():
    def __init__(self):
        self.flag = True
        self.is_connected = False
        thread.start_new_thread(self.ping, ())
            
    def ping(self):
        def task(sp):
            time.sleep(8)
            if sp.returncode == None: #mistake 'if not sp.returncode:'
                self.is_connected = False
                logging.debug("internet not connected sp.returncode")            
                sp.kill()
        
         
        while self.flag:
            sp = Popen(['ping', 'google.com', '-c 2'], stdout=PIPE, stderr=PIPE)
            timer = Thread(target=task, args=(sp,))    
            timer.start()
            out, err = sp.communicate()
            if err:
                self.is_connected = False
                logging.debug("internet not connected err")
            elif out:
                self.is_connected = True
            
            time.sleep(10)
    
    def _dialog(self):
        logging.warning("No internet connection")
        dialog_entry.info_dialog("Internet Connection", "Internet not available")
    
    def is_internet(self):
        if self.is_connected:
            return True
        else:
            self._dialog()
            return False
            
    def execute(self,func, *args):
        if self.is_connected:
            logging.info("Success internet connection")
            return func(*args) if args else func()
        else:
            self._dialog()
            return None