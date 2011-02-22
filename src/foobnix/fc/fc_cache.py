#-*- coding: utf-8 -*-
'''
Created on 20 February 2010

@author: Dmitry Kogura (zavlab1)
'''

import os
import thread
import logging
import cPickle

from foobnix.util.singleton import Singleton
from foobnix.fc.fc_helper import FCHelper, CONFIG_DIR

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
        
        self = self._load()
        
    def save(self, in_thread=True):
        if in_thread:
            thread.start_new_thread(FCHelper().save, (self,))
        else:
            FCHelper().save(self)
        
    def _load(self):
        """restore from file"""
        object = FCHelper().load()
        if object:
            dict = object.__dict__
            keys = self.__dict__.keys()
            for i in dict:
                try:
                    if i in keys:
                        setattr(self, i, dict[i])
                except Exception, e:
                    logging.warn("Value not found" + str(e))
                    return False
        return True
