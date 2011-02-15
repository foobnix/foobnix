#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''
import gtk
import time
import thread

class SearchProgressBarOld(gtk.ProgressBar):
    def __init__(self):
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

if gtk.pygtk_version >= (2, 21, 0):
    class SearchProgressBarNew(gtk.Spinner):
        def __init__(self):
            super(SearchProgressBarNew, self).__init__()
            self.hide()
    
        def start(self, trash=""):
            self.show()
            super(SearchProgressBarNew, self).start()
        
        def stop(self):
            super(SearchProgressBarNew, self).stop()
            self.hide()
    class SearchProgressBar(SearchProgressBarNew):
        def __init__(self):
                SearchProgressBarNew.__init__(self)
else:
    class SearchProgressBar(SearchProgressBarOld):
        def __init__(self):
                SearchProgressBarOld.__init__(self)
