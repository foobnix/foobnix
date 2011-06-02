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


CONNECTION = True

class ConnectionChecker():
    def __init__(self):
        self.stop = False
        #self.start_ping()
        
    
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
        def task():
            
            time.sleep(5)
            if sp.returncode == None: #mistake 'if not sp.returncode:'
                sp.kill()
                self.set_connection(False)
                           
        list = ['ping', 'google.com', '-c 4']
        
        while True:
            if self.stop:
                return
            sp = Popen(list, stdout=PIPE, stderr=PIPE)
            timer = Thread(target=task)    
            timer.start()
            out, err = sp.communicate()
            if err:
                self.set_connection(False)
            elif out:
                self.set_connection(True)
            time.sleep(2)
      
    def break_connection(self):
        self.stop_ping()
        self.connection = False
          
    def restore_connection(self):
        self.start_ping()
    
    def set_connection(self, to_connect):
        global CONNECTION
        CONNECTION = True if to_connect else False
        
    
def net_exec(func, *args):
    return func(*args) if args else func()
    if CONNECTION:
            logging.info("Connection to internet exists")
            #print "is", func, args
            return func(*args) if args else func()
    else:
            #print "not"
            logging.warning("no connection to internet")
            return func(*args) if args else func()