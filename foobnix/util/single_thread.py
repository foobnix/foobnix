#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''

import sys
import time
import thread
import logging
import traceback

from threading import Lock


class SingleThread():
    def __init__(self, spinner=None):
        self.lock = Lock()
        self.spinner = spinner

    def run_with_spinner(self, method, args=None, text='', no_thread=False):
        if no_thread:
            if method and args:
                method(args)
            if method:
                method()
        else:
            self._run(method, args, text)

    def _run(self, method, args=None, text=''):
        if self.lock.acquire(False):
            if self.spinner:
                self.spinner.start(text)
            thread.start_new_thread(self._thread_task, (method, args,))
        else:
            logging.warning("Previous thread not finished " + str(method) + " " + str(args))

    def _thread_task(self, method, args):
        try:
            if method and args:
                method(args)
            elif method:
                method()
        except Exception, e:
            logging.error(str(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        finally:
            if self.lock.locked():
                if self.spinner:
                    self.spinner.stop()
                self.lock.release()