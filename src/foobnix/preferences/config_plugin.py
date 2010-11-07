#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
class ConfigPlugin():
    name = 'undefined'
    widget = "error"
    
    def show(self):
        self.widget.show()
    
    def hide(self):
        self.widget.hide()
    
    def on_load(self):
        pass
    
    def on_save(self):
        pass
    
    
