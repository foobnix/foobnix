#-*- coding: utf-8 -*-
'''
Created on 21 февр. 2011

@author: ivan
'''

from __future__ import with_statement
import os
import logging
import cPickle
import threading

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "foobnix-3", "")
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "foobnix-3", "")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


class FCStates:
    def save(self, fc, file):
        #if in_thread:
        #    thread.start_new_thread(FCHelper().save, (fc,))
        #else:
        FCHelper().save(fc, file)

    def load(self, fc, file):
        """restore from file"""
        object = FCHelper().load(file)
        if object:
            dict = object.__dict__
            keys = fc.__dict__.keys()
            for i in dict:
                try:
                    if i in keys:
                        setattr(fc, i, dict[i])
                except Exception as e:
                    logging.warn("Value not found" + str(e))
                    return False
        return True

    def info(self):
        FCHelper().print_info(self)

    def delete(self, file_path):
        FCHelper().delete(file_path)


class FCHelper():
    def __init__(self):
        self.save_lock = threading.Lock()
        pass

    def save(self, object, file_path):
        self.save_lock.acquire()
        try:
            save_file = open(file_path, 'w')
            try:
                cPickle.dump(object, save_file)
            except Exception as e:
                logging.error("Error dumping pickle conf " + str(e))
            save_file.close()
            logging.debug("Config save")
            self.print_info(object)
        finally:
            if self.save_lock.locked():
                self.save_lock.release()

    def load(self, file_path):
        if not os.path.exists(file_path):
            logging.debug("Config file not found" + file_path)
            if not file_path.endswith("_backup"):
                logging.info("Try to load config backup")
                return self.load(file_path + "_backup")
            return None

        with open(file_path, 'r') as load_file:
                load_file = open(file_path, 'r')
                pickled = load_file.read()

                object = cPickle.loads(pickled)
                logging.debug("Config loaded")
                self.print_info(object)
                return object

        return None

    def delete(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def print_info(self, object):
        dict = object.__dict__
        for i in object.__dict__:
            if i not in ["user_id", "access_token", "vk_user", "vk_pass", "lfm_login", "lfm_password", "uuid"]:
                value = dict[i] if isinstance(dict[i], unicode) else str(dict[i])
                logging.debug(i + " " + value[:500])
