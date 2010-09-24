#-*- coding: utf-8 -*-
'''
Created on 24 сент. 2010

@author: ivan
'''
"""common system bean"""
class FBean():
    TYPE_SONG = "SONG"
    TYPE_FOLDER = "FOLDER"
    
    def __init__(self):
        self.path = None
        self.type = None 
    
    def song(self, path):
        self.type = self.TYPE_SONG
        self.path = path
        
        
    def folder(self, path):
        self.type = self.TYPE_FOLDER
        self.path = path
