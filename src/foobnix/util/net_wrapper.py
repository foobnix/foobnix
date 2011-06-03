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

class NetWrapper():
    def __init__(self):
        self.flag = True
        self.start_ping()
        self.is_connected = False
        
    def start_ping(self):
        self.flag = True
        thread.start_new_thread(self.ping, ())
         
    def stop_ping(self):
        self.flag = False
            
    def ping(self):
        def task(sp):
            time.sleep(10)
            if sp.returncode == None: #mistake 'if not sp.returncode:'
                sp.kill()
                self.is_connected = False
                           
        sp = Popen(['ping', 'google.com', '-c 1'], stdout=PIPE, stderr=PIPE)
        while self.flag:
            timer = Thread(target=task, args=(sp,))    
            timer.start()
            out, err = sp.communicate()
            if err:
                self.is_connected = False
            elif out:
                self.is_connected = True
            
            time.sleep(20)
      
    def break_connection(self):
        self.stop_ping()
        self.connection = False
          
    def restore_connection(self):
        self.start_ping()
        
    def execute(self,func, *args):
        if not self.is_connected:
            logging.warning("No internet connection")
            return None
        else:
            logging.info("Success internet connection")
            return func(*args) if args else func()