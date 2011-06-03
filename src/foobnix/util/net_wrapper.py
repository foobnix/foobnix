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
        self.stop = False
        self.start_ping()
        self.is_connected = False
        
    
    def start_ping(self):
        self.stop = False
        thread.start_new_thread(self.ping, ()) 
        
        """ OR USE SO METHOD (but thread must be only daemon thread):
        import threading
        ping_thread = threading.Thread(target=self.ping)
        ping_thread.daemon = True
        ping_thread.start()"""
        
        
    def stop_ping(self):
        self.stop = True
            
    def ping(self):
        def task(sp):
            time.sleep(10)
            if sp.returncode == None: #mistake 'if not sp.returncode:'
                sp.kill()
                self.set_connection(False)
                           
        list = ['ping', 'google.com', '-c 1']
        
        while True:
            if self.stop:
                return
            sp = Popen(list, stdout=PIPE, stderr=PIPE)
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
            logging.info("Connection to internet NOT exists")
            return None
        else:
            logging.info("connectioned to internet success")
            return func(*args) if args else func()