#-*- coding: utf-8 -*-
'''
Created on June 12 2011

@author: zavlab1
'''

import os
import time
import threading
from foobnix.fc.fc import FC

def antiscreensaver():
    def task():
        while FC().antiscreensaver:
            os.system("xscreensaver-command -deactivate &") 
            time.sleep(55)

    t = threading.Thread(target=task)
    t.daemon = True #this thread must be only deamonic, else python process can't finish"
    t.start()