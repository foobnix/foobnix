#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''
import gtk
from foobnix.regui.model.signal import FControl
import time
import thread
class SearchProgressBar(FControl, gtk.ProgressBar):
    def __init__(self, controls):
        FControl.__init__(self, controls)  
        gtk.ProgressBar.__init__(self)
        self.hide()
        
        self.flag = True
        
    def start(self, text):
        self.set_text(text)
        self.show()        
        self.flag = True
        def pulse_thread():
            while self.flag:
                self.pulse()
                time.sleep(0.1)
        thread.start_new_thread(pulse_thread, ())
    
    def stop(self):
        self.flag = False
        self.hide()
