#-*- coding: utf-8 -*-
'''
Created on 27 сент. 2010

@author: ivan
'''
import gtk

class SearchProgressBar(gtk.Spinner):
    
    def __init__(self, controls):
        super(SearchProgressBar, self).__init__()
        self.hide()

    def start(self, trash=""):
        self.show()
        super(SearchProgressBar, self).start()
    
    def stop(self):
        super(SearchProgressBar, self).stop()
        self.hide()