#-*- coding: utf-8 -*-
'''
Created on 24 сент. 2010

@author: ivan
'''
"""common system bean"""
class FBean():
    TYPE_SONG = "SONG"
    TYPE_FOLDER = "FOLDER"
    
    def __init__(self, text=None, path=None, type=TYPE_SONG, play_icon=None, time=None):
        self.text = text        
        self.path = path
        self.type = type
        self.play_icon = play_icon
        self.time = time
