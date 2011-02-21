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
from foobnix.fc.fc_helper import CONFIG_DIR

CACHE_FILE = os.path.join(CONFIG_DIR, "foobnix_cache.pkl")
COVERS_DIR = os.path.join(CONFIG_DIR, 'Covers')
LYRICS_DIR = os.path.join(CONFIG_DIR, 'Lirics')

"""Foobnix cache"""
class FCache:
    __metaclass__ = Singleton
    def __init__(self):
        self.covers = {}
        self.album_titles = {}
        
        self = self._load()
        
    def save(self, in_thread=True):
        if in_thread:
            thread.start_new_thread(FCacheHelper().save, (self,))
        else:
            FCacheHelper().save(self)
        
    def _load(self):
        """restore from file"""
        object = FCacheHelper().load()
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
        
class FCacheHelper():
    def __init__(self):
        pass

    def save(self, object):
        save_file = file(CACHE_FILE, 'w')
        try:
            cPickle.dump(object, save_file)
        except Exception, e:
            logging.error("Error dumping pickle cache config" + str(e))
        save_file.close()
        logging.debug("Cache config save")
        self.print_info(object);


    def load(self):
        if not os.path.exists(CACHE_FILE):
            logging.debug("Cache config file not found" + CACHE_FILE)
            return None

        with file(CACHE_FILE, 'r') as load_file:
            try:
                load_file = file(CACHE_FILE, 'r')
                pickled = load_file.read()

                object = cPickle.loads(pickled)
                logging.debug("Cache config loaded")
                self.print_info(object);
                return object
            except Exception, e:
                logging.error("Error load cache config" + str(e))
        return None
    
    def print_info(self, object):
        dict = object.__dict__
        for i in object.__dict__:
            logging.debug(i + str(dict[i])[:500])