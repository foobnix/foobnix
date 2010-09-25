#-*- coding: utf-8 -*-
'''
Created on 24 сент. 2010

@author: ivan
'''
"""common system bean"""
class FBean():
    TYPE_SONG = "SONG"
    TYPE_FOLDER = "FOLDER"
    
    def __init__(self, text=None, path=None):
        self.text = text        
        self.path = path
        self.type = None
        self.play_icon = None
        self.time = None
        self.level = None
        self.font = None
        self.is_file = None
    
    def add_level(self, level):
        self.level = level
        return self 
    
    def add_font(self, font):
        self.font = font
        return self
    
    def add_is_file(self, is_file):
        self.is_file = is_file
        return self
    
    def add_play_icon(self, play_icon):
        self.play_icon = play_icon
        return self
