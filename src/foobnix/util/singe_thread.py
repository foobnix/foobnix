#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''
import thread
from threading import Lock
from foobnix.util import LOG
import time

class SingreThread():
    def __init__(self, progressbar):
        self.lock = Lock()
        self.progressbar = progressbar
    
    def run(self, method, args=None):
        if not self.lock.locked():            
            self.lock.acquire()            
            thread.start_new_thread(self.thread_task, (method, args,))
        else:
            LOG.warn("Thread not finished", method, args)
    
    def run_with_text(self, method, args, text):
        self.progressbar.start(text)
        self.run(method, args)
    
    def thread_task(self, method, args):
        try:
            if args:
                method(args)
            else:
                method()
            time.sleep(0.1)
        except Exception, e:
            LOG.error(e)
        finally:
            self.progressbar.stop()        
            self.lock.release()
