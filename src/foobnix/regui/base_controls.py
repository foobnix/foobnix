#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util.fc import FC
from foobnix.util import LOG
from foobnix.regui.state import LoadSave
class BaseFoobnixControls(LoadSave):
    def __init__(self):
        pass
        
    def append_to_notebook(self, text):
        self.notetabs.append_tab(text)
    
    def quit(self, *a):
        LOG.info("Controls - Quit")
        self.on_save()
        FC().save()
        
        gtk.main_quit()
    
    
    def on_load(self):
        for element in self.__dict__:
            self.__dict__[element].on_load()
            
    def on_save(self):
        for element in self.__dict__:
            self.__dict__[element].on_save()
