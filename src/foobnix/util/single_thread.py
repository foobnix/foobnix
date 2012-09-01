#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''
import time
import thread
import logging

from threading import Lock


class SingleThread():
    def __init__(self, progressbar=None):
        self.lock = Lock()
        self.progressbar = progressbar
        
    def run_with_progressbar(self, method, args=None, text=None, no_thread=False, with_lock=True):
        #with_lock - shows, does it necessarily to do a lock or not
        
        if no_thread:
            if method and args:
                method(args)
            if method:
                method()
        else:
            self._run(method, args, text, with_lock)
                
    def _run(self, method, args=None, text=None, with_lock=True):
        if not self.lock.locked():            
            self.lock.acquire()
            if self.progressbar:
                self.progressbar.start(text)
            thread.start_new_thread(self._thread_task, (method, args,))
        else:
            logging.warning("Previous thread not finished " + str(method) + " " + str(args))
            if not with_lock:
                logging.info("Try to run method without progress bar")
                thread.start_new_thread(self._thread_task, (method, args))  
    
    def _thread_task(self, method, args, with_lock=True):
        try:
            if method and args:
                method(args)
            elif method:
                method()
            time.sleep(0.1)
        except Exception, e:
            logging.error(str(e))
        finally:
            if self.lock.locked():
                if self.progressbar:
                    self.progressbar.stop()        
                self.lock.release()
            