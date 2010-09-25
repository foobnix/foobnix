#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
class BaseFoobnixControls():
    def __init__(self):
        self.notetabs = None
        self.tree = None
        
    def append_to_notebook(self, text):
        self.notetabs.append_tab(text)
