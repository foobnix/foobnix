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
        self.set_size_request(20, -1)
        
        #self.hide()
        self.set_pulse_step(0.2)
        self.set_fraction(0)
        self.flag = True
        self.started = False
        self.set_text("...")

            
    def start(self, text):
        #self.progresbar.set_text(text)
        if self.started:
            return None
            
        self.show_all()        
        
        self.flag = True
        def pulse_thread(): 
            self.started = True          
            while self.flag:
                self.pulse()
                time.sleep(0.1)
            self.started = False
        thread.start_new_thread(pulse_thread, ())
    
    def stop(self):
        self.flag = False
        self.set_fraction(0)
        #self.hide()
