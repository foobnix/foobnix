#-*- coding: utf-8 -*-
'''
Created on 20 February 2010

@author: Dmitry Kogura (zavlab1)
'''

import os
from foobnix.util.singleton import Singleton
from foobnix.fc.fc_helper import CONFIG_DIR, FCStates

CACHE_FILE = os.path.join(CONFIG_DIR, "foobnix_cache.pkl")
COVERS_DIR = os.path.join(CONFIG_DIR, 'Covers')
LYRICS_DIR = os.path.join(CONFIG_DIR, 'Lirics')

"""Foobnix cache"""
class FCache:
    __metaclass__ = Singleton
    def __init__(self):
        self.covers = {}
        self.album_titles = {}
        
        """music library"""
        self.tab_names = [_("Empty tab"), ]
        self.last_music_path = None
        self.music_paths = [[], ]
        self.cache_music_tree_beans = [[], ]
        
        self.cache_virtual_tree_beans = []
        self.cache_radio_tree_beans = []
        self.cache_pl_tab_contents = []
        self.tab_pl_names = [_("Empty tab"), ]
        
        self.load()
        
    def save(self):
        FCStates().save(self, CACHE_FILE)
    
    def load(self):
        FCStates().load(self, CACHE_FILE)

       
